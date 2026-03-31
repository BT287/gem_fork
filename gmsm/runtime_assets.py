import hashlib
import html
import http.cookiejar
import json
import os
import re
import shutil
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path


_LFS_POINTER_PREFIX = b"version https://git-lfs.github.com/spec/v1"
_DEFAULT_ASSET_ROOT_NAME = ".runtime-assets"
_DEFAULT_MANIFEST_RELPATH = "scripts/runtime_assets_manifest.json"


def get_repo_root():
    return Path(__file__).resolve().parent.parent


def get_default_manifest_path():
    return get_repo_root() / _DEFAULT_MANIFEST_RELPATH


def get_runtime_asset_root():
    configured = os.environ.get("GMSM_RUNTIME_ASSET_ROOT")
    if configured:
        return Path(configured).expanduser().resolve()
    return get_repo_root() / _DEFAULT_ASSET_ROOT_NAME


def _normalize_repo_relative_path(path):
    path = str(path)
    if os.path.isabs(path):
        try:
            return Path(path).resolve().relative_to(get_repo_root()).as_posix()
        except ValueError:
            return Path(path).name

    while path.startswith("./"):
        path = path[2:]
    return path


def _repo_abspath(path):
    path = str(path)
    if os.path.isabs(path):
        return Path(path).resolve()
    return (get_repo_root() / _normalize_repo_relative_path(path)).resolve()


def is_lfs_pointer_file(path):
    candidate = Path(path)
    if not candidate.is_file():
        return False

    try:
        with candidate.open("rb") as handle:
            return handle.read(len(_LFS_POINTER_PREFIX)) == _LFS_POINTER_PREFIX
    except OSError:
        return False


def resolve_runtime_asset_path(path, asset_root=None):
    original_path = _repo_abspath(path)
    if original_path.is_file() and not is_lfs_pointer_file(original_path):
        return original_path

    root = Path(asset_root) if asset_root else get_runtime_asset_root()
    cached_path = root / _normalize_repo_relative_path(path)
    if cached_path.is_file() and not is_lfs_pointer_file(cached_path):
        return cached_path

    return original_path


def runtime_asset_missing_message(path):
    return (
        "Required runtime asset is missing or still an unresolved Git LFS pointer: "
        f"{path}. Run `python scripts/fetch_runtime_assets.py` to materialize "
        "the external runtime assets."
    )


def load_runtime_asset_manifest(manifest_path=None):
    manifest_path = Path(manifest_path) if manifest_path else get_default_manifest_path()
    with manifest_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def compute_sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _build_drive_opener():
    cookie_jar = http.cookiejar.CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))


def _stream_response_to_path(response, destination):
    with open(destination, "wb") as handle:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            handle.write(chunk)


def _parse_google_drive_confirm_form(html_text):
    action_match = re.search(r'<form[^>]+action="([^"]+)"', html_text)
    confirm_match = re.search(r'name="confirm" value="([^"]+)"', html_text)
    uuid_match = re.search(r'name="uuid" value="([^"]+)"', html_text)

    if not action_match or not confirm_match:
        return None

    params = {
        "confirm": html.unescape(confirm_match.group(1)),
    }
    if uuid_match:
        params["uuid"] = html.unescape(uuid_match.group(1))

    return {
        "action": html.unescape(action_match.group(1)),
        "params": params,
    }


def _download_google_drive_asset(file_id, destination):
    opener = _build_drive_opener()
    initial_url = f"https://drive.google.com/uc?export=download&id={file_id}"
    request = urllib.request.Request(initial_url, headers={"User-Agent": "Mozilla/5.0"})

    with opener.open(request, timeout=60) as response:
        content_disposition = response.getheader("Content-Disposition") or ""
        content_type = response.getheader("Content-Type") or ""

        if "attachment;" in content_disposition.lower() or content_type == "application/octet-stream":
            _stream_response_to_path(response, destination)
            return

        html_text = response.read().decode("utf-8", "ignore")

    parsed = _parse_google_drive_confirm_form(html_text)
    if parsed is None:
        raise RuntimeError(f"Could not resolve Google Drive download confirmation for file id {file_id}")

    params = {
        "id": file_id,
        "export": "download",
        **parsed["params"],
    }
    confirmed_url = parsed["action"] + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(confirmed_url, headers={"User-Agent": "Mozilla/5.0"})
    with opener.open(request, timeout=60) as response:
        _stream_response_to_path(response, destination)


def download_asset(source, destination):
    source_type = source["type"]
    if source_type != "google_drive":
        raise ValueError(f"Unsupported runtime asset source type: {source_type}")

    _download_google_drive_asset(source["file_id"], destination)


def _copy_repo_materialized_asset(asset, destination):
    repo_path = _repo_abspath(asset["target_relpath"])
    if not repo_path.is_file() or is_lfs_pointer_file(repo_path):
        return False
    if compute_sha256(repo_path) != asset["sha256"]:
        return False

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(repo_path, destination)
    return True


def fetch_runtime_assets(manifest_path=None, asset_root=None, force=False):
    manifest = load_runtime_asset_manifest(manifest_path)
    root = Path(asset_root) if asset_root else get_runtime_asset_root()
    results = []

    for asset in manifest["assets"]:
        destination = root / asset["target_relpath"]
        destination.parent.mkdir(parents=True, exist_ok=True)

        if destination.is_file() and not force:
            current_digest = compute_sha256(destination)
            if current_digest == asset["sha256"]:
                results.append({"name": asset["name"], "status": "cached", "path": str(destination)})
                continue

        if _copy_repo_materialized_asset(asset, destination):
            results.append({"name": asset["name"], "status": "mirrored-from-repo", "path": str(destination)})
            continue

        tmp_handle, tmp_path = tempfile.mkstemp(prefix="runtime-asset-", suffix="-" + Path(asset["target_relpath"]).name)
        os.close(tmp_handle)
        try:
            download_asset(asset["source"], tmp_path)
            digest = compute_sha256(tmp_path)
            if digest != asset["sha256"]:
                raise RuntimeError(
                    f"Checksum mismatch for {asset['name']}: expected {asset['sha256']}, got {digest}"
                )
            shutil.move(tmp_path, destination)
            results.append({"name": asset["name"], "status": "downloaded", "path": str(destination)})
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    return {
        "asset_root": str(root),
        "assets": results,
    }

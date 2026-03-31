#!/usr/bin/env python

import argparse
import hashlib
import json
import shutil
import tempfile
import urllib.request
import zipfile
from pathlib import Path


DEFAULT_VERSION = "2.1.24"
DEFAULT_URL = (
    "https://github.com/bbuchfink/diamond/releases/download/"
    f"v{DEFAULT_VERSION}/diamond-windows.zip"
)
DEFAULT_SHA256 = "905381f00990bffa0932d1ec81a4c833107b8fc06d5bdbbd9e9a81981586339c"


def repo_root():
    return Path(__file__).resolve().parent.parent


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ensure_sha256(path, expected_sha256):
    actual = sha256_file(path)
    if actual != expected_sha256:
        raise ValueError(
            "SHA256 mismatch for %s: expected %s but found %s"
            % (path, expected_sha256, actual)
        )
    return actual


def download_file(url, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url) as response, destination.open("wb") as handle:
        shutil.copyfileobj(response, handle)


def extract_diamond_exe(zip_path, destination_dir):
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / "diamond.exe"
    with zipfile.ZipFile(zip_path) as archive:
        member_name = None
        for info in archive.infolist():
            if info.is_dir():
                continue
            if Path(info.filename).name.lower() == "diamond.exe":
                member_name = info.filename
                break
        if member_name is None:
            raise FileNotFoundError("diamond.exe not found in %s" % zip_path)
        with archive.open(member_name) as source, destination.open("wb") as target:
            shutil.copyfileobj(source, target)
    return destination


def install_diamond(dest_dir, url, expected_sha256, force=False):
    destination_dir = Path(dest_dir).resolve()
    destination = destination_dir / "diamond.exe"
    if destination.is_file() and not force:
        return {
            "status": "reused",
            "diamond_path": str(destination),
            "download_url": url,
        }

    with tempfile.TemporaryDirectory() as tmp_dir:
        archive_path = Path(tmp_dir) / "diamond-windows.zip"
        download_file(url, archive_path)
        archive_sha256 = ensure_sha256(archive_path, expected_sha256)
        extracted = extract_diamond_exe(archive_path, destination_dir)

    return {
        "status": "installed",
        "diamond_path": str(extracted),
        "download_url": url,
        "archive_sha256": archive_sha256,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Download the official DIAMOND Windows release and install diamond.exe into bin/."
    )
    parser.add_argument(
        "--dest-dir",
        default=str(repo_root() / "bin"),
        help="Destination directory for diamond.exe (default: repo-root/bin)",
    )
    parser.add_argument(
        "--url",
        default=DEFAULT_URL,
        help="Download URL for the DIAMOND Windows zip",
    )
    parser.add_argument(
        "--sha256",
        default=DEFAULT_SHA256,
        help="Expected SHA256 for the downloaded DIAMOND Windows zip",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Redownload and overwrite diamond.exe even if it already exists",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the installation report as JSON",
    )
    args = parser.parse_args()

    report = install_diamond(
        dest_dir=args.dest_dir,
        url=args.url,
        expected_sha256=args.sha256,
        force=args.force,
    )
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("status: %s" % report["status"])
        print("diamond_path: %s" % report["diamond_path"])
        print("download_url: %s" % report["download_url"])
        if "archive_sha256" in report:
            print("archive_sha256: %s" % report["archive_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

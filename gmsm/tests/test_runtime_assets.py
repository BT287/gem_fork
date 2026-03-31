import pickle
from pathlib import Path

from gmsm import utils
from gmsm import runtime_assets


def test_is_lfs_pointer_file_detects_pointer(tmp_path):
    pointer = tmp_path / "pointer.p"
    pointer.write_text(
        "version https://git-lfs.github.com/spec/v1\n"
        "oid sha256:deadbeef\n"
        "size 123\n",
        encoding="utf-8",
    )

    assert runtime_assets.is_lfs_pointer_file(pointer)


def test_resolve_runtime_asset_path_uses_cache_when_repo_file_is_pointer(tmp_path, monkeypatch):
    repo_root = tmp_path / "repo"
    asset_root = tmp_path / "cache"
    repo_target = repo_root / "gmsm/io/data/input2/mnxm_compoundInfo_dict.p"
    cache_target = asset_root / "gmsm/io/data/input2/mnxm_compoundInfo_dict.p"

    repo_target.parent.mkdir(parents=True, exist_ok=True)
    cache_target.parent.mkdir(parents=True, exist_ok=True)

    repo_target.write_text(
        "version https://git-lfs.github.com/spec/v1\n"
        "oid sha256:deadbeef\n"
        "size 123\n",
        encoding="utf-8",
    )
    cache_target.write_bytes(b"real-binary-payload")

    monkeypatch.setattr(runtime_assets, "get_repo_root", lambda: repo_root)

    resolved = runtime_assets.resolve_runtime_asset_path(
        "./gmsm/io/data/input2/mnxm_compoundInfo_dict.p",
        asset_root=asset_root,
    )

    assert resolved == cache_target.resolve()


def test_parse_google_drive_confirm_form_extracts_action_and_tokens():
    html = """
    <form id="download-form" action="https://drive.usercontent.google.com/download" method="get">
      <input type="hidden" name="id" value="FILE_ID">
      <input type="hidden" name="export" value="download">
      <input type="hidden" name="confirm" value="t">
      <input type="hidden" name="uuid" value="abc-123">
    </form>
    """

    parsed = runtime_assets._parse_google_drive_confirm_form(html)

    assert parsed == {
        "action": "https://drive.usercontent.google.com/download",
        "params": {
            "confirm": "t",
            "uuid": "abc-123",
        },
    }


def test_runtime_asset_missing_message_points_to_fetch_script():
    message = runtime_assets.runtime_asset_missing_message(
        "./gmsm/io/data/input2/mnxm_compoundInfo_dict.p"
    )

    assert "fetch_runtime_assets.py" in message


def test_load_legacy_pickle_uses_cached_asset_when_repo_file_is_pointer(tmp_path, monkeypatch):
    repo_root = tmp_path / "repo"
    asset_root = tmp_path / "cache"
    repo_target = repo_root / "gmsm/io/data/input2/mnxm_compoundInfo_dict.p"
    cache_target = asset_root / "gmsm/io/data/input2/mnxm_compoundInfo_dict.p"

    repo_target.parent.mkdir(parents=True, exist_ok=True)
    cache_target.parent.mkdir(parents=True, exist_ok=True)

    repo_target.write_text(
        "version https://git-lfs.github.com/spec/v1\n"
        "oid sha256:deadbeef\n"
        "size 123\n",
        encoding="utf-8",
    )
    with cache_target.open("wb") as handle:
        pickle.dump({"ok": True}, handle, protocol=pickle.HIGHEST_PROTOCOL)

    monkeypatch.setattr(runtime_assets, "get_repo_root", lambda: repo_root)
    monkeypatch.setenv("GMSM_RUNTIME_ASSET_ROOT", str(asset_root))

    loaded = utils.load_legacy_pickle("./gmsm/io/data/input2/mnxm_compoundInfo_dict.p")

    assert loaded == {"ok": True}

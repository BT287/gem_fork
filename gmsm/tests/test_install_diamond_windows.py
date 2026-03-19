import zipfile
from pathlib import Path

import pytest

from scripts import install_diamond_windows


def test_extract_diamond_exe_from_nested_zip(tmp_test_dir):
    tmp_path = Path(tmp_test_dir)
    archive_path = tmp_path / "diamond-windows.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("diamond-v2.1.24/diamond.exe", b"windows-binary")
        archive.writestr("diamond-v2.1.24/README.txt", b"notes")

    destination = install_diamond_windows.extract_diamond_exe(archive_path, tmp_path / "bin")

    assert destination.name == "diamond.exe"
    assert destination.read_bytes() == b"windows-binary"


def test_ensure_sha256_accepts_matching_hash(tmp_test_dir):
    tmp_path = Path(tmp_test_dir)
    file_path = tmp_path / "diamond-windows.zip"
    file_path.write_bytes(b"diamond-data")

    actual = install_diamond_windows.sha256_file(file_path)

    assert install_diamond_windows.ensure_sha256(file_path, actual) == actual


def test_ensure_sha256_rejects_mismatch(tmp_test_dir):
    tmp_path = Path(tmp_test_dir)
    file_path = tmp_path / "diamond-windows.zip"
    file_path.write_bytes(b"diamond-data")

    with pytest.raises(ValueError, match="SHA256 mismatch"):
        install_diamond_windows.ensure_sha256(file_path, "0" * 64)


def test_install_diamond_reuses_existing_binary_without_force(tmp_test_dir):
    tmp_path = Path(tmp_test_dir)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    diamond_path = bin_dir / "diamond.exe"
    diamond_path.write_bytes(b"existing-binary")

    report = install_diamond_windows.install_diamond(
        dest_dir=bin_dir,
        url="https://example.invalid/diamond-windows.zip",
        expected_sha256="0" * 64,
        force=False,
    )

    assert report["status"] == "reused"
    assert report["diamond_path"] == str(diamond_path.resolve())
    assert diamond_path.read_bytes() == b"existing-binary"

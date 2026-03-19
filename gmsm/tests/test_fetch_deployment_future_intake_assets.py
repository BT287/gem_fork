import importlib.util
from pathlib import Path


def load_module():
    script_path = (
        Path(__file__).resolve().parents[2]
        / "scripts"
        / "fetch_deployment_future_intake_assets.py"
    )
    spec = importlib.util.spec_from_file_location(
        "fetch_deployment_future_intake_assets",
        script_path,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class TestFetchDeploymentFutureIntakeAssets:

    def test_resolve_case_ids_rejects_unknown_case(self):
        module = load_module()
        try:
            module.resolve_case_ids(["not_a_case"])
        except RuntimeError as exc:
            assert "Unknown case IDs" in str(exc)
        else:
            raise AssertionError("Expected RuntimeError for unknown case id")

    def test_build_efetch_url_uses_nuccore_gbwithparts(self):
        module = load_module()

        url = module.build_efetch_url("CP004370.1")

        assert "db=nuccore" in url
        assert "CP004370.1" in url
        assert "rettype=gbwithparts" in url

    def test_build_curl_command_points_to_destination(self, tmp_path):
        module = load_module()
        destination_path = tmp_path / "input.gbk"

        command = module.build_curl_command("https://example.org/test", str(destination_path))

        assert command[0] == "curl"
        assert "https://example.org/test" in command
        assert str(destination_path) in command

    def test_write_download_metadata_records_soft_neighbors(self, tmp_path):
        module = load_module()
        destination_dir = tmp_path / "case"
        destination_dir.mkdir()

        module.write_download_metadata(
            str(destination_dir),
            "actino_salbus_j1074",
            module.CASE_SPECS["actino_salbus_j1074"],
        )

        content = (destination_dir / "download_metadata.json").read_text(encoding="utf-8")
        assert "actino_salbus_j1074" in content
        assert "\"soft_neighbors\"" in content
        assert "\"sco\"" in content

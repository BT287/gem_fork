import importlib.util
from pathlib import Path


def load_module():
    script_path = Path(__file__).resolve().parents[2] / "scripts" / "fetch_phase3_boundary_round3_assets.py"
    spec = importlib.util.spec_from_file_location("fetch_phase3_boundary_round3_assets", script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class TestFetchPhase3BoundaryRound3Assets:

    def test_resolve_case_ids_rejects_unknown_case(self):
        module = load_module()
        try:
            module.resolve_case_ids(["not_a_case"])
        except RuntimeError as exc:
            assert "Unknown case IDs" in str(exc)
        else:
            raise AssertionError("Expected RuntimeError for unknown case id")

    def test_find_single_gbff_prefers_genomic_gbff(self, tmp_path):
        module = load_module()
        extract_dir = tmp_path / "extract"
        nested_dir = extract_dir / "ncbi_dataset" / "data" / "GCA_000008765.1"
        nested_dir.mkdir(parents=True)
        (nested_dir / "genomic.gbff").write_text("LOCUS TEST\n", encoding="utf-8")
        (nested_dir / "other.gbff").write_text("LOCUS OTHER\n", encoding="utf-8")

        found = module.find_single_gbff(str(extract_dir), accession="GCA_000008765.1")

        assert found is not None
        assert found.endswith("genomic.gbff")

    def test_default_output_root_is_round3_specific(self):
        module = load_module()

        output_root = module.get_default_output_root("/tmp/repo")

        assert output_root.endswith("benchmarks/query_assets/phase3_boundary_round3_candidates")

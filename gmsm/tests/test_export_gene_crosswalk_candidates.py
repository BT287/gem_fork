import importlib.util
import json
from pathlib import Path


def load_module():
    script_path = Path(__file__).resolve().parents[2] / "scripts" / "export_gene_crosswalk_candidates.py"
    spec = importlib.util.spec_from_file_location("export_gene_crosswalk_candidates", script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class TestExportGeneCrosswalkCandidates:

    def test_build_candidate_crosswalk_rows_filters_by_shared_alias_count(self):
        module = load_module()
        payload = {
            "gene_alias_metrics": {
                "status": "evaluated",
                "matched_pairs": [
                    {
                        "predicted_gene_id": "pred1",
                        "reference_gene_id": "ref1",
                        "shared_aliases": ["thrA"],
                    },
                    {
                        "predicted_gene_id": "pred2",
                        "reference_gene_id": "ref2",
                        "shared_aliases": ["geneB", "b0002"],
                    },
                ],
            }
        }

        rows = module.build_candidate_crosswalk_rows(payload, min_shared_aliases=2)

        assert rows == [
            {
                "predicted_gene_id": "pred2",
                "reference_gene_id": "ref2",
                "shared_alias_count": 2,
                "shared_aliases": "geneB;b0002",
            }
        ]

    def test_write_crosswalk_tsv_and_summary(self, tmp_path):
        module = load_module()
        rows = [
            {
                "predicted_gene_id": "predA",
                "reference_gene_id": "refA",
                "shared_alias_count": 1,
                "shared_aliases": "geneA",
            }
        ]
        tsv_path = tmp_path / "crosswalk.tsv"
        summary_path = tmp_path / "summary.json"

        module.write_crosswalk_tsv(tsv_path, rows)
        module.write_summary_json(summary_path, {"candidate_row_count": 1})

        assert tsv_path.read_text(encoding="utf-8").splitlines()[1] == "predA\trefA\t1\tgeneA"
        assert json.loads(summary_path.read_text(encoding="utf-8"))["candidate_row_count"] == 1

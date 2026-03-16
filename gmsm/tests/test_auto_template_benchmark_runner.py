import importlib.util
import json
from argparse import Namespace
from pathlib import Path

import pytest


def load_benchmark_runner_module():
    script_path = Path(__file__).resolve().parents[2] / "scripts" / "run_auto_template_benchmark.py"
    spec = importlib.util.spec_from_file_location("run_auto_template_benchmark", script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class TestAutoTemplateBenchmarkRunner:

    def test_load_manifest_accepts_json_subset_yaml(self, tmp_path):
        module = load_benchmark_runner_module()
        manifest_path = tmp_path / "benchmark.yaml"
        manifest_path.write_text(
            json.dumps(
                {
                    "manifest_version": 1,
                    "cases": [
                        {
                            "case_id": "case1",
                            "query_input": "input/sample.gbk",
                            "ec_file": None,
                            "reference_model": None,
                            "expected_taxonomic_neighbors": ["sco"],
                            "exclude_templates": [],
                            "tags": ["seed"],
                            "notes": "test case",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

        payload = module.load_manifest(manifest_path)

        assert payload["manifest_version"] == 1
        assert payload["cases"][0]["case_id"] == "case1"

    def test_normalize_case_requires_mandatory_fields(self, tmp_path):
        module = load_benchmark_runner_module()
        input_path = tmp_path / "input.gbk"
        input_path.write_text("LOCUS TEST\n", encoding="utf-8")

        with pytest.raises(ValueError):
            module.normalize_case(
                {
                    "case_id": "broken_case",
                    "query_input": str(input_path),
                },
                tmp_path,
            )

    def test_run_benchmark_writes_summary_and_copies_outputs(self, tmp_path, monkeypatch):
        module = load_benchmark_runner_module()
        repo_root = tmp_path
        manifest_dir = repo_root / "benchmarks"
        input_dir = repo_root / "input"
        manifest_dir.mkdir(parents=True)
        input_dir.mkdir(parents=True)
        (input_dir / "sample.gbk").write_text("LOCUS TEST\n", encoding="utf-8")
        (input_dir / "sample_ec.txt").write_text("gene1\t1.1.1.1\n", encoding="utf-8")

        manifest_path = manifest_dir / "manifest.yaml"
        manifest_path.write_text(
            json.dumps(
                {
                    "manifest_version": 1,
                    "cases": [
                        {
                            "case_id": "case1",
                            "query_input": "input/sample.gbk",
                            "ec_file": "input/sample_ec.txt",
                            "reference_model": None,
                            "expected_template": "sco",
                            "expected_taxonomic_neighbors": ["sco"],
                            "exclude_templates": [],
                            "template_backend": "diamond",
                            "template_rerank_topn": 0,
                            "tags": ["seed"],
                            "notes": "test case",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

        def fake_stream_command(command, cwd, log_path):
            output_dir = Path(command[command.index("-o") + 1])
            recommendation_dir = output_dir / "0_template_recommendation"
            recommendation_dir.mkdir(parents=True, exist_ok=True)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_path.write_text("ok\n", encoding="utf-8")
            (recommendation_dir / "template_recommendation.json").write_text(
                json.dumps(
                    {
                        "selection_mode": "auto",
                        "backend": "diamond",
                        "selection_strategy": "coarse_only",
                        "recommended_template": "sco",
                        "candidates": [{"template_id": "sco"}],
                    }
                ),
                encoding="utf-8",
            )
            (recommendation_dir / "template_candidates.tsv").write_text(
                "template_id\tscore\nsco\t0.9\n",
                encoding="utf-8",
            )
            return 0

        monkeypatch.setattr(module, "repo_root", lambda: repo_root)
        monkeypatch.setattr(module, "stream_command", fake_stream_command)

        args = Namespace(
            python="python",
            manifest="benchmarks/manifest.yaml",
            report_dir="benchmark-results",
            label="unit-test-run",
            case_id=[],
            max_cases=None,
            template_backend="auto",
            template_topk=3,
            template_rerank_topn=3,
            template_genome_bank=None,
            template_ani_weight=None,
            template_af_weight=None,
            template_diamond_hit_weight=None,
            template_diamond_identity_weight=None,
            template_bbh_template_weight=None,
            template_bbh_target_weight=None,
            template_coarse_weight=None,
            template_rerank_weight=None,
        )

        exit_code = module.run_benchmark(args)

        summary_path = repo_root / "benchmark-results" / "unit-test-run" / "benchmark_summary.json"
        copied_report = repo_root / "benchmark-results" / "unit-test-run" / "case1" / "template_recommendation.json"
        copied_candidates = repo_root / "benchmark-results" / "unit-test-run" / "case1" / "template_candidates.tsv"

        assert exit_code == 0
        assert summary_path.is_file()
        assert copied_report.is_file()
        assert copied_candidates.is_file()

        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        assert summary["status"] == "passed"
        assert summary["cases"][0]["status"] == "passed"
        assert summary["cases"][0]["neighbor_metrics"]["top1_expected_hit"] is True
        assert summary["cases"][0]["expected_template_metrics"]["top1_expected_template_hit"] is True
        assert summary["aggregate_metrics"]["top1_expected_template_hit_count"] == 1
        assert summary["aggregate_metrics"]["top1_expected_template_hit_rate"] == 1.0

    def test_build_command_uses_case_level_overrides(self):
        module = load_benchmark_runner_module()
        args = Namespace(
            python="python",
            template_backend="auto",
            template_topk=3,
            template_rerank_topn=3,
            template_genome_bank=None,
            template_ani_weight=None,
            template_af_weight=None,
            template_diamond_hit_weight=None,
            template_diamond_identity_weight=None,
            template_bbh_template_weight=None,
            template_bbh_target_weight=None,
            template_coarse_weight=None,
            template_rerank_weight=None,
        )
        case = {
            "case_id": "case1",
            "query_input": "/tmp/query.fa",
            "ec_file": None,
            "template_backend": "diamond",
            "template_topk": 5,
            "template_rerank_topn": 0,
        }

        command = module.build_command(args, case, Path("/tmp/output"))

        assert "--template-backend" in command
        assert command[command.index("--template-backend") + 1] == "diamond"
        assert command[command.index("--template-topk") + 1] == "5"
        assert command[command.index("--template-rerank-topn") + 1] == "0"

    def test_run_benchmark_continues_after_case_failure(self, tmp_path, monkeypatch):
        module = load_benchmark_runner_module()
        repo_root = tmp_path
        manifest_dir = repo_root / "benchmarks"
        input_dir = repo_root / "input"
        manifest_dir.mkdir(parents=True)
        input_dir.mkdir(parents=True)
        (input_dir / "sample.gbk").write_text("LOCUS TEST\n", encoding="utf-8")

        manifest_path = manifest_dir / "manifest.yaml"
        manifest_path.write_text(
            json.dumps(
                {
                    "manifest_version": 1,
                    "cases": [
                        {
                            "case_id": "case_pass",
                            "query_input": "input/sample.gbk",
                            "ec_file": None,
                            "reference_model": None,
                            "expected_taxonomic_neighbors": ["sco"],
                            "exclude_templates": [],
                            "tags": ["seed"],
                            "notes": "pass case",
                        },
                        {
                            "case_id": "case_fail",
                            "query_input": "input/sample.gbk",
                            "ec_file": None,
                            "reference_model": None,
                            "expected_taxonomic_neighbors": [],
                            "exclude_templates": [],
                            "tags": ["seed"],
                            "notes": "fail case",
                        },
                    ],
                }
            ),
            encoding="utf-8",
        )

        def fake_stream_command(command, cwd, log_path):
            output_dir = Path(command[command.index("-o") + 1])
            case_id = output_dir.parent.name
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_path.write_text(case_id + "\n", encoding="utf-8")
            if case_id == "case_fail":
                return 2

            recommendation_dir = output_dir / "0_template_recommendation"
            recommendation_dir.mkdir(parents=True, exist_ok=True)
            (recommendation_dir / "template_recommendation.json").write_text(
                json.dumps(
                    {
                        "selection_mode": "auto",
                        "backend": "diamond",
                        "selection_strategy": "coarse_only",
                        "recommended_template": "sco",
                        "candidates": [{"template_id": "sco"}],
                    }
                ),
                encoding="utf-8",
            )
            (recommendation_dir / "template_candidates.tsv").write_text(
                "template_id\tscore\nsco\t0.9\n",
                encoding="utf-8",
            )
            return 0

        monkeypatch.setattr(module, "repo_root", lambda: repo_root)
        monkeypatch.setattr(module, "stream_command", fake_stream_command)

        args = Namespace(
            python="python",
            manifest="benchmarks/manifest.yaml",
            report_dir="benchmark-results",
            label="failure-run",
            case_id=[],
            max_cases=None,
            template_backend="auto",
            template_topk=3,
            template_rerank_topn=3,
            template_genome_bank=None,
            template_ani_weight=None,
            template_af_weight=None,
            template_diamond_hit_weight=None,
            template_diamond_identity_weight=None,
            template_bbh_template_weight=None,
            template_bbh_target_weight=None,
            template_coarse_weight=None,
            template_rerank_weight=None,
        )

        exit_code = module.run_benchmark(args)
        summary_path = repo_root / "benchmark-results" / "failure-run" / "benchmark_summary.json"
        summary = json.loads(summary_path.read_text(encoding="utf-8"))

        assert exit_code == 1
        assert summary["failure_count"] == 1
        assert {case["case_id"] for case in summary["cases"]} == {"case_pass", "case_fail"}

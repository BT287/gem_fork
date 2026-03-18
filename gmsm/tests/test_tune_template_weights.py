import importlib.util
import json
from argparse import Namespace
from pathlib import Path


def load_module():
    script_path = Path(__file__).resolve().parents[2] / "scripts" / "tune_template_weights.py"
    spec = importlib.util.spec_from_file_location("tune_template_weights", script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def make_args(**overrides):
    defaults = {
        "python": "python",
        "manifest": "benchmarks/manifest.yaml",
        "report_dir": "benchmark-results",
        "label": "unit-tuning",
        "case_id": [],
        "max_cases": None,
        "max_configs": None,
        "template_backend": "diamond",
        "template_topk": 3,
        "template_genome_bank": None,
        "model_kind": "primary",
        "cpus": 1,
        "template_diamond_hit_weights": "0.01,0.10",
        "template_ani_weights": "0.5,0.9",
        "template_bbh_template_weights": "0.5",
        "template_coarse_weights": "0.95",
        "template_rerank_topn_values": "3",
    }
    defaults.update(overrides)
    return Namespace(**defaults)


class TestTuneTemplateWeights:

    def test_build_search_configs_for_diamond_backend_derives_complements(self):
        module = load_module()
        args = make_args(
            template_backend="diamond",
            template_diamond_hit_weights="0.8",
            template_bbh_template_weights="0.65",
            template_coarse_weights="0.55",
            template_rerank_topn_values="3",
        )

        configs = module.build_search_configs(args)

        assert len(configs) == 1
        config = configs[0]
        assert config["template_backend"] == "diamond"
        assert config["template_diamond_hit_weight"] == 0.8
        assert config["template_diamond_identity_weight"] == 0.2
        assert config["template_bbh_template_weight"] == 0.65
        assert config["template_bbh_target_weight"] == 0.35
        assert config["template_coarse_weight"] == 0.55
        assert config["template_rerank_weight"] == 0.45
        assert config["template_rerank_topn"] == 3

    def test_build_search_configs_for_skani_backend_uses_ani_weights(self):
        module = load_module()
        args = make_args(
            template_backend="skani",
            template_ani_weights="0.6",
            template_bbh_template_weights="0.7",
            template_coarse_weights="0.4",
            template_rerank_topn_values="1",
        )

        configs = module.build_search_configs(args)

        assert len(configs) == 1
        config = configs[0]
        assert config["template_backend"] == "skani"
        assert config["template_ani_weight"] == 0.6
        assert config["template_af_weight"] == 0.4
        assert config["template_diamond_hit_weight"] == 0.05
        assert config["template_diamond_identity_weight"] == 0.95

    def test_build_case_command_uses_recommendation_only_for_boundary_screening(self):
        module = load_module()
        args = make_args()
        config = module.build_search_configs(
            make_args(
                template_backend="diamond",
                template_diamond_hit_weights="0.8",
                template_bbh_template_weights="0.7",
                template_coarse_weights="0.6",
                template_rerank_topn_values="3",
            )
        )[0]
        case = {
            "case_id": "boundary_case",
            "query_input": "input/sample.gbk",
            "ec_file": None,
            "reference_model": None,
            "evaluation_tier": "boundary_screening",
            "expected_template": None,
            "expected_taxonomic_neighbors": ["sco"],
        }

        command = module.build_case_command(args, case, config, Path("tmp/out"))

        assert "--template-recommendation-only" in command
        assert "-p" in command

    def test_run_tuning_records_boundary_screening_without_reference_metrics(self, tmp_path, monkeypatch):
        module = load_module()
        repo_root = tmp_path
        manifest_dir = repo_root / "benchmarks"
        input_dir = repo_root / "input"
        manifest_dir.mkdir(parents=True)
        input_dir.mkdir(parents=True)
        (input_dir / "sample.gbk").write_text("LOCUS TEST\n", encoding="utf-8")

        manifest_path = manifest_dir / "boundary_manifest.yaml"
        manifest_path.write_text(
            json.dumps(
                {
                    "manifest_version": 1,
                    "cases": [
                        {
                            "case_id": "boundary_case",
                            "query_input": "input/sample.gbk",
                            "ec_file": None,
                            "reference_model": None,
                            "evaluation_tier": "boundary_screening",
                            "expected_template": None,
                            "expected_taxonomic_neighbors": ["sco"],
                            "exclude_templates": [],
                            "tags": ["boundary-case"],
                            "notes": "synthetic boundary screening case",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

        def fake_stream_command(command, cwd, log_path):
            assert "--template-recommendation-only" in command
            output_dir = Path(command[command.index("-o") + 1])
            recommendation_dir = output_dir / "0_template_recommendation"
            recommendation_dir.mkdir(parents=True, exist_ok=True)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_path.write_text("boundary\n", encoding="utf-8")
            (recommendation_dir / "template_recommendation.json").write_text(
                json.dumps(
                    {
                        "selection_mode": "auto",
                        "backend": "diamond",
                        "selection_strategy": "coarse_plus_bbh",
                        "recommended_template": "sco",
                        "candidates": [{"template_id": "sco"}],
                    }
                ),
                encoding="utf-8",
            )
            return 0

        monkeypatch.setattr(module, "repo_root", lambda: repo_root)
        monkeypatch.setattr(module, "stream_command", fake_stream_command)

        args = make_args(
            manifest="benchmarks/boundary_manifest.yaml",
            label="boundary-run",
            template_backend="diamond",
            template_diamond_hit_weights="0.95",
            template_bbh_template_weights="0.7",
            template_coarse_weights="0.6",
            template_rerank_topn_values="1",
        )

        exit_code = module.run_tuning(args)
        summary = json.loads(
            (repo_root / "benchmark-results" / "boundary-run" / "tuning_summary.json").read_text(encoding="utf-8")
        )
        best = summary["best_configuration"]

        assert exit_code == 0
        assert best["objective_reaction_f1_mean"] is None
        assert best["evaluated_reference_case_count"] == 0
        assert best["tier_screening_metrics"]["boundary_screening"]["top1_expected_neighbor_hit_rate"] == 1.0
        assert best["cases"][0]["execution_mode"] == "template_recommendation_only"
        assert best["cases"][0]["evaluation_tier"] == "boundary_screening"
        assert "evaluation" not in best["cases"][0]

    def test_run_tuning_writes_ranked_summary(self, tmp_path, monkeypatch):
        module = load_module()
        repo_root = tmp_path
        manifest_dir = repo_root / "benchmarks"
        input_dir = repo_root / "input"
        manifest_dir.mkdir(parents=True)
        input_dir.mkdir(parents=True)
        (input_dir / "sample.gbk").write_text("LOCUS TEST\n", encoding="utf-8")
        (input_dir / "reference.xml").write_text("<sbml/>", encoding="utf-8")

        manifest_path = manifest_dir / "manifest.yaml"
        manifest_path.write_text(
            json.dumps(
                {
                    "manifest_version": 1,
                    "cases": [
                        {
                            "case_id": "eco_w3110",
                            "query_input": "input/sample.gbk",
                            "ec_file": None,
                            "reference_model": "input/reference.xml",
                            "evaluation_tier": "primary_exact",
                            "expected_template": "eco",
                            "expected_taxonomic_neighbors": ["eco"],
                            "exclude_templates": [],
                            "tags": ["same-species", "exact-reference"],
                            "notes": "synthetic tuning case",
                        },
                        {
                            "case_id": "eco_bw25113",
                            "query_input": "input/sample.gbk",
                            "ec_file": None,
                            "reference_model": "input/reference.xml",
                            "evaluation_tier": "secondary_approximate",
                            "expected_template": "eco",
                            "expected_taxonomic_neighbors": ["eco"],
                            "exclude_templates": [],
                            "tags": ["same-species", "approximate-reference"],
                            "notes": "synthetic approximate case",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

        def fake_stream_command(command, cwd, log_path):
            output_dir = Path(command[command.index("-o") + 1])
            config_dir_name = output_dir.parent.parent.name
            recommendation_dir = output_dir / "0_template_recommendation"
            recommendation_dir.mkdir(parents=True, exist_ok=True)
            recommended_template = "eco" if "diamondhit0p95" in config_dir_name else "bsu"
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_path.write_text(config_dir_name + "\n", encoding="utf-8")
            (recommendation_dir / "template_recommendation.json").write_text(
                json.dumps(
                    {
                        "selection_mode": "auto",
                        "backend": "diamond",
                        "selection_strategy": "coarse_plus_bbh",
                        "recommended_template": recommended_template,
                        "candidates": [{"template_id": recommended_template}],
                    }
                ),
                encoding="utf-8",
            )
            return 0

        def fake_evaluate_case(evaluation_module, predicted_path, reference_path, case_id, model_kind, query_genbank):
            predicted_str = str(predicted_path)
            if case_id == "eco_w3110":
                f1 = 0.91
            else:
                f1 = 0.72 if "diamondhit0p95" in predicted_str else 0.52
            return {
                "label": case_id,
                "reaction_metrics": {
                    "precision": f1,
                    "recall": f1,
                    "f1": f1,
                },
                "gene_alias_metrics": {
                    "status": "evaluated",
                    "f1": round(f1 / 2.0, 6),
                },
            }

        monkeypatch.setattr(module, "repo_root", lambda: repo_root)
        monkeypatch.setattr(module, "stream_command", fake_stream_command)
        monkeypatch.setattr(module, "evaluate_case", fake_evaluate_case)

        args = make_args(
            manifest="benchmarks/manifest.yaml",
            label="tuning-run",
            template_backend="diamond",
            template_diamond_hit_weights="0.75,0.95",
            template_bbh_template_weights="0.7",
            template_coarse_weights="0.6",
            template_rerank_topn_values="1",
        )

        exit_code = module.run_tuning(args)

        summary_path = repo_root / "benchmark-results" / "tuning-run" / "tuning_summary.json"
        results_tsv_path = repo_root / "benchmark-results" / "tuning-run" / "tuning_results.tsv"
        summary = json.loads(summary_path.read_text(encoding="utf-8"))

        assert exit_code == 0
        assert summary_path.is_file()
        assert results_tsv_path.is_file()
        assert summary["configuration_count"] == 2
        assert summary["best_configuration"]["config_id"].endswith("diamondhit0p95_bbh0p7_coarse0p6_topn1")
        assert summary["best_configuration"]["objective_reaction_f1_mean"] == 0.91
        assert summary["best_configuration"]["primary_exact_reaction_f1_mean"] == 0.91
        assert summary["best_configuration"]["secondary_approximate_reaction_f1_mean"] == 0.72
        assert summary["best_configuration"]["aggregate_metrics"]["top1_expected_template_hit_rate"] == 1.0
        assert summary["ranked_configurations"][1]["objective_reaction_f1_mean"] == 0.91
        assert summary["ranked_configurations"][1]["secondary_approximate_reaction_f1_mean"] == 0.52

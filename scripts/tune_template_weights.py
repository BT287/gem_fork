#!/usr/bin/env python

import argparse
import csv
import datetime
import importlib.util
import itertools
import json
import statistics
import subprocess
import sys
from collections import defaultdict
from pathlib import Path


WEIGHT_OPTION_MAP = (
    ("template_ani_weight", "--template-ani-weight"),
    ("template_af_weight", "--template-af-weight"),
    ("template_diamond_hit_weight", "--template-diamond-hit-weight"),
    ("template_diamond_identity_weight", "--template-diamond-identity-weight"),
    ("template_bbh_template_weight", "--template-bbh-template-weight"),
    ("template_bbh_target_weight", "--template-bbh-target-weight"),
    ("template_coarse_weight", "--template-coarse-weight"),
    ("template_rerank_weight", "--template-rerank-weight"),
)

DEFAULT_FIXED_WEIGHTS = {
    "template_ani_weight": 0.7,
    "template_af_weight": 0.3,
    "template_diamond_hit_weight": 0.05,
    "template_diamond_identity_weight": 0.95,
    "template_bbh_template_weight": 0.5,
    "template_bbh_target_weight": 0.5,
    "template_coarse_weight": 0.95,
    "template_rerank_weight": 0.05,
}

DEFAULT_GRID_VALUES = {
    "diamond_hit_weights": "0.01,0.05,0.10",
    "ani_weights": "0.5,0.7,0.9",
    "bbh_template_weights": "0.3,0.5,0.7",
    "coarse_weights": "0.95",
    "rerank_topn_values": "3",
}


def repo_root():
    return Path(__file__).resolve().parent.parent


def load_module(script_name, module_name):
    script_path = Path(__file__).resolve().parent / script_name
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_benchmark_module():
    return load_module("run_auto_template_benchmark.py", "run_auto_template_benchmark")


def load_evaluation_module():
    return load_module("evaluate_reconstruction_quality.py", "evaluate_reconstruction_quality")


def parse_csv_values(raw_value, cast_type, option_name):
    values = []
    for token in str(raw_value or "").split(","):
        token = token.strip()
        if not token:
            continue
        values.append(cast_type(token))
    if not values:
        raise ValueError("Option '%s' must contain at least one value" % option_name)
    return values


def validate_probability_values(values, option_name):
    for value in values:
        if value < 0.0 or value > 1.0:
            raise ValueError("Option '%s' values must stay within [0, 1]" % option_name)


def validate_positive_integer_values(values, option_name):
    for value in values:
        if int(value) < 0:
            raise ValueError("Option '%s' values must be non-negative integers" % option_name)


def format_float_for_id(value):
    text = ("%.2f" % float(value)).rstrip("0").rstrip(".")
    return text.replace(".", "p")


def build_config_id(config):
    coarse_metric_label = "diamondhit" if config["template_backend"] == "diamond" else "ani"
    coarse_metric_value = (
        config["template_diamond_hit_weight"]
        if config["template_backend"] == "diamond"
        else config["template_ani_weight"]
    )
    return (
        "%s_%s%s_bbh%s_coarse%s_topn%s"
        % (
            config["template_backend"],
            coarse_metric_label,
            format_float_for_id(coarse_metric_value),
            format_float_for_id(config["template_bbh_template_weight"]),
            format_float_for_id(config["template_coarse_weight"]),
            int(config["template_rerank_topn"]),
        )
    )


def build_search_configs(args):
    if args.template_backend not in ("diamond", "skani"):
        raise ValueError("The first tuning loop requires a fixed backend: choose 'diamond' or 'skani'")

    bbh_template_weights = parse_csv_values(
        args.template_bbh_template_weights,
        float,
        "--template-bbh-template-weights",
    )
    coarse_weights = parse_csv_values(args.template_coarse_weights, float, "--template-coarse-weights")
    rerank_topn_values = parse_csv_values(
        args.template_rerank_topn_values,
        int,
        "--template-rerank-topn-values",
    )
    validate_probability_values(bbh_template_weights, "--template-bbh-template-weights")
    validate_probability_values(coarse_weights, "--template-coarse-weights")
    validate_positive_integer_values(rerank_topn_values, "--template-rerank-topn-values")

    if args.template_backend == "diamond":
        coarse_metric_weights = parse_csv_values(
            args.template_diamond_hit_weights,
            float,
            "--template-diamond-hit-weights",
        )
        validate_probability_values(coarse_metric_weights, "--template-diamond-hit-weights")
        coarse_metric_key = "template_diamond_hit_weight"
        coarse_metric_complement_key = "template_diamond_identity_weight"
    else:
        coarse_metric_weights = parse_csv_values(args.template_ani_weights, float, "--template-ani-weights")
        validate_probability_values(coarse_metric_weights, "--template-ani-weights")
        coarse_metric_key = "template_ani_weight"
        coarse_metric_complement_key = "template_af_weight"

    configs = []
    for coarse_metric_weight, bbh_template_weight, coarse_weight, rerank_topn in itertools.product(
        coarse_metric_weights,
        bbh_template_weights,
        coarse_weights,
        rerank_topn_values,
    ):
        config = dict(DEFAULT_FIXED_WEIGHTS)
        config["template_backend"] = args.template_backend
        config["template_rerank_topn"] = int(rerank_topn)
        config["template_bbh_template_weight"] = round(float(bbh_template_weight), 6)
        config["template_bbh_target_weight"] = round(1.0 - float(bbh_template_weight), 6)
        config["template_coarse_weight"] = round(float(coarse_weight), 6)
        config["template_rerank_weight"] = round(1.0 - float(coarse_weight), 6)
        config[coarse_metric_key] = round(float(coarse_metric_weight), 6)
        config[coarse_metric_complement_key] = round(1.0 - float(coarse_metric_weight), 6)
        config["config_id"] = build_config_id(config)
        configs.append(config)

    if args.max_configs is not None:
        configs = configs[: max(0, int(args.max_configs))]
    return configs


def stream_command(command, cwd, log_path):
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as log_handle:
        process = subprocess.Popen(
            command,
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        assert process.stdout is not None
        for line in process.stdout:
            sys.stdout.write(line)
            log_handle.write(line)
        process.wait()
        return process.returncode


def build_case_command(args, case, config, output_dir):
    evaluation_tier = resolve_case_evaluation_tier(case)
    command = [
        args.python,
        "run_gmsm.py",
        "-i",
        case["query_input"],
        "--auto-template",
        "--template-backend",
        config["template_backend"],
        "--template-topk",
        str(args.template_topk),
        "--template-rerank-topn",
        str(config["template_rerank_topn"]),
        "-p",
        "-d",
        "-c",
        str(args.cpus),
        "-o",
        str(output_dir),
    ]
    if evaluation_tier == "boundary_screening":
        command.append("--template-recommendation-only")
    if case.get("ec_file"):
        command.extend(["-e", case["ec_file"]])
    if args.template_genome_bank:
        command.extend(["--template-genome-bank", args.template_genome_bank])
    for field_name, cli_option in WEIGHT_OPTION_MAP:
        command.extend([cli_option, str(config[field_name])])
    return command


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, payload):
    output_path = Path(path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_results_tsv(path, rows):
    output_path = Path(path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = (
        "rank",
        "config_id",
        "template_backend",
        "objective_reaction_f1_mean",
        "primary_exact_reaction_f1_mean",
        "secondary_approximate_reaction_f1_mean",
        "overall_reaction_f1_mean",
        "evaluated_reference_case_count",
        "primary_exact_reference_case_count",
        "secondary_approximate_reference_case_count",
        "failed_case_count",
        "top1_expected_template_hit_rate",
        "top1_expected_neighbor_hit_rate",
        "reaction_precision_mean",
        "reaction_recall_mean",
        "gene_alias_f1_mean",
        "primary_exact_gene_alias_f1_mean",
        "secondary_approximate_gene_alias_f1_mean",
        "template_rerank_topn",
        "template_ani_weight",
        "template_af_weight",
        "template_diamond_hit_weight",
        "template_diamond_identity_weight",
        "template_bbh_template_weight",
        "template_bbh_target_weight",
        "template_coarse_weight",
        "template_rerank_weight",
    )
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        for row in rows:
            flat_row = dict(row)
            flat_row["top1_expected_template_hit_rate"] = row.get("aggregate_metrics", {}).get(
                "top1_expected_template_hit_rate"
            )
            flat_row["top1_expected_neighbor_hit_rate"] = row.get("aggregate_metrics", {}).get(
                "top1_expected_neighbor_hit_rate"
            )
            writer.writerow({field: flat_row.get(field) for field in fieldnames})


def safe_mean(values):
    cleaned = [float(value) for value in values if value is not None]
    if not cleaned:
        return None
    return round(statistics.mean(cleaned), 6)


def resolve_case_evaluation_tier(case):
    if case.get("evaluation_tier"):
        return case["evaluation_tier"]
    if case.get("reference_model"):
        return "primary_exact"
    return None


def summarize_screening_metrics(benchmark_module, case_results):
    aggregate_metrics = benchmark_module.build_aggregate_metrics(case_results)
    tier_case_map = defaultdict(list)
    for case in case_results:
        tier = case.get("evaluation_tier")
        if not tier:
            continue
        tier_case_map[tier].append(case)

    tier_metrics = {}
    for tier, tier_cases in sorted(tier_case_map.items()):
        tier_metrics[tier] = benchmark_module.build_aggregate_metrics(tier_cases)
    return aggregate_metrics, tier_metrics


def evaluate_case(evaluation_module, predicted_path, reference_path, case_id, model_kind, query_genbank):
    return evaluation_module.evaluate_single_case(
        predicted_path=predicted_path,
        reference_path=reference_path,
        label=case_id,
        model_kind=model_kind,
        query_genbank=query_genbank,
    )


def aggregate_configuration_result(benchmark_module, config, case_results):
    aggregate_metrics, tier_screening_metrics = summarize_screening_metrics(benchmark_module, case_results)

    evaluated_cases = [
        case
        for case in case_results
        if case.get("status") == "passed" and case.get("evaluation", {}).get("reaction_metrics")
    ]
    tier_to_cases = defaultdict(list)
    for case in evaluated_cases:
        tier_to_cases[case.get("evaluation_tier") or "primary_exact"].append(case)

    primary_exact_cases = tier_to_cases.get("primary_exact", [])
    secondary_approximate_cases = tier_to_cases.get("secondary_approximate", [])
    reaction_f1_values = [case["evaluation"]["reaction_metrics"].get("f1") for case in evaluated_cases]
    reaction_precision_values = [case["evaluation"]["reaction_metrics"].get("precision") for case in evaluated_cases]
    reaction_recall_values = [case["evaluation"]["reaction_metrics"].get("recall") for case in evaluated_cases]
    primary_exact_reaction_f1_values = [
        case["evaluation"]["reaction_metrics"].get("f1") for case in primary_exact_cases
    ]
    secondary_approximate_reaction_f1_values = [
        case["evaluation"]["reaction_metrics"].get("f1") for case in secondary_approximate_cases
    ]
    gene_alias_f1_values = [
        case["evaluation"].get("gene_alias_metrics", {}).get("f1")
        for case in evaluated_cases
        if case["evaluation"].get("gene_alias_metrics", {}).get("status") == "evaluated"
    ]
    primary_exact_gene_alias_f1_values = [
        case["evaluation"].get("gene_alias_metrics", {}).get("f1")
        for case in primary_exact_cases
        if case["evaluation"].get("gene_alias_metrics", {}).get("status") == "evaluated"
    ]
    secondary_approximate_gene_alias_f1_values = [
        case["evaluation"].get("gene_alias_metrics", {}).get("f1")
        for case in secondary_approximate_cases
        if case["evaluation"].get("gene_alias_metrics", {}).get("status") == "evaluated"
    ]

    primary_exact_reaction_f1_mean = safe_mean(primary_exact_reaction_f1_values)
    overall_reaction_f1_mean = safe_mean(reaction_f1_values)

    return {
        "config_id": config["config_id"],
        "template_backend": config["template_backend"],
        "template_rerank_topn": config["template_rerank_topn"],
        "template_ani_weight": config["template_ani_weight"],
        "template_af_weight": config["template_af_weight"],
        "template_diamond_hit_weight": config["template_diamond_hit_weight"],
        "template_diamond_identity_weight": config["template_diamond_identity_weight"],
        "template_bbh_template_weight": config["template_bbh_template_weight"],
        "template_bbh_target_weight": config["template_bbh_target_weight"],
        "template_coarse_weight": config["template_coarse_weight"],
        "template_rerank_weight": config["template_rerank_weight"],
        "objective_reaction_f1_mean": primary_exact_reaction_f1_mean or overall_reaction_f1_mean,
        "primary_exact_reaction_f1_mean": primary_exact_reaction_f1_mean,
        "secondary_approximate_reaction_f1_mean": safe_mean(secondary_approximate_reaction_f1_values),
        "overall_reaction_f1_mean": overall_reaction_f1_mean,
        "reaction_precision_mean": safe_mean(reaction_precision_values),
        "reaction_recall_mean": safe_mean(reaction_recall_values),
        "gene_alias_f1_mean": safe_mean(gene_alias_f1_values),
        "primary_exact_gene_alias_f1_mean": safe_mean(primary_exact_gene_alias_f1_values),
        "secondary_approximate_gene_alias_f1_mean": safe_mean(secondary_approximate_gene_alias_f1_values),
        "evaluated_reference_case_count": len(evaluated_cases),
        "primary_exact_reference_case_count": len(primary_exact_cases),
        "secondary_approximate_reference_case_count": len(secondary_approximate_cases),
        "failed_case_count": sum(case.get("status") != "passed" for case in case_results),
        "aggregate_metrics": aggregate_metrics,
        "tier_screening_metrics": tier_screening_metrics,
    }


def ranking_sort_key(result):
    objective = result.get("objective_reaction_f1_mean")
    if objective is None:
        objective = -1.0
    secondary = result.get("secondary_approximate_reaction_f1_mean")
    if secondary is None:
        secondary = -1.0
    return (
        -objective,
        -secondary,
        -int(result.get("primary_exact_reference_case_count", 0)),
        -float(result.get("aggregate_metrics", {}).get("top1_expected_neighbor_hit_rate") or 0.0),
        int(result.get("failed_case_count", 0)),
        result.get("config_id", ""),
    )


def run_tuning(args):
    root = repo_root()
    benchmark_module = load_benchmark_module()
    evaluation_module = load_evaluation_module()
    manifest_path = benchmark_module.resolve_manifest_path(root, args.manifest)
    manifest = benchmark_module.load_benchmark_cases(manifest_path, root)
    selected_cases = benchmark_module.select_cases(
        manifest["cases"],
        case_ids=args.case_id or [],
        max_cases=args.max_cases,
    )
    configs = build_search_configs(args)

    label = args.label or datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    run_dir = (root / args.report_dir / label).resolve()
    run_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "manifest_path": str(manifest_path),
        "label": label,
        "run_dir": str(run_dir),
        "python": args.python,
        "template_backend": args.template_backend,
        "objective_policy": {
            "primary_metric": "primary_exact_reaction_f1_mean",
            "screening_metrics": [
                "top1_expected_template_hit_rate",
                "top1_expected_neighbor_hit_rate",
            ],
            "secondary_metrics": [
                "secondary_approximate_reaction_f1_mean",
                "gene_alias_f1_mean",
            ],
        },
        "search_space": {
            "template_backend": args.template_backend,
            "template_topk": int(args.template_topk),
            "template_diamond_hit_weights": (
                parse_csv_values(args.template_diamond_hit_weights, float, "--template-diamond-hit-weights")
                if args.template_backend == "diamond"
                else None
            ),
            "template_ani_weights": (
                parse_csv_values(args.template_ani_weights, float, "--template-ani-weights")
                if args.template_backend == "skani"
                else None
            ),
            "template_bbh_template_weights": parse_csv_values(
                args.template_bbh_template_weights,
                float,
                "--template-bbh-template-weights",
            ),
            "template_coarse_weights": parse_csv_values(args.template_coarse_weights, float, "--template-coarse-weights"),
            "template_rerank_topn_values": parse_csv_values(
                args.template_rerank_topn_values,
                int,
                "--template-rerank-topn-values",
            ),
        },
        "selected_case_count": len(selected_cases),
        "configuration_count": len(configs),
        "configurations": [],
    }

    for index, config in enumerate(configs, start=1):
        config_dir = run_dir / ("%03d_%s" % (index, config["config_id"]))
        case_results = []
        for case in selected_cases:
            case_dir = config_dir / case["case_id"]
            output_dir = case_dir / "run-output"
            log_path = case_dir / "tuning_case.log"
            command = build_case_command(args, case, config, output_dir)
            case_summary = {
                "case_id": case["case_id"],
                "query_input": case["query_input"],
                "reference_model": case.get("reference_model"),
                "evaluation_tier": resolve_case_evaluation_tier(case),
                "execution_mode": (
                    "template_recommendation_only"
                    if resolve_case_evaluation_tier(case) == "boundary_screening"
                    else "full_reconstruction"
                ),
                "expected_template": case.get("expected_template"),
                "expected_taxonomic_neighbors": case.get("expected_taxonomic_neighbors", []),
                "config_id": config["config_id"],
                "command": command,
                "output_dir": str(output_dir),
                "log_path": str(log_path),
            }
            try:
                returncode = stream_command(command, cwd=root, log_path=log_path)
                case_summary["returncode"] = returncode
                if returncode != 0:
                    raise RuntimeError("run_gmsm.py exited with code %s" % returncode)

                recommendation_path = output_dir / "0_template_recommendation" / "template_recommendation.json"
                report = load_json(recommendation_path)
                errors = benchmark_module.validate_report(report)
                if errors:
                    raise RuntimeError("; ".join(errors))

                case_summary["status"] = "passed"
                case_summary["recommended_template"] = report.get("recommended_template")
                case_summary["backend"] = report.get("backend")
                case_summary["selection_strategy"] = report.get("selection_strategy")
                case_summary["report"] = report
                case_summary["neighbor_metrics"] = benchmark_module.compute_neighbor_metrics(
                    report,
                    case.get("expected_taxonomic_neighbors", []),
                )
                case_summary["expected_template_metrics"] = benchmark_module.compute_expected_template_metrics(
                    report,
                    case.get("expected_template"),
                )

                if case.get("reference_model"):
                    evaluation = evaluate_case(
                        evaluation_module=evaluation_module,
                        predicted_path=output_dir,
                        reference_path=case["reference_model"],
                        case_id=case["case_id"],
                        model_kind=args.model_kind,
                        query_genbank=case.get("query_input"),
                    )
                    case_summary["evaluation"] = evaluation
                    write_json(case_dir / "evaluation.json", evaluation)
            except Exception as exc:
                case_summary["status"] = "failed"
                case_summary["error"] = str(exc)
            case_results.append(case_summary)

        config_summary = aggregate_configuration_result(benchmark_module, config, case_results)
        config_summary["configuration_index"] = index
        config_summary["cases"] = case_results
        summary["configurations"].append(config_summary)

    ranked = sorted(summary["configurations"], key=ranking_sort_key)
    for rank, item in enumerate(ranked, start=1):
        item["rank"] = rank

    summary["ranked_configurations"] = ranked
    summary["best_configuration"] = ranked[0] if ranked else None
    summary_path = run_dir / "tuning_summary.json"
    write_json(summary_path, summary)
    write_results_tsv(run_dir / "tuning_results.tsv", ranked)
    print("Tuning summary written to %s" % summary_path)
    return 0


def build_parser():
    parser = argparse.ArgumentParser(
        description="Run a narrow backend-fixed weight search and rank candidate settings by E2E reconstruction quality."
    )
    parser.add_argument(
        "--python",
        default=sys.executable,
        help="Python executable used to launch run_gmsm.py (default: current interpreter)",
    )
    parser.add_argument(
        "--manifest",
        default="benchmarks/auto_template_benchmark_manifest.yaml",
        help="Benchmark manifest path relative to the repo root unless absolute",
    )
    parser.add_argument(
        "--report-dir",
        default="benchmark-results",
        help="Base directory for tuning outputs relative to the repo root",
    )
    parser.add_argument(
        "--label",
        default=None,
        help="Optional fixed output label. Defaults to a UTC timestamp.",
    )
    parser.add_argument(
        "--case-id",
        action="append",
        default=[],
        help="Run only the specified benchmark case id. Repeatable.",
    )
    parser.add_argument(
        "--max-cases",
        type=int,
        default=None,
        help="Optional cap on how many selected cases to run.",
    )
    parser.add_argument(
        "--max-configs",
        type=int,
        default=None,
        help="Optional cap on how many generated weight configurations to try.",
    )
    parser.add_argument(
        "--template-backend",
        default="diamond",
        choices=["diamond", "skani"],
        help="Fixed backend for the first tuning loop. 'auto' is intentionally disallowed.",
    )
    parser.add_argument(
        "--template-topk",
        type=int,
        default=3,
        help="Value forwarded to run_gmsm.py --template-topk",
    )
    parser.add_argument(
        "--template-genome-bank",
        default=None,
        help="Optional explicit template genome bank path forwarded to run_gmsm.py",
    )
    parser.add_argument(
        "--model-kind",
        default="primary",
        choices=["auto", "primary", "complete"],
        help="How to resolve model.xml when evaluating a run directory.",
    )
    parser.add_argument(
        "--cpus",
        type=int,
        default=1,
        help="CPU count forwarded to run_gmsm.py -c (default: %(default)s)",
    )
    parser.add_argument(
        "--template-diamond-hit-weights",
        default=DEFAULT_GRID_VALUES["diamond_hit_weights"],
        help="Comma-separated search values for template_diamond_hit_weight when backend is diamond.",
    )
    parser.add_argument(
        "--template-ani-weights",
        default=DEFAULT_GRID_VALUES["ani_weights"],
        help="Comma-separated search values for template_ani_weight when backend is skani.",
    )
    parser.add_argument(
        "--template-bbh-template-weights",
        default=DEFAULT_GRID_VALUES["bbh_template_weights"],
        help="Comma-separated search values for template_bbh_template_weight.",
    )
    parser.add_argument(
        "--template-coarse-weights",
        default=DEFAULT_GRID_VALUES["coarse_weights"],
        help="Comma-separated search values for template_coarse_weight.",
    )
    parser.add_argument(
        "--template-rerank-topn-values",
        default=DEFAULT_GRID_VALUES["rerank_topn_values"],
        help="Comma-separated search values for template_rerank_topn.",
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    return run_tuning(args)


if __name__ == "__main__":
    raise SystemExit(main())

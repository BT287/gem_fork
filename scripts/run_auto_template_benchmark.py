#!/usr/bin/env python

import argparse
import datetime
import json
import shutil
import subprocess
import sys
from pathlib import Path


REQUIRED_CASE_FIELDS = (
    "case_id",
    "query_input",
    "ec_file",
    "expected_taxonomic_neighbors",
    "reference_model",
    "notes",
    "exclude_templates",
    "tags",
)

OPTIONAL_CASE_FIELDS = (
    "expected_template",
    "template_backend",
    "template_topk",
    "template_rerank_topn",
)

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


def repo_root():
    return Path(__file__).resolve().parent.parent


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


def resolve_manifest_path(root, manifest_path):
    path = Path(manifest_path)
    if not path.is_absolute():
        path = (root / path).resolve()
    return path


def load_manifest(manifest_path):
    raw = manifest_path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore
    except ImportError:
        payload = json.loads(raw)
    else:
        payload = yaml.safe_load(raw)

    if not isinstance(payload, dict):
        raise ValueError("Benchmark manifest must decode to a mapping")

    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("Benchmark manifest must contain a non-empty 'cases' list")

    return payload


def resolve_optional_path(root, value, must_exist=True):
    if value in (None, ""):
        return None
    path = Path(value)
    if not path.is_absolute():
        path = (root / path).resolve()
    if must_exist and not path.is_file():
        raise FileNotFoundError("Referenced file not found: %s" % path)
    return path


def normalize_case(case, root):
    missing = [field for field in REQUIRED_CASE_FIELDS if field not in case]
    if missing:
        raise ValueError("Benchmark case missing required fields: %s" % ", ".join(sorted(missing)))

    case_id = str(case["case_id"]).strip()
    if not case_id:
        raise ValueError("Benchmark case must define a non-empty case_id")

    expected_neighbors = case.get("expected_taxonomic_neighbors")
    exclude_templates = case.get("exclude_templates")
    tags = case.get("tags")
    if not isinstance(expected_neighbors, list):
        raise ValueError("Case '%s' expected_taxonomic_neighbors must be a list" % case_id)
    if not isinstance(exclude_templates, list):
        raise ValueError("Case '%s' exclude_templates must be a list" % case_id)
    if not isinstance(tags, list):
        raise ValueError("Case '%s' tags must be a list" % case_id)

    normalized = dict(case)
    normalized["case_id"] = case_id
    normalized["query_input"] = str(resolve_optional_path(root, case["query_input"], must_exist=True))
    normalized["ec_file"] = (
        str(resolve_optional_path(root, case.get("ec_file"), must_exist=True))
        if case.get("ec_file")
        else None
    )
    normalized["reference_model"] = (
        str(resolve_optional_path(root, case.get("reference_model"), must_exist=True))
        if case.get("reference_model")
        else None
    )
    normalized["expected_taxonomic_neighbors"] = expected_neighbors
    normalized["exclude_templates"] = exclude_templates
    normalized["tags"] = tags
    normalized["notes"] = case.get("notes")
    normalized["expected_template"] = case.get("expected_template")
    normalized["template_backend"] = case.get("template_backend")
    normalized["template_topk"] = case.get("template_topk")
    normalized["template_rerank_topn"] = case.get("template_rerank_topn")
    return normalized


def load_benchmark_cases(manifest_path, root):
    manifest = load_manifest(manifest_path)
    normalized_cases = [normalize_case(case, root) for case in manifest["cases"]]
    manifest["cases"] = normalized_cases
    return manifest


def select_cases(cases, case_ids=None, max_cases=None):
    selected = list(cases)
    if case_ids:
        requested = set(case_ids)
        selected = [case for case in selected if case["case_id"] in requested]
        found = {case["case_id"] for case in selected}
        missing = sorted(requested - found)
        if missing:
            raise ValueError("Requested benchmark case ids not found: %s" % ", ".join(missing))

    if max_cases is not None:
        selected = selected[: max(0, int(max_cases))]

    if not selected:
        raise ValueError("No benchmark cases selected")
    return selected


def build_command(args, case, output_dir):
    template_backend = case.get("template_backend") or args.template_backend
    template_topk = case.get("template_topk")
    if template_topk is None:
        template_topk = args.template_topk
    template_rerank_topn = case.get("template_rerank_topn")
    if template_rerank_topn is None:
        template_rerank_topn = args.template_rerank_topn

    command = [
        args.python,
        "run_gmsm.py",
        "-i",
        case["query_input"],
        "--auto-template",
        "--template-recommendation-only",
        "--template-topk",
        str(template_topk),
        "--template-rerank-topn",
        str(template_rerank_topn),
        "-p",
        "-d",
        "-o",
        str(output_dir),
    ]
    if case.get("ec_file"):
        command.extend(["-e", case["ec_file"]])
    if template_backend != "auto":
        command.extend(["--template-backend", template_backend])
    if args.template_genome_bank:
        command.extend(["--template-genome-bank", args.template_genome_bank])
    for field_name, cli_option in WEIGHT_OPTION_MAP:
        value = getattr(args, field_name, None)
        if value is not None:
            command.extend([cli_option, str(value)])
    return command


def validate_report(report):
    errors = []
    if report.get("selection_mode") not in (None, "auto"):
        errors.append("selection_mode=%r" % report.get("selection_mode"))
    if not report.get("backend"):
        errors.append("backend is empty")
    if not report.get("selection_strategy"):
        errors.append("selection_strategy is empty")
    if not report.get("recommended_template"):
        errors.append("recommended_template is empty")
    return errors


def compute_neighbor_metrics(report, expected_neighbors):
    if not expected_neighbors:
        return {
            "top1_expected_hit": None,
            "topk_expected_hit": None,
        }

    expected = set(expected_neighbors)
    candidate_ids = [candidate.get("template_id") for candidate in report.get("candidates", [])]
    top1 = report.get("recommended_template")
    return {
        "top1_expected_hit": top1 in expected if top1 else False,
        "topk_expected_hit": any(candidate_id in expected for candidate_id in candidate_ids),
    }


def compute_expected_template_metrics(report, expected_template):
    if not expected_template:
        return {
            "top1_expected_template_hit": None,
            "topk_expected_template_hit": None,
        }

    candidate_ids = [candidate.get("template_id") for candidate in report.get("candidates", [])]
    top1 = report.get("recommended_template")
    return {
        "top1_expected_template_hit": top1 == expected_template,
        "topk_expected_template_hit": expected_template in candidate_ids,
    }


def build_aggregate_metrics(case_summaries):
    aggregate = {
        "passed_case_count": 0,
        "failed_case_count": 0,
        "cases_with_expected_template": 0,
        "top1_expected_template_hit_count": 0,
        "topk_expected_template_hit_count": 0,
        "cases_with_expected_neighbors": 0,
        "top1_expected_neighbor_hit_count": 0,
        "topk_expected_neighbor_hit_count": 0,
    }

    for case in case_summaries:
        if case.get("status") == "passed":
            aggregate["passed_case_count"] += 1
        else:
            aggregate["failed_case_count"] += 1

        expected_template_metrics = case.get("expected_template_metrics", {})
        if expected_template_metrics.get("top1_expected_template_hit") is not None:
            aggregate["cases_with_expected_template"] += 1
            if expected_template_metrics.get("top1_expected_template_hit"):
                aggregate["top1_expected_template_hit_count"] += 1
            if expected_template_metrics.get("topk_expected_template_hit"):
                aggregate["topk_expected_template_hit_count"] += 1

        neighbor_metrics = case.get("neighbor_metrics", {})
        if neighbor_metrics.get("top1_expected_hit") is not None:
            aggregate["cases_with_expected_neighbors"] += 1
            if neighbor_metrics.get("top1_expected_hit"):
                aggregate["top1_expected_neighbor_hit_count"] += 1
            if neighbor_metrics.get("topk_expected_hit"):
                aggregate["topk_expected_neighbor_hit_count"] += 1

    if aggregate["cases_with_expected_template"] > 0:
        aggregate["top1_expected_template_hit_rate"] = round(
            aggregate["top1_expected_template_hit_count"] / float(aggregate["cases_with_expected_template"]),
            6,
        )
        aggregate["topk_expected_template_hit_rate"] = round(
            aggregate["topk_expected_template_hit_count"] / float(aggregate["cases_with_expected_template"]),
            6,
        )
    else:
        aggregate["top1_expected_template_hit_rate"] = None
        aggregate["topk_expected_template_hit_rate"] = None

    if aggregate["cases_with_expected_neighbors"] > 0:
        aggregate["top1_expected_neighbor_hit_rate"] = round(
            aggregate["top1_expected_neighbor_hit_count"] / float(aggregate["cases_with_expected_neighbors"]),
            6,
        )
        aggregate["topk_expected_neighbor_hit_rate"] = round(
            aggregate["topk_expected_neighbor_hit_count"] / float(aggregate["cases_with_expected_neighbors"]),
            6,
        )
    else:
        aggregate["top1_expected_neighbor_hit_rate"] = None
        aggregate["topk_expected_neighbor_hit_rate"] = None

    return aggregate


def load_json(path):
    if not path.is_file():
        raise FileNotFoundError("Missing JSON file: %s" % path)
    return json.loads(path.read_text(encoding="utf-8"))


def copy_if_exists(source, destination):
    if source.is_file():
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)


def run_benchmark(args):
    root = repo_root()
    manifest_path = resolve_manifest_path(root, args.manifest)
    manifest = load_benchmark_cases(manifest_path, root)
    selected_cases = select_cases(
        manifest["cases"],
        case_ids=args.case_id or [],
        max_cases=args.max_cases,
    )

    label = args.label or datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    run_dir = (root / args.report_dir / label).resolve()
    run_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(manifest_path, run_dir / manifest_path.name)

    summary = {
        "manifest_path": str(manifest_path),
        "run_dir": str(run_dir),
        "label": label,
        "python": args.python,
        "template_backend": args.template_backend,
        "template_topk": int(args.template_topk),
        "template_rerank_topn": int(args.template_rerank_topn),
        "selected_case_count": len(selected_cases),
        "cases": [],
    }

    failures = []
    for case in selected_cases:
        case_dir = run_dir / case["case_id"]
        output_dir = case_dir / "run-output"
        log_path = case_dir / "benchmark_case.log"
        command = build_command(args, case, output_dir)
        case_summary = {
            "case_id": case["case_id"],
            "query_input": case["query_input"],
            "ec_file": case.get("ec_file"),
            "reference_model": case.get("reference_model"),
            "expected_template": case.get("expected_template"),
            "expected_taxonomic_neighbors": case.get("expected_taxonomic_neighbors", []),
            "exclude_templates": case.get("exclude_templates", []),
            "tags": case.get("tags", []),
            "notes": case.get("notes"),
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
            candidates_path = output_dir / "0_template_recommendation" / "template_candidates.tsv"
            report = load_json(recommendation_path)
            errors = validate_report(report)
            if errors:
                raise RuntimeError("; ".join(errors))

            copy_if_exists(recommendation_path, case_dir / "template_recommendation.json")
            copy_if_exists(candidates_path, case_dir / "template_candidates.tsv")

            case_summary["status"] = "passed"
            case_summary["template_recommendation_path"] = str(recommendation_path)
            case_summary["template_candidates_path"] = str(candidates_path)
            case_summary["recommended_template"] = report.get("recommended_template")
            case_summary["backend"] = report.get("backend")
            case_summary["selection_strategy"] = report.get("selection_strategy")
            case_summary["neighbor_metrics"] = compute_neighbor_metrics(
                report,
                case.get("expected_taxonomic_neighbors", []),
            )
            case_summary["expected_template_metrics"] = compute_expected_template_metrics(
                report,
                case.get("expected_template"),
            )
            case_summary["report"] = report
        except Exception as exc:
            case_summary["status"] = "failed"
            case_summary["error"] = str(exc)
            failures.append(case_summary)

        summary["cases"].append(case_summary)

    summary["failure_count"] = len(failures)
    summary["status"] = "failed" if failures else "passed"
    summary["aggregate_metrics"] = build_aggregate_metrics(summary["cases"])
    summary_path = run_dir / "benchmark_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("Benchmark summary written to %s" % summary_path)

    if failures:
        print("Benchmark run completed with failures:", file=sys.stderr)
        for failure in failures:
            print(
                "  %s: %s"
                % (failure["case_id"], failure.get("error", "unknown error")),
                file=sys.stderr,
            )
        return 1
    return 0


def build_parser():
    parser = argparse.ArgumentParser(
        description="Run recommendation-only auto-template benchmark cases and collect machine-readable summaries."
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
        help="Base directory for benchmark outputs relative to the repo root",
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
        help="Run only the specified case id. Repeatable.",
    )
    parser.add_argument(
        "--max-cases",
        type=int,
        default=None,
        help="Optional cap on how many manifest cases to run.",
    )
    parser.add_argument(
        "--template-backend",
        default="auto",
        choices=["auto", "skani", "diamond"],
        help="Value forwarded to run_gmsm.py --template-backend",
    )
    parser.add_argument(
        "--template-topk",
        type=int,
        default=3,
        help="Value forwarded to run_gmsm.py --template-topk",
    )
    parser.add_argument(
        "--template-rerank-topn",
        type=int,
        default=3,
        help="Value forwarded to run_gmsm.py --template-rerank-topn",
    )
    parser.add_argument(
        "--template-genome-bank",
        default=None,
        help="Optional explicit template genome bank path forwarded to run_gmsm.py",
    )
    for field_name, cli_option in WEIGHT_OPTION_MAP:
        parser.add_argument(
            cli_option,
            dest=field_name,
            type=float,
            default=None,
            help="Optional score-weight override forwarded to run_gmsm.py",
        )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    return run_benchmark(args)


if __name__ == "__main__":
    sys.exit(main())

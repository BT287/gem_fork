#!/usr/bin/env python

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


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


def load_report(report_path):
    if not report_path.is_file():
        raise FileNotFoundError("Recommendation report not found: %s" % report_path)
    return json.loads(report_path.read_text())


def validate_case(report, expected_backend, expected_strategy, rerank_topn):
    errors = []
    if report.get("backend") != expected_backend:
        errors.append("backend=%r (expected %r)" % (report.get("backend"), expected_backend))
    if report.get("selection_strategy") != expected_strategy:
        errors.append(
            "selection_strategy=%r (expected %r)"
            % (report.get("selection_strategy"), expected_strategy)
        )
    if int(report.get("rerank_topn", -1)) != int(rerank_topn):
        errors.append("rerank_topn=%r (expected %r)" % (report.get("rerank_topn"), rerank_topn))
    if not report.get("recommended_template"):
        errors.append("recommended_template is empty")
    if errors:
        raise RuntimeError("; ".join(errors))


def case_output_name(rerank_topn):
    if int(rerank_topn) == 0:
        return "output_auto_template_smoke"
    return "output_auto_template_rerank"


def build_command(args, output_dir, rerank_topn):
    command = [
        args.python,
        "run_gmsm.py",
        "-i",
        args.input,
        "--auto-template",
        "--template-recommendation-only",
        "--template-rerank-topn",
        str(rerank_topn),
        "-p",
        "-d",
        "-o",
        str(output_dir),
    ]
    if args.template_backend != "auto":
        command.extend(["--template-backend", args.template_backend])
    if args.template_genome_bank:
        command.extend(["--template-genome-bank", args.template_genome_bank])
    if args.ec_file:
        command.extend(["-e", args.ec_file])
    return command


def main():
    parser = argparse.ArgumentParser(
        description="Run recommendation-only smoke tests and validate the generated template recommendation JSON."
    )
    parser.add_argument(
        "--python",
        default=sys.executable,
        help="Python executable used to launch run_gmsm.py (default: current interpreter)",
    )
    parser.add_argument(
        "--input",
        default="input/NC_021985.1_antismash8.gbk",
        help="Input genome file passed to run_gmsm.py",
    )
    parser.add_argument(
        "--ec-file",
        default=None,
        help="Optional EC prediction file passed through to run_gmsm.py",
    )
    parser.add_argument(
        "--expected-backend",
        required=True,
        choices=["skani", "diamond"],
        help="Backend that must appear in template_recommendation.json",
    )
    parser.add_argument(
        "--template-backend",
        default="auto",
        choices=["auto", "skani", "diamond"],
        help="Value to pass to --template-backend when launching run_gmsm.py",
    )
    parser.add_argument(
        "--template-genome-bank",
        default=None,
        help="Optional explicit template genome bank path",
    )
    parser.add_argument(
        "--report-dir",
        default="smoke-artifacts",
        help="Directory for smoke logs, outputs, and the summary JSON",
    )
    parser.add_argument(
        "--rerank-topn",
        action="append",
        type=int,
        default=[],
        help="Rerank value to test. Repeatable. Defaults to 0 and 3.",
    )
    args = parser.parse_args()

    root = repo_root()
    report_dir = (root / args.report_dir).resolve()
    report_dir.mkdir(parents=True, exist_ok=True)
    rerank_values = args.rerank_topn or [0, 3]

    summary = {
        "expected_backend": args.expected_backend,
        "template_backend": args.template_backend,
        "cases": [],
    }

    failures = []
    for rerank_topn in rerank_values:
        expected_strategy = "coarse_plus_bbh" if int(rerank_topn) > 0 else "coarse_only"
        output_dir = report_dir / case_output_name(rerank_topn)
        log_path = report_dir / ("smoke_rerank_%s.log" % rerank_topn)
        command = build_command(args, output_dir, rerank_topn)

        print("Running smoke case rerank_topn=%s" % rerank_topn)
        print("Command: %s" % " ".join(command))
        returncode = stream_command(command, cwd=root, log_path=log_path)

        report_path = output_dir / "0_template_recommendation" / "template_recommendation.json"
        case_summary = {
            "rerank_topn": int(rerank_topn),
            "expected_strategy": expected_strategy,
            "output_dir": str(output_dir),
            "log_path": str(log_path),
            "report_path": str(report_path),
            "returncode": returncode,
        }

        try:
            if returncode != 0:
                raise RuntimeError("run_gmsm.py exited with code %s" % returncode)
            report = load_report(report_path)
            validate_case(report, args.expected_backend, expected_strategy, rerank_topn)
            case_summary["report"] = report
            case_summary["status"] = "passed"
        except Exception as exc:
            case_summary["status"] = "failed"
            case_summary["error"] = str(exc)
            failures.append(case_summary)

        summary["cases"].append(case_summary)

    summary_path = report_dir / "template_recommendation_smoke_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print("Smoke summary written to %s" % summary_path)

    if failures:
        print("Smoke validation failed:", file=sys.stderr)
        for failure in failures:
            print(
                "  rerank_topn=%s: %s"
                % (failure["rerank_topn"], failure.get("error", "unknown error")),
                file=sys.stderr,
            )
        return 1

    print("Smoke validation passed for rerank values: %s" % ", ".join(map(str, rerank_values)))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


PRIMARY_REQUIRED_FILES = [
    "model.xml",
    "manifest.json",
    "summary_report.json",
    "report.md",
    "reactions.tsv",
    "metabolites.tsv",
    "gpr_notes.tsv",
    "template_remaining_reactions.tsv",
    "kegg_added_reactions.tsv",
]

COMPLETE_REQUIRED_FILES = PRIMARY_REQUIRED_FILES + [
    "bgc_fluxes.tsv",
    "gapfilling_needed.tsv",
]


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


def load_json(path):
    if not path.is_file():
        raise FileNotFoundError("Missing JSON file: %s" % path)
    return json.loads(path.read_text())


def ensure_files_exist(folder, required_files, label):
    errors = []
    for filename in required_files:
        path = folder / filename
        if not path.is_file():
            errors.append("%s missing required file %s" % (label, filename))
    return errors


def validate_template_report(report, expected_backend):
    errors = []
    if report.get("selection_mode") not in (None, "auto"):
        errors.append("template report selection_mode=%r (expected None or 'auto')" % report.get("selection_mode"))
    if expected_backend and report.get("backend") != expected_backend:
        errors.append("template report backend=%r (expected %r)" % (report.get("backend"), expected_backend))
    if not report.get("selection_strategy"):
        errors.append("template report selection_strategy is empty")
    if not report.get("recommended_template"):
        errors.append("template report recommended_template is empty")
    return errors


def validate_manifest(manifest, expected_model_kind, required_logical_names, label):
    errors = []
    if manifest.get("model_kind") != expected_model_kind:
        errors.append("%s manifest model_kind=%r (expected %r)" % (label, manifest.get("model_kind"), expected_model_kind))
    logical_names = {entry.get("logical_name") for entry in manifest.get("files", [])}
    for logical_name in required_logical_names:
        if logical_name not in logical_names:
            errors.append("%s manifest missing logical_name %r" % (label, logical_name))
    return errors


def validate_summary(summary, expected_backend, label, require_secondary):
    errors = []
    if summary.get("template_selection_mode") != "auto":
        errors.append("%s summary template_selection_mode=%r (expected 'auto')" % (label, summary.get("template_selection_mode")))
    if expected_backend and summary.get("template_selection_backend") != expected_backend:
        errors.append(
            "%s summary template_selection_backend=%r (expected %r)"
            % (label, summary.get("template_selection_backend"), expected_backend)
        )
    if not summary.get("template_selection_strategy"):
        errors.append("%s summary template_selection_strategy is empty" % label)
    if not summary.get("template_selection_confidence"):
        errors.append("%s summary template_selection_confidence is empty" % label)
    if summary.get("primary_metabolic_modeling") is not True:
        errors.append("%s summary primary_metabolic_modeling=%r (expected True)" % (label, summary.get("primary_metabolic_modeling")))
    if require_secondary and summary.get("secondary_metabolic_modeling") is not True:
        errors.append(
            "%s summary secondary_metabolic_modeling=%r (expected True)"
            % (label, summary.get("secondary_metabolic_modeling"))
        )
    for count_key in ("number_reactions", "number_metabolites", "number_genes"):
        value = summary.get(count_key)
        if not isinstance(value, int) or value <= 0:
            errors.append("%s summary %s=%r (expected positive integer)" % (label, count_key, value))
    if not summary.get("runtime"):
        errors.append("%s summary runtime is empty" % label)
    return errors


def copy_if_exists(source, destination):
    if source.is_file():
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)


def build_command(args, output_dir):
    command = [
        args.python,
        "run_gmsm.py",
        "-i",
        args.input,
        "-e",
        args.ec_file,
        "--auto-template",
        "-p",
        "-d",
        "-o",
        str(output_dir),
    ]
    if not args.skip_secondary:
        command.append("-s")
    if args.template_backend != "auto":
        command.extend(["--template-backend", args.template_backend])
    if args.template_genome_bank:
        command.extend(["--template-genome-bank", args.template_genome_bank])
    return command


def collect_validation_summary(output_dir, report_dir, expected_backend, require_secondary):
    template_dir = output_dir / "0_template_recommendation"
    primary_dir = output_dir / "3_primary_metabolic_model"
    complete_dir = output_dir / "4_complete_model"

    template_report_path = template_dir / "template_recommendation.json"
    primary_manifest_path = primary_dir / "manifest.json"
    primary_summary_path = primary_dir / "summary_report.json"
    complete_manifest_path = complete_dir / "manifest.json"
    complete_summary_path = complete_dir / "summary_report.json"

    summary = {
        "output_dir": str(output_dir),
        "expected_backend": expected_backend,
        "require_secondary": require_secondary,
        "checks": [],
    }

    errors = []

    template_report = load_json(template_report_path)
    template_errors = validate_template_report(template_report, expected_backend)
    summary["checks"].append({
        "label": "template_recommendation",
        "path": str(template_report_path),
        "status": "passed" if not template_errors else "failed",
        "errors": template_errors,
        "report": template_report,
    })
    errors.extend(template_errors)

    primary_file_errors = ensure_files_exist(primary_dir, PRIMARY_REQUIRED_FILES, "primary")
    primary_manifest = load_json(primary_manifest_path)
    primary_summary = load_json(primary_summary_path)
    primary_manifest_errors = validate_manifest(
        primary_manifest,
        "primary",
        ["model", "summary_json", "report", "reactions", "metabolites", "gpr_notes", "template_remaining_reactions", "kegg_added_reactions"],
        "primary",
    )
    primary_summary_errors = validate_summary(primary_summary, expected_backend, "primary", require_secondary)
    primary_errors = primary_file_errors + primary_manifest_errors + primary_summary_errors
    summary["checks"].append({
        "label": "primary_model",
        "path": str(primary_dir),
        "status": "passed" if not primary_errors else "failed",
        "errors": primary_errors,
        "manifest": primary_manifest,
        "summary_report": primary_summary,
    })
    errors.extend(primary_errors)

    copy_if_exists(template_report_path, report_dir / "template_recommendation.json")
    copy_if_exists(primary_manifest_path, report_dir / "primary_manifest.json")
    copy_if_exists(primary_summary_path, report_dir / "primary_summary_report.json")

    if require_secondary:
        complete_file_errors = ensure_files_exist(complete_dir, COMPLETE_REQUIRED_FILES, "complete")
        complete_manifest = load_json(complete_manifest_path)
        complete_summary = load_json(complete_summary_path)
        complete_manifest_errors = validate_manifest(
            complete_manifest,
            "complete",
            [
                "model",
                "summary_json",
                "report",
                "reactions",
                "metabolites",
                "gpr_notes",
                "template_remaining_reactions",
                "kegg_added_reactions",
                "bgc_fluxes",
                "gapfilling_needed",
            ],
            "complete",
        )
        complete_summary_errors = validate_summary(complete_summary, expected_backend, "complete", require_secondary)
        complete_errors = complete_file_errors + complete_manifest_errors + complete_summary_errors
        summary["checks"].append({
            "label": "complete_model",
            "path": str(complete_dir),
            "status": "passed" if not complete_errors else "failed",
            "errors": complete_errors,
            "manifest": complete_manifest,
            "summary_report": complete_summary,
        })
        errors.extend(complete_errors)

        copy_if_exists(complete_manifest_path, report_dir / "complete_manifest.json")
        copy_if_exists(complete_summary_path, report_dir / "complete_summary_report.json")

    return summary, errors


def main():
    parser = argparse.ArgumentParser(
        description="Run the full GMSM integration path and validate the key output artifacts."
    )
    parser.add_argument("--python", default=sys.executable, help="Python executable used to launch run_gmsm.py")
    parser.add_argument(
        "--input",
        default="input/NC_021985.1_antismash8.gbk",
        help="Input genome file passed to run_gmsm.py",
    )
    parser.add_argument(
        "--ec-file",
        default="input/NC_021985.1_deepec.txt",
        help="EC prediction file passed to run_gmsm.py",
    )
    parser.add_argument(
        "--template-backend",
        default="auto",
        choices=["auto", "skani", "diamond"],
        help="Value to pass to --template-backend",
    )
    parser.add_argument(
        "--expected-backend",
        default=None,
        choices=["skani", "diamond"],
        help="Expected backend recorded in the template recommendation outputs",
    )
    parser.add_argument(
        "--template-genome-bank",
        default=None,
        help="Optional explicit template genome bank path",
    )
    parser.add_argument(
        "--report-dir",
        default="full-integration-artifacts",
        help="Directory for the validator log, copied JSON reports, and summary JSON",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Directory passed to run_gmsm.py. Defaults to <report-dir>/run_output",
    )
    parser.add_argument(
        "--skip-secondary",
        action="store_true",
        help="Run only the primary modeling path and skip the -s secondary modeling stage",
    )
    parser.add_argument(
        "--validate-existing",
        action="store_true",
        help="Skip launching run_gmsm.py and validate an existing output directory",
    )
    args = parser.parse_args()

    root = repo_root()
    report_dir = (root / args.report_dir).resolve()
    report_dir.mkdir(parents=True, exist_ok=True)
    output_dir = (root / args.output_dir).resolve() if args.output_dir else (report_dir / "run_output")
    log_path = report_dir / "full_integration.log"

    summary = {
        "report_dir": str(report_dir),
        "output_dir": str(output_dir),
        "validate_existing": bool(args.validate_existing),
        "template_backend": args.template_backend,
        "expected_backend": args.expected_backend,
        "secondary_modeling": not args.skip_secondary,
        "log_path": str(log_path),
    }

    returncode = None
    if not args.validate_existing:
        if output_dir.exists():
            shutil.rmtree(output_dir)
        command = build_command(args, output_dir)
        print("Running full integration command:")
        print("  %s" % " ".join(command))
        returncode = stream_command(command, cwd=root, log_path=log_path)
    else:
        print("Validating existing full integration output at %s" % output_dir)

    summary["returncode"] = returncode

    errors = []
    if returncode not in (None, 0):
        errors.append("run_gmsm.py exited with code %s" % returncode)

    try:
        validation_summary, validation_errors = collect_validation_summary(
            output_dir,
            report_dir,
            args.expected_backend,
            not args.skip_secondary,
        )
        summary.update(validation_summary)
        errors.extend(validation_errors)
    except Exception as exc:
        errors.append(str(exc))

    summary["status"] = "passed" if not errors else "failed"
    summary["errors"] = errors

    summary_path = report_dir / "full_integration_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print("Full integration summary written to %s" % summary_path)

    if errors:
        print("Full integration validation failed:", file=sys.stderr)
        for error in errors:
            print("  %s" % error, file=sys.stderr)
        return 1

    print("Full integration validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())

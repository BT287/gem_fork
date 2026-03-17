#!/usr/bin/env python

import argparse
import json
from pathlib import Path

import cobra


def precision_recall_f1(predicted_ids, reference_ids):
    predicted = set(predicted_ids)
    reference = set(reference_ids)
    overlap = predicted & reference

    predicted_count = len(predicted)
    reference_count = len(reference)
    overlap_count = len(overlap)

    precision = overlap_count / float(predicted_count) if predicted_count else None
    recall = overlap_count / float(reference_count) if reference_count else None
    if precision is None or recall is None or (precision + recall) == 0:
        f1 = None if precision is None or recall is None else 0.0
    else:
        f1 = 2.0 * precision * recall / (precision + recall)

    return {
        "predicted_count": predicted_count,
        "reference_count": reference_count,
        "overlap_count": overlap_count,
        "precision": round(precision, 6) if precision is not None else None,
        "recall": round(recall, 6) if recall is not None else None,
        "f1": round(f1, 6) if f1 is not None else None,
        "overlap_ids": sorted(overlap),
    }


def resolve_model_xml(path_value, model_kind="auto"):
    path = Path(path_value).resolve()
    if path.is_file():
        return path

    if not path.exists():
        raise FileNotFoundError("Model path not found: %s" % path)

    if model_kind == "complete":
        candidates = [path / "4_complete_model" / "model.xml", path / "model.xml"]
    elif model_kind == "primary":
        candidates = [path / "3_primary_metabolic_model" / "model.xml", path / "model.xml"]
    else:
        candidates = [
            path / "4_complete_model" / "model.xml",
            path / "3_primary_metabolic_model" / "model.xml",
            path / "model.xml",
        ]

    for candidate in candidates:
        if candidate.is_file():
            return candidate

    raise FileNotFoundError("Could not resolve model.xml under %s" % path)


def load_model_sets(model_path):
    model = cobra.io.read_sbml_model(str(model_path))
    reaction_ids = sorted(reaction.id for reaction in model.reactions)
    gene_ids = sorted(gene.id for gene in model.genes if gene.id)
    return {
        "model_id": model.id,
        "reaction_ids": reaction_ids,
        "gene_ids": gene_ids,
    }


def evaluate_single_case(predicted_path, reference_path, label=None, model_kind="auto"):
    predicted_model_path = resolve_model_xml(predicted_path, model_kind=model_kind)
    reference_model_path = resolve_model_xml(reference_path, model_kind="auto")

    predicted = load_model_sets(predicted_model_path)
    reference = load_model_sets(reference_model_path)

    return {
        "label": label,
        "predicted_model_path": str(predicted_model_path),
        "reference_model_path": str(reference_model_path),
        "predicted_model_id": predicted["model_id"],
        "reference_model_id": reference["model_id"],
        "reaction_metrics": precision_recall_f1(predicted["reaction_ids"], reference["reaction_ids"]),
        "gene_metrics": precision_recall_f1(predicted["gene_ids"], reference["gene_ids"]),
    }


def load_manifest(path):
    raw = Path(path).read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore
    except ImportError:
        payload = json.loads(raw)
    else:
        payload = yaml.safe_load(raw)
    return payload


def evaluate_benchmark_batch(manifest_path, benchmark_run_dir, model_kind="auto"):
    manifest = load_manifest(manifest_path)
    run_dir = Path(benchmark_run_dir).resolve()
    case_results = []

    for case in manifest.get("cases", []):
        case_id = case["case_id"]
        reference_model = case.get("reference_model")
        case_result = {
            "case_id": case_id,
            "reference_model": reference_model,
        }
        if not reference_model:
            case_result["status"] = "skipped"
            case_result["reason"] = "reference_model is not set"
            case_results.append(case_result)
            continue

        predicted_case_dir = run_dir / case_id / "run-output"
        try:
            case_result["evaluation"] = evaluate_single_case(
                predicted_path=predicted_case_dir,
                reference_path=reference_model,
                label=case_id,
                model_kind=model_kind,
            )
            case_result["status"] = "evaluated"
        except Exception as exc:
            case_result["status"] = "failed"
            case_result["reason"] = str(exc)
        case_results.append(case_result)

    evaluated = [case for case in case_results if case["status"] == "evaluated"]
    return {
        "manifest_path": str(Path(manifest_path).resolve()),
        "benchmark_run_dir": str(run_dir),
        "model_kind": model_kind,
        "case_count": len(case_results),
        "evaluated_case_count": len(evaluated),
        "skipped_case_count": sum(case["status"] == "skipped" for case in case_results),
        "failed_case_count": sum(case["status"] == "failed" for case in case_results),
        "cases": case_results,
    }


def write_json(path, payload):
    output_path = Path(path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_parser():
    parser = argparse.ArgumentParser(
        description="Evaluate reconstructed model quality against a trusted reference SBML."
    )
    parser.add_argument("--predicted", help="Predicted model path or output directory.")
    parser.add_argument("--reference", help="Reference SBML path or directory containing model.xml.")
    parser.add_argument("--label", default=None, help="Optional label for the output JSON.")
    parser.add_argument(
        "--model-kind",
        default="auto",
        choices=["auto", "primary", "complete"],
        help="How to resolve model.xml when a directory is given.",
    )
    parser.add_argument(
        "--output-json",
        default=None,
        help="Where to write the evaluation JSON. Defaults next to the predicted model.",
    )
    parser.add_argument("--manifest", default=None, help="Benchmark manifest for batch evaluation.")
    parser.add_argument("--benchmark-run-dir", default=None, help="Benchmark run directory for batch evaluation.")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.manifest or args.benchmark_run_dir:
        if not (args.manifest and args.benchmark_run_dir):
            parser.error("--manifest and --benchmark-run-dir must be provided together for batch mode")
        payload = evaluate_benchmark_batch(
            manifest_path=args.manifest,
            benchmark_run_dir=args.benchmark_run_dir,
            model_kind=args.model_kind,
        )
        output_json = args.output_json or str(Path(args.benchmark_run_dir).resolve() / "evaluation_summary.json")
        write_json(output_json, payload)
        print("Evaluation summary written to %s" % output_json)
        return 0

    if not (args.predicted and args.reference):
        parser.error("single-case mode requires --predicted and --reference")

    payload = evaluate_single_case(
        predicted_path=args.predicted,
        reference_path=args.reference,
        label=args.label,
        model_kind=args.model_kind,
    )
    predicted_model_path = Path(payload["predicted_model_path"])
    output_json = args.output_json or str(predicted_model_path.parent / "evaluation.json")
    write_json(output_json, payload)
    print("Evaluation summary written to %s" % output_json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

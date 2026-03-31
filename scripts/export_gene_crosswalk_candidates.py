#!/usr/bin/env python

import argparse
import csv
import importlib.util
import json
from pathlib import Path


def load_reconstruction_eval_module():
    script_path = Path(__file__).resolve().parent / "evaluate_reconstruction_quality.py"
    spec = importlib.util.spec_from_file_location("evaluate_reconstruction_quality", script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_evaluation_payload(
    evaluation_json=None,
    predicted=None,
    reference=None,
    query_genbank=None,
    label=None,
    model_kind="auto",
):
    if evaluation_json:
        return json.loads(Path(evaluation_json).read_text(encoding="utf-8"))

    module = load_reconstruction_eval_module()
    return module.evaluate_single_case(
        predicted_path=predicted,
        reference_path=reference,
        query_genbank=query_genbank,
        label=label,
        model_kind=model_kind,
    )


def build_candidate_crosswalk_rows(payload, min_shared_aliases=1):
    gene_alias_metrics = payload.get("gene_alias_metrics") or {}
    if gene_alias_metrics.get("status") != "evaluated":
        raise ValueError("gene_alias_metrics are not available in this evaluation payload")

    rows = []
    for pair in gene_alias_metrics.get("matched_pairs", []):
        shared_aliases = list(pair.get("shared_aliases", []))
        if len(shared_aliases) < int(min_shared_aliases):
            continue
        rows.append(
            {
                "predicted_gene_id": pair["predicted_gene_id"],
                "reference_gene_id": pair["reference_gene_id"],
                "shared_alias_count": len(shared_aliases),
                "shared_aliases": ";".join(shared_aliases),
            }
        )
    return rows


def write_crosswalk_tsv(path, rows):
    output_path = Path(path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=("predicted_gene_id", "reference_gene_id", "shared_alias_count", "shared_aliases"),
            delimiter="\t",
        )
        writer.writeheader()
        writer.writerows(rows)


def write_summary_json(path, payload):
    output_path = Path(path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_parser():
    parser = argparse.ArgumentParser(
        description="Export candidate predicted-to-reference gene crosswalk rows from an E2E evaluation payload."
    )
    parser.add_argument("--evaluation-json", default=None, help="Existing evaluation JSON containing gene_alias_metrics.")
    parser.add_argument("--predicted", default=None, help="Predicted model path or output directory.")
    parser.add_argument("--reference", default=None, help="Reference SBML path or directory containing model.xml.")
    parser.add_argument("--query-genbank", default=None, help="Query GenBank used for alias-based harmonization.")
    parser.add_argument("--label", default=None, help="Optional label when evaluating on the fly.")
    parser.add_argument(
        "--model-kind",
        default="auto",
        choices=["auto", "primary", "complete"],
        help="How to resolve model.xml when a directory is given.",
    )
    parser.add_argument(
        "--min-shared-aliases",
        type=int,
        default=1,
        help="Only export rows with at least this many shared aliases (default: %(default)s).",
    )
    parser.add_argument("--output-tsv", required=True, help="Where to write the candidate crosswalk TSV.")
    parser.add_argument(
        "--output-summary-json",
        default=None,
        help="Optional JSON summary for the exported candidate crosswalk rows.",
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.evaluation_json and not (args.predicted and args.reference):
        parser.error("provide either --evaluation-json or the trio of --predicted/--reference with optional --query-genbank")

    payload = load_evaluation_payload(
        evaluation_json=args.evaluation_json,
        predicted=args.predicted,
        reference=args.reference,
        query_genbank=args.query_genbank,
        label=args.label,
        model_kind=args.model_kind,
    )
    rows = build_candidate_crosswalk_rows(payload, min_shared_aliases=args.min_shared_aliases)
    write_crosswalk_tsv(args.output_tsv, rows)

    summary = {
        "label": payload.get("label"),
        "predicted_model_id": payload.get("predicted_model_id"),
        "reference_model_id": payload.get("reference_model_id"),
        "candidate_row_count": len(rows),
        "min_shared_aliases": int(args.min_shared_aliases),
        "output_tsv": str(Path(args.output_tsv).resolve()),
    }
    if args.output_summary_json:
        write_summary_json(args.output_summary_json, summary)

    print("Exported %d candidate crosswalk rows to %s" % (len(rows), args.output_tsv))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

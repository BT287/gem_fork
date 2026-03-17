#!/usr/bin/env python

import argparse
import ast
import json
import re
from collections import defaultdict
from pathlib import Path

import cobra

try:
    from Bio import SeqIO
except ImportError:  # pragma: no cover - runtime dependency handled by CLI flow
    SeqIO = None


GENBANK_SUFFIXES = {".gb", ".gbk", ".gbff", ".genbank"}
REFERENCE_ALIAS_FIELDS = (
    "refseq_name",
    "name",
    "gene",
    "refseq_locus_tag",
    "refseq_old_locus_tag",
    "old_locus_tag",
    "locus_tag",
    "ncbigi",
    "ncbigene",
)
NOTE_ALIAS_SPLIT_RE = re.compile(r"[:;,|]")
NOTE_ALIAS_TOKEN_RE = re.compile(r"^[A-Za-z0-9_.-]{2,40}$")


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


def iter_annotation_values(value):
    if value in (None, ""):
        return []
    if isinstance(value, (list, tuple, set)):
        items = value
    else:
        items = [value]
    normalized = []
    for item in items:
        text = str(item).strip()
        if text:
            normalized.append(text)
    return normalized


def extract_note_aliases(note_values):
    aliases = set()
    for note in note_values or []:
        for token in NOTE_ALIAS_SPLIT_RE.split(str(note)):
            token = token.strip()
            if not token or " " in token:
                continue
            if not NOTE_ALIAS_TOKEN_RE.match(token):
                continue
            if not any(character.isdigit() for character in token):
                continue
            aliases.add(token)
    return aliases


def build_query_alias_lookup(query_genbank_path):
    if SeqIO is None:
        raise ImportError("Biopython is required for GenBank-based gene harmonization")

    query_path = Path(query_genbank_path).resolve()
    alias_lookup = defaultdict(set)

    for record in SeqIO.parse(str(query_path), "genbank"):
        for feature in record.features:
            if feature.type != "CDS":
                continue

            qualifiers = feature.qualifiers
            direct_ids = set()
            alias_values = set()

            for field_name in ("gene", "locus_tag", "protein_id", "old_locus_tag"):
                for value in iter_annotation_values(qualifiers.get(field_name)):
                    direct_ids.add(value)
                    alias_values.add(value)

            for value in iter_annotation_values(qualifiers.get("db_xref")):
                direct_ids.add(value)
                alias_values.add(value)

            note_aliases = extract_note_aliases(qualifiers.get("note"))
            direct_ids.update(note_aliases)
            alias_values.update(note_aliases)

            if not direct_ids:
                continue

            for raw_identifier in direct_ids:
                alias_lookup[raw_identifier].update(alias_values)

    return dict(alias_lookup)


def build_reference_gene_aliases(reference_model):
    alias_map = {}
    for gene in reference_model.genes:
        aliases = {gene.id}
        annotation = getattr(gene, "annotation", {}) or {}
        for field_name in REFERENCE_ALIAS_FIELDS:
            for value in iter_annotation_values(annotation.get(field_name)):
                aliases.add(value)
        alias_map[gene.id] = aliases
    return alias_map


def resolve_run_root(predicted_path, predicted_model_path):
    original = Path(predicted_path).resolve()
    if original.is_dir():
        return original

    model_parent = predicted_model_path.parent
    if model_parent.name in ("3_primary_metabolic_model", "4_complete_model"):
        return model_parent.parent
    return model_parent


def load_template_to_target_bbh(run_root):
    bbh_path = Path(run_root).resolve() / "2_blastp_results" / "temp_target_BBH_dict.txt"
    if not bbh_path.is_file():
        return {}

    mapping = {}
    for raw_line in bbh_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        template_gene_id, targets_raw = line.split("\t", 1)
        mapping[template_gene_id] = set(ast.literal_eval(targets_raw))
    return mapping


def build_predicted_gene_aliases(predicted_model, query_alias_lookup, template_to_target_bbh):
    alias_map = {}
    for gene in predicted_model.genes:
        aliases = {gene.id}
        aliases.update(query_alias_lookup.get(gene.id, set()))
        for target_gene_id in template_to_target_bbh.get(gene.id, set()):
            aliases.update(query_alias_lookup.get(target_gene_id, set()))
        alias_map[gene.id] = aliases
    return alias_map


def build_candidate_reference_map(predicted_aliases, reference_aliases):
    alias_to_reference_gene_ids = defaultdict(set)
    for reference_gene_id, aliases in reference_aliases.items():
        for alias in aliases:
            alias_to_reference_gene_ids[alias].add(reference_gene_id)

    candidate_map = {}
    for predicted_gene_id, aliases in predicted_aliases.items():
        candidates = set()
        for alias in aliases:
            candidates.update(alias_to_reference_gene_ids.get(alias, set()))
        candidate_map[predicted_gene_id] = candidates
    return candidate_map


def maximum_bipartite_matching(candidate_map):
    matched_reference = {}

    def _augment(predicted_gene_id, seen_reference_gene_ids):
        for reference_gene_id in sorted(candidate_map[predicted_gene_id]):
            if reference_gene_id in seen_reference_gene_ids:
                continue
            seen_reference_gene_ids.add(reference_gene_id)
            if reference_gene_id not in matched_reference or _augment(
                matched_reference[reference_gene_id], seen_reference_gene_ids
            ):
                matched_reference[reference_gene_id] = predicted_gene_id
                return True
        return False

    for predicted_gene_id in sorted(candidate_map):
        _augment(predicted_gene_id, set())

    return {predicted_gene_id: reference_gene_id for reference_gene_id, predicted_gene_id in matched_reference.items()}


def compute_gene_alias_metrics(predicted_path, predicted_model_path, reference_model_path, query_genbank_path=None):
    if not query_genbank_path:
        return {
            "status": "skipped",
            "reason": "query_genbank is not set",
        }

    query_path = Path(query_genbank_path).resolve()
    if query_path.suffix.lower() not in GENBANK_SUFFIXES:
        return {
            "status": "skipped",
            "reason": "query_genbank is not a GenBank-like file",
            "query_genbank_path": str(query_path),
        }

    query_alias_lookup = build_query_alias_lookup(query_path)
    run_root = resolve_run_root(predicted_path, predicted_model_path)
    template_to_target_bbh = load_template_to_target_bbh(run_root)

    predicted_model = cobra.io.read_sbml_model(str(predicted_model_path))
    reference_model = cobra.io.read_sbml_model(str(reference_model_path))

    predicted_aliases = build_predicted_gene_aliases(predicted_model, query_alias_lookup, template_to_target_bbh)
    reference_aliases = build_reference_gene_aliases(reference_model)
    candidate_map = build_candidate_reference_map(predicted_aliases, reference_aliases)
    matched_pairs = maximum_bipartite_matching(candidate_map)

    matched_reference_gene_ids = sorted(matched_pairs.values())
    predicted_count = len(predicted_aliases)
    reference_count = len(reference_aliases)
    overlap_count = len(matched_pairs)

    precision = overlap_count / float(predicted_count) if predicted_count else None
    recall = overlap_count / float(reference_count) if reference_count else None
    if precision is None or recall is None or (precision + recall) == 0:
        f1 = None if precision is None or recall is None else 0.0
    else:
        f1 = 2.0 * precision * recall / (precision + recall)

    matched_pair_rows = []
    for predicted_gene_id, reference_gene_id in sorted(matched_pairs.items()):
        shared_aliases = sorted(predicted_aliases[predicted_gene_id] & reference_aliases[reference_gene_id])
        matched_pair_rows.append(
            {
                "predicted_gene_id": predicted_gene_id,
                "reference_gene_id": reference_gene_id,
                "shared_aliases": shared_aliases,
            }
        )

    return {
        "status": "evaluated",
        "strategy": "query_alias_intersection_max_matching",
        "query_genbank_path": str(query_path),
        "predicted_count": predicted_count,
        "reference_count": reference_count,
        "overlap_count": overlap_count,
        "precision": round(precision, 6) if precision is not None else None,
        "recall": round(recall, 6) if recall is not None else None,
        "f1": round(f1, 6) if f1 is not None else None,
        "overlap_ids": matched_reference_gene_ids,
        "predicted_genes_with_query_aliases": sum(len(aliases) > 1 for aliases in predicted_aliases.values()),
        "reference_genes_with_annotation_aliases": sum(len(aliases) > 1 for aliases in reference_aliases.values()),
        "predicted_genes_with_candidate_reference": sum(bool(candidates) for candidates in candidate_map.values()),
        "bbh_template_gene_count": len(template_to_target_bbh),
        "matched_pairs": matched_pair_rows,
    }


def evaluate_single_case(predicted_path, reference_path, label=None, model_kind="auto", query_genbank=None):
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
        "gene_alias_metrics": compute_gene_alias_metrics(
            predicted_path=predicted_path,
            predicted_model_path=predicted_model_path,
            reference_model_path=reference_model_path,
            query_genbank_path=query_genbank,
        ),
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
        query_input = case.get("query_input")
        try:
            case_result["evaluation"] = evaluate_single_case(
                predicted_path=predicted_case_dir,
                reference_path=reference_model,
                label=case_id,
                model_kind=model_kind,
                query_genbank=query_input,
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
        "--query-genbank",
        default=None,
        help="Optional GenBank query input used for alias-based gene harmonization.",
    )
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
        query_genbank=args.query_genbank,
    )
    predicted_model_path = Path(payload["predicted_model_path"])
    output_json = args.output_json or str(predicted_model_path.parent / "evaluation.json")
    write_json(output_json, payload)
    print("Evaluation summary written to %s" % output_json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

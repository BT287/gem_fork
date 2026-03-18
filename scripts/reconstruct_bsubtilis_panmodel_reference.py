#!/usr/bin/env python

import argparse
import json
import re
from pathlib import Path

import cobra
import numpy as np
from cobra.io.mat import from_mat_struct
from scipy.io import loadmat


X_GENE_RULE_PATTERN = re.compile(r"\bx\s*\(\s*(\d+)\s*\)")
NAMED_CALL_PATTERN = re.compile(
    r"\b(?!x\b)(?!and\b)(?!or\b)([A-Za-z_][A-Za-z0-9_]*)\s*\(\s*(\d+)\s*\)"
)
BARE_NUMERIC_PATTERN = re.compile(r"(?<![A-Za-z0-9_])\(\s*(\d+)\s*\)")
RULE_GENE_TOKEN_PATTERN = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\b")
BOOLEAN_TOKENS = {"and", "or", "not"}


def sanitize_gene_identifier(raw_gene_id):
    token = str(raw_gene_id).strip()
    if token.startswith("ogc_"):
        return token
    if token.isdigit():
        return f"ogc_{token}"
    token = re.sub(r"[^A-Za-z0-9_]+", "_", token).strip("_")
    return token or "ogc_unknown"


def sanitize_gr_rule(raw_rule):
    rule = str(raw_rule).strip()
    if not rule:
        return ""
    rule = X_GENE_RULE_PATTERN.sub(
        lambda match: sanitize_gene_identifier(match.group(1)),
        rule,
    )
    rule = NAMED_CALL_PATTERN.sub(
        lambda match: sanitize_gene_identifier(f"{match.group(1)}_{match.group(2)}"),
        rule,
    )
    rule = BARE_NUMERIC_PATTERN.sub(
        lambda match: sanitize_gene_identifier(match.group(1)),
        rule,
    )
    return rule


def extract_rule_gene_identifiers(rules):
    identifiers = []
    seen = set()
    for rule in rules:
        for token in RULE_GENE_TOKEN_PATTERN.findall(rule):
            if token in BOOLEAN_TOKENS:
                continue
            if token not in seen:
                identifiers.append(token)
                seen.add(token)
    return identifiers


def _wrap_matlab_cell_strings(values):
    wrapped = np.empty((len(values), 1), dtype=object)
    for index, value in enumerate(values):
        wrapped[index, 0] = np.array([value])
    return wrapped


def load_sanitized_pan_model(pan_model_path):
    payload = loadmat(str(pan_model_path), squeeze_me=False, struct_as_record=True)
    model_struct = payload["model"]

    genes = [
        sanitize_gene_identifier(entry[0])
        for entry in model_struct["genes"][0, 0].flatten()
    ]
    gr_rules = [
        sanitize_gr_rule(entry[0])
        for entry in model_struct["grRules"][0, 0].flatten()
    ]
    for gene_id in extract_rule_gene_identifiers(gr_rules):
        if gene_id not in genes:
            genes.append(gene_id)

    model_struct["genes"][0, 0] = _wrap_matlab_cell_strings(genes)
    model_struct["grRules"][0, 0] = _wrap_matlab_cell_strings(gr_rules)

    return from_mat_struct(model_struct, model_id=Path(pan_model_path).stem)


def coerce_scalar_string(value):
    current = value
    while isinstance(current, np.ndarray):
        if current.size == 0:
            return ""
        current = current.flat[0]
    return str(current)


def load_strain_accessions(strain_list_path):
    payload = loadmat(str(strain_list_path), squeeze_me=True, struct_as_record=False)
    strain_list = payload["strain_list"]
    if getattr(strain_list, "ndim", 0) == 0:
        return [coerce_scalar_string(strain_list)]
    return [coerce_scalar_string(entry) for entry in strain_list]


def resolve_accession_index(accessions, accession):
    if accession not in accessions:
        raise RuntimeError(f"Accession '{accession}' was not found in strain_list.mat")
    return accessions.index(accession)


def load_reaction_presence_vector(rxn_strain_matrix_path, accession_index):
    payload = loadmat(str(rxn_strain_matrix_path), squeeze_me=True, struct_as_record=False)
    matrix = payload["rxn_strain_matrix"]
    return matrix[:, accession_index].astype(bool)


def reconstruct_strain_model(pan_model, reaction_presence, model_id):
    strain_model = pan_model.copy()
    absent_ids = [
        reaction.id
        for reaction, is_present in zip(strain_model.reactions, reaction_presence)
        if not is_present
    ]
    if absent_ids:
        strain_model.remove_reactions(absent_ids, remove_orphans=True)
    strain_model.id = model_id
    return strain_model


def write_summary_json(path, payload):
    output_path = Path(path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_parser():
    parser = argparse.ArgumentParser(
        description="Reconstruct a strain-specific Bacillus subtilis model from the public pan-model source."
    )
    parser.add_argument(
        "--source-dir",
        required=True,
        help="Directory containing pan_model.mat, rxn_strain_matrix.mat, and strain_list.mat.",
    )
    parser.add_argument("--accession", required=True, help="Exact accession present in strain_list.mat, e.g. GCF_000497485_1.")
    parser.add_argument("--model-id", required=True, help="Model identifier to assign to the reconstructed strain model.")
    parser.add_argument("--output-model", required=True, help="Where to write the reconstructed SBML model.")
    parser.add_argument("--output-summary-json", default=None, help="Optional JSON summary path.")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    source_dir = Path(args.source_dir).resolve()
    pan_model_path = source_dir / "pan_model.mat"
    rxn_strain_matrix_path = source_dir / "rxn_strain_matrix.mat"
    strain_list_path = source_dir / "strain_list.mat"

    pan_model = load_sanitized_pan_model(pan_model_path)
    accessions = load_strain_accessions(strain_list_path)
    accession_index = resolve_accession_index(accessions, args.accession)
    reaction_presence = load_reaction_presence_vector(rxn_strain_matrix_path, accession_index)
    strain_model = reconstruct_strain_model(pan_model, reaction_presence, model_id=args.model_id)

    output_model_path = Path(args.output_model).resolve()
    output_model_path.parent.mkdir(parents=True, exist_ok=True)
    cobra.io.write_sbml_model(strain_model, str(output_model_path))

    summary = {
        "accession": args.accession,
        "accession_index": accession_index,
        "model_id": strain_model.id,
        "source_dir": str(source_dir),
        "output_model": str(output_model_path),
        "pan_model_reaction_count": len(pan_model.reactions),
        "pan_model_gene_count": len(pan_model.genes),
        "strain_reaction_count": len(strain_model.reactions),
        "strain_gene_count": len(strain_model.genes),
        "removed_reaction_count": int(len(pan_model.reactions) - len(strain_model.reactions)),
    }
    if args.output_summary_json:
        write_summary_json(args.output_summary_json, summary)

    print(
        "Reconstructed %s with %d reactions (%d removed from pan-model)"
        % (args.model_id, len(strain_model.reactions), summary["removed_reaction_count"])
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

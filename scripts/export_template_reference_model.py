#!/usr/bin/env python

import argparse
import sys
from pathlib import Path

import cobra


def repo_root():
    return Path(__file__).resolve().parent.parent


REPO_ROOT = repo_root()
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from gmsm import utils


def resolve_template_pickle(template_id):
    pickle_path = REPO_ROOT / "gmsm" / "io" / "data" / "input1" / template_id / "model.p"
    if not pickle_path.is_file():
        raise FileNotFoundError("Template pickle not found: %s" % pickle_path)
    return pickle_path


def export_template_reference_model(template_id, output_path):
    model = utils.load_legacy_cobra_pickle(str(resolve_template_pickle(template_id)))
    utils.ensure_modern_cobra_attrs(model)
    for reaction in model.reactions:
        if reaction.gene_reaction_rule == "()":
            reaction.gene_reaction_rule = ""

    output_file = Path(output_path).resolve()
    output_file.parent.mkdir(parents=True, exist_ok=True)
    cobra.io.write_sbml_model(model, str(output_file))
    reloaded = cobra.io.read_sbml_model(str(output_file))
    return {
        "template_id": template_id,
        "output_path": str(output_file),
        "model_id": reloaded.id,
        "reaction_count": len(reloaded.reactions),
        "gene_count": len(reloaded.genes),
    }


def build_parser():
    parser = argparse.ArgumentParser(
        description="Export a curated template pickle under gmsm/io/data/input1 as an SBML reference model."
    )
    parser.add_argument("--template-id", required=True, help="Template id such as eco or bsu.")
    parser.add_argument("--output", required=True, help="Output SBML path.")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    summary = export_template_reference_model(args.template_id, args.output)
    print(
        "Exported template '%s' as SBML to %s (model_id=%s, reactions=%d, genes=%d)"
        % (
            summary["template_id"],
            summary["output_path"],
            summary["model_id"],
            summary["reaction_count"],
            summary["gene_count"],
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

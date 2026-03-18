import importlib.util

import cobra


def load_module():
    from pathlib import Path

    script_path = Path(__file__).resolve().parents[2] / "scripts" / "reconstruct_bsubtilis_panmodel_reference.py"
    spec = importlib.util.spec_from_file_location("reconstruct_bsubtilis_panmodel_reference", script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class TestReconstructBsubtilisPanmodelReference:

    def test_sanitize_gene_identifier_numeric_cluster(self):
        module = load_module()

        assert module.sanitize_gene_identifier("987") == "ogc_987"
        assert module.sanitize_gene_identifier("ogc_987") == "ogc_987"

    def test_sanitize_gr_rule_rewrites_function_like_tokens(self):
        module = load_module()

        rule = "x ( 926 ) or x ( 3553 ) and x ( 4147 )"

        assert module.sanitize_gr_rule(rule) == "ogc_926 or ogc_3553 and ogc_4147"

    def test_sanitize_gr_rule_rewrites_gap_calls_and_bare_numeric_terms(self):
        module = load_module()

        rule = "x ( 428 ) or strain_GAP ( 5 ) or ( 495 )"

        assert module.sanitize_gr_rule(rule) == "ogc_428 or strain_GAP_5 or ogc_495"

    def test_extract_rule_gene_identifiers_ignores_boolean_tokens(self):
        module = load_module()

        identifiers = module.extract_rule_gene_identifiers(
            [
                "ogc_428 and strain_GAP_5 or ogc_495",
                "strain_GAP_5 or ogc_926",
            ]
        )

        assert identifiers == ["ogc_428", "strain_GAP_5", "ogc_495", "ogc_926"]

    def test_coerce_scalar_string_handles_nested_arrays(self):
        module = load_module()

        import numpy as np

        wrapped = np.array([np.array(["GCF_000497485_1"])], dtype=object)

        assert module.coerce_scalar_string(wrapped) == "GCF_000497485_1"

    def test_resolve_accession_index_rejects_unknown_accession(self):
        module = load_module()

        try:
            module.resolve_accession_index(["GCF_000497485_1"], "GCF_missing")
        except RuntimeError as exc:
            assert "was not found" in str(exc)
        else:
            raise AssertionError("Expected RuntimeError for unknown accession")

    def test_reconstruct_strain_model_removes_absent_reactions(self):
        module = load_module()
        model = cobra.Model("pan")
        metabolite = cobra.Metabolite("m_c", compartment="c")
        for reaction_id in ("R1", "R2", "R3"):
            reaction = cobra.Reaction(reaction_id)
            reaction.lower_bound = 0.0
            reaction.upper_bound = 1000.0
            reaction.add_metabolites({metabolite: -1.0})
            model.add_reactions([reaction])

        reconstructed = module.reconstruct_strain_model(
            model,
            reaction_presence=[True, False, True],
            model_id="strain_model",
        )

        assert reconstructed.id == "strain_model"
        assert [reaction.id for reaction in reconstructed.reactions] == ["R1", "R3"]

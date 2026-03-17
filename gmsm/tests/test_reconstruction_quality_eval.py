import importlib.util
import json
from pathlib import Path

import cobra
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqFeature import FeatureLocation, SeqFeature
from Bio.SeqRecord import SeqRecord


def load_module():
    script_path = Path(__file__).resolve().parents[2] / "scripts" / "evaluate_reconstruction_quality.py"
    spec = importlib.util.spec_from_file_location("evaluate_reconstruction_quality", script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def make_model(path, model_id, reaction_ids, gene_rule_map):
    model = cobra.Model(model_id)
    metabolite = cobra.Metabolite("m_c", compartment="c")
    for reaction_id in reaction_ids:
        reaction = cobra.Reaction(reaction_id)
        reaction.lower_bound = 0.0
        reaction.upper_bound = 1000.0
        reaction.add_metabolites({metabolite: -1.0})
        reaction.gene_reaction_rule = gene_rule_map.get(reaction_id, "")
        model.add_reactions([reaction])
    cobra.io.write_sbml_model(model, str(path))


def make_annotated_model(path, model_id, reaction_ids, gene_rule_map, gene_annotations):
    model = cobra.Model(model_id)
    metabolite = cobra.Metabolite("m_c", compartment="c")
    for reaction_id in reaction_ids:
        reaction = cobra.Reaction(reaction_id)
        reaction.lower_bound = 0.0
        reaction.upper_bound = 1000.0
        reaction.add_metabolites({metabolite: -1.0})
        reaction.gene_reaction_rule = gene_rule_map.get(reaction_id, "")
        model.add_reactions([reaction])

    for gene_id, annotation in gene_annotations.items():
        model.genes.get_by_id(gene_id).annotation = annotation

    cobra.io.write_sbml_model(model, str(path))


def make_query_genbank(path):
    record = SeqRecord(Seq("ATG" * 200), id="TEST", name="TEST", description="synthetic")
    record.annotations["molecule_type"] = "DNA"
    record.features = [
        SeqFeature(
            FeatureLocation(0, 90),
            type="CDS",
            qualifiers={
                "gene": ["geneA"],
                "protein_id": ["protA"],
                "translation": ["M" * 30],
            },
        ),
        SeqFeature(
            FeatureLocation(90, 180),
            type="CDS",
            qualifiers={
                "gene": ["thrA"],
                "protein_id": ["protThrA"],
                "note": ["ECK0002:JW0001:b0002"],
                "translation": ["M" * 30],
            },
        ),
    ]
    SeqIO.write(record, str(path), "genbank")


class TestReconstructionQualityEval:

    def test_precision_recall_f1_basic(self):
        module = load_module()

        metrics = module.precision_recall_f1({"a", "b"}, {"b", "c"})

        assert metrics["predicted_count"] == 2
        assert metrics["reference_count"] == 2
        assert metrics["overlap_count"] == 1
        assert metrics["precision"] == 0.5
        assert metrics["recall"] == 0.5
        assert metrics["f1"] == 0.5

    def test_resolve_model_xml_prefers_complete_then_primary(self, tmp_path):
        module = load_module()
        complete_dir = tmp_path / "4_complete_model"
        complete_dir.mkdir(parents=True)
        model_path = complete_dir / "model.xml"
        model_path.write_text("<sbml/>", encoding="utf-8")

        resolved = module.resolve_model_xml(tmp_path, model_kind="auto")

        assert resolved == model_path.resolve()

    def test_evaluate_single_case_writes_expected_metrics(self, tmp_path):
        module = load_module()
        predicted_path = tmp_path / "pred.xml"
        reference_path = tmp_path / "ref.xml"
        make_model(
            predicted_path,
            "pred_model",
            ["R_A", "R_B"],
            {"R_A": "g1", "R_B": "g2"},
        )
        make_model(
            reference_path,
            "ref_model",
            ["R_B", "R_C"],
            {"R_B": "g2", "R_C": "g3"},
        )

        payload = module.evaluate_single_case(predicted_path, reference_path, label="case1")

        assert payload["label"] == "case1"
        assert payload["reaction_metrics"]["precision"] == 0.5
        assert payload["reaction_metrics"]["recall"] == 0.5
        assert payload["gene_metrics"]["precision"] == 0.5
        assert payload["gene_metrics"]["recall"] == 0.5

    def test_evaluate_benchmark_batch_skips_missing_reference_models(self, tmp_path):
        module = load_module()
        run_dir = tmp_path / "benchmark-results" / "batch1"
        case_dir = run_dir / "case1" / "run-output" / "3_primary_metabolic_model"
        case_dir.mkdir(parents=True)
        make_model(case_dir / "model.xml", "pred_model", ["R_A"], {"R_A": "g1"})
        ref_path = tmp_path / "reference.xml"
        make_model(ref_path, "ref_model", ["R_A"], {"R_A": "g1"})
        manifest_path = tmp_path / "manifest.yaml"
        manifest_path.write_text(
            json.dumps(
                {
                    "cases": [
                        {"case_id": "case1", "reference_model": str(ref_path)},
                        {"case_id": "case2", "reference_model": None},
                    ]
                }
            ),
            encoding="utf-8",
        )

        payload = module.evaluate_benchmark_batch(manifest_path, run_dir, model_kind="primary")

        assert payload["evaluated_case_count"] == 1
        assert payload["skipped_case_count"] == 1
        assert payload["cases"][0]["status"] == "evaluated"
        assert payload["cases"][1]["status"] == "skipped"

    def test_evaluate_single_case_reports_gene_alias_metrics(self, tmp_path):
        module = load_module()
        run_dir = tmp_path / "run-output"
        primary_dir = run_dir / "3_primary_metabolic_model"
        bbh_dir = run_dir / "2_blastp_results"
        primary_dir.mkdir(parents=True)
        bbh_dir.mkdir(parents=True)

        predicted_path = primary_dir / "model.xml"
        reference_path = tmp_path / "reference.xml"
        query_genbank = tmp_path / "query.gbk"

        make_model(
            predicted_path,
            "pred_model",
            ["R_A", "R_B", "R_C"],
            {"R_A": "protA", "R_B": "b0002", "R_C": "unmapped"},
        )
        make_annotated_model(
            reference_path,
            "ref_model",
            ["R_A", "R_B"],
            {"R_A": "REF_A", "R_B": "REF_THRA"},
            {
                "REF_A": {"refseq_name": "geneA"},
                "REF_THRA": {"refseq_name": "thrA"},
            },
        )
        make_query_genbank(query_genbank)
        (bbh_dir / "temp_target_BBH_dict.txt").write_text("b0002\t['protThrA']\n", encoding="utf-8")

        payload = module.evaluate_single_case(
            run_dir,
            reference_path,
            label="case_alias",
            model_kind="primary",
            query_genbank=query_genbank,
        )

        assert payload["gene_metrics"]["overlap_count"] == 0
        assert payload["gene_alias_metrics"]["status"] == "evaluated"
        assert payload["gene_alias_metrics"]["overlap_count"] == 2
        assert payload["gene_alias_metrics"]["precision"] == 0.666667
        assert payload["gene_alias_metrics"]["recall"] == 1.0
        assert payload["gene_alias_metrics"]["f1"] == 0.8

    def test_evaluate_benchmark_batch_uses_query_input_for_gene_alias_metrics(self, tmp_path):
        module = load_module()
        run_dir = tmp_path / "benchmark-results" / "batch2"
        case_dir = run_dir / "case1" / "run-output" / "3_primary_metabolic_model"
        bbh_dir = run_dir / "case1" / "run-output" / "2_blastp_results"
        case_dir.mkdir(parents=True)
        bbh_dir.mkdir(parents=True)

        predicted_path = case_dir / "model.xml"
        reference_path = tmp_path / "reference.xml"
        query_genbank = tmp_path / "query.gbk"
        manifest_path = tmp_path / "manifest.yaml"

        make_model(
            predicted_path,
            "pred_model",
            ["R_A", "R_B"],
            {"R_A": "protA", "R_B": "b0002"},
        )
        make_annotated_model(
            reference_path,
            "ref_model",
            ["R_A", "R_B"],
            {"R_A": "REF_A", "R_B": "REF_THRA"},
            {
                "REF_A": {"refseq_name": "geneA"},
                "REF_THRA": {"refseq_name": "thrA"},
            },
        )
        make_query_genbank(query_genbank)
        (bbh_dir / "temp_target_BBH_dict.txt").write_text("b0002\t['protThrA']\n", encoding="utf-8")
        manifest_path.write_text(
            json.dumps(
                {
                    "cases": [
                        {
                            "case_id": "case1",
                            "query_input": str(query_genbank),
                            "reference_model": str(reference_path),
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )

        payload = module.evaluate_benchmark_batch(manifest_path, run_dir, model_kind="primary")

        assert payload["evaluated_case_count"] == 1
        assert payload["cases"][0]["evaluation"]["gene_alias_metrics"]["status"] == "evaluated"
        assert payload["cases"][0]["evaluation"]["gene_alias_metrics"]["overlap_count"] == 2

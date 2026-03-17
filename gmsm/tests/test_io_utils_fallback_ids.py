from types import SimpleNamespace

from Bio.Seq import Seq
from Bio.SeqFeature import FeatureLocation, SeqFeature
from Bio.SeqRecord import SeqRecord

from gmsm.io import io_utils


def make_options():
    return SimpleNamespace(
        eficaz=False,
        ec_file=False,
        eficaz_file=False,
        targetGenome_locusTag_aaSeq_dict={},
        targetGenome_locusTag_ec_dict={},
        targetGenome_locusTag_prod_dict={},
        seq_record_BGC_num_lists=[],
        total_region=0,
        total_cluster=0,
    )


class TestIoUtilsFallbackIds:

    def test_get_features_from_gbk_falls_back_to_protein_id(self):
        seq_record = SeqRecord(Seq("ATGGCCATTGTAATGGGCCGCTGAAAGGGTGCCCGATAG"))
        seq_record.features = [
            SeqFeature(
                FeatureLocation(0, 39),
                type="CDS",
                qualifiers={
                    "protein_id": ["ABC123.1"],
                    "product": ["test enzyme"],
                    "translation": ["MAIVMGR"],
                    "EC_number": ["1.2.3.4"],
                },
            )
        ]
        options = make_options()

        io_utils.get_features_from_gbk(seq_record, options, options)

        assert "ABC123.1" in options.targetGenome_locusTag_aaSeq_dict
        assert options.targetGenome_locusTag_prod_dict["ABC123.1"] == "test enzyme"
        assert options.targetGenome_locusTag_ec_dict["ABC123.1"] == ["1.2.3.4"]

    def test_get_features_from_gbk_falls_back_to_gene_when_needed(self):
        seq_record = SeqRecord(Seq("ATGGCCATTGTAATGGGCCGCTGAAAGGGTGCCCGATAG"))
        seq_record.features = [
            SeqFeature(
                FeatureLocation(0, 39),
                type="CDS",
                qualifiers={
                    "gene": ["thrA"],
                    "product": ["test enzyme"],
                    "translation": ["MAIVMGR"],
                },
            )
        ]
        options = make_options()

        io_utils.get_features_from_gbk(seq_record, options, options)

        assert "thrA" in options.targetGenome_locusTag_aaSeq_dict

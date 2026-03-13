import csv
import json
import logging
import os
import shutil
from statistics import mean

from Bio import SeqIO

from gmsm import utils


_TEMPLATE_METADATA = {
    'bsu': {'organism': 'Bacillus subtilis subsp. subtilis str. 168', 'model': 'iYO844'},
    'clj': {'organism': 'Clostridium ljungdahlii DSM 13528', 'model': 'iHN637'},
    'cre': {'organism': 'Chlamydomonas reinhardtii', 'model': 'iCre1355'},
    'eco': {'organism': 'Escherichia coli str. K-12 substr. MG1655', 'model': 'iML1515'},
    'hpy': {'organism': 'Helicobacter pylori 26695', 'model': 'iIT341'},
    'mtu': {'organism': 'Mycobacterium tuberculosis H37Rv', 'model': 'iNJ661'},
    'nsal': {'organism': 'Nannochloropsis salina', 'model': 'iNS934'},
    'ppu': {'organism': 'Pseudomonas putida KT2440', 'model': 'iJN746'},
    'sce': {'organism': 'Saccharomyces cerevisiae S288C', 'model': 'iMM904'},
    'sco': {'organism': 'Streptomyces coelicolor A3(2)', 'model': 'iKS1317'},
}

_NUCLEOTIDE_CHARS = set("ACGTUNWSMKRYBDHV-")


def recommend_template(filetype, run_ns, io_ns):
    catalog = discover_template_catalog()
    if not catalog:
        raise RuntimeError("No template catalog entries were discovered under gmsm/io/data/input1")

    backend = resolve_template_backend(filetype, run_ns, catalog)
    logging.info("Running automatic template recommendation via '%s'", backend)

    if backend == 'skani':
        candidates = score_templates_with_skani(filetype, run_ns, io_ns, catalog)
    elif backend == 'diamond':
        candidates = score_templates_with_diamond(run_ns, io_ns, catalog)
    else:
        raise RuntimeError("Unsupported template recommendation backend: %s" % backend)

    if not candidates:
        raise RuntimeError("Automatic template recommendation did not produce any candidates")

    sorted_candidates = sorted(
        candidates,
        key=lambda item: (
            -float(item.get('score', 0.0)),
            -float(item.get('primary_metric', 0.0)),
            -float(item.get('secondary_metric', 0.0)),
            item['template_id'],
        ),
    )

    topk = max(1, int(getattr(run_ns, 'template_topk', 3)))
    selected_candidates = sorted_candidates[:topk]
    selected_template = selected_candidates[0]['template_id']
    confidence = classify_recommendation_confidence(selected_candidates)

    result = {
        'selection_mode': 'auto',
        'backend': backend,
        'recommended_template': selected_template,
        'previous_template': getattr(run_ns, 'orgName', None),
        'confidence': confidence,
        'candidates': selected_candidates,
    }

    run_ns.orgName = selected_template
    run_ns.template_selection_mode = 'auto'
    run_ns.template_selection_backend = backend
    run_ns.template_selection_confidence = confidence
    run_ns.template_selection_topk = topk
    run_ns.template_selection_result = result

    write_template_recommendation_outputs(io_ns.outputfolder0, result)
    logging.info(
        "Selected template '%s' via '%s' backend (confidence: %s)",
        selected_template,
        backend,
        confidence,
    )
    return result


def discover_template_catalog(input1_root=None):
    if input1_root is None:
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
        input1_root = os.path.join(repo_root, 'gmsm', 'io', 'data', 'input1')

    catalog = []
    if not os.path.isdir(input1_root):
        return catalog

    for template_id in sorted(os.listdir(input1_root)):
        template_dir = os.path.join(input1_root, template_id)
        if not os.path.isdir(template_dir):
            continue

        proteome_fasta = os.path.join(template_dir, 'tempModel_locusTag_aaSeq.fa')
        if not os.path.isfile(proteome_fasta):
            continue

        genome_fasta = None
        for candidate_name in (
            'template_genome.fna',
            'template_genome.fa',
            'template_genome.fasta',
            'genome.fna',
            'genome.fa',
            'genome.fasta',
        ):
            candidate_path = os.path.join(template_dir, candidate_name)
            if os.path.isfile(candidate_path):
                genome_fasta = candidate_path
                break

        metadata = _TEMPLATE_METADATA.get(template_id, {})
        catalog.append(
            {
                'template_id': template_id,
                'template_dir': template_dir,
                'proteome_fasta': proteome_fasta,
                'genome_fasta': genome_fasta,
                'organism': metadata.get('organism', template_id),
                'model': metadata.get('model', template_id),
            }
        )

    return catalog


def resolve_template_backend(filetype, run_ns, catalog):
    backend = getattr(run_ns, 'template_backend', 'auto')
    if backend == 'diamond':
        return backend

    if backend == 'skani':
        if not skani_backend_ready(filetype, run_ns, catalog):
            raise RuntimeError(
                "Template backend 'skani' requires a skani executable and template genome FASTA files"
            )
        return backend

    if skani_backend_ready(filetype, run_ns, catalog):
        return 'skani'

    return 'diamond'


def skani_backend_ready(filetype, run_ns, catalog):
    if utils.locate_executable('skani') is None:
        return False

    if not any(entry.get('genome_fasta') for entry in catalog):
        return False

    return target_input_supports_skani(filetype, run_ns)


def target_input_supports_skani(filetype, run_ns):
    if filetype == 'genbank':
        return True
    if filetype != 'fasta':
        return False
    return is_probably_nucleotide_fasta(run_ns.input)


def is_probably_nucleotide_fasta(path, max_records=20):
    examined = 0
    for record in SeqIO.parse(path, 'fasta'):
        seq = str(record.seq).upper()
        if not seq:
            continue
        examined += 1
        residue_set = {char for char in seq if char.isalpha() or char == '-'}
        if residue_set and not residue_set.issubset(_NUCLEOTIDE_CHARS):
            return False
        if examined >= max_records:
            break
    return examined > 0


def prepare_target_proteome_fasta(io_ns, output_dir):
    target_fasta = os.path.join(output_dir, 'target_proteome_for_template_recommendation.faa')
    with open(target_fasta, 'w') as handle:
        for locus_tag, aa_seq in sorted(io_ns.targetGenome_locusTag_aaSeq_dict.items()):
            handle.write('>%s\n%s\n' % (locus_tag, aa_seq))
    return target_fasta


def prepare_target_genome_fasta(filetype, run_ns, output_dir):
    target_fasta = os.path.join(output_dir, 'target_genome_for_template_recommendation.fna')

    if filetype == 'genbank':
        records = list(SeqIO.parse(run_ns.input, 'genbank'))
        with open(target_fasta, 'w') as handle:
            SeqIO.write(records, handle, 'fasta')
        return target_fasta

    if filetype == 'fasta' and is_probably_nucleotide_fasta(run_ns.input):
        shutil.copyfile(run_ns.input, target_fasta)
        return target_fasta

    raise RuntimeError(
        "skani-based template recommendation requires GenBank input or a nucleotide FASTA input"
    )


def score_templates_with_skani(filetype, run_ns, io_ns, catalog):
    skani = utils.locate_executable('skani')
    if skani is None:
        raise RuntimeError("skani executable not found")

    tmp_dir = ensure_tmp_template_dir(io_ns)
    query_fasta = prepare_target_genome_fasta(filetype, run_ns, tmp_dir)

    references = [entry for entry in catalog if entry.get('genome_fasta')]
    output_path = os.path.join(tmp_dir, 'skani_template_candidates.tsv')
    command = [skani, 'dist', '-q', query_fasta, '-o', output_path]
    for entry in references:
        command.extend(['-r', entry['genome_fasta']])

    run_command(command, "skani template recommendation failed")

    parsed_rows = parse_skani_output(output_path)
    rows_by_template = {}
    for row in parsed_rows:
        template_id = infer_template_id_from_path(row.get('Ref_file'), catalog)
        if template_id is None:
            continue
        ani = safe_float(row.get('ANI'))
        af_ref = safe_float(row.get('Align_fraction_ref'))
        af_query = safe_float(row.get('Align_fraction_query'))
        af_mean = mean([value for value in (af_ref, af_query) if value is not None]) if any(
            value is not None for value in (af_ref, af_query)
        ) else 0.0
        score = round((0.7 * normalize_ani(ani)) + (0.3 * af_mean), 6)
        rows_by_template[template_id] = {
            'template_id': template_id,
            'organism': get_template_metadata(template_id, catalog).get('organism', template_id),
            'model': get_template_metadata(template_id, catalog).get('model', template_id),
            'backend': 'skani',
            'score': score,
            'primary_metric': ani or 0.0,
            'secondary_metric': af_mean or 0.0,
            'ani': ani,
            'aligned_fraction': af_mean,
            'aligned_fraction_ref': af_ref,
            'aligned_fraction_query': af_query,
            'matched_queries': None,
            'total_queries': None,
            'hit_coverage': None,
            'mean_identity': None,
            'mean_bitscore': None,
        }

    candidates = []
    for entry in catalog:
        candidate = rows_by_template.get(
            entry['template_id'],
            {
                'template_id': entry['template_id'],
                'organism': entry['organism'],
                'model': entry['model'],
                'backend': 'skani',
                'score': 0.0,
                'primary_metric': 0.0,
                'secondary_metric': 0.0,
                'ani': None,
                'aligned_fraction': 0.0,
                'aligned_fraction_ref': None,
                'aligned_fraction_query': None,
                'matched_queries': None,
                'total_queries': None,
                'hit_coverage': None,
                'mean_identity': None,
                'mean_bitscore': None,
            },
        )
        candidates.append(candidate)
    return candidates


def score_templates_with_diamond(run_ns, io_ns, catalog):
    diamond = utils.locate_executable('diamond')
    if diamond is None:
        raise RuntimeError("diamond executable not found")

    tmp_dir = ensure_tmp_template_dir(io_ns)
    target_fasta = prepare_target_proteome_fasta(io_ns, tmp_dir)
    total_queries = max(1, len(io_ns.targetGenome_locusTag_aaSeq_dict))
    candidates = []

    for entry in catalog:
        db_prefix = os.path.join(tmp_dir, '%s_db' % entry['template_id'])
        blast_output = os.path.join(tmp_dir, '%s_hits.tsv' % entry['template_id'])

        run_command(
            [diamond, 'makedb', '--in', entry['proteome_fasta'], '-d', db_prefix],
            "DIAMOND database creation failed for template '%s'" % entry['template_id'],
        )
        run_command(
            [
                diamond,
                'blastp',
                '-d',
                db_prefix,
                '-q',
                target_fasta,
                '-o',
                blast_output,
                '--evalue',
                '1e-20',
                '--id',
                '30',
                '--max-target-seqs',
                '1',
                '--outfmt',
                '6',
                'qseqid',
                'bitscore',
                'pident',
            ],
            "DIAMOND template scoring failed for template '%s'" % entry['template_id'],
        )

        matched_queries, mean_bitscore, mean_identity = parse_diamond_template_hits(blast_output)
        hit_coverage = matched_queries / float(total_queries)
        score = round((0.85 * hit_coverage) + (0.15 * ((mean_identity or 0.0) / 100.0)), 6)
        candidates.append(
            {
                'template_id': entry['template_id'],
                'organism': entry['organism'],
                'model': entry['model'],
                'backend': 'diamond',
                'score': score,
                'primary_metric': hit_coverage,
                'secondary_metric': mean_identity or 0.0,
                'ani': None,
                'aligned_fraction': None,
                'aligned_fraction_ref': None,
                'aligned_fraction_query': None,
                'matched_queries': matched_queries,
                'total_queries': total_queries,
                'hit_coverage': round(hit_coverage, 6),
                'mean_identity': round(mean_identity, 6) if mean_identity is not None else None,
                'mean_bitscore': round(mean_bitscore, 6) if mean_bitscore is not None else None,
            }
        )

    return candidates


def parse_diamond_template_hits(path):
    best_hits = {}
    with open(path, 'r') as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            query_id, bitscore, identity = line.split('\t')
            bitscore = float(bitscore)
            identity = float(identity)
            previous = best_hits.get(query_id)
            if previous is None or bitscore > previous[0]:
                best_hits[query_id] = (bitscore, identity)

    if not best_hits:
        return 0, None, None

    bit_scores = [values[0] for values in best_hits.values()]
    identities = [values[1] for values in best_hits.values()]
    return len(best_hits), mean(bit_scores), mean(identities)


def parse_skani_output(path):
    with open(path, 'r', newline='') as handle:
        reader = csv.DictReader(handle, delimiter='\t')
        return list(reader)


def infer_template_id_from_path(path, catalog):
    if not path:
        return None
    normalized = os.path.normcase(os.path.abspath(path))
    for entry in catalog:
        genome_fasta = entry.get('genome_fasta')
        if genome_fasta and normalized == os.path.normcase(os.path.abspath(genome_fasta)):
            return entry['template_id']
    return None


def get_template_metadata(template_id, catalog):
    for entry in catalog:
        if entry['template_id'] == template_id:
            return entry
    return {}


def normalize_ani(value):
    if value is None:
        return 0.0
    return max(0.0, min(1.0, (value - 80.0) / 15.0))


def safe_float(value):
    if value in (None, ''):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def classify_recommendation_confidence(candidates):
    if not candidates:
        return 'low'
    if len(candidates) == 1:
        return 'high'

    score_gap = float(candidates[0].get('score', 0.0)) - float(candidates[1].get('score', 0.0))
    top_score = float(candidates[0].get('score', 0.0))

    if top_score >= 0.85 and score_gap >= 0.10:
        return 'high'
    if top_score >= 0.60 and score_gap >= 0.03:
        return 'medium'
    return 'low'


def write_template_recommendation_outputs(folder, result):
    os.makedirs(folder, exist_ok=True)
    write_template_candidates_tsv(folder, result)
    with open(os.path.join(folder, 'template_recommendation.json'), 'w') as handle:
        json.dump(result, handle, indent=2, sort_keys=True)


def write_template_candidates_tsv(folder, result):
    fields = [
        'rank',
        'template_id',
        'organism',
        'model',
        'backend',
        'score',
        'primary_metric',
        'secondary_metric',
        'ani',
        'aligned_fraction',
        'aligned_fraction_ref',
        'aligned_fraction_query',
        'matched_queries',
        'total_queries',
        'hit_coverage',
        'mean_identity',
        'mean_bitscore',
    ]
    with open(os.path.join(folder, 'template_candidates.tsv'), 'w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter='\t')
        writer.writeheader()
        for rank, candidate in enumerate(result['candidates'], start=1):
            row = dict(candidate)
            row['rank'] = rank
            writer.writerow(row)


def ensure_tmp_template_dir(io_ns):
    tmp_dir = os.path.join(io_ns.outputfolder6, 'auto_template')
    os.makedirs(tmp_dir, exist_ok=True)
    return tmp_dir


def run_command(command, failure_message):
    out, err, retcode = utils.execute(command)
    if retcode != 0:
        stdout = out.decode('utf-8', errors='replace') if isinstance(out, bytes) else str(out)
        stderr = err.decode('utf-8', errors='replace') if isinstance(err, bytes) else str(err)
        raise RuntimeError("%s\nSTDOUT:\n%s\nSTDERR:\n%s" % (failure_message, stdout, stderr))

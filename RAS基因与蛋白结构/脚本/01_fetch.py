#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""最小权威组合数据抓取：NCBI Gene / Ensembl / UniProt / RCSB PDB / AlphaFold DB / cBioPortal
用法: python3 -I 01_fetch.py <输出根目录>
所有原始返回按库落盘到 <根>/数据/raw/，解析后的结构化表落盘到 <根>/数据/。
"""
import json, os, sys, time, urllib.request, urllib.parse, urllib.error

ROOT = sys.argv[1]
DATA = os.path.join(ROOT, '数据')
RAW = os.path.join(DATA, 'raw')
STRU = os.path.join(ROOT, '结构文件')
for d in (DATA, RAW, STRU):
    os.makedirs(d, exist_ok=True)

UA = {'User-Agent': 'RAS-review-structure-collection/1.0 (academic use)'}
LOG = []


def get(url, tries=4, binary=False, data=None, ctype=None):
    hdr = dict(UA)
    if ctype:
        hdr['Content-Type'] = ctype
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=hdr, data=data)
            with urllib.request.urlopen(req, timeout=90) as r:
                b = r.read()
            return b if binary else b.decode('utf-8', 'replace')
        except Exception as e:
            if i == tries - 1:
                LOG.append('FAIL %s %s' % (url, e))
                return None
            time.sleep(1.5 * (i + 1))


def save(name, text, sub=RAW):
    p = os.path.join(sub, name)
    mode = 'wb' if isinstance(text, bytes) else 'w'
    with open(p, mode) as f:
        f.write(text)
    return p


def jdump(name, obj, sub=DATA):
    with open(os.path.join(sub, name), 'w') as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)


GENES = {
    'KRAS': {'entrez': '3845', 'ensg': 'ENSG00000133703', 'uniprot': 'P01116'},
    'HRAS': {'entrez': '3265', 'ensg': 'ENSG00000174775', 'uniprot': 'P01112'},
    'NRAS': {'entrez': '4893', 'ensg': 'ENSG00000213281', 'uniprot': 'P01111'},
}

# ---------- 1. NCBI Gene ----------
ids = ','.join(v['entrez'] for v in GENES.values())
u = ('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi'
     '?db=gene&id=%s&retmode=json' % ids)
t = get(u)
if t:
    save('ncbi_gene_esummary.json', t)
    js = json.loads(t)
    for g, v in GENES.items():
        r = js['result'][v['entrez']]
        loc = (r.get('genomicinfo') or [{}])[0]
        v['ncbi'] = {
            'symbol': r.get('name'), 'desc': r.get('description'),
            'map_location': r.get('maplocation'),
            'chr': loc.get('chrloc'), 'start': loc.get('chrstart'),
            'stop': loc.get('chrstop'), 'summary': (r.get('summary') or '')[:1500],
            'otherdesignations': r.get('otheraliases'),
        }
    time.sleep(0.4)

# ---------- 2. Ensembl: 转录本 + 外显子 + MANE ----------
E = 'https://rest.ensembl.org'
for g, v in GENES.items():
    t = get(E + '/lookup/id/%s?expand=1;content-type=application/json' % v['ensg'])
    if not t:
        continue
    save('ensembl_%s_gene.json' % g, t)
    js = json.loads(t)
    v['ensembl'] = {'strand': js['strand'], 'chr': js['seq_region_name'],
                    'start': js['start'], 'end': js['end'],
                    'assembly': js.get('assembly_name'),
                    'n_transcripts': len(js.get('Transcript', []))}
    tx = []
    for x in js.get('Transcript', []):
        tx.append({'id': x['id'], 'biotype': x['biotype'],
                   'canonical': x.get('is_canonical', 0),
                   'display': x.get('display_name'),
                   'length': x.get('length'),
                   'start': x['start'], 'end': x['end']})
    v['transcripts'] = tx
    time.sleep(0.25)

# MANE Select（Ensembl 专用端点，拿 RefSeq 对应关系）
for g, v in GENES.items():
    t = get(E + '/lookup/symbol/homo_sapiens/%s?expand=0;mane=1;content-type=application/json' % g)
    if t:
        save('ensembl_%s_mane.json' % g, t)
        try:
            v['mane_raw'] = json.loads(t).get('MANE')
        except Exception:
            pass
    time.sleep(0.25)

# 候选 MANE / canonical 转录本的外显子与 CDS
PREF = {'KRAS': ['ENST00000311936', 'ENST00000256078'],  # 4B / 4A
        'HRAS': ['ENST00000311189'], 'NRAS': ['ENST00000369535']}
for g, v in GENES.items():
    cans = [x['id'] for x in v.get('transcripts', []) if x['canonical']]
    want = []
    for p in PREF.get(g, []):
        for x in v.get('transcripts', []):
            if x['id'].startswith(p):
                want.append(x['id'])
    for c in cans:
        if c not in want:
            want.append(c)
    v['exon_models'] = {}
    for tid in want:
        t = get(E + '/lookup/id/%s?expand=1;utr=1;content-type=application/json' % tid)
        if not t:
            continue
        save('ensembl_tx_%s_%s.json' % (g, tid), t)
        js = json.loads(t)
        ex = [{'id': e['id'], 'start': e['start'], 'end': e['end'],
               'rank': i + 1} for i, e in enumerate(js.get('Exon', []))]
        cds = [{'start': c['start'], 'end': c['end']} for c in js.get('Translation', {}) and [] or []]
        tr = js.get('Translation') or {}
        v['exon_models'][tid] = {
            'biotype': js['biotype'], 'canonical': js.get('is_canonical', 0),
            'strand': js['strand'], 'start': js['start'], 'end': js['end'],
            'protein_id': tr.get('id'), 'protein_length': tr.get('length'),
            'cds_genomic_start': tr.get('start'), 'cds_genomic_end': tr.get('end'),
            'exons': ex, 'display': js.get('display_name'),
        }
        time.sleep(0.25)

# 热点密码子 → 基因组坐标（Ensembl map/cds）
HOT = {'KRAS': [12, 13, 61, 117, 146], 'HRAS': [12, 13, 61], 'NRAS': [12, 13, 61]}
for g, v in GENES.items():
    tid = (PREF.get(g) or [None])[0]
    real = None
    for k in v.get('exon_models', {}):
        if tid and k.startswith(tid):
            real = k
    if real is None and v.get('exon_models'):
        real = sorted(v['exon_models'])[0]
    v['hotspot_map'] = {}
    if not real:
        continue
    for codon in HOT[g]:
        a, b = (codon - 1) * 3 + 1, codon * 3
        t = get(E + '/map/cds/%s/%d..%d?content-type=application/json' % (real, a, b))
        if t:
            try:
                m = json.loads(t)['mappings']
                v['hotspot_map'][str(codon)] = {'cds': [a, b], 'genomic': m}
            except Exception:
                pass
        time.sleep(0.25)
    v['hotspot_tx'] = real

# ---------- 3. UniProt ----------
for g, v in GENES.items():
    acc = v['uniprot']
    t = get('https://rest.uniprot.org/uniprotkb/%s.json' % acc)
    if t:
        save('uniprot_%s.json' % acc, t)
        js = json.loads(t)
        seq = js['sequence']['value']
        feats = []
        for f in js.get('features', []):
            loc = f.get('location', {})
            feats.append({'type': f['type'],
                          'start': (loc.get('start') or {}).get('value'),
                          'end': (loc.get('end') or {}).get('value'),
                          'desc': f.get('description', '')})
        iso = []
        for c in js.get('comments', []):
            if c.get('commentType') == 'ALTERNATIVE PRODUCTS':
                for s in c.get('isoforms', []):
                    iso.append({'name': (s.get('name') or {}).get('value'),
                                'ids': s.get('isoformIds'),
                                'type': s.get('isoformSequenceStatus')})
        v['uniprot_data'] = {
            'accession': acc, 'length': js['sequence']['length'],
            'sequence': seq, 'protein_name':
                js['proteinDescription']['recommendedName']['fullName']['value'],
            'features': feats, 'isoforms': iso,
            'pdb_xrefs': [x['id'] for x in js.get('uniProtKBCrossReferences', [])
                          if x['database'] == 'PDB'],
        }
        save('uniprot_%s.fasta' % acc, '>%s|%s\n%s\n' % (acc, g, seq))
    time.sleep(0.3)

# ---------- 4. RCSB PDB ----------
PDBS = {
    '5P21': 'HRAS G域-GppNHp 1.35Å 活性态标准结构',
    '4Q21': 'HRAS p21-GDP 非活性态',
    '1WQ1': 'HRAS–p120RasGAP 过渡态(Scheffzek 1997)',
    '1NVV': 'HRAS–SOS1 核苷酸交换复合物',
    '4G0N': 'HRAS–RAF1 RBD 效应器复合物',
    '4OBE': 'KRAS-GDP 高分辨',
    '6OIM': 'KRAS G12C + 索托拉西布(AMG 510) 共价加合',
    '5VQ2': 'KRAS WT-GTP 类似物',
    '4LDJ': 'KRAS G12C-GDP',
    '6GJ8': 'KRAS G12D',
    '7RPZ': 'KRAS G12D + MRTX1133',
    '3CON': 'NRAS 结构',
}
pdbmeta = {}
for pid, note in PDBS.items():
    t = get('https://data.rcsb.org/rest/v1/core/entry/%s' % pid)
    if t:
        js = json.loads(t)
        ent = js.get('rcsb_entry_info', {})
        pdbmeta[pid] = {
            'note': note,
            'title': js.get('struct', {}).get('title'),
            'method': ent.get('experimental_method'),
            'resolution': (ent.get('resolution_combined') or [None])[0],
            'released': (js.get('rcsb_accession_info') or {}).get('initial_release_date', '')[:10],
            'ligands': ent.get('nonpolymer_bound_components'),
            'polymer_entities': ent.get('polymer_entity_count'),
            'doi': (js.get('rcsb_primary_citation') or {}).get('pdbx_database_id_DOI'),
            'pubmed': (js.get('rcsb_primary_citation') or {}).get('pdbx_database_id_PubMed'),
            'journal': (js.get('rcsb_primary_citation') or {}).get('journal_abbrev'),
            'year': (js.get('rcsb_primary_citation') or {}).get('year'),
        }
    b = get('https://files.rcsb.org/download/%s.pdb' % pid, binary=True)
    if b and b[:4] in (b'HEAD', b'ATOM', b'REMA', b'CRYS', b'TITL', b'DATA', b'EXPD', b'OBSL'):
        save('%s.pdb' % pid, b, STRU)
    time.sleep(0.3)
jdump('pdb_entries.json', pdbmeta)

# 每个 UniProt 的结构计数（RCSB search API）
for g, v in GENES.items():
    q = {"query": {"type": "terminal", "service": "text", "parameters": {
        "attribute": "rcsb_polymer_entity_container_identifiers.reference_sequence_identifiers.database_accession",
        "operator": "exact_match", "value": v['uniprot']}},
        "return_type": "entry", "request_options": {"return_counts": True}}
    u = 'https://search.rcsb.org/rcsbsearch/v2/query?json=' + urllib.parse.quote(json.dumps(q))
    t = get(u)
    if t:
        try:
            v['pdb_entry_count'] = json.loads(t).get('total_count')
        except Exception:
            pass
    time.sleep(0.4)

# ---------- 5. AlphaFold DB ----------
for g, v in GENES.items():
    acc = v['uniprot']
    t = get('https://alphafold.ebi.ac.uk/api/prediction/%s' % acc)
    if not t:
        continue
    save('alphafold_%s.json' % acc, t)
    js = json.loads(t)
    if not js:
        continue
    e = js[0]
    v['alphafold'] = {k: e.get(k) for k in
                      ('entryId', 'modelCreatedDate', 'latestVersion',
                       'uniprotStart', 'uniprotEnd', 'modelUrl', 'pdbUrl')}
    pu = e.get('pdbUrl')
    if pu:
        b = get(pu, binary=True)
        if b:
            save('AF-%s-F1-model.pdb' % acc, b, STRU)
    time.sleep(0.3)

# ---------- 6. cBioPortal ----------
CB = 'https://www.cbioportal.org/api'
STUDY = 'msk_impact_2017'
prof = STUDY + '_mutations'
slist = STUDY + '_all'
ent = {v['entrez']: g for g, v in GENES.items()}
muts = {}
for g, v in GENES.items():
    u = ('%s/molecular-profiles/%s/mutations?sampleListId=%s&entrezGeneId=%s'
         '&projection=DETAILED&direction=ASC' % (CB, prof, slist, v['entrez']))
    t = get(u)
    if not t:
        continue
    save('cbioportal_%s_%s.json' % (STUDY, g), t)
    js = json.loads(t)
    rows = []
    for m in js:
        rows.append({'sample': m.get('sampleId'), 'patient': m.get('patientId'),
                     'protein': m.get('proteinChange'),
                     'type': m.get('mutationType'),
                     'start': m.get('proteinPosStart'),
                     'ref': m.get('referenceAllele'), 'var': m.get('variantAllele'),
                     'vtype': m.get('variantType')})
    muts[g] = rows
jdump('cbioportal_mutations.json', muts)

# 样本的癌种标签 + 该研究样本总数
t = get('%s/studies/%s/clinical-data?clinicalDataType=SAMPLE&attributeId=CANCER_TYPE'
        '&projection=SUMMARY' % (CB, STUDY))
ct = {}
if t:
    save('cbioportal_cancertype.json', t)
    for r in json.loads(t):
        ct[r['sampleId']] = r['value']
jdump('cbioportal_sample_cancertype.json', ct)
t = get('%s/studies/%s' % (CB, STUDY))
if t:
    save('cbioportal_study.json', t)
    GENES['_study'] = json.loads(t)

jdump('genes_core.json', GENES)
with open(os.path.join(DATA, 'fetch_log.txt'), 'w') as f:
    f.write('\n'.join(LOG) or 'all ok')
print('fetch done; failures=%d' % len(LOG))
for l in LOG:
    print(l)

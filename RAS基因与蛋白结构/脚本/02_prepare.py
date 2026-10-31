#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 raw 返回整形成作图/写作可直接用的表。用法: python3 -I 02_prepare.py <根目录> [--offline]

两处线上查询（Ensembl MANE、UniProt P01116-2）的原始返回落在 数据/raw/；
--offline 只读这些缓存、不联网也不改写 raw（复现包 reproduce.sh 默认如此）。
"""
import collections, csv, json, os, sys, time, urllib.request

ROOT = sys.argv[1]
DATA = os.path.join(ROOT, '数据')
RAW = os.path.join(DATA, 'raw')
STRU = os.path.join(ROOT, '结构文件')
UA = {'User-Agent': 'RAS-review-structure-collection/1.0 (academic use)'}
OFFLINE = '--offline' in sys.argv[2:]
G = json.load(open(os.path.join(DATA, 'genes_core.json')))
OUT = {}


def get(u):
    if OFFLINE:
        return None
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60) as r:
            return r.read().decode('utf-8', 'replace')
    except Exception as e:
        print('WARN', u, e)
        return None


def wcsv(name, rows, cols):
    with open(os.path.join(DATA, name), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, '') for c in cols})


# ---------- MANE Select（Ensembl overlap feature=mane） ----------
mane = {}
for g in ('KRAS', 'HRAS', 'NRAS'):
    e = G[g]['ensembl']
    u = ('https://rest.ensembl.org/overlap/region/human/%s:%d-%d?feature=mane;'
         'content-type=application/json' % (e['chr'], e['start'], e['end']))
    t = get(u)
    cache = os.path.join(RAW, 'ensembl_%s_mane_overlap.json' % g)
    if t:
        open(cache, 'w').write(t)
    elif os.path.exists(cache):                     # 线上失败时用上次落盘的原始返回
        print('  用缓存', cache)
        t = open(cache).read()
    if t:
        for r in json.loads(t):
            if r.get('Parent') == G[g]['ensg']:
                mane.setdefault(g, []).append(
                    {'ensembl_tx': '%s.%s' % (r['id'], r.get('version')),
                     'refseq': r.get('refseq_match'), 'type': r.get('type')})
    time.sleep(0.25)
OUT['mane'] = mane

# ---------- KRAS 4B(P01116-2) 序列，建立 188aa 坐标系 ----------
t = get('https://rest.uniprot.org/uniprotkb/P01116-2.fasta')
cache = os.path.join(RAW, 'uniprot_P01116-2.fasta')
if t:
    open(cache, 'w').write(t)
elif os.path.exists(cache):
    print('  用缓存', cache)
    t = open(cache).read()
if t:
    OUT['kras4b_seq'] = ''.join(t.split('\n')[1:]).strip()

# ---------- 外显子表 + 外显子↔密码子映射 ----------
exon_rows, map_rows = [], []
for g in ('KRAS', 'HRAS', 'NRAS'):
    v = G[g]
    for tid, m in v['exon_models'].items():
        strand, cs, ce = m['strand'], m['cds_genomic_start'], m['cds_genomic_end']
        ex = sorted(m['exons'], key=lambda e: e['start'], reverse=(strand < 0))
        cum = 0
        for i, e in enumerate(ex, 1):
            L = e['end'] - e['start'] + 1
            # 编码区交集
            a, b = max(e['start'], cs or 0), min(e['end'], ce or 0)
            cl = max(0, b - a + 1) if cs else 0
            row = {'gene': g, 'transcript': tid, 'exon_rank': i, 'exon_id': e['id'],
                   'chr': v['ensembl']['chr'], 'strand': strand,
                   'exon_start': e['start'], 'exon_end': e['end'], 'exon_len': L,
                   'coding_len': cl, 'utr_len': L - cl,
                   'coding_start': a if cl else '', 'coding_end': b if cl else '',
                   'cds_offset_start': cum + 1 if cl else '',
                   'cds_offset_end': cum + cl if cl else '',
                   'codon_first': (cum // 3) + 1 if cl else '',
                   'codon_last': (cum + cl + 2) // 3 if cl else ''}
            if i < len(ex):
                nx = ex[i]
                row['intron_len'] = (nx['start'] - e['end'] - 1) if strand > 0 \
                    else (e['start'] - nx['end'] - 1)
            cum += cl
            exon_rows.append(row)
        if cum:
            map_rows.append({'gene': g, 'transcript': tid, 'cds_len': cum,
                             'aa_len': cum // 3 - 1, 'protein': m['protein_id'],
                             'n_exons': len(ex),
                             'n_coding_exons': sum(1 for r in exon_rows
                                                   if r['transcript'] == tid and r['coding_len'])})
wcsv('表1_外显子结构.csv', exon_rows,
     ['gene', 'transcript', 'exon_rank', 'exon_id', 'chr', 'strand', 'exon_start',
      'exon_end', 'exon_len', 'coding_len', 'utr_len', 'coding_start', 'coding_end',
      'cds_offset_start', 'cds_offset_end', 'codon_first', 'codon_last', 'intron_len'])
OUT['transcript_summary'] = map_rows

# ---------- 热点密码子所在外显子 ----------
hot_rows = []
for g in ('KRAS', 'HRAS', 'NRAS'):
    v = G[g]
    tid = v['hotspot_tx']
    for codon, d in sorted(v['hotspot_map'].items(), key=lambda x: int(x[0])):
        gm = d['genomic'][0]
        ex = ''
        for r in exon_rows:
            if r['transcript'] == tid and r['coding_len'] and \
               r['codon_first'] != '' and r['codon_first'] <= int(codon) <= r['codon_last']:
                ex = r['exon_rank']
        hot_rows.append({'gene': g, 'transcript': tid, 'codon': int(codon),
                         'cds': '%d-%d' % (d['cds'][0], d['cds'][1]),
                         'chr': gm['seq_region_name'], 'g_start': gm['start'],
                         'g_end': gm['end'], 'exon_rank': ex})
wcsv('表2_热点密码子定位.csv', hot_rows,
     ['gene', 'transcript', 'codon', 'cds', 'chr', 'g_start', 'g_end', 'exon_rank'])

# ---------- 蛋白特征表（G 结构域 motif 以文献定义补齐） ----------
MOTIF = [('G1 / P-loop (GxxxxGKS)', 10, 17), ('switch I (G2 / effector lobe)', 30, 38),
         ('switch II (G3, DxxGQ/H)', 57, 64), ('G4 (NKxD)', 116, 119),
         ('G5 (SAK)', 145, 147)]
feat_rows = []
for g in ('KRAS', 'HRAS', 'NRAS'):
    ud = G[g]['uniprot_data']
    for n, a, b in MOTIF:
        feat_rows.append({'gene': g, 'accession': ud['accession'], 'source': '文献共识/UniProt',
                          'type': 'Motif(G-box)', 'start': a, 'end': b, 'desc': n})
    for f in ud['features']:
        if f['type'] in ('Region', 'Motif', 'Binding site', 'Lipidation',
                         'Modified residue', 'Propeptide', 'Helix', 'Beta strand',
                         'Turn', 'Alternative sequence'):
            feat_rows.append({'gene': g, 'accession': ud['accession'], 'source': 'UniProt',
                              'type': f['type'], 'start': f['start'], 'end': f['end'],
                              'desc': f['desc']})
wcsv('表3_蛋白结构特征.csv', feat_rows,
     ['gene', 'accession', 'source', 'type', 'start', 'end', 'desc'])

# ---------- 突变谱（MSK-IMPACT 泛癌） ----------
M = json.load(open(os.path.join(DATA, 'cbioportal_mutations.json')))
CT = json.load(open(os.path.join(DATA, 'cbioportal_sample_cancertype.json')))
study = json.load(open(os.path.join(RAW, 'cbioportal_study.json')))
ntot = study['allSampleCount']
nct = collections.Counter(CT.values())
mut_rows, byct_rows = [], []
for g, rows in M.items():
    c = collections.Counter(r['protein'] for r in rows if r['protein'])
    pos = collections.Counter(r['start'] for r in rows if r['start'])
    for p, n in sorted(c.items(), key=lambda x: -x[1]):
        st = [r['start'] for r in rows if r['protein'] == p][0]
        mut_rows.append({'gene': g, 'protein_change': p, 'codon': st, 'n': n,
                         'pct_of_gene_mut': round(100.0 * n / len(rows), 2),
                         'pct_of_cohort': round(100.0 * n / ntot, 3)})
    sm = collections.defaultdict(set)
    for r in rows:
        if r['sample'] in CT:
            sm[CT[r['sample']]].add(r['sample'])
    for k, s in sm.items():
        if nct[k] >= 40:
            byct_rows.append({'gene': g, 'cancer_type': k, 'n_mut_samples': len(s),
                              'n_samples': nct[k],
                              'freq_pct': round(100.0 * len(s) / nct[k], 1)})
wcsv('表4_突变谱_MSK-IMPACT.csv', sorted(mut_rows, key=lambda r: (r['gene'], -r['n'])),
     ['gene', 'protein_change', 'codon', 'n', 'pct_of_gene_mut', 'pct_of_cohort'])
wcsv('表5_各癌种突变频率_MSK-IMPACT.csv',
     sorted(byct_rows, key=lambda r: (r['gene'], -r['freq_pct'])),
     ['gene', 'cancer_type', 'n_samples', 'n_mut_samples', 'freq_pct'])
OUT['cohort'] = {'study': study['studyId'], 'name': study['name'],
                 'n_samples': ntot, 'reference_pmid': 28481359}

# ---------- AlphaFold pLDDT ----------
plddt = {}
for g in ('KRAS', 'HRAS', 'NRAS'):
    acc = G[g]['uniprot']
    p = os.path.join(STRU, 'AF-%s-F1-model.pdb' % acc)
    if not os.path.exists(p):
        continue
    d = {}
    for l in open(p):
        if l.startswith('ATOM') and l[12:16].strip() == 'CA':
            d[int(l[22:26])] = float(l[60:66])
    plddt[g] = [d[k] for k in sorted(d)]
json.dump(plddt, open(os.path.join(DATA, 'alphafold_plddt.json'), 'w'))
wcsv('表6_AlphaFold_pLDDT.csv',
     [{'gene': g, 'residue': i + 1, 'plddt': v} for g, a in plddt.items()
      for i, v in enumerate(a)], ['gene', 'residue', 'plddt'])

# ---------- 实验结构的可见残基范围 ----------
cov = []
for pid in ('5P21', '4Q21', '1WQ1', '4G0N', '4OBE', '4LDJ', '6OIM', '5VQ2',
            '6GJ8', '7RPZ', '3CON', '1NVV'):
    p = os.path.join(STRU, '%s.pdb' % pid)
    if not os.path.exists(p):
        continue
    ch = collections.defaultdict(set)
    for l in open(p):
        if l.startswith('ATOM'):
            ch[l[21]].add(int(l[22:26]))
    best = max(ch.items(), key=lambda x: len(x[1]))
    rs = sorted(r for r in best[1] if 0 < r < 400)
    if rs:
        gaps = [r for i, r in enumerate(rs[:-1]) if rs[i + 1] - r > 1]
        cov.append({'pdb': pid, 'chain': best[0], 'first_obs': rs[0], 'last_obs': rs[-1],
                    'n_obs': len(rs), 'missing_internal': len(set(range(rs[0], rs[-1] + 1)) - set(rs)),
                    'gap_after': ';'.join(str(x) for x in gaps)})
wcsv('表7_实验结构可见残基.csv', cov,
     ['pdb', 'chain', 'first_obs', 'last_obs', 'n_obs', 'missing_internal', 'gap_after'])

json.dump(OUT, open(os.path.join(DATA, 'prepared_meta.json'), 'w'),
          ensure_ascii=False, indent=1)
print('prepare ok  exons=%d hotspots=%d feats=%d muts=%d cov=%d' %
      (len(exon_rows), len(hot_rows), len(feat_rows), len(mut_rows), len(cov)))
print('MANE:', json.dumps(mane, ensure_ascii=False))
print('tx:', json.dumps(map_rows, ensure_ascii=False))

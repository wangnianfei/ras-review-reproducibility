#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""英文版表1–3：出表1，核表2、表3（make 时出表，make check 时 --check）。

表1：与中文版同源——药物集合、阶段、试验计数取自图9 的 `图八_药物泳道.csv`，
     英文文字取自 `数据/表一_补充列_en.tsv`；写 `英文版/Table1_RAS-directed_drug_landscape.md`。
表2、表3：英文版是人工翻译件（`英文版/Table2_*.md`、`Table3_*.md`），不由脚本生成。

核对（任何一条不过即非零退出）：
  1. 英文补充列与中文补充列、图9 三方的药物集合一致，节号列逐药相同；
  2. 表1 逐药：中文补充列每个字段里的每个数，英文同字段里都要出现（按多重集合，
     英文可以多：「Ⅱ期」译成 phase 2 会多出一个 2）；
  3. 表2、表3 逐行：表格行（以 | 开头、非分隔行）数目相同，中文行里的每个数，
     英文对应行里都要出现。附注是意译（去掉了项目内部的流程记录），不逐数核。
中文表改了而英文没跟上，这里就会报出来。

用法：python3 脚本/02_tables_en.py [--check]
"""
import collections, csv, glob, io, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LANES = os.path.join(os.path.dirname(ROOT), 'RAS综述示意图', '数据', '图八_药物泳道.csv')
ZH = os.path.join(ROOT, '数据', '表一_补充列.tsv')
EN = os.path.join(ROOT, '数据', '表一_补充列_en.tsv')
ENDIR = os.path.join(ROOT, '英文版')
OUT = os.path.join(ENDIR, 'Table1_RAS-directed_drug_landscape.md')
PAIRS = [('表二_获批药物与适应证、监管路径.md', 'Table2_approved_drugs_indications_regulatory_routes.md'),
         ('表三_关键临床研究汇总表.md', 'Table3_key_clinical_studies.md')]

SNAP = '2026-10-20'
LANE_NAME = {
    '1': 'OFF-state covalent inhibitors',
    '2': 'Non-covalent / reversible inhibitors (non-cysteine alleles)',
    '3': 'RAS(ON) tri-complex inhibitors',
    '4': 'Degraders and other direct modalities',
    '5': 'Upstream nodes and immune strategies',
    '6': 'Downstream pathway combination (does not bind RAS directly)',
}
STAGE_EN = {'Preclinical': 'Preclinical', 'Phase 1': 'Phase 1', 'Phase 1/2': 'Phase 1/2',
            'Phase 2': 'Phase 2', 'Phase 3': 'Phase 3', 'Approved': 'Approved'}
ORDER = ['Preclinical', 'Phase 1', 'Phase 1/2', 'Phase 2', 'Phase 3', 'Approved']
NUM = re.compile(r'\d+(?:\.\d+)?')
GENE = re.compile(r'(?<![*\w])(KRAS|NRAS|HRAS|RAS)(?![*\w])')


def nums(s):
    return collections.Counter(NUM.findall(s.replace('·', '.')))


def missing(zh, en):
    """中文里有、英文里不够数的数（多重集合差）。"""
    return sorted((nums(zh) - nums(en)).elements())


def tsv(p):
    return {r['drug']: r for r in csv.DictReader(io.open(p, encoding='utf-8'), delimiter='\t')}


def table_rows(p):
    out = []
    for line in io.open(p, encoding='utf-8'):
        s = line.strip()
        if s.startswith('|') and not re.match(r'^\|[\s|:-]+\|$', s):
            out.append(s)
    return out


def check():
    bad = []
    lanes = {r['drug'] for r in csv.DictReader(io.open(LANES, encoding='utf-8'))}
    zh, en = tsv(ZH), tsv(EN)
    for name, s in (('中文补充列', set(zh)), ('英文补充列', set(en))):
        if s != lanes:
            bad.append('%s ↔ 图9 药物集合不一致：只在图9 %s；只在%s %s'
                       % (name, sorted(lanes - s), name, sorted(s - lanes)))
    for d in sorted(set(zh) & set(en)):
        if zh[d]['section'] != en[d]['section']:
            bad.append('表1 %s：节号 %s ≠ %s' % (d, zh[d]['section'], en[d]['section']))
        for col in ('gene', 'alleles', 'state', 'mechanism', 'result'):
            m = missing(zh[d][col], en[d][col])
            if m:
                bad.append('表1 %s [%s]：英文缺 %s' % (d, col, ' '.join(m)))
    for zp, ep in PAIRS:
        zr, er = table_rows(os.path.join(ROOT, zp)), table_rows(os.path.join(ENDIR, ep))
        if len(zr) != len(er):
            bad.append('%s：表格行数 %d ≠ 英文 %d' % (zp, len(zr), len(er)))
            continue
        for i, (a, b) in enumerate(zip(zr, er), 1):
            m = missing(a, b)
            if m:
                bad.append('%s 第 %d 行（%s）：英文缺 %s' % (zp, i, b.split('|')[1].strip()[:40], ' '.join(m)))
    # 表注上标字母（Nature／Lancet 体例，2026-11-02）：表身用到的字母按首现顺序为 a、b、c…，
    # 每个都在表注里定义、表注里不多出；单元格里不再写「（见表注）」「(see Note)」。
    files = [os.path.join(ROOT, '表一_药物全景表.md')] + [os.path.join(ROOT, z) for z, _ in PAIRS] \
        + [os.path.join(ENDIR, e) for _, e in PAIRS]
    files.append(os.path.join(ENDIR, 'Table1_RAS-directed_drug_landscape.md'))
    for f in files:
        if not os.path.exists(f):
            continue
        txt = io.open(f, encoding='utf-8').read()
        rows = '\n'.join(table_rows(f))
        note = '\n'.join(l for l in txt.splitlines() if l.startswith(('注：', 'Note:')))
        used = list(dict.fromkeys(re.findall(r'<sup>([a-z])</sup>', rows)))
        defd = re.findall(r'<sup>([a-z])</sup>', note)
        name = os.path.basename(f)
        if used != [chr(97 + k) for k in range(len(used))]:
            bad.append('%s：表身上标字母未按 a、b、c 顺序首现（%s）' % (name, ''.join(used)))
        if defd != used:
            bad.append('%s：表注定义的字母 %s ≠ 表身用到的 %s' % (name, ''.join(defd), ''.join(used)))
        if re.search(r'见表注|see Note', rows):
            bad.append('%s：单元格里仍有「见表注」式指向，改用上标字母' % name)
    return bad


def build():
    lanes = list(csv.DictReader(io.open(LANES, encoding='utf-8')))
    en = tsv(EN)
    rows = sorted(lanes, key=lambda r: (int(r['lane']), -ORDER.index(r['stage']), r['drug'].lower()))
    o = io.StringIO()
    o.write('# Table 1　Landscape of RAS-directed drugs\n\n')
    # 维护者须知写成 HTML 注释：渲染后不可见，表头只留读者要的（2026-11-01 剥离内部痕迹）
    o.write('<!-- Generated by 脚本/02_tables_en.py from the Figure 9 data file (RAS综述示意图/数据/图八_药物泳道.csv) '
            'and 数据/表一_补充列_en.tsv; do not edit by hand. -->\n\n')
    o.write('> Placed at the end of §4.7. Wide table; set in landscape where needed.\n\n')
    # 一张表，不是六张（与中文版同改）：表头只出现一次，组名写成横跨整行的分组行
    o.write('| Drug (code) | Target | Alleles covered | Conformational state | Mechanism | Highest phase | '
            'Registered trials | Representative studies and key results | Section |\n')
    o.write('|---|---|---|---|---|---|---|---|---|\n')
    cur = None
    for r in rows:
        if r['lane'] != cur:
            cur = r['lane']
            o.write('| **%s** | | | | | | | | |\n' % LANE_NAME[cur])   # group rows unnumbered
        e = en[r['drug']]
        code = ' / '.join(p.strip() for p in re.split(r'[;；]', r['code']) if p.strip())
        drug = r['drug']
        if re.fullmatch(r'[a-z]{5,}', code) and not re.fullmatch(r'[a-z]{5,}', drug):
            drug, code = code, drug   # INN first, code in brackets (as in the Chinese table)
        name = drug + (' (%s)' % code if code else '')
        if r['lane'] == '6':
            name += '<sup>a</sup>'    # footnote a: no direct RAS binding
        it = lambda s: GENE.sub(r'*\1*', s)
        o.write('| %s | %s | %s | %s | %s | %s | %s | %s | %s |\n' % (
            name, it(e['gene']), it(e['alleles']), e['state'], it(e['mechanism']),
            STAGE_EN[r['stage']], r['n_trials'], e['result'], e['section']))
    # 表注只写一段（2026-11-02 作者，与中文版同改）：短语式，缩略语接在同段末尾。
    o.write('\nNote: Drug set and six groups as in Figure 9 (%d drugs); highest phase and registered trials from '
            'ClinicalTrials.gov (cut-off %s; 1 133 RAS-related phase 1–3 interventional oncology trials); registered '
            'trials: development activity, not efficacy, including trials with the drug only as a combination component, '
            'so counts overlap; approval information in Table 2; <sup>a</sup>no direct RAS binding, included for its FDA indication '
            'defined by *KRAS* mutation. '
            'Abbreviations: CRC / mCRC, (metastatic) colorectal cancer; DCR, disease control rate; IRRC, independent radiology review committee; LGSOC, low-grade serous ovarian cancer; MTD, maximum tolerated dose; NSCLC, non-small-cell lung cancer; ORR, objective response rate; OS, overall survival; PFS, progression-free survival; TCR, T-cell receptor; TRAE, treatment-related adverse event; VAF, variant allele frequency.\n' % (len(lanes), SNAP))
    os.makedirs(ENDIR, exist_ok=True)
    io.open(OUT, 'w', encoding='utf-8').write(o.getvalue())
    print('已写 英文版/%s：%d 药' % (os.path.basename(OUT), len(rows)))


if __name__ == '__main__':
    if '--check' not in sys.argv[1:]:
        build()
    bad = check()
    for b in bad:
        print('✗ ' + b)
    print('英文版表1–3 ↔ 中文版：不一致 %d 处' % len(bad))
    sys.exit(1 if bad else 0)

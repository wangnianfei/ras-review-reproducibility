#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KRAS／NRAS／HRAS 突变落在热点密码子的比例（2.4 段三引用的三个百分比）。

输入（本目录 数据/）
  cbioportal_mutations.json        泛癌队列的三基因突变记录（cBioPortal 导出）
  cbioportal_sample_cancertype.json 样本 → 癌种映射（其样本数即位点数，正文的 10 945）

输出
  数据/表6_密码子占比.csv           正文数字的复算结果，口径写明「按突变记录数」

纪律：正文里的 77%／66%／38% 必须由本脚本现算，不得手改。
口径说明：同一患者若带多条记录会被计多次，这是正文采用的口径（按记录数）；
          按患者去重时 HRAS 为 39.2%，与按记录数的 37.6% 差 1.6 个百分点，
          故正文必须写明「按突变记录数」，不可只写百分比。

密码子归位：cBioPortal 的 `proteinPosStart` 与 `protein_change` 在少数记录上不同。
其中 6 条**落在热点上**且两字段差 1：3 条 KRAS G12C 记作 11、2 条 KRAS 与 1 条 NRAS
的 Q61K 记作 60——按 `proteinPosStart` 算会把它们漏掉（KRAS 密码子 12 由 1 286 掉到
1 283）。另有若干移码／无义记录（如 `D105Tfs*9` 记作 104、`K5*` 记作 4），那是两个
字段的含义本不同，不涉及热点。故密码子一律从 `protein_change`
（如 `G12C`、`Q61K`、`A11_G12delinsTD`）的首个残基号解析，解析不出才回落到
`proteinPosStart`。这与 表4（图7 的棒棒糖图）用的是同一条规则，两件成品才不会互斥。

用法：python3 05_codon_share.py
"""
import collections
import csv
import json
import os
import re

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    '数据')
HOT = {'KRAS': 12, 'NRAS': 61, 'HRAS': 61}   # 各基因的热点密码子


def codon_of(m):
    """突变记录落在哪个密码子：优先从 protein_change 的首个残基号解析。"""
    mt = re.match(r'^[A-Za-z](\d+)', m.get('protein') or '')
    return int(mt.group(1)) if mt else m['start']


def main():
    muts = json.load(open(os.path.join(DATA, 'cbioportal_mutations.json')))
    ct = json.load(open(os.path.join(DATA, 'cbioportal_sample_cancertype.json')))
    rows = []
    for gene in ('KRAS', 'NRAS', 'HRAS'):
        ms = muts[gene]
        codon = collections.Counter(str(codon_of(m)) for m in ms)
        n = len(ms)
        hot = HOT[gene]
        # 患者层面，仅用于口径对照
        per = {}
        for m in ms:
            per.setdefault(m['patient'], codon_of(m))
        pc = collections.Counter(str(v) for v in per.values())
        rows.append(dict(gene=gene, cohort_samples=len(ct),
                         hot_codon=hot,
                         n_records=n, n_hot_records=codon[str(hot)],
                         pct_by_record=round(100.0 * codon[str(hot)] / n, 2),
                         n_patients=len(per), pct_by_patient=round(
                             100.0 * pc[str(hot)] / len(per), 2)))
    out = os.path.join(DATA, '表6_密码子占比.csv')
    with open(out, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        print('%-5s 密码子 %-3s 记录 %5d 中 %5d 条 = %5.2f%%  '
              '（按患者 %d 人 = %5.2f%%）' % (
                  r['gene'], r['hot_codon'], r['n_records'], r['n_hot_records'],
                  r['pct_by_record'], r['n_patients'], r['pct_by_patient']))
    print('样本总数 %d → 已写 %s' % (len(ct), out))


if __name__ == '__main__':
    main()

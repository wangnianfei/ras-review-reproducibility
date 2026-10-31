#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""图9（图件基名 Fig8_drug_class_swimlanes）n_trials 列的重算与核对。

**口径（2026-10-30 作者定）**：只按**通用名**匹配；没有通用名的药按**代号**匹配；
**不用商品名**（lumakras／krazati／zarnestra 一类不计）。匹配方式：归一化后
（NFKC → 大写 → 去非字母数字）在 `interventions + brief_title` 里找子串，
即「AMG 510」「AMG-510」「AMG510」视为同一写法。一条试验只要有一种写法命中即计一次。

两处例外，都是「这一行不是一个通用名」的情形，写在 EXCEPTIONS 里并标明理由：
  · 类别行 mutant-RAS TCR-T —— 不是分子：干预含 TCR，且 KRAS 在干预／标题／适应证中
    点名（只写“TCR-T cells”而没说针对哪个等位基因的 4 项不计）；
  · iExosome siG12D —— 无 INN，语料里该试验的干预原文写 “KRAS G12D siRNA”，
    按原文取别名，否则按药名／代号一个字都搜不到（NCT03608631）。

**别名＝通用名＋代号，逐一有出处（规矩 A10）**。`code` 列可以用「;」写多个代号／INN，
一个都不许省，也不许把两个分子并成一个（2026-10-30 督导更正令第一、三组）：
  · sosimerasib ＝ HBI-2438（HUYABIO，Ⅰ期 NCT05485974）＝ JMKX001899（济民可信／
    上海杰佑，Ⅲ期 NCT07242274、Ⅰb 期 NCT06946927），中文通用名索西美雷塞。出处：
    库内 `1.4_MolinaArcasM_2024`、`5.4_ChoucairK_2025`、`7.1_EbrightRY_2025` 的原表都把
    GH35 与 HBI-2438 列为**同表的两行不同药**；`4.7_RiedlJM_2026` 的疗效表把 sosimerasib
    对到 ChiCTR2200059986（Zhong 2025，ORR 52.4%）；注册表三条 JMKX001899／sosimerasib
    试验的申办方分别是 Jemincare 与 Shanghai Jeyou Pharmaceutical，HBI-2438 那条是
    HUYABIO International。**GH35 是苏州信诺维（Suzhou Genhouse Bio）的另一个 G12C 分子**
    （只登记了 NCT05010694，Ⅰ期），既不是 sosimerasib，也不并入本行计数。
  · TNO155 ＝ batoprotafib（诺华）；RMC-4630 ＝ SAR442720 ＝ vociprotafib（Revolution
    Medicines／赛诺菲，NCT04418661 以 INN 登记）。
  · QTX3034 与 QTX3046 是两个分子（NCT06227377 对 NCT06428500），不得合并。
  · fulzerasib ＝ IBI351（信达生物）＝ GFH925（劲方医药，海外／合作开发用此代号）。
    出处：库内 `4.2_YuanY_2025_40715048` 原文 “fulzerasib (also known as IBI351 or
    GFH925)”。语料里关键Ⅱ期 NCT05005234（GFH925X1101）与 KROCUS 联合研究
    NCT05756153（GFH925X0201）只用 GFH925 登记，别名漏了它就会漏计这两项
    （2026-10-31 督导更正令第一组）。
  · avutometinib＋defactinib（VS-6766＋VS-6063）—— **两个分子一排、按 avutometinib 计**：
    它是共包装的联合方案（AVMAPKI FAKZYNJA CO-PACK，FDA 2025-05-08 加速批准），
    而 defactinib（VS-6063）单独也登记了 FAK 单药试验，若把 defactinib 计入别名，
    那些单药试验会被算成这组合的（12 条含 DEFACTINIB，其中 2 条没有 avutometinib：
    NCT01951690 是 defactinib 单药Ⅱ期，NCT07020221 是 VS-7375 联合方案），
    与「这一行的干预是否含本组合」就不是同一件事。故别名只取
    avutometinib／VS-6766／RO5126766（后两个是同一分子的旧代号，见
    NCT03875820、NCT02407509、NCT03681483）；合共 14 项。出处：库内
    `4.1_BanerjeeSN_2025` 原文写 “avutometinib 3.2 mg two times per week in combination
    with oral defactinib 200 mg two times per day”，语料里同一试验的
    interventions 列为 “Avutometinib (VS-6766) + Defactinib (VS-6063)”。

历史沿革（不要照抄旧数）：2026-10-20 建图那次用的是一张手写别名字典，含商品名
（sotorasib 因此是 52）、且未搜 R115777／SCH66336（tipifarnib 79、lonafarnib 17）；
另有一条 `['sirna','antisense','mrna-5671']` 的合计量 2 被同时抄进 siG12D 与 V941
两行，两行各自把对方的试验算成了自己的。取证与差异见
`RAS综述原始文献/证据卡/图表核对_说明.md` §3.4。

用法：
  python3 -I 脚本/00_count_swimlane_trials.py           # 只核对试验计数，有差异即非零退出
  python3 -I 脚本/00_count_swimlane_trials.py --write    # 把重算值写回 CSV
  python3 -I 脚本/00_count_swimlane_trials.py --stage    # 只核对 stage／「语料最高阶段」，进 make check

**阶段口径（2026-10-31f 督导更正令第二组定，`--stage` 守这个）**：图9 的 `stage` 列与候选台账的
「语料最高阶段」列一律取该药命中试验里语料 `phase` 字段的**最高值**——Phase 1/Phase 2 记
Phase 1/2、Phase 2/Phase 3 记 Phase 2/3、Early Phase 1 与 Phase 1 都记 Phase 1——**不是**
`phase_group` 字段。后者把Ⅰ/Ⅱ期坍缩成Ⅱ期，上一轮新入图的三味药（HYP-2090PTSA、QLC1101、
FMC-376）就是这样被抬高的：三条登记在 `phase` 里都是 Phase 1/Phase 2，只有 `phase_group`
写 Phase 2。例：ZG19018（NCT06237400）一直画在 Ph 1/2，用的就是这个口径。
"""
import csv
import io
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                       # RAS综述示意图
BASE = os.path.dirname(ROOT)                       # 仓库根
LANES = os.path.join(ROOT, '数据', '图八_药物泳道.csv')
AUDIT = os.path.join(ROOT, '数据', '图八_试验命中.tsv')
TRIALS = os.path.join(BASE, 'RAS临床试验注册分析', '数据', '表1_临床试验总表.csv')
CAND = os.path.join(ROOT, '数据', '图八_直接RAS候选.tsv')

PRECLINICAL_OK = {'BI-2865', 'ADT-007'}            # 临床前，预期 0 命中

EXCEPTIONS = {
    'mutant-RAS TCR-T': ['TCR'],        # 另加 KRAS 限定，见 aliases_of()
    'iExosome siG12D': ['KRASG12DSIRNA', 'SIG12D', 'SIG12DLODER'],
    # 联合方案行：两个分子排在一排，但只按 avutometinib 计（不单按 defactinib 计），
    # 理由与三条代号（VS-6766／RO5126766）的出处见文件头注。
    'avutometinib + defactinib': ['AVUTOMETINIB', 'VS6766', 'RO5126766'],
}


def norm(s):
    s = unicodedata.normalize('NFKC', s or '').upper()
    return re.sub(r'[^A-Z0-9]', '', s)


# ---------- 阶段核对（--stage，已进 make check）----------
# 语料 phase 字段的五个取值按序数排；同分时取更后者（Phase 1/Phase 2 高于 Phase 1）。
PHASE_RANK = {'Early Phase 1': 1, 'Phase 1': 1, 'Phase 1/Phase 2': 1.5,
              'Phase 2': 2, 'Phase 2/Phase 3': 2.5, 'Phase 3': 3}
PHASE_LABEL = {1: 'Phase 1', 1.5: 'Phase 1/2', 2: 'Phase 2', 2.5: 'Phase 2/3', 3: 'Phase 3'}

# 逐行例外（stage 列不按语料 phase 记），理由与 CLAUDE.md 规矩同层：
#  · 获批药：stage 记监管状态 Approved，不以语料最高阶段覆盖它——获批是更强的状态，
#    而且获批后新增的早期试验会把「最高阶段」变得没有意义（图上标记也不再分阶段）。
#  · 临床前：语料 0 命中（PRECLINICAL_OK），无 phase 可算。
#  · 个案：此处留空；加行时必须同时把理由写进本注释与图注或说明文档。
STAGE_OVERRIDE = {}
APPROVED_LABEL = 'Approved'
PRECLINICAL_LABEL = 'Preclinical'

# 上图标准里「已发表临床读数」那一支：仅Ⅰ期但库内有已发表临床读数者可以上图。
# 这是判断层，不靠脚本推，逐条给理由（规矩 A8：决定与缺口分开写）。
READOUT_OK = {
    'GEC255': '仅Ⅰ期，但 4.7_OyaY_2024 报 ORR 77%（16 例入组、13 例可评估）',
}


def calc_stage(hits, by):
    """命中试验的 phase 字段最高值 → stage 标签；无命中返回 None。"""
    ranks = [PHASE_RANK[by[n]['phase']] for n in hits
             if n in by and by[n]['phase'] in PHASE_RANK]
    return PHASE_LABEL[max(ranks)] if ranks else None


def check_stage(trials, blob, blob3, rows):
    """stage 列与「语料最高阶段」列 ↔ 语料 phase 最高值；不一致即非零退出。"""
    by = {r['nct_id']: r for r in trials}
    bad = []

    print('== 泳道表：图八_药物泳道.csv 的 stage ↔ 语料 phase 最高值')
    print('%-24s %-12s %-12s %s' % ('drug', 'stated', 'calc', '判'))
    for r in rows:
        drug, stated = r['drug'], r['stage']
        hits = hits_of(r, blob, blob3)
        calc = calc_stage(hits, by)
        if stated == APPROVED_LABEL:
            verdict = '豁免：获批药记监管状态（语料最高 %s）' % (calc or '—')
        elif stated == PRECLINICAL_LABEL:
            verdict = ('豁免：临床前、语料 0 命中' if not hits
                       else '临床前但语料有 %d 项命中，先查别名' % len(hits))
            if hits:
                bad.append((drug, stated, '有 %d 项命中' % len(hits)))
        elif drug in STAGE_OVERRIDE:
            verdict = '豁免：' + STAGE_OVERRIDE[drug]
        elif calc == stated:
            verdict = '一致'
        else:
            verdict = '不一致'
            bad.append((drug, stated, calc or '无命中'))
        print('%-24s %-12s %-12s %s' % (drug[:23], stated, calc or '—', verdict))

    print('\n== 候选台账：图八_直接RAS候选.tsv 的「语料最高阶段」↔ 语料 phase 最高值，及「是否上图」')
    cand = list(csv.DictReader((l for l in io.open(CAND, encoding='utf-8')
                                if not l.startswith('#')), delimiter='\t'))
    for r in cand:
        code, stated = r['code'], r['语料最高阶段']
        ids = [x.strip() for x in re.split(r'[;；]', r['NCT 号'])
               if x.strip().startswith('NCT')]
        hits = [i for i in ids if i in by]
        calc = calc_stage(hits, by)
        note = ''
        if stated == '语料未登记':
            if hits:
                bad.append((code, stated, calc))
                note = '不一致：表记未登记，语料内有 %d 项' % len(hits)
            else:
                note = '豁免：语料未登记（无 phase 可算）'
        elif calc == stated:
            note = '一致'
        else:
            note = '不一致'
            bad.append((code, stated, calc or '无命中'))
        miss = [i for i in ids if i not in by]
        if miss:
            note += '；语料无此登记号 %s' % '、'.join(miss)
        # 是否上图：是 → 阶段达Ⅰ/Ⅱ期及以上，或已在 READOUT_OK 备案已发表读数
        if r['是否上图'] == '是':
            rank = max((PHASE_RANK[by[i]['phase']] for i in hits
                        if by[i]['phase'] in PHASE_RANK), default=0)
            if rank == 0:
                note += '；上图但语料无阶段可算'
                bad.append((code, '上图', '无阶段'))
            elif rank < 1.5 and code not in READOUT_OK:
                note += '；上图但仅Ⅰ期且无备案的已发表读数'
                bad.append((code, '上图', calc))
        print('%-16s %-10s %-10s %s' % (code[:15], stated, calc or '—', note))

    # 只报告：阶段已达标、身份已证实、却未上图的行（可能是有理由的个案，不拦）
    soft = [r['code'] for r in cand
            if r['是否上图'] == '否' and r['身份证据类型'] in ('registry_title', 'library_paper')
            and calc_stage([i for i in re.split(r'[;；]', r['NCT 号'])
                            if i.strip().startswith('NCT') and i.strip() in by], by)
            in ('Phase 1/2', 'Phase 2', 'Phase 2/3', 'Phase 3')]
    if soft:
        print('\n（只报告）阶段已达标、身份已证实但未上图：%s（逐条理由见末列）' % '、'.join(soft))

    print('\n不一致 %d 行' % len(bad))
    for b in bad:
        print('  · %s：现写 %s → 应为 %s' % b)
    return 1 if bad else 0


def aliases_of(row):
    if row['drug'] in EXCEPTIONS:
        return EXCEPTIONS[row['drug']]      # 类别行另在计数处加 KRAS 限定
    out = [norm(row['drug'])]
    # code 可写多个，用「;」分隔（图9 与表1 显示成「A／B」）
    for c in re.split(r'[;；]', row.get('code', '')):
        out.append(norm(c))
    return [a for a in out if a]


def hits_of(row, blob, blob3):
    """该行在语料里的命中试验号（与「图八_试验命中.tsv」同一套别名规则）。"""
    pats = aliases_of(row)
    if row['drug'] == 'mutant-RAS TCR-T':
        # 类别行：干预含 TCR 且 KRAS（或突变等位基因）在干预／标题／适应证中点名
        return sorted(n for n, iv, ctx in blob3
                      if any(p in iv for p in pats) and 'KRAS' in iv + ctx)
    return sorted(n for n, t in blob if any(p in t for p in pats))


def main():
    write = '--write' in sys.argv
    trials = list(csv.DictReader(io.open(TRIALS, encoding='utf-8-sig')))
    blob = [(r['nct_id'], norm(r['interventions'] + ' ' + r['brief_title'])) for r in trials]
    blob3 = [(r['nct_id'], norm(r['interventions']), norm(r['brief_title'] + ' ' + r['conditions']))
             for r in trials]
    rows = list(csv.DictReader(io.open(LANES, encoding='utf-8-sig')))
    fields = list(rows[0].keys())

    if '--stage' in sys.argv:
        return check_stage(trials, blob, blob3, rows)

    print('%-22s %-12s %6s %6s %5s' % ('drug', 'stage', 'stated', 'calc', 'diff'))
    bad, zero, audit = [], [], []
    for r in rows:
        hits = hits_of(r, blob, blob3)
        calc, stated = len(hits), int(r['n_trials'])
        print('%-22s %-12s %6d %6d %+5d%s'
              % (r['drug'][:21], r['stage'], stated, calc, calc - stated,
                 '' if calc == stated else '  <<<'))
        if calc != stated:
            bad.append((r['drug'], stated, calc))
        if calc == 0 and r['drug'] not in PRECLINICAL_OK:
            zero.append(r['drug'])
        audit.append((r['drug'], calc, ';'.join(hits)))
        if write:
            r['n_trials'] = str(calc)

    with io.open(AUDIT, 'w', encoding='utf-8') as f:
        f.write('# 图9 试验计数重算的命中清单（由 00_count_swimlane_trials.py 生成，勿手改）\n')
        f.write('# 语料：RAS临床试验注册分析/数据/表1_临床试验总表.csv（%d 项）\n' % len(trials))
        f.write('drug\tn_trials\tnct_ids\n')
        for a in audit:
            f.write('%s\t%d\t%s\n' % a)

    if write:
        with io.open(LANES, 'w', encoding='utf-8', newline='') as f:
            w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
            w.writeheader()
            w.writerows(rows)
        print('\n已写回 %s' % os.path.relpath(LANES, BASE))

    print('\n差异 %d 行；命中清单 %s' % (len(bad), os.path.relpath(AUDIT, BASE)))
    for d, s, c in bad:
        print('  · %s：表 %d → 重算 %d' % (d, s, c))
    if zero:
        print('零命中且非临床前（先查别名）：%s' % '、'.join(zero))
    return 1 if (bad or zero) and not write else 0


if __name__ == '__main__':
    sys.exit(main())

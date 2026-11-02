#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""表1「RAS 靶向药物全景表」的生成器。

**为什么要用脚本生成**：附录三的图表总则写着「图9的药物集合须与表1完全一致」。
手工维护两份清单，迟早会漂——这正是 §七十三 在登记表上量出来的那类漂移。所以
表1的**药物集合、最高阶段与试验计数一律取自图9的数据文件**，脚本只负责把
「构象态／机制／代表研究与关键结果」这三列补上；两边的药名集合一旦不等，脚本
直接报错退出，不出表。

补充列（`数据/表一_补充列.tsv`）里的每一条关键结果都标了正文节号，数值必须能在
该节找到同源陈述与引用。正文没有展开读数的药，这一列写「本综述正文未展开疗效
读数」，**不从别处补**——表1不是独立的证据来源。

用法：python3 01_build_table1.py
      python3 01_build_table1.py --check   # 只核「代表研究与关键结果」列，不出表
输出：../表一_药物全景表.md

**--check 的口径（2026-10-31g 第二组起，已进 make check）**：「代表研究与关键结果」
一列的每个数值，必须在所标「正文」节的 md 里出现同一个数；凡写成 k/n 或 n=NN 者，
分子分母都要对得上。它拦不住的是「正文本身就写错」——那一类只能回原文核，脚本
只报正文与表不一致，不判谁对。
"""
import csv, importlib.util, io, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LANES = os.path.join(os.path.dirname(ROOT), 'RAS综述示意图', '数据',
                     '图八_药物泳道.csv')
EXTRA = os.path.join(ROOT, '数据', '表一_补充列.tsv')
OUT = os.path.join(ROOT, '表一_药物全景表.md')

SNAP = '2026-10-20'
LANE_NAME = {
    '1': 'OFF 态共价抑制剂',
    '2': '非共价／可逆抑制剂（非半胱氨酸等位基因）',
    '3': 'RAS(ON) 三元复合物抑制剂',
    '4': '降解剂及其他直接作用模式',
    '5': '上游节点与免疫策略',
    '6': '下游通路联合（不直接结合 RAS）',
}
STAGE_CN = {'Preclinical': '临床前', 'Phase 1': 'Ⅰ期', 'Phase 1/2': 'Ⅰ/Ⅱ期',
            'Phase 2': 'Ⅱ期', 'Phase 3': 'Ⅲ期', 'Approved': '已获批'}

lanes = list(csv.DictReader(io.open(LANES, encoding='utf-8')))
extra = {r['drug']: r for r in
         csv.DictReader(io.open(EXTRA, encoding='utf-8'), delimiter='\t')}
SECS = os.path.join(os.path.dirname(ROOT), 'RAS综述原始文献', '正文')

NUM = re.compile(r'\d+(?:\.\d+)?')
FRAC = re.compile(r'(\d+)\s*/\s*(\d+)')


def _norm(t):
    """把表1与正文的排版差异抹平后再比数：全角斜杠→/，间隔号→小数点
    （正文里 Lancet 体例的「0·66」与表里的「0.66」是同一个数），
    并删去日期、「RECIST 1.1」这类版本号与「见 4.1 段三」这类节号回指——
    它们不是疗效数值。"""
    t = t.replace('**', '').replace('／', '/').replace('·', '.')
    t = re.sub(r'\d{4}-\d{2}-\d{2}', ' ', t)          # 2025-05-08
    t = re.sub(r'RECIST \d+\.\d+', ' ', t)            # RECIST 1.1
    t = re.sub(r'\d+\.\d+\s*段[一二三四五六七八九十a-z]*', ' ', t)  # 见 4.1 段三
    return t


def check_results():
    """「代表研究与关键结果」列 ↔ 所标正文节。返回不一致项清单。

    两条判据：① 列里出现的每个数，都要在正文里出现同一个数（防 126 写成 124）；
    ② 凡写成 k/n 的，k 与 n 在正文中须挨着出现（±80 字），防分子分母错位。

    **它拦不住什么**（2026-10-31g 实测）：若表里把「入组例数」当成「缓解率的分母」，
    而这个错数在正文里另有出处（5.1 的「纳入 126 例经治患者」就是），①号判据会因为
    「126 在正文里确实出现」而放过它——sotorasib 那处 n=126→46/124 的错正是这样
    躲过脚本、由人读 Skoulidis 2021 的 Table 2 才发现的。②号判据只在表写成 k/n 时
    才起作用，所以本轮把两处缓解率一律改成 k/n 写法，以后同类漂移能被它拦住。
    """
    cache, bad = {}, []
    for drug, e in sorted(extra.items()):
        secs = [s.strip() for s in re.split(r'[/／、]', e['section']) if s.strip()]
        res = _norm(e['result'])
        text = ''
        for s in secs:
            p = os.path.join(SECS, s + '.md')
            if not os.path.exists(p):
                bad.append((drug, e['section'], '节文件不存在：%s' % s, ''))
                continue
            if s not in cache:
                cache[s] = _norm(io.open(p, encoding='utf-8').read())
            text += cache[s]
        if not text:
            continue
        toks = set(NUM.findall(text))
        missing = sorted({t for t in NUM.findall(res) if t not in toks},
                         key=lambda x: (len(x), x))
        if missing:
            bad.append((drug, e['section'], '正文缺这些数：' + '、'.join(missing),
                        e['result']))
        for k, n in FRAC.findall(res):
            near = False
            for m in re.finditer(r'(?<![\d.])%s(?![\d.])' % re.escape(n), text):
                seg = text[max(0, m.start() - 80):m.end() + 80]
                if re.search(r'(?<![\d.])%s(?![\d.])' % re.escape(k), seg):
                    near = True
                    break
            if not near:
                bad.append((drug, e['section'],
                            'k/n 的分子分母在正文中不挨着：%s/%s' % (k, n),
                            e['result']))
    return bad


if '--check' in sys.argv[1:]:
    bad = check_results()
    for drug, sec, why, res in bad:
        print('✗ %-22s 正文 %-10s %s' % (drug, sec, why))
        print('    表1：%s' % res)
    print('表1 结果列 ↔ 正文：%d 行，不一致 %d 处' % (len(extra), len(bad)))
    sys.exit(1 if bad else 0)

a, b = {r['drug'] for r in lanes}, set(extra)
if a != b:
    print('图9药物集合与表1补充列不一致，拒绝出表：', file=sys.stderr)
    for d in sorted(a - b):
        print('  只在图9：', d, file=sys.stderr)
    for d in sorted(b - a):
        print('  只在表1：', d, file=sys.stderr)
    sys.exit(1)

rows = sorted(lanes, key=lambda r: (int(r['lane']),
                                    -['Preclinical', 'Phase 1', 'Phase 1/2',
                                      'Phase 2', 'Phase 3',
                                      'Approved'].index(r['stage']),
                                    r['drug'].lower()))

out = io.StringIO()
out.write('# 表1　RAS 靶向药物全景表\n\n')
out.write('> 位置：4.7 节末。横向宽表，排版时必要处横置页面。\n>\n')
out.write('> **本表由 `脚本/01_build_table1.py` 生成，请勿手改。**药物集合、最高'
          '阶段与试验计数取自图9的数据文件（`RAS综述示意图/数据/图八_药物泳道'
          '.csv`），两边不一致时脚本拒绝出表。\n\n')
# 一张表，不是六张：六个机制组原先各起一张子表，表头因此重复六遍，读者翻到
# 第三组时还要回去对表头。现在只有一行表头，组名写成横跨整行的分组行
# （`doctable.add_table` 认「只有第一格有字」的行，合并单元格并加粗）。
out.write('| 药物（代号） | 靶向基因 | 覆盖等位基因 | 构象态 | 机制 | '
          '最高阶段 | 登记试验数 | 代表研究与关键结果 | 正文 |\n')
out.write('|---|---|---|---|---|---|---|---|---|\n')
cur = None
for r in rows:
    if r['lane'] != cur:
        cur = r['lane']
        out.write('| **%s、%s** | | | | | | | | |\n'
                  % ('一二三四五六七八九十'[int(cur) - 1], LANE_NAME[cur]))
    e = extra[r['drug']]
    # code 列可写多个代号（用「;」分隔，出处见 00_count_swimlane_trials.py 头注），
    # 表里用全角「／」连写：sosimerasib（HBI-2438／JMKX001899）
    code = '／'.join(p.strip() for p in re.split(r'[;；]', r['code']) if p.strip())
    name = r['drug'] + ('（%s）' % code if code else '')
    # 基因符号斜体、蛋白正体（同正文与图注的写法规范）：靶向基因一栏里的
    # KRAS/NRAS/HRAS/RAS 是基因名，输出成 *KRAS*；「突变 RAS 新抗原」里的 RAS
    # 亦指基因，一并斜体。等位基因与氨基酸改变（G12C 等）保持正体。
    gene = re.sub(r'\b(KRAS|NRAS|HRAS|RAS)\b', r'*\1*', e['gene'])
    out.write('| %s | %s | %s | %s | %s | %s | %s | %s | %s |\n' % (
        name, gene, e['alleles'], e['state'], e['mechanism'],
        STAGE_CN[r['stage']], r['n_trials'], e['result'], e['section']))

# 表注只写一段、300 个汉字以内（2026-11-02 作者）：原先三条编号附注加表头三段口径说明，
# 读者要翻两处才看全。现在口径、收录边界与 avutometinib＋defactinib 的收录理由并成一段，
# 置于表下；投稿稿按小五、单倍行距排（`02_make_docx.py` 认段首「注：」）。
out.write('\n注：药物集合与六组同图9（共 %d 个药）；最高阶段与登记试验数据 ClinicalTrials.gov（截取日 %s，'
          '1 133 项 RAS 相关Ⅰ–Ⅲ期干预性肿瘤试验），登记试验数示研发活跃度、非疗效，含作为联合组分的登记，各药间不互斥；'
          '第六组 avutometinib＋defactinib 不直接结合 RAS，按 *KRAS* 突变界定的 FDA 适应证收录；获批信息见表2。'
          '\n' % (len(lanes), SNAP))

# 全表再过一遍基因／蛋白判定：靶向基因列已就地标了斜体，这里补的是
# 「代表研究与关键结果」与附注里以散文出现的基因名（HRAS 突变人群、KRAS G12C 等）。
# 判定与正文共用 `原始文献/RAG/脚本/辅助/geneprotein.py`，不另立一套。
_gp = os.path.join(os.path.dirname(ROOT),
                   'RAS综述原始文献', 'RAG', '脚本', '辅助', 'geneprotein.py')
_spec = importlib.util.spec_from_file_location('geneprotein', _gp)
_gmod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_gmod)
txt, _n = _gmod.GeneProtein().italicise(out.getvalue(), [])
io.open(OUT, 'w', encoding='utf-8').write(txt)
print('已写 表一_药物全景表.md：%d 药 / %d 组' % (len(rows), len(LANE_NAME)))

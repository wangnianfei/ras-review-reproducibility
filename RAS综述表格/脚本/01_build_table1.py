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
          '.csv`），两边不一致时脚本拒绝出表。\n>\n')
out.write('> 「登记试验数」为该药在本综述自建 ClinicalTrials.gov 语料（REST API '
          'v2，%s 快照，1 133 项 RAS 相关Ⅰ–Ⅲ期干预性肿瘤试验）中被登记的试验'
          '数，衡量研发活跃度而非疗效；仅作为联合方案组分出现者亦计入，故彼此'
          '不互斥。「最高阶段」为该药在该语料中所达最高阶段。\n>\n' % SNAP)
out.write('> 「代表研究与关键结果」一列的每个数值都能在所标正文节中找到同源陈述'
          '与引用；**单臂缓解率一律连样本量与评审方式同写**。正文未展开读数者如实'
          '写明，不从表外补数。获批信息见表2，并须在校样阶段按最新标签重核。\n\n')

cur = None
for r in rows:
    if r['lane'] != cur:
        cur = r['lane']
        out.write('\n## %s、%s\n\n' % ('一二三四五六七八九十'[int(cur) - 1],
                                      LANE_NAME[cur]))
        out.write('| 药物（代号） | 靶向基因 | 覆盖等位基因 | 构象态 | 机制 | '
                  '最高阶段 | 登记试验数 | 代表研究与关键结果 | 正文 |\n')
        out.write('|---|---|---|---|---|---|---|---|---|\n')
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

out.write('\n---\n\n## 表1附注\n\n')
out.write('**一、本表与图9同集合，因此也同边界。**本表的六个分组'
          '与图9 的六条泳道一一对应、次序相同（本表按序号编组，泳道是图上的横轨）。'
          '坐标只覆盖**作用于 RAS 蛋白'
          '的药物**，以及其上游加工与调控节点、针对突变 RAS 新抗原的免疫策略。'
          '基因治疗（siRNA／miRNA／CRISPR）靶向的是基因与转录本而非 RAS 蛋白，'
          '构象态对它没有取值，故不入坐标（见 4.7 段一d）；唯一的例外是'
          ' iExosome siG12D，它已有人体读数且在 5.3 段六a展开，按「RNA 疗法」'
          '列出并在构象态一栏写明「不适用」。\n\n')
out.write('**二、正文提到、但不在本表内的药物，以及为什么。**\n\n')
out.write('| 药物 | 出现处 | 不入表的理由 |\n|---|---|---|\n')
out.write('| ifebemtinib | 6.5 段四e、图12（联合 garsorasib，一线确认 ORR 82%）'
          ' | FAK 抑制剂，既不作用于 RAS 蛋白，也不属上游输入节点或免疫策略，在'
          '坐标之外；它是联合搭档，不是 RAS 靶向药。 |\n')
out.write('| cetuximab、panitumumab | 5.2、6.5 段二 | 抗 EGFR 抗体，同上，属联合'
          '搭档。 |\n')
out.write('| 卡铂、培美曲塞、吉西他滨、白蛋白结合型紫杉醇、多西他赛 | 5.1、5.3、'
          '6.5 段五 | 细胞毒药物，属对照臂或联合搭档。 |\n')
out.write('| avutometinib、defactinib、binimetinib、selumetinib、trametinib、'
          'CI-1040 | 4.1、5.4 | 下游激酶抑制剂与 RAF/MEK 分子胶，作用点在 RAS '
          '之下，不在坐标内；它们在 4.1 作为「间接策略时代」的证据出现。**例外**：'
          'avutometinib＋defactinib 本表已收（第六组），理由见附注五——不是因为它'
          '作用于 RAS，而是因为它的适应证以 *KRAS* 突变界定且已获批准。 |\n')
out.write('\n**三、一处需要校样核对的计数。**图9与本表的药物数**由本脚本现算**，'
          '当前为 **%d 个**（历次变动：初稿 43 → 补入 D3S-001 为 44 → §九十二 '
          '补入 QTX3544 与 RMC-5127 为 46 → 2026-10-31 补入 avutometinib＋defactinib '
          '为 47 → 同日按督导第三组补入 HS-10370、ZG19018、YL-15293、GEC255、JAB-23E73、'
          'ZG2001、GFH276 与 ARV-806 为 55 → 2026-10-31e 全量扫描补入 DN022150、FMC-376、'
          'HYP-2090PTSA 与 QLC1101 为 %d，'
          '身份与出处见 `RAS综述示意图/数据/图八_直接RAS候选.tsv`）。'
          '**凡正文或提纲写死这个数，改药后都要回查**'
          '，提纲附录三的图9行与图件清单行各有一处。\n' % (len(lanes), len(lanes)))
out.write('\n**四、sitneprotafib 的身份已查实（§八十）。**它就是 **JAB-3312**，'
          '不是另一个分子，因此本表不增行，只把第五组原有的那一行改写为'
          '「sitneprotafib（JAB-3312）」。两个独立来源一致：库内 '
          '`6.3_HendriksLEL_2026_42702211`（Lancet Respir Med 2026，综述）原文写'
          '“plus the SHP2 inhibitor sitneprotafib (JAB-3312), objective”；厂商'
          '公开资料与 ClinicalTrials.gov 登记号 NCT05288205（glecirasib 联合的'
          'Ⅰ/Ⅱa 期，一线 ORR 71%）亦指向同一分子，而该登记号正在本综述语料里'
          '以 JAB-3312 归属的 5 项试验之中。**命名以厂商／FDA 公布者为准**'
          '（用户 2026-10-27 裁定）：加科思（Jacobio）自家公告即写 '
          '「Sitneprotafib（JAB-3312）」，与上述原文一致，此条就此结清，'
          '不再挂「查 WHO INN 名录」。\n')
out.write('\n**五、第六组里的 avutometinib＋defactinib 是「按适应证收入」，'
          '不是按机制收入（2026-10-31 作者裁定）。**avutometinib 是 RAF/MEK 分子胶'
          '（钳制剂），defactinib 是 FAK 抑制剂，**两者都不直接结合 RAS**，'
          '作用点在 RAS 下游与平行链——所以它**单列第六组（下游通路联合）**，不放进第五组（上游节点与免疫策略）。它进本表是因为 FDA 2025-05-08 的加速批准'
          '以 *KRAS* 突变界定适应证（KRAS 突变复发 LGSOC，见表2 附注七）；'
          '第六组的题名（下游通路联合，不直接结合 RAS）因此与这一行相符，'
          '图9 同位置的行标签已在括号里写明靶点，图注另有一句说明。'
          '若日后把它移出坐标，应同时改图9 数据、图注与 4.1。\n')

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

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""项目内部痕迹的剥离表：投稿稿、专著版与公开复现包三处共用的唯一来源。

源文件（正文、表注、图注）是脚手架，带着裁定日期、谁拍板、文件放在哪个目录；
各出口在输出层剥掉，事实一律留下。

- 投稿稿 `01_build_draft.py`：`trace_rules('投稿')` 接在 POLISH 末尾。
- 专著版 `02_build_book.py`：落盘前 `strip_traces(doc, '专著')`。
- 复现包：`export.py` 复制表与图注后 `strip_package`（逐句规则 → 整段剥离 → 表注重排），
  包里 `reproduce.sh` 重出表1 后按随包的 `表注重排.tsv` 再剥一次——所以本文件随包分发，
  **只用标准库**。

三样东西都在这里：逐句规则 `TRACE`、整段剥离 `DROP_PARA`、表注重排 `renumber_notes`
（投稿稿用 '投稿' 形态，复现包用 '源' 形态；专著版只用 TRACE，保留全部附注与原编号）。

每条 `(旧, 新)` 或 `(旧, 新, 出口)`。不标出口的各出口都用；标「投稿」的只在投稿稿用；
标「专著」的是**源文件原样**的写法（投稿稿先做过「本综述→本文」等改写，字面不同），
专著版与复现包都用。`re:` 前缀为正则。投稿稿与专著版要求每条都命中（落空即退出码 1）；
复现包只收表与图注、不收正文，命中多少报多少。

命令行（复现包用）：python3 traces.py [--map 表注重排.tsv] <文件…>   就地剥；坏指向退出码 1
"""
import io
import re
import sys

TRACE = (
    # ── 前期收口里属于内部痕迹的条目（2026-11-01 自 POLISH 迁入，两出口共用）
    ('止于它在 1 133 项 ClinicalTrials.gov 语料中所达到的最高研发阶段',
     '止于它在 1 133 项登记试验中所达到的最高研发阶段'),
    ('右侧轨道的数字为该药在同一语料中被登记的试验数',
     '右侧轨道的数字为该药在同一批登记试验中被登记的试验数'),
    ('这一日期与适应证取自一篇前临床论文的引言，已对 FDA 的肿瘤批准公告逐字核过'
     '（2026-10-27），两者一致。', ''),
    ('re:这是全节约束最紧的一条纪律。', '这是本节最严格的一条约束。'),
    ('提纲列了三条机制，即 ', '通路图上常列三条机制，即 '),
    ('；且该文为期刊预校样版本，校样阶段须换正式版重核', '；该文为预校样版本'),
    ('按纪律这类跨研究比较只能降级不能升级', '此类跨研究比较只能降级不能升级'),

    # ── 项目内部痕迹（作者 2026-11-01 裁定，逐条对应裁定表 A1–C4）─────────────
    # 这些是脚手架：项目编号、裁定日期、谁拍板、文件放在哪个目录。事实一律留下，
    # 只去掉「这是哪个项目、谁在哪天定的」。与 DROP_PARA 同纪律：每条必须命中。
    # 内部痕迹 A1（作者 2026-11-01 裁定）图9 图注的裁定痕迹
    ('**本图的纳入标准（2026-10-31 补，作者授权督导定）。**',
     '**本图的纳入标准。**'),
    # 内部痕迹 B2：图7 图注的复算脚本路径
    ('复算脚本 `脚本/05_codon_share.py`', '复算脚本见公开复现包'),
    # 内部痕迹 B4：图9 图注里的数据文件路径（清单本身改指补充材料）
    ('列于 `数据/图八_直接RAS候选.tsv`', '列于补充材料'),
    # 内部痕迹 B5：图9 图注里的扫描脚本路径
    # （2026-11-01 作者改定：扫描脚本要读全文库，按 export.py 的 SKIP 不随复现包分发，
    #   原先写的「可由公开复现包中的扫描脚本复跑」不成立；口径与英文图注一致）
    ('两个方向都由 `RAS综述示意图/脚本/05_scan_direct_ras_candidates.py` 复跑',
     '两个方向都由脚本对本综述收集的全文逐篇扫描（全文受版权限制，不随复现包分发）'),
    # 内部痕迹 D（作者 2026-11-01 裁定）：「语料」是项目内部对自建试验集的叫法。
    # 全稿第一次出现处写全称并补口径，之后每个图注／表／节内首次写
    # 「本文的试验登记数据集」、同单元内再出现写「该数据集」。
    ('语料中凡能证明是直接 RAS 抑制剂',
     '本文的试验登记数据集（ClinicalTrials.gov，截取日 2026 年 10 月 20 日，'
     '共 1 133 项 RAS 相关Ⅰ–Ⅲ期干预性肿瘤试验）中凡能证明是直接 RAS 抑制剂'),
    # 表1 表体：单元格里用短式
    ('未载（语料记 Undisclosed）', '未载（数据集记为 Undisclosed）'),
    ('（语料最高阶段Ⅲ期）', '（数据集内最高阶段Ⅲ期）'),
    # 图11 图注
    ('本图的语料只取自 ClinicalTrials.gov',
     '本文的试验登记数据集只取自 ClinicalTrials.gov'),
    # 图9 图注余下的各处
    ('**上图只收**语料最高阶段', '**上图只收**该数据集内最高阶段'),
    ('只在综述表里出现而语料未登记', '只在综述表里出现而该数据集未登记'),
    ('——语料登记为Ⅱ期但已停止开发', '——该数据集登记为Ⅱ期但已停止开发'),
    ('——语料未载作用方式', '——该数据集未载作用方式'),
    ('① 语料 1 133 项试验的干预字段', '① 该数据集 1 133 项试验的干预字段'),
    ('再与语料对照', '再与该数据集对照'),
    ('不再用语料 `target_class`', '不再用该数据集 `target_class`'),
    ('泳道的归属依语料所载机制', '泳道的归属依该数据集所载机制'),
    ('：语料只写靶点', '：该数据集只写靶点'),
    # 内部痕迹 F3（作者 2026-11-01 裁定，清单外补）：图9 图注的核法起点日期
    ('**完整性的核法（2026-10-31 起）**', '**完整性的核法**'),

    # ── 只在投稿稿出现的形态（投稿稿先做过「本综述→本文」「本库→…」，字面与专著版不同；
    #    专著版的对应条目在下一组）
    ('，本文检索范围内（PubMed 与 ClinicalTrials.gov，截至 2026-10-22）未见选择性分子进入关键试验',
     '，截至 2026 年 10 月未见选择性分子进入关键试验', '投稿'),

    # ── 只在专著版出现的形态（投稿稿那一侧已由 `strip_records`、改写清单或「本综述→本文」先改过，
    #    同一处痕迹在两个出口里字面不同）。事实与上面的对应条目一致。
    ('，本综述检索范围内（PubMed 与 ClinicalTrials.gov，截至 2026-10-22）未见选择性分子进入关键试验',
     '，截至 2026 年 10 月未见选择性分子进入关键试验', '专著'),
    # 正文里的四处：投稿稿在 `改写清单.tsv` 那一层改（2.4／4.1／4.7／5.5 各一行），专著版不走改写清单
    ('脚本 `05_codon_share.py`、输出 `表6_密码子占比.csv`，截取日 2026-10-20',
     '数据截取日 2026 年 10 月 20 日，复算脚本见公开复现包', '专著'),
    ('（一手件见 `证据卡/监管公告/2026-10-31_FDA_avutometinib_defactinib_*`）', '', '专著'),
    ('要补齐须另建 ChiCTR 与药监登记的语料，本轮的计数不含它们。',
     '本综述的计数不含 ChiCTR 与中国药监登记的研究。', '专著'),
    ('（批准函与公告存档见 `证据卡/监管公告/`）', '', '专著'),
    # ── 只在复现包用的条目：源文件的表头引用块（投稿稿不印这一块，专著版照印）──────────
    # 表二表头：截取日那句的校样重核要求（投稿稿不印这一块）
    ('**语料与计数以此日为准**；批准类型已按截至 2026-10-31 的一手批准函逐件核过。'
     '获批状态数月之内即会变化，**全表须在校样阶段按最新标签重核**。',
     '**试验登记数据集与计数以此日为准**；批准类型已按截至 2026-10-31 的一手批准函核过。'
     '获批状态数月之内即会变化，各行应对照各监管机构的最新标签阅读。',
     '复现包'),
    # 表三表头：「语料」
    ('或在本综述自建的 ClinicalTrials.gov 语料（REST API v2，2026-10-20 快照）中按研究简称核对一致；'
     '核对不到的写「语料中未检索到」',
     '或在本综述的 ClinicalTrials.gov 试验登记数据集（REST API v2，2026-10-20 快照）中按研究简称核对一致；'
     '核对不到的如实写明', '复现包'),
    ('**三条读数纪律**', '**三条读数规则**', '复现包'),
    # 表一表头（由 01_build_table1.py 生成）：脚本名与数据文件路径、「语料」、校样重核要求
    ('**本表由 `脚本/01_build_table1.py` 生成，请勿手改。**药物集合、最高阶段与试验计数取自图9的数据文件'
     '（`RAS综述示意图/数据/图八_药物泳道.csv`），两边不一致时脚本拒绝出表。',
     '药物集合、最高阶段与试验计数与图9 同源。', '复现包'),
    ('为该药在本综述自建 ClinicalTrials.gov 语料（REST API v2',
     '为该药在本综述的 ClinicalTrials.gov 试验登记数据集（REST API v2', '复现包'),
    ('「最高阶段」为该药在该语料中所达最高阶段。', '「最高阶段」为该药在该数据集中所达最高阶段。', '复现包'),
    ('获批信息见表2，并须在校样阶段按最新标签重核。', '获批信息见表2。', '复现包'),
    # ── 只在复现包用：英文图注与图注里的维护者说明节（投稿稿与专著版都不用英文图注，
    #    也不印「撰写时须注意」「排版注意」这几节；复现包原样分发图注文件，故在这里剥）──
    # 「corpus」是项目内部对自建试验集的叫法，英文表已改作 dataset，图注同口径
    (r're:\bcorpus\b', 'dataset', '复现包'),
    (r're:the\s+ClinicalTrials\.gov dataset assembled for this review',
     'trial registration dataset assembled for this review from ClinicalTrials.gov', '复现包'),
    # 修订日志：重画日期、核法的起算日
    (r're:Prepared 20 October 2026 \(Figures 9 and 12 redrawn as a swimlane map and a matrix\s+heatmap on 30 October 2026\)\.',
     'Prepared 20 October 2026.', '复现包'),
    ('（图9、图12 于 10 月 30 日按泳道图与矩阵热图重画）', '', '复现包'),
    (r're:\*\*How completeness is checked\s+\(from 31 October 2026\)\*\*', '**How completeness is checked**', '复现包'),
    # 扫描脚本要读全文库、不随包分发（export.py 的 SKIP），不能写成「可复跑」
    (r're:Both directions are re-runnable through\s+`RAS综述示意图/脚本/05_scan_direct_ras_candidates\.py`;',
     'Both directions were swept by script against the full-text documents collected for this review (not '
     'distributed, for copyright reasons);', '复现包'),
    # 「the library」＝项目内部的文献库（中文的「本库」）
    ('or if the library holds a published clinical readout',
     'or if a published clinical readout is cited in this review', '复现包'),
    (r're:in all 518 documents of the\s+library;', 'in all 518 full-text documents collected for this review;', '复现包'),
    (r're:the drug tables of three reviews in the\s+library \(', 'the drug tables of three reviews cited in this review (', '复现包'),
    ('because the library papers predate the approval', 'because the cited papers predate the approval', '复现包'),
    ('本综述自建的 ClinicalTrials.gov 语料', '本综述的 ClinicalTrials.gov 试验登记数据集', '复现包'),
    # 写给作者自己的说明节：英文 Notes 与中文「撰写时须注意」（到文件末尾），以及图11 的「排版注意」
    (r're:\n---\n\n## Notes for the figure captions in the final manuscript\n[\s\S]*?(?=\n---\n|\Z)', '', '复现包'),
    (r're:\n---\n\n## 撰写时须注意（对应英文版 Notes）\n[\s\S]*\Z', '\n', '复现包'),
    (r're:\n### 排版注意\n(?:- [^\n]*\n?)+', '\n', '复现包'),
    # 图11 图注头：中英两版的「哪份投稿、哪份只供校对」是工作说明
    (r're:Nature-style legends\. English version is what goes to the journal; the Chinese\s+version below is a working translation for proof-reading only and must not be\s+submitted\.',
     'Nature-style legends, with a Chinese translation below.', '复现包'),
    ('# 中文对照（仅供校对，不用于投稿）', '# 中文对照', '复现包'),
    # 结构图注末的那一节讲的是署名与引用要求（PDB、AlphaFold、cBioPortal），对复用者有用，留；
    # 只把「给定稿稿件」的标题改中性。示意图那一节（稿件内部的一致性要求）上面已整节剥掉。
    ('## Notes for the figure captions in the final manuscript', '## Notes on attribution and methods', '复现包'),
    ('## 定稿图注时的注意事项', '## 引用与方法说明', '复现包'),
    ('校样阶段若决定补全，须按正常流程取证据卡、核逐字引文，再回填本表。', '', '复现包'),
    # 中文对照图注的抬头：「投稿用哪份」是工作说明
    ('本文件是 `Figure_legends.md` 的逐条中译，**仅供对照与讨论，投稿时请用英文版**；',
     '本文件是 `Figure_legends.md` 的逐条中译；', '复现包'),
    ('与 `Figure_legends.md` 逐段对应，供撰写与核对时参照；**正式投稿仍以英文版为准**，中文版不随稿提交。',
     '与 `Figure_legends.md` 逐段对应。', '复现包'),
)


# 复现包剥的是源文件原样的文本，故标「专著」的条目（源文件写法）也用；另有只属复现包的
# 条目（标「复现包」）：表头引用块（投稿稿整块不印、专著版保留）与指向整段剥离附注的指针
# （专著版不剥那几段，指针仍有效）。
_USES = {'投稿': ('投稿',), '专著': ('专著',), '复现包': ('专著', '复现包')}


def trace_rules(exit_):
    use = _USES[exit_]
    return tuple(e[:2] for e in TRACE if len(e) < 3 or e[2] in use)


def strip_traces(doc, exit_='专著'):
    """按 TRACE 剥内部痕迹；返回 (新文本, 落空的条目)。"""
    miss = []
    for a, b in trace_rules(exit_):
        if a.startswith('re:'):
            if not re.search(a[3:], doc):
                miss.append(a)
            doc = re.sub(a[3:], b, doc)
            continue
        if a not in doc:
            miss.append(a)
        doc = doc.replace(a, b)
    return doc, miss



# ── 整段剥离 ─────────────────────────────────────────────────────────────────
# 图注与表注里**整段都是裁定记录**的那种：带引文与数字，逐句规则（上表、投稿稿的
# `strip_records`）按设计不碰它们。这里按段首逐条点名、整段剥掉。投稿稿要求每条都命中；
# 专著版不剥（保留全部附注与原编号）；复现包剥，并随后重排表注号。
DROP_PARA = (
)


def drop_head(block):
    """该段若以某条 DROP_PARA 开头，返回那一条；否则 None。"""
    for p in DROP_PARA:
        if block.startswith(p):
            return p
    return None


def drop_paras(doc):
    """按段（空行分隔）剥掉 DROP_PARA 点名的整段；返回 (新文本, 命中的段首集合)。"""
    out, hit = [], set()
    for b in doc.split('\n\n'):
        h = drop_head(b.strip())
        if h:
            hit.add(h)
            continue
        out.append(b)
    return '\n\n'.join(out), hit


# ── 表注重排 ─────────────────────────────────────────────────────────────────
# 为什么要机器做：表注在源文件里是手写编号（`**五、…**`），剥掉几条整段之后编号断档。
# 早先靠人工补号只补了一半，留下两处**静默错指**（「见表2 附注六」指的那条已被顺位改号；
# 「见表2 附注四」指的那条整段剥掉了）。现在按「谁在前谁在先」整表重排，并改掉全部
# 「附注X」指向；指向已剥离的附注一律记为坏指向，由调用方报必改。
# 两种输出形态：
#   * '投稿'：表注改成 `**表2 注5.　…**`（每条自带表号；表注与表内分组标题 `**一、…**`
#     在投稿稿里原先长得一模一样，读者分不出），指向写 `表2 注5`；
#   * '源'：保留源文件的中文序号 `**五、…**` 与 `表2 附注五` 的写法，只改号（复现包用）。
# 两种文本的结构也不同：投稿稿里表内标题已降成粗体段落、`**表N附注**` 是表注区抬头，
# 下一个 `#`–`###` 标题（正文的章节）结束辖区；源文件里 `## 表N附注` 是抬头，
# `## 一、…` 是表内分组，只有 `# ` 一级标题（下一张表）才结束辖区。
CN_NUM = '一二三四五六七八九十'
NOTE_HEAD = re.compile(r'^\*\*([' + CN_NUM + r']+(?:之一)?)、')
NOTE_REF = re.compile(r'(?:(表\s*)([0-9' + CN_NUM + r'])(\s*))?附注([' + CN_NUM + r']+(?:之一)?)')
NOTE_SEC = re.compile(r'^(?:\*\*表\s*(\d+)\s*附注\*\*|##\s*表\s*(\d+)\s*附注)$')
TAB_CAP = re.compile(r'^(?:\*\*|#\s+)表\s*(\d+)[　 ]')
TAB_NUM = {'一': '1', '二': '2', '三': '3'}
# 「附注三、十」这种连写里，顿号后的号不带「附注」二字，NOTE_REF 认不出、会被静默漏改；
# 一律当坏指向报出来，改写成「附注三与附注十」。
NOTE_CHAIN = re.compile(r'附注[' + CN_NUM + r']+(?:之一)?[、，,][' + CN_NUM + r']+(?![' + CN_NUM + r'])')


def _cn(k):
    return CN_NUM[k - 1] if k <= 10 else str(k)


def _scan(blocks, style):
    """逐段标出表注区（tab）与表的辖区（scope），并收集各表的附注顺序。"""
    tab, scope, owner, area, order = None, None, [], [], {}
    for b in blocks:
        s = b.strip()
        m = NOTE_SEC.match(s)
        if m:
            tab = scope = m.group(1) or m.group(2)
        elif TAB_CAP.match(s):
            tab, scope = None, TAB_CAP.match(s).group(1)
        elif style == '投稿' and re.match(r'^#{1,3}\s', s):
            tab = scope = None
        elif style == '源' and re.match(r'^#{1,6}\s', s):
            tab = None                      # 表内分组标题：离开表注区，但仍在本表辖区
        owner.append(tab)
        area.append(scope)
        h = NOTE_HEAD.match(s)
        if h and tab:
            order.setdefault(tab, []).append(h.group(1))
    return owner, area, order


def note_order(doc, style='源'):
    """{表号: [按出现顺序的旧附注号…]}。"""
    return _scan(doc.split('\n\n'), style)[2]


def note_map(order, style='源'):
    """由附注顺序得到 {表号: {旧号: 新号}}。"""
    f = str if style == '投稿' else _cn
    return {t: {old: f(k) for k, old in enumerate(v, 1)} for t, v in order.items()}


def renumber_notes(doc, style='投稿', extmap=None):
    """重排表注编号并改掉指向；返回 (新文本, 改动条数, 坏指向列表)。

    本文里出现的表按本文的附注顺序重排；本文里没有的表（只被指向）查 `extmap`
    （同形态的 {表号: {旧号: 新号}}，复现包里由导出时写下的对照表提供）。
    """
    blocks = doc.split('\n\n')
    owner, area, order = _scan(blocks, style)
    new = dict(extmap or {})
    new.update(note_map(order, style))
    bad, n = [], 0
    for i, b in enumerate(blocks):
        s = b.strip()
        m = NOTE_SEC.match(s)
        if m:
            if style == '投稿':
                blocks[i] = '**表%s　注**' % (m.group(1) or m.group(2))
            continue
        h = NOTE_HEAD.match(s)
        if h and owner[i]:
            k = new[owner[i]][h.group(1)]
            head = ('**表%s 注%s.　' % (owner[i], k)) if style == '投稿' else ('**%s、' % k)
            if head != h.group(0):
                n += 1
            blocks[i] = s.replace(h.group(0), head, 1)

        def ref(m, _i=i):
            t = TAB_NUM.get(m.group(2), m.group(2)) or area[_i]
            got = new.get(t or '', {}).get(m.group(4))
            if got is None:
                bad.append('%s 的「%s」' % (owner[_i] or area[_i] or '?', m.group(0).strip()))
                return m.group(0)
            if style == '投稿':
                return '表%s 注%s' % (t, got)
            pre = (m.group(1) + m.group(2) + m.group(3)) if m.group(2) else ''
            return '%s附注%s' % (pre, got)

        for c in NOTE_CHAIN.findall(blocks[i]):
            bad.append('%s 的「%s」（连写，顿号后的号改不到）' % (owner[i] or area[i] or '?', c))
        fixed = NOTE_REF.sub(ref, blocks[i])
        if fixed != blocks[i]:
            blocks[i] = fixed
            n += 1
    return '\n\n'.join(blocks), n, bad


# ── 1b 段号互指 → 节号互指 ────────────────────────────────────────────────
# 「见 5.2 段三」这种写法是本项目内部的定位方式，期刊体例里没有段号这一级。
# 机械降一级为「见 5.2」，195 处节段互指里的大多数由此解决，不必逐句改写。
# 连写的「5.1 段一、段四」「6.5 段一与段四」整串一起去掉：只去第一个会留下「5.1、段四」
# （投稿稿曾为此在 POLISH 里逐条手补「（见 4.7、段三）」，复现包里又冒出同类一处）。
_SEGNO = r'段[一二三四五六七八九十]+[a-z]?'
SEG = re.compile(r'(?<=\d\.\d) ?' + _SEGNO + r'(?:[、与和及]' + _SEGNO + r')*')


def drop_one_seg(m):
    """删掉段号，但**把节号与后文之间的空格留住**。

    「见 4.2 段二与图六」里的空格属于 `段二`，整段删掉就粘成「4.2与图六」。
    全文曾因此出现 30 处节号紧贴汉字。后文是汉字时补回一个空格，
    是标点或行尾时不补——否则会留下「见 4.2 。」。
    """
    nxt = m.string[m.end():m.end() + 1]
    return ' ' if '一' <= nxt <= '鿿' else ''

SELF = (('本库检索范围内均未见', '目前均未见报道'),
        ('本库检索范围内', '目前'),
        ('本库没有一篇文献', '尚无文献'),
        ('本库没有', '目前尚无'),
        ('本库中没有', '目前尚无'),
        ('本库未见', '目前未见报道'),
        ('本库连', '现有文献连'),
        ('本库里', '现有文献中'),
        ('本库', '现有文献'),
        ('本综述', '本文'))


def drop_seg(txt):
    parts = re.split(r'(“[^”]*”|<sup>.*?</sup>)', txt, flags=re.S)
    for i in range(0, len(parts), 2):
        parts[i] = SEG.sub(drop_one_seg, parts[i])
        for a, b in SELF:
            parts[i] = parts[i].replace(a, b)
    return ''.join(parts)


# ── 复现包：表注对照表 ───────────────────────────────────────────────────────
# 包里的中文表1 由 reproduce.sh 重新生成，生成物里写的是表2 的**旧**附注号；包里的表2 已经
# 重排过，推不回旧号。所以导出时把「旧号→新号」写成一张 tsv 随包分发，重跑时按它改号。
def write_map(path, m):
    with io.open(path, 'w', encoding='utf-8') as f:
        f.write('表\t旧附注号\t新附注号\n')
        for t in sorted(m):
            for old, k in m[t].items():
                f.write('%s\t%s\t%s\n' % (t, old, k))


def read_map(path):
    m = {}
    for i, line in enumerate(io.open(path, encoding='utf-8')):
        if i == 0 or not line.strip():
            continue
        t, old, k = line.rstrip('\n').split('\t')
        m.setdefault(t, {})[old] = k
    return m


def strip_package(texts, extmap=None):
    """复现包一批 md：逐句规则 → 整段剥离 → 段号去除 → 表注重排（各表的新号由这批里的表定出）。

    `texts`：{路径: 文本}。返回 ({路径: 新文本}, 合并后的对照表, 坏指向列表)。
    """
    out, bad = {}, []
    for p, t in texts.items():
        t, _ = strip_traces(t, '复现包')
        t, _ = drop_paras(t)
        out[p] = drop_seg(t)
    m = dict(extmap or {})
    for t in out.values():
        m.update(note_map(note_order(t, '源'), '源'))
    for p, t in out.items():
        out[p], _, b = renumber_notes(t, '源', m)
        bad += ['%s：%s' % (p, x) for x in b]
    return out, m, bad

def main(argv):
    """python3 traces.py [--map 表注重排.tsv] <文件…>：就地剥（复现包用）。"""
    extmap = None
    if argv[:1] == ['--map']:
        extmap = read_map(argv[1])
        argv = argv[2:]
    texts = {p: io.open(p, encoding='utf-8').read() for p in argv}
    out, _, bad = strip_package(texts, extmap)
    for p in argv:
        if out[p] != texts[p]:
            io.open(p, 'w', encoding='utf-8').write(out[p])
        print('  剥内部痕迹%s  %s' % ('（有改动）' if out[p] != texts[p] else '（无改动）', p))
    for b in bad:
        print('  [必改] 附注指向不存在（已剥离？）：%s' % b)
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

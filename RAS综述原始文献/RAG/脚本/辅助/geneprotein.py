#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""基因斜体／蛋白正体：两条出口（投稿初稿、专著版）共用的一套判定。

**为什么要有这个共享模块**：写法判定原先只写在 `RAS综述投稿初稿/脚本/01_build_draft.py` 里，
于是只有投稿初稿加了斜体，**专著版几乎全篇正体**（实测同一句里投稿初稿 `*KRAS*`、
专著版 `KRAS`）。同一篇稿子两个出口写法不一致，这是评审一眼能看出的不专业。
现在判定只有一份，两个 builder 都调它。

判据（四档，自上而下，先命中先用）：
  ① 人工判定表优先——`数据/写法判定_基因.tsv`（判为基因，加斜体）与
     `数据/写法判定_蛋白.tsv`（判为蛋白，正体且不再进待判清单）。人判过的就是判过的，
     启发式不得覆盖它。
  ② 右侧紧跟 `GENE_R`（基因／突变／外显子／缺失…）→ 基因；紧跟 `PROT_R`
     （蛋白／抑制剂／激酶／结合…）→ 蛋白。
  ③ 同一句后文先遇基因词还是蛋白词，按先到者判。
  ④ 都没有 → 按 `DEFAULT` 的**逐符号默认身份**（见下表）；表里没有的才进待判清单。
     KRAS／NRAS／HRAS 等默认基因（斜体），SOS1／SHP2 默认蛋白（正体）。
     语境词永远优先于默认：`KRAS 蛋白`、`EGFR 抑制剂` 仍是正体。

用法（builder 内）：
    from geneprotein import GeneProtein
    gp = GeneProtein()
    text, n = gp.italicise(text, review)
    gp.write_review(review, '基因蛋白写法_复核清单.md')
"""
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '数据')
GENETSV = os.path.join(DATA, '写法判定_基因.tsv')
PROTTSV = os.path.join(DATA, '写法判定_蛋白.tsv')

SYMS = ['KRAS4A', 'KRAS4B', 'KRAS', 'NRAS', 'HRAS', 'MRAS', 'BRAF', 'ARAF', 'CRAF',
        'RAF1', 'EGFR', 'ERBB3', 'HER2', 'MET', 'ALK', 'RET', 'FGFR1', 'FGFR3', 'FLT3',
        'STK11', 'KEAP1', 'TP53', 'SMAD4', 'CDKN2A', 'PIK3CA', 'PTEN', 'ARID1A', 'U2AF1',
        'CDK6', 'LZTR1', 'NF1', 'RASA1', 'SOS1', 'SHP2', 'MAP2K1', 'YAP1', 'MYC', 'RREB1',
        'ZBTB11', 'USP25', 'GPX4', 'TIAM1', 'SHOC2', 'PKN2', 'CYP3A4', 'ELF3',
        'TTF1', 'IRF2', 'HMGB1', 'CXCL3', 'CXCR2', 'MCT4', 'TBK1', 'BRD4', 'PPIA',
        'NQO1', 'SLC7A11', 'HMOX1', 'CCND1', 'RB1', 'ATM', 'ATR', 'MTOR', 'AKT1',
        'MAPK1', 'MAPK3', 'RAC1', 'RIT1', 'RRAS', 'PTPN11', 'CBL', 'JAK2', 'KIT',
        'PDGFRA', 'IDH1', 'IDH2', 'TSC1', 'TSC2', 'VHL', 'APC', 'CTNNB1', 'FBXW7']
# 右侧紧跟这些词 ＝ 基因（斜体）；「突变体」「突变型蛋白」指蛋白，故用否定前瞻排除
GENE_R = r'(?:基因|突变(?!体|型|蛋白)|等位基因|野生型|扩增|缺失|失活|融合|外显子|密码子|' \
         r'共突变|变异|突变谱|启动子|转录本|位点|检测|测序|驱动|状态|阳性|阴性|' \
         r'的命名|的多态|的表达)'
# 左侧紧跟这些词 ＝ 基因（斜体）
GENE_L = r'(?:携带|突变的|野生型|检出)'
PROT_R = r'(?:蛋白|抑制剂|激酶|活性|结合|降解|复合物|信号|通路|磷酸化|单抗|抗体|' \
         r'构象| GTP| GDP)'


def _load(path, want_protein=False):
    out = []
    if not os.path.exists(path):
        return out
    for line in io.open(path, encoding='utf-8'):
        line = line.rstrip('\n')
        if not line or line.startswith('#'):
            continue
        c = (line.split('\t') + ['', ''])[:3]
        if c[0] in ('符号', 'drug'):
            continue
        out.append((c[0], c[1].replace('*', ''), c[2]))
    return out


# 每个符号的**默认身份**：语境判不出时按哪一类写。
# 依据是本文库的用法：KRAS/NRAS/HRAS 等在正文里多数是在说基因与突变（斜体），
# 真正说蛋白时后面几乎都跟着「蛋白／抑制剂／结合／复合物」，由 PROT_R 先一步拦下。
# SOS1 与 SHP2 例外——它们是通路里以蛋白身份出现最多的名字（且 SHP2 并无同名基因
# 写法习惯），故默认正体。这个默认表是**可覆盖**的：右侧语境仍优先。
FORCE_PROTEIN = {'SOS1', 'SHP2', 'KRAS4A', 'KRAS4B'}   # 通路蛋白名与蛋白亚型名
DEFAULT = {}
for _s in SYMS:
    DEFAULT[_s] = 'gene'
for _s in ('SOS1', 'SHP2'):
    DEFAULT[_s] = 'protein'


class GeneProtein:
    def __init__(self):
        self.calls = set(_load(GENETSV))          # 判为基因
        self.protein = set(_load(PROTTSV))        # 判为蛋白

    # ---------- 判定 ----------
    def _call(self, sym, key, left):
        for s, f, lf in self.calls:
            if s != sym:
                continue
            if lf and not left.endswith(lf):
                continue
            if not f:
                return True
            if key == f or key.startswith(f) or f.startswith(key):
                return True
        return False

    def _is_protein_call(self, sym, key, left):
        for s, f, lf in self.protein:
            if s != sym:
                continue
            if lf and not left.endswith(lf):
                continue
            if not f:
                return True
            if key == f or key.startswith(f) or f.startswith(key):
                return True
        return False

    def italicise(self, txt, review, added=None):
        """只加、不减；拿不准的不动，记进 review 交人。返回 (文本, 加了几处)。

        added 给了就顺手记下「加在哪」——闸门要打印出来给人看的那种。
        """
        n = 0
        cur = ''

        def one(m):
            nonlocal n
            left = cur[max(0, m.start() - 18):m.start()]
            sym, rest = m.group(1), m.group(2)
            # 判定表里的片段是**纯文本**；而此处的 rest 可能已被上一轮标了斜体
            # （" 中有效、在 *KRAS* 中失效"）。比对前先去掉星号，否则同一句话
            # 第二次过机时匹配不上，会再判一次——闸门就是这么误报的。
            key = rest.replace('*', '')[:18] or '（句末）'

            if m.group(0).startswith('*'):        # 已经是斜体
                return m.group(0)
            if sym in FORCE_PROTEIN:
                return m.group(0)
            if self._call(sym, key, left):
                n += 1
                if added is not None:
                    added.append('%s｜%s' % (sym, cur[max(0, m.start() - 12):m.start()]))
                return '*%s*' % sym
            if self._is_protein_call(sym, key, left):
                return m.group(0)
            rest_s = rest.lstrip()
            if re.match(PROT_R, rest_s):
                return m.group(0)
            if re.match(GENE_R, rest_s):
                n += 1
                if added is not None:
                    added.append('%s｜%s' % (sym, cur[max(0, m.start() - 12):m.start()]))
                return '*%s*' % sym
            # 第二档只看**并列语境**：符号后面紧跟「与／和／／／、」时，身份要靠同句后半截说。
            # 放宽到任意后文会误伤——实测「SOS1 作为…而非杀死突变细胞」里的「突变」
            # 会把一个蛋白名判成基因。并列之外一律交给第三档（人工表）与第四档（默认身份）。
            coord = re.match(r'\s*(?:[与和或及／/、]|以及|[、,]\s*[A-Z])', rest_s[:6])
            if coord:
                g = re.search(GENE_R, rest_s)
                pr = re.search(PROT_R, rest_s)
                if g and (not pr or g.start() < pr.start()):
                    n += 1
                    if added is not None:
                        added.append('%s｜%s' % (sym, cur[max(0, m.start() - 12):m.start()]))
                    return '*%s*' % sym
                if pr and (not g or pr.start() < g.start()):
                    return m.group(0)
            if DEFAULT.get(sym) == 'gene':
                n += 1
                if added is not None:
                    added.append('%s｜%s' % (sym, cur[max(0, m.start() - 12):m.start()]))
                return '*%s*' % sym
            if DEFAULT.get(sym) == 'protein':
                return m.group(0)
            review.append('%s｜%s' % (sym, key))
            return m.group(0)

        # 右侧语境用前瞻而不是捕获：窗口里的下一个符号不能被 re.sub 跳过
        pat = r'(?<![*A-Za-z])(%s)(?![*A-Za-z0-9])(?=([^。！？]{0,26}))' % '|'.join(SYMS)
        # 以下四处一律不动：① 英文逐字引文与著录上标（那是原文，不能改排版）；
        # ② 图片与链接的地址（`FigS1_KRAS_GDP_structure.png` 里的 KRAS 是文件名）；
        # ③ 行内代码（`command`）；④ 已有的 **粗体** 记号内部照常处理，无需豁免。
        parts = re.split(r'(“[^”]*”|<sup>.*?</sup>|!\[[^\]]*\]\([^)]*\)'
                         r'|\[[^\]]*\]\([^)]*\)|`[^`]*`)', txt, flags=re.S)
        for i, seg in enumerate(parts):
            if i % 2:                       # 引文、上标、链接、行内代码
                # 引号里若是**中文**（本综述自己的转述），照常判定；只有英文逐字引文才不动。
                if seg.startswith('“') and re.search(r'[\u4e00-\u9fa5]', seg):
                    cur = seg
                    parts[i] = re.sub(pat, one, seg)
                continue
            cur = seg
            parts[i] = re.sub(pat, one, seg)
        return ''.join(parts), n

    # ---------- 报告 ----------
    def write_review(self, review, path, title='基因／蛋白写法：**尚未判定**的处'):
        seen = {}
        for r in review:
            seen[r] = seen.get(r, 0) + 1
        lines = ['# %s' % title, '',
                 '> 判定分四档：① 人工表（`数据/写法判定_基因.tsv`／`_蛋白.tsv`）优先；'
                 '② 右接「基因／突变／外显子…」→ 基因，右接「蛋白／抑制剂／结合…」→ 蛋白；'
                 '③ 同句后文先遇哪类词按哪类；④ 都没有 → 默认蛋白正体，记在下面。',
                 '> **默认不加斜体**，故漏判只少一个斜体，不会把蛋白错标成基因。',
                 '> 下面这些判完了，把片段抄进 `数据/写法判定_基因.tsv`（基因）或 '
                 '`数据/写法判定_蛋白.tsv`（蛋白）即可。', '']
        for r, c in sorted(seen.items(), key=lambda kv: -kv[1]):
            lines.append('- %s　×%d' % (r, c))
        if not seen:
            lines.append('（无）')
        io.open(path, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
        return len(seen), sum(seen.values())

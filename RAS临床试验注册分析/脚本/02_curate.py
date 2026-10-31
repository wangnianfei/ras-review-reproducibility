#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Curate the raw ClinicalTrials.gov harvest into analysis-ready tables.

Decision rules are deliberately explicit so that every count in the manuscript
can be re-derived or challenged:

  keep   = interventional AND (a RAS gene token OR a RAS-directed agent appears
           in title / official title / brief summary / condition / intervention)
           AND the condition list is oncological
           AND phase is EARLY_PHASE1 / PHASE1 / PHASE2 / PHASE3 (or a combination)
  tier   = RAS-targeted            intervention is a RAS-directed agent
           RAS-regulator-targeted  SOS1 / SHP2 / farnesyl-transferase strategies
           RAS-biomarker-selected  RAS genotype used for eligibility/stratification
           RAS-mentioned           RAS appears but is neither target nor selector
  excluded records are written out with the reason, never silently dropped.

Usage: python3 02_curate.py <root>
"""
import csv, json, os, re, sys
from collections import Counter, defaultdict

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, '数据')
RAW = os.path.join(DATA, 'raw')

with open(os.path.join(RAW, 'studies_raw.json')) as f:
    BLOB = json.load(f)
STUDIES = BLOB['studies']
PROV = BLOB['provenance']

# ------------------------------------------------------------------ vocabulary
# "RAS" alone is ambiguous: in cardiology/nephrology trials it is the
# renin-angiotensin system. Accept it only when a gene letter is attached or
# when the sentence puts it in an oncogene/signalling context.
GENE_RE = re.compile(r'\b(K-?RAS|N-?RAS|H-?RAS)\b', re.I)
RAS_CTX_RE = re.compile(
    r'\bRAS\b[\s-]{0,3}(mutat|mutant|wild.?type|wt\b|status|genotyp|pathway|'
    r'inhibitor|GTPase|oncogene|signal|/MAPK|/RAF|/MEK|protein|G12|G13|Q61|'
    r'A146|K117|family|isoform|driven|dependen)'
    r'|(onco|proto.?onco|mutant|mutated|wild.?type|activat\w+|pan.?|anti.?)[\s-]{0,3}\bRAS\b'
    r'|\bRAS\b[\s-]{0,3}\(.{0,20}(KRAS|NRAS|HRAS)', re.I)
RENIN_RE = re.compile(r'renin.?angiotensin|angiotensin.converting|\bACE ?I+\b|'
                      r'losartan|valsartan|candesartan|telmisartan|enalapril|'
                      r'lisinopril|spironolacton|aliskiren', re.I)

G12C = ['sotorasib', 'amg 510', 'amg510', 'lumakras', 'adagrasib', 'mrtx849',
        'krazati', 'divarasib', 'gdc-6036', 'gdc6036', 'olomorasib', 'ly3537982',
        'glecirasib', 'jab-21822', 'jab21822', 'fulzerasib', 'ibi351',
        'garsorasib', 'd-1553', 'd1553', 'opnurasib', 'jdq443', 'mk-1084',
        'mk1084', 'hrs-4642', 'bi 1823911', 'bi1823911', 'jmkx1899', 'gfh925',
        'yl-15293', 'sy-5933', 'ja107', 'bpi-421286', 'lzm005', 'kras g12c inhibitor']
G12D = ['mrtx1133', 'asp3082', 'rmc-9805', 'zoldonrasib', 'incb161734',
        'eras-4001', 'qtx3034', 'qtx3046', 'tsn1611', 'gfh375', 'vs-7375',
        'hrs-4642', 'kras g12d inhibitor', 'asp2453']
PANRAS = ['rmc-6236', 'daraxonrasib', 'rmc-6291', 'elironrasib', 'adt-007',
          'bi 2865', 'pan-kras', 'pan-ras', 'bbo-8520', 'ras(on)', 'ras-on',
          'multi-selective ras']
VACCINE = ['eli-002', 'mrna-5671', 'kras vaccine', 'ras peptide vaccine',
           'mutant kras vaccine', 'tg01', 'gi-4000', 'ras peptide']
FTI = ['tipifarnib', 'lonafarnib', 'salirasib', 'zarnestra', 'farnesyltransferase',
       'farnesyl transferase', 'farnesyl-transferase']
SOS1 = ['bi 1701963', 'bi1701963', 'mrtx0902', 'sos1 inhibitor', 'bay-293']
SHP2 = ['tno155', 'rmc-4630', 'jab-3312', 'rly-1971', 'migoprotafib', 'eras-601',
        'shp2 inhibitor', 'shp099', 'ic-fak', 'bbp-398', 'hbi-2376', 'etx-636']

RAS_DIRECT = G12C + G12D + PANRAS + VACCINE
RAS_REG = SOS1 + SHP2 + FTI

# New RAS inhibitors enter the registry faster than any hand-kept name list, so
# two generic rules back the list up: the INN stem -rasib is reserved for KRAS
# inhibitors, and an intervention that spells out the gene plus a modality is
# RAS-directed whatever its code name.
RASIB_RE = re.compile(r'\b\w*rasib\b', re.I)
MODALITY_RE = re.compile(
    r'\b(K|N|H)?RAS\b[^|]{0,40}(inhibitor|degrader|protac|molecular glue|'
    r'vaccine|sirna|mrna|antisense|binder|blocker|tcr|cell therapy)'
    r'|(inhibitor|degrader|vaccine|tcr)[^|]{0,40}\b(K|N|H)?RAS\b', re.I)
ALLELE_RE = [('KRAS G12C', r'G12C'), ('KRAS G12D/other codon 12-13', r'G12D|G12V|G12R|G13D|G12A|G12S'),
             ('KRAS Q61 / other alleles', r'Q61|A146|K117'),
             ('pan-RAS / multi-selective RAS(ON)', r'pan.?RAS|pan.?KRAS|multi.?selective|RAS\(ON\)|RAS.?ON\b')]

ONCO_RE = re.compile(
    r'cancer|carcinom|neoplas|tumor|tumour|malignan|leukaem|leukem|lymphom|'
    r'myelom|melanom|sarcom|gliom|glioblast|blastom|adenocarcinom|mesotheliom|'
    r'cholangiocarcinom|nsclc|sclc|crc\b|mcrc|pdac|aml\b|cml\b|all\b|cmml|'
    r'myelodysplas|myeloprolifer|histiocyt|oncolog|metastat|solid tumo|'
    r'carcinoid|chordom|thymom|teratom|seminom|germ cell|mycosis fungoides|'
    r'gastrointestinal stromal|gist\b|multiple myeloma|plasma cell|'
    r'squamous cell|hepatocellular|cholangio|pheochromocyt|paragangliom|'
    r'neuroendocrin|wilms|retinoblastom|medulloblastom|neuroblastom', re.I)
NONONCO_RE = re.compile(
    r'progeri|hutchinson-gilford|hepatitis d|noonan|costello syndrome|'
    r'cardiofaciocutaneous|neurofibromatosis type 1 plexiform|rasopath|'
    r'lymphatic malformation|capillary malformation|arteriovenous malformation|'
    r'healthy volunteer|psoriasis|covid', re.I)

PHASE_OK = {'EARLY_PHASE1', 'PHASE1', 'PHASE2', 'PHASE3'}

TARGETLIST = [('KRAS G12C', G12C), ('KRAS G12D/other codon 12-13', G12D),
              ('pan-RAS / multi-selective RAS(ON)', PANRAS),
              ('RAS vaccine / immunotherapy', VACCINE),
              ('farnesyl-transferase (HRAS)', FTI),
              ('SOS1', SOS1), ('SHP2', SHP2)]

TUMOUR_BUCKETS = [
    ('Non-small cell lung cancer', r'non.?small cell|nsclc|lung adenocarcinom'),
    ('Small cell lung cancer', r'(?<!non-)(?<!non )small cell lung|\bsclc\b'),
    ('Colorectal cancer', r'colorect|colon cancer|rectal cancer|mcrc|crc\b'),
    ('Pancreatic cancer', r'pancrea'),
    ('Biliary tract / hepatobiliary', r'cholangio|biliary|gallbladder|hepatocellular|liver cancer'),
    ('Melanoma / skin', r'melanom|cutaneous squamous|basal cell|skin cancer'),
    ('Head and neck', r'head and neck|hnscc|oral cavity|nasopharyn|laryng|salivary|thyroid'),
    ('Haematologic malignancy', r'leukaem|leukem|lymphom|myelom|myelodysplas|myeloprolifer|cmml|aml\b|cml\b|histiocyt'),
    ('Gynaecologic', r'ovarian|endometri|cervic|uterin'),
    ('Gastro-oesophageal', r'gastric|oesophag|esophag|stomach|gastroesophageal'),
    ('Genitourinary', r'prostate|bladder|urothelial|renal cell|kidney cancer|testic'),
    ('Breast', r'breast'),
    ('CNS', r'gliom|glioblast|medulloblast|brain|cns\b'),
    ('Advanced solid tumours (histology-agnostic)', r'solid tumo|advanced cancer|metastatic cancer|neoplasms?$'),
]


def txt(s):
    p = s['protocolSection']
    idm = p.get('identificationModule', {})
    bits = [idm.get('briefTitle', ''), idm.get('officialTitle', ''),
            idm.get('acronym', '') or '',
            p.get('descriptionModule', {}).get('briefSummary', '')]
    bits += p.get('conditionsModule', {}).get('conditions', [])
    bits += [i.get('name', '') for i in
             p.get('armsInterventionsModule', {}).get('interventions', [])]
    bits += [o for i in p.get('armsInterventionsModule', {}).get('interventions', [])
             for o in i.get('otherNames', []) or []]
    bits += p.get('conditionsModule', {}).get('keywords', []) or []
    bits.append(p.get('eligibilityModule', {}).get('eligibilityCriteria', '') or '')
    om = p.get('outcomesModule', {}) or {}
    bits += [o.get('measure', '') for o in (om.get('primaryOutcomes') or [])]
    bits += [o.get('measure', '') for o in (om.get('secondaryOutcomes') or [])]
    return ' | '.join(bits)


def interv_text(s):
    p = s['protocolSection'].get('armsInterventionsModule', {})
    names = []
    for i in p.get('interventions', []):
        names.append(i.get('name', ''))
        names += i.get('otherNames', []) or []
    return ' | '.join(names)


def any_in(hay, needles):
    return [n for n in needles if n in hay]


rows, excluded = [], []
for nid, s in STUDIES.items():
    p = s['protocolSection']
    idm = p.get('identificationModule', {})
    stm = p.get('statusModule', {})
    dsm = p.get('designModule', {})
    spm = p.get('sponsorCollaboratorsModule', {})
    conds = p.get('conditionsModule', {}).get('conditions', [])
    locs = p.get('contactsLocationsModule', {}).get('locations', []) or []

    T = txt(s)
    tl, il = T.lower(), interv_text(s).lower()
    phases = dsm.get('phases', []) or ['NA']
    phase_lbl = '/'.join(x.replace('EARLY_PHASE1', 'Early Phase 1')
                         .replace('PHASE', 'Phase ') for x in phases)

    direct = (any_in(il, RAS_DIRECT) or any_in(tl, RAS_DIRECT)
              or bool(RASIB_RE.search(il)) or bool(MODALITY_RE.search(il))
              or bool(RASIB_RE.search(tl)))
    reg = any_in(il, RAS_REG) or any_in(tl, RAS_REG)
    gene = bool(GENE_RE.search(T)) or (bool(RAS_CTX_RE.search(T)) and
                                       not RENIN_RE.search(T))

    def drop(reason):
        excluded.append({'nct_id': nid, 'brief_title': idm.get('briefTitle', ''),
                         'phase': phase_lbl, 'conditions': '; '.join(conds),
                         'exclusion_reason': reason})

    if not (gene or direct or reg):
        drop('RAS not referenced as a gene/target (e.g. renin-angiotensin system, '
             'or RAS appears in neither title, summary, condition, keyword, '
             'eligibility criteria nor outcome measure)')
        continue
    onco = bool(ONCO_RE.search(' | '.join(conds))) or bool(ONCO_RE.search(T))
    if not onco:
        drop('condition is not oncological')
        continue
    if NONONCO_RE.search(' | '.join(conds)) and not ONCO_RE.search(' | '.join(conds)):
        drop('non-malignant RASopathy / non-oncology indication')
        continue
    if not set(phases) & PHASE_OK:
        drop('phase outside I-III (%s)' % phase_lbl)
        continue

    # ---- target class
    tgs = [lbl for lbl, lst in TARGETLIST if any_in(il, lst) or any_in(tl, lst)]
    if direct and not tgs:                      # agent not in the name list
        tgs = [lbl for lbl, rx in ALLELE_RE if re.search(rx, T, re.I)]
        if not tgs:
            tgs = ['RAS-directed, allele not specified']
    if direct:
        tier = 'RAS-targeted'
    elif reg:
        tier = 'RAS-regulator-targeted'
    elif re.search(r'\b(K|N|H)?RAS\b[^|]{0,60}(mutat|wild.?type|wt\b|status|'
                   r'genotyp|amplif|G12|G13|Q61|A146|K117)', T, re.I) or \
            re.search(r'(mutat|wild.?type|status)[^|]{0,30}\b(K|N|H)?RAS\b', T, re.I):
        tier = 'RAS-biomarker-selected'
    else:
        tier = 'RAS-mentioned'

    # ---- tumour buckets
    buckets = [b for b, rx in TUMOUR_BUCKETS
               if re.search(rx, ' | '.join(conds), re.I)]
    if not buckets:
        buckets = ['Other / unspecified']

    countries = sorted({l.get('country', '') for l in locs if l.get('country')})
    csite = Counter(l.get('country', '') for l in locs if l.get('country'))

    rows.append({
        'nct_id': nid,
        'brief_title': idm.get('briefTitle', ''),
        'acronym': idm.get('acronym', '') or '',
        'org_study_id': (idm.get('orgStudyIdInfo') or {}).get('id', ''),
        'phase': phase_lbl,
        'phase_group': ('Phase 3' if 'PHASE3' in phases else
                        'Phase 2' if 'PHASE2' in phases else
                        'Phase 1' if 'PHASE1' in phases else 'Early Phase 1'),
        'overall_status': stm.get('overallStatus', ''),
        'status_group': ('Ongoing' if stm.get('overallStatus') in
                         ('RECRUITING', 'ACTIVE_NOT_RECRUITING', 'ENROLLING_BY_INVITATION') else
                         'Not yet recruiting' if stm.get('overallStatus') == 'NOT_YET_RECRUITING' else
                         'Completed' if stm.get('overallStatus') == 'COMPLETED' else
                         'Stopped early' if stm.get('overallStatus') in
                         ('TERMINATED', 'WITHDRAWN', 'SUSPENDED') else 'Other/unknown'),
        'why_stopped': stm.get('whyStopped', '') or '',
        'start_date': (stm.get('startDateStruct') or {}).get('date', ''),
        'primary_completion_date': (stm.get('primaryCompletionDateStruct') or {}).get('date', ''),
        'completion_date': (stm.get('completionDateStruct') or {}).get('date', ''),
        'first_posted': (stm.get('studyFirstPostDateStruct') or {}).get('date', ''),
        'first_posted_year': ((stm.get('studyFirstPostDateStruct') or {}).get('date', '') or '')[:4],
        'last_update_posted': (stm.get('lastUpdatePostDateStruct') or {}).get('date', ''),
        'has_results_posted': 'yes' if (stm.get('resultsFirstPostDateStruct') or {}).get('date') else 'no',
        'enrollment': (dsm.get('enrollmentInfo') or {}).get('count', ''),
        'enrollment_type': (dsm.get('enrollmentInfo') or {}).get('type', ''),
        'allocation': (dsm.get('designInfo') or {}).get('allocation', ''),
        'primary_purpose': (dsm.get('designInfo') or {}).get('primaryPurpose', ''),
        'lead_sponsor': (spm.get('leadSponsor') or {}).get('name', ''),
        'lead_sponsor_class': (spm.get('leadSponsor') or {}).get('class', ''),
        'collaborators': '; '.join(c.get('name', '') for c in spm.get('collaborators', []) or []),
        'conditions': '; '.join(conds),
        'tumour_group': '; '.join(buckets),
        'interventions': interv_text(s),
        'ras_tier': tier,
        'target_class': '; '.join(tgs) if tgs else ('Not RAS-directed' if tier in
                                                    ('RAS-biomarker-selected', 'RAS-mentioned') else 'Other RAS-directed'),
        'n_sites': len(locs),
        'n_countries': len(countries),
        'is_multinational': 'yes' if len(countries) > 1 else 'no',
        'countries': '; '.join(countries),
        'sites_per_country': '; '.join('%s:%d' % (k, v) for k, v in csite.most_common()),
        'found_via': '; '.join(PROV.get(nid, [])),
        'url': 'https://clinicaltrials.gov/study/' + nid,
    })

rows.sort(key=lambda r: (r['first_posted'] or '', r['nct_id']), reverse=True)


def write(name, data, cols=None):
    path = os.path.join(DATA, name)
    cols = cols or list(data[0].keys())
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(data)
    print('  %-34s %5d rows' % (name, len(data)))


print('curated %d trials, excluded %d' % (len(rows), len(excluded)))
write('表1_临床试验总表.csv', rows)
write('表2_排除记录与原因.csv', excluded)

# ---------------------------------------------------------- country aggregate
cy = defaultdict(lambda: {'n_trials': 0, 'n_sites': 0, 'Phase 1': 0, 'Phase 2': 0,
                          'Phase 3': 0, 'Early Phase 1': 0, 'n_ras_targeted': 0,
                          'n_ongoing': 0, 'n_industry': 0})
for r in rows:
    per = dict(x.split(':') for x in r['sites_per_country'].split('; ') if x)
    for c in [x for x in r['countries'].split('; ') if x]:
        d = cy[c]
        d['n_trials'] += 1
        d['n_sites'] += int(per.get(c, 0))
        d[r['phase_group']] += 1
        d['n_ras_targeted'] += 1 if r['ras_tier'] == 'RAS-targeted' else 0
        d['n_ongoing'] += 1 if r['status_group'] == 'Ongoing' else 0
        d['n_industry'] += 1 if r['lead_sponsor_class'] == 'INDUSTRY' else 0
country_rows = [dict(country=c, **v) for c, v in
                sorted(cy.items(), key=lambda kv: -kv[1]['n_trials'])]
write('表3_国家分布.csv', country_rows)

# country x year, for the trend panel
yrs = sorted({r['first_posted_year'] for r in rows if r['first_posted_year']})
m = defaultdict(Counter)
for r in rows:
    for c in [x for x in r['countries'].split('; ') if x]:
        m[c][r['first_posted_year']] += 1
write('表4_国家×首次登记年份.csv',
      [dict(country=c, **{y: m[c].get(y, 0) for y in yrs}) for c in
       sorted(m, key=lambda c: -sum(m[c].values()))],
      ['country'] + yrs)


def tally(name, keyfn, label='category'):
    cnt = Counter()
    for r in rows:
        k = keyfn(r)
        for kk in (k if isinstance(k, list) else [k]):
            cnt[kk] += 1
    write(name, [{label: k, 'n_trials': v} for k, v in cnt.most_common()],
          [label, 'n_trials'])
    return cnt


tally('表5_分期分布.csv', lambda r: r['phase'], 'phase')
tally('表6_状态分布.csv', lambda r: r['overall_status'], 'overall_status')
tally('表7_申办方类别.csv', lambda r: r['lead_sponsor_class'], 'lead_sponsor_class')
tally('表8_靶点类别.csv', lambda r: [x for x in r['target_class'].split('; ')], 'target_class')
tally('表9_瘤种分布.csv', lambda r: [x for x in r['tumour_group'].split('; ')], 'tumour_group')
tally('表10_RAS相关层级.csv', lambda r: r['ras_tier'], 'ras_tier')
tally('表11_首次登记年份.csv', lambda r: r['first_posted_year'] or 'unknown', 'year')
sp = tally('表12_牵头申办方.csv', lambda r: r['lead_sponsor'], 'lead_sponsor')

summary = {
    'fetched': BLOB['fetched'],
    'source': 'ClinicalTrials.gov REST API v2',
    'raw_interventional_union': len(STUDIES),
    'curated_trials': len(rows),
    'excluded': len(excluded),
    'excluded_reasons': dict(Counter(e['exclusion_reason'] for e in excluded)),
    'by_tier': dict(Counter(r['ras_tier'] for r in rows)),
    'by_phase_group': dict(Counter(r['phase_group'] for r in rows)),
    'by_status_group': dict(Counter(r['status_group'] for r in rows)),
    'by_sponsor_class': dict(Counter(r['lead_sponsor_class'] for r in rows)),
    'trials_with_no_location': sum(1 for r in rows if r['n_countries'] == 0),
    'multinational_trials': sum(1 for r in rows if r['is_multinational'] == 'yes'),
    'median_sites': sorted(int(r['n_sites']) for r in rows)[len(rows) // 2],
    'total_site_records': sum(int(r['n_sites']) for r in rows),
    'countries_covered': len(cy),
    'top10_countries': [(c, v['n_trials']) for c, v in
                        sorted(cy.items(), key=lambda kv: -kv[1]['n_trials'])[:10]],
    'top10_sponsors': sp.most_common(10),
    'enrollment_total_reported': sum(int(r['enrollment']) for r in rows if str(r['enrollment']).isdigit()),
}
with open(os.path.join(DATA, 'summary.json'), 'w') as f:
    json.dump(summary, f, ensure_ascii=False, indent=1)
print(json.dumps(summary, ensure_ascii=False, indent=1)[:2600])

"""Extract all published tables from the pinned CC BY 4.0 arXiv HTML.

Run with the bundled Python (lxml) and a local HTML path. No network or model run.
"""
from pathlib import Path
from copy import deepcopy
import hashlib
import json
import re
import sys
from lxml import html

ROOT=Path(__file__).resolve().parents[1]


def clean(element):
    element=deepcopy(element)
    for math in element.xpath('.//math'):
        span=html.Element('span')
        span.text=math.get('alttext','')
        span.tail=math.tail
        math.getparent().replace(math,span)
    text=' '.join(element.itertext())
    text=text.replace(r'\pm','±').replace(r'\mathcal{D}','D')
    text=re.sub(r'\\(?:bm|mathbf|textbf|underline|mathrm|text)\{([^{}]*)\}',r'\1',text)
    text=re.sub(r'\s+',' ',text).strip()
    text=re.sub(r'(?<=[A-Za-z/-])\s+(?=\d)','',text)
    text=re.sub(r'(?<=\d)\s+(?=[A-Za-z/])','',text)
    text=text.replace('D (best)','D-Best')
    text=re.sub(r'ParetoFlow\s*\(\s*ours\s*\)','ParetoFlow',text)
    return re.sub(r'MOBO-\s*q\s*ParEGO','MOBO-qParEGO',text)


def extract(path):
    content=path.read_bytes()
    document=html.fromstring(content)
    tables=[]
    for figure in document.xpath('//figure[contains(@class,"ltx_table")]'):
        rows=[[clean(c) for c in row.xpath('./th|./td')] for row in figure.xpath('.//tr')]
        rows=[r for r in rows if r]
        width=len(rows[0])
        assert all(len(r)==width for r in rows),(figure.get('id'),[len(r) for r in rows])
        tables.append({'id':figure.get('id'),'caption':clean(figure.xpath('./figcaption')[0]),
                       'columns':rows[0],'rows':rows[1:]})
    assert len(tables)==23
    result={'title':'ParetoFlow: Guided Flows in Multi-Objective Optimization',
            'authors':['Ye Yuan','Can Chen','Christopher Pal','Xue Liu'],
            'version':'arXiv:2412.03718v2 · 20 February 2025',
            'url':'https://arxiv.org/html/2412.03718v2','license':'CC BY 4.0',
            'source_sha256':hashlib.sha256(content).hexdigest(),
            'transformation':'Math markup normalized; numeric values and missing-value markers preserved. No values digitized from figures.',
            'tables':tables}
    target=ROOT/'data/paper_tables.json'
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Extracted {len(tables)} tables to {target}')
    for table in tables:
        print(table['id'],len(table['rows']),len(table['columns']),table['columns'])


if __name__=='__main__':
    extract(Path(sys.argv[1]))

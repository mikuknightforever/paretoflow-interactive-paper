"""Published evidence, kept separate from the locally computed sample."""
import json
import re
from pathlib import Path

PAPER=json.loads((Path(__file__).parent/'data/paper_tables.json').read_text(encoding='utf-8'))
TABLES={t['id']:t for t in PAPER['tables']}
METHODS=[r[0] for r in TABLES['S4.T1']['rows']]


def cell(table_id,row,column):
    table=TABLES[table_id]
    # Table 16 abbreviates COMs as COM; keep source text in the library while
    # allowing one consistent comparator choice across percentiles.
    aliases={row,'MM + COM'} if row=='MM + COMs' else {row}
    value=next(r for r in table['rows'] if r[0] in aliases)[table['columns'].index(column)]
    if value=='N/A':
        return None,None,value
    parts=re.fullmatch(r'([\d.]+)(?:\s*±\s*([\d.]+))?',value)
    if not parts:
        raise ValueError(value)
    return float(parts[1]),float(parts[2]) if parts[2] else None,value


TASKS={}
for number,family in [(8,'Synthetic'),(9,'MO-NAS'),(10,'MO-NAS'),(11,'MORL'),(12,'Sci-Design'),(13,'RE')]:
    for task in TABLES[f'A1.T{number}']['columns'][1:]:
        TASKS[task]={'family':family,'100':f'A1.T{number}','50':f'A1.T{number+7}'}


def task_cell(task,percentile,method):
    return cell(TASKS[task][str(percentile)],method,task)

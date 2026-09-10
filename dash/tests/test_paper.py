import csv
import io
import json
from pathlib import Path
import unittest
import numpy as np
from app import server, PAPER_PANELS
from paper_data import PAPER, TABLES, METHODS, TASKS, cell, task_cell
from paper_views import guidance_view, neighbor_view, rank_view, benchmark_view, ablation_view, cost_view, method_view, sorted_source_rows


class PaperTests(unittest.TestCase):
    def test_complete_source_coverage_and_reference_values(self):
        self.assertEqual(len(TABLES),23)
        self.assertEqual(len(TASKS),52)
        self.assertEqual(len(METHODS),22)
        self.assertEqual(PAPER['license'],'CC BY 4.0')
        self.assertEqual(cell('S4.T1','ParetoFlow','All Tasks')[:2],(3.12,3.77))
        self.assertEqual(cell('A1.T14','ParetoFlow','All Tasks')[:2],(4.85,3.97))
        self.assertEqual(task_cell('ZDT2','100','ParetoFlow')[:2],(6.79,.16))
        self.assertEqual(task_cell('ZDT6','100','E2E')[:2],(4.92,0))
        count=0
        for task in TASKS:
            for percentile in ['100','50']:
                for method in METHODS:
                    mean,spread,text=task_cell(task,percentile,method)
                    self.assertTrue(mean is None or np.isfinite(mean))
                    self.assertTrue(spread is None or spread>=0)
                    if mean is None:self.assertEqual(text,'N/A')
                    count+=1
        self.assertEqual(count,2288)

    def test_paper_and_local_evidence_are_separate(self):
        for tid in TABLES:
            table=TABLES[tid]
            self.assertTrue(all(len(r)==len(table['columns']) for r in table['rows']))
        fig,detail,_=benchmark_view('ZDT2','100','MM')
        self.assertAlmostEqual(fig.data[0].x[0],6.79)
        self.assertNotAlmostEqual(fig.data[0].x[0],6.7225611)
        self.assertIn('6.79',detail)
        # Unreported combinations remain absent bars, not fabricated zeros.
        absent=next((t,p,m) for t in TASKS for p in ['100','50'] for m in METHODS if task_cell(t,p,m)[0] is None)
        fig,detail,_=benchmark_view(*absent)
        self.assertIn('N/A',detail)
        self.assertNotIn(absent[2],fig.data[0].y)

    def test_geometric_filter_and_neighbor_selection(self):
        unrestricted=guidance_view('nonconvex',.5,[])[0].data[-1]
        restricted=guidance_view('nonconvex',.5,['on'])[0].data[-1]
        self.assertIn(unrestricted.x[0],(0,1))
        self.assertTrue(.4<restricted.x[0]<.8)
        for direction in [0,4,8]:
            for k in [1,3,5]:
                pool,detail=neighbor_view(direction,k,'pool')
                self.assertEqual(len(pool.data[1].x),k*3)
                chosen,_=neighbor_view(direction,k,'select')
                for trace in chosen.data:
                    self.assertTrue(np.isfinite(trace.x).all())
        for step in range(7):
            self.assertEqual(len(method_view(step)),2)

    def test_result_variants_and_cost_components(self):
        for percentile in ['100','50']:
            fig,_,_=rank_view(percentile,'MM')
            self.assertEqual(len(fig.data[0].x),6)
        for tid in ['S4.T2','A1.T3','A1.T4','A1.T21','A1.T22','A1.T23']:
            for task in TABLES[tid]['columns'][1:]:
                fig,_,_=ablation_view(task,tid)
                self.assertEqual(len(fig.data[0].x),len(TABLES[tid]['rows']))
        for mode,tid in [('representative','A1.T5'),('scaling','A1.T7')]:
            fig,_,_=cost_view(mode)
            self.assertEqual(len(fig.data),3)
            totals=np.sum([trace.y for trace in fig.data],axis=0)
            totalrow=next(r[0] for r in TABLES[tid]['rows'] if r[0].lower().startswith('overall'))
            expected=[cell(tid,totalrow,t)[0] for t in TABLES[tid]['columns'][1:]]
            np.testing.assert_allclose(totals,expected,atol=.011)

    def test_routes_callbacks_and_downloads(self):
        c=server.test_client()
        for name in PAPER_PANELS:
            for suffix in ['','_dash-layout','_dash-dependencies','assets/paper.css']:
                response=c.get('/'+name+'/'+suffix)
                self.assertEqual(response.status_code,200)
                response.close()
        for tid,table in TABLES.items():
            response=c.get('/paper-table/'+tid+'.csv')
            rows=list(csv.reader(io.StringIO(response.data.decode('utf-8-sig'))))
            self.assertEqual(rows,[table['columns'],*table['rows']])
        self.assertEqual(c.get('/paper-data').json['source_sha256'],PAPER['source_sha256'])
        panel=PAPER_PANELS['benchmarks']
        key=next(iter(panel.callback_map))
        r=c.post('/benchmarks/_dash-update-component',json={
            'output':key,'outputs':[{'id':'bench-plot','property':'figure'},{'id':'bench-detail','property':'children'},{'id':'bench-source','property':'children'}],
            'inputs':[{'id':'bench-task','property':'value','value':'ZDT6'},{'id':'bench-percentile','property':'value','value':'100'},{'id':'bench-baseline','property':'value','value':'E2E'}],
            'state':[],'changedPropIds':['bench-task.value']})
        self.assertEqual(r.status_code,200)
        self.assertIn('difference -0.30',r.json['response']['bench-detail']['children'])

    def test_source_sorting_uses_numeric_means(self):
        for direction in ['asc','desc']:
            rows=sorted_source_rows('S4.T1',[{'column_id':'6','direction':direction}])
            values=[float(row[6].split('±')[0]) for row in rows]
            self.assertEqual(values,sorted(values,reverse=direction=='desc'))
        rows=sorted_source_rows('A1.T11',[{'column_id':'1','direction':'desc'}])
        missing=[i for i,r in enumerate(rows) if r[1]=='N/A']
        self.assertEqual(missing,list(range(len(rows)-len(missing),len(rows))))


if __name__=='__main__':unittest.main()

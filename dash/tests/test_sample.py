import hashlib
import unittest
import numpy as np
from app import app, server, render, download
from model import ROOT, DATA, META, MODES, HV, nondominated, hypervolume, view


class SampleTests(unittest.TestCase):
    def test_provenance_hashes(self):
        self.assertEqual(hashlib.sha256((ROOT/'data/sample.npz').read_bytes()).hexdigest(), META['sample_sha256'])
        for name,digest in META['files'].items():
            self.assertEqual(hashlib.sha256((ROOT/'data'/name).read_bytes()).hexdigest(),digest)

    def test_saved_objectives_and_bounds(self):
        for mode in MODES:
            x=DATA[mode+'_x']
            self.assertEqual(x.shape,(161,400,30))
            self.assertTrue(np.isfinite(x).all())
            self.assertGreaterEqual(x.min(),-1e-6)
            self.assertLessEqual(x.max(),1+1e-6)
            g=1+9*x[...,1:].mean(-1)
            expected=np.stack((x[...,0],g-x[...,0]**2/g),-1)
            np.testing.assert_allclose(expected,DATA[mode+'_y'],atol=1e-5)
            self.assertGreater(np.abs(np.diff(x,axis=0)).sum(),1)
            self.assertTrue(np.isfinite(DATA[mode+'_pred']).all())
        self.assertFalse(np.array_equal(DATA['guided_x'],DATA['no_guidance_x']))
        for mode in MODES:
            np.testing.assert_array_equal(DATA['guided_x'][0],DATA[mode+'_x'][0])

    def test_minimization_metrics(self):
        y=np.array([[1,3],[2,2],[3,1],[3,3],[4,4]],dtype=float)
        np.testing.assert_array_equal(nondominated(y),[True,True,True,False,False])
        self.assertEqual(hypervolume(y,reference=(4,4)),6)
        self.assertEqual(hypervolume(np.array([[1,1],[1,1]]),reference=(2,2)),1)

    def test_state_and_export(self):
        for mode in MODES:
            for step in [0,128,160]:
                result=render(mode,step,'truth',[5,20,100],['offline','front'])
                self.assertEqual(len(result),6)
                np.testing.assert_allclose(result[1].data[-1].y,DATA[mode+'_x'][step,[5,20,100]].mean(0))
        result=render('guided',160,'proxy',[5],[])
        self.assertEqual(len(result[0].data),2)
        exported=download(1,'guided',160,[5,20])
        self.assertEqual(len(exported['content'].splitlines()),3)
        with self.assertRaises(ValueError):
            view('bad',160,[0])
        with self.assertRaises(ValueError):
            view('guided',161,[0])

    def callback(self,key,outputs,inputs,state,changed):
        return server.test_client().post('/_dash-update-component',json={'output':key,'outputs':outputs,'inputs':inputs,'state':state,'changedPropIds':[changed]})

    def test_selection_and_replay_http(self):
        response=self.callback('selection.data',{'id':'selection','property':'data'},[
            {'id':'cloud','property':'clickData','value':{'points':[{'customdata':17}]}},
            {'id':'cloud','property':'selectedData','value':None},
            {'id':'clear','property':'n_clicks','value':0}],
            [{'id':'selection','property':'data','value':[200]}],'cloud.clickData')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json['response']['selection']['data'],[17])
        key=next(k for k in app.callback_map if 'clock.disabled' in k)
        response=self.callback(key,[{'id':'clock','property':'disabled'},{'id':'play','property':'children'},{'id':'step','property':'value'}],
            [{'id':'play','property':'n_clicks','value':1},{'id':'clock','property':'n_intervals','value':0}],
            [{'id':'clock','property':'disabled','value':True},{'id':'step','property':'value','value':160}],'play.n_clicks')
        self.assertEqual(response.status_code,200)
        self.assertFalse(response.json['response']['clock']['disabled'])
        self.assertEqual(response.json['response']['step']['value'],124)

    def test_http_routes(self):
        c=server.test_client()
        for path in ['/','/health','/_dash-layout','/_dash-dependencies','/provenance']:
            self.assertEqual(c.get(path).status_code,200)


if __name__=='__main__':
    unittest.main()

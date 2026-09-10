import unittest
import json
import subprocess
from pathlib import Path
import numpy as np
from app import PANELS, server
from model import DATA, HV
from panels import FRONT, ERROR, EVOLUTION


class PanelTests(unittest.TestCase):
    def test_isolated_routes_and_assets(self):
        client = server.test_client()
        for name in PANELS:
            self.assertEqual(client.get('/'+name).status_code,302)
            for suffix in ('','_dash-layout','_dash-dependencies','assets/mini.css','assets/playback.js'):
                response=client.get(f'/{name}/{suffix}')
                self.assertEqual(response.status_code,200)
                if suffix=='_dash-layout':
                    self.assertIn('mini-panel',response.get_data(as_text=True))
                    self.assertNotIn('A moving frontier',response.get_data(as_text=True))
                if suffix.endswith('.css'):
                    self.assertIn('text/css',response.content_type)
                response.close()
        self.assertEqual(client.get('/explorer').status_code,200)

    def test_filtered_candidates_keep_original_identity(self):
        fig,detail=PANELS['frontier'].panel_render(['front'],{'points':[{'customdata':200}]})
        ids=np.asarray(fig.data[-1].customdata)
        np.testing.assert_array_equal(ids,np.flatnonzero(FRONT))
        np.testing.assert_allclose(fig.data[-1].x,DATA['guided_y'][-1,ids,0])
        self.assertIn('Non-dominated',detail)

    def test_design_selection_and_linked_data(self):
        client=server.test_client()
        response=client.post('/design/_dash-update-component',json={
            'output':'design-choice.value','outputs':{'id':'design-choice','property':'value'},
            'inputs':[{'id':'design-cloud','property':'clickData','value':{'points':[{'customdata':17}]}}],
            'state':[],'changedPropIds':['design-cloud.clickData']})
        self.assertEqual(response.status_code,200)
        chosen=response.json['response']['design-choice']['value']
        self.assertEqual(chosen,17)
        cloud,variables,detail=PANELS['design'].panel_render(chosen)
        self.assertEqual(list(cloud.data[-1].selectedpoints),[17])
        np.testing.assert_allclose(variables.data[-1].y,DATA['guided_x'][-1,17])

    def test_replay_and_recorded_frames(self):
        panel=PANELS['evolution']
        dependencies=server.test_client().get('/evolution/_dash-dependencies').json
        self.assertEqual(len(dependencies),2)
        self.assertEqual({d['clientside_function']['function_name'] for d in dependencies},{'control','frame'})
        # These are the exact coordinates shipped to the browser, including the
        # unchanged prefix. Scrubbing must still expose every original frame.
        for step,frame in enumerate(EVOLUTION['frames']):
            np.testing.assert_array_equal(frame['x'],DATA['guided_y'][step,:,0])
            np.testing.assert_array_equal(frame['y'],DATA['guided_y'][step,:,1])
        for step in (0,124,140,160):
            fig,detail=panel.panel_render(step)
            np.testing.assert_allclose(fig.data[-1].y,DATA['guided_y'][step,:,1])
            self.assertIn(f'{HV["guided"][step]:.3f}',detail)
            self.assertEqual(fig.data[-1].type,'scatter')

    def test_local_playback_pause_resume_and_frame_updates(self):
        script=Path(__file__).with_name('test_playback.cjs')
        result=subprocess.run(['node',str(script)],input=json.dumps(EVOLUTION),text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_comparison_metrics_use_all_recorded_values(self):
        for metric,values in [('hv',HV),('error',ERROR)]:
            fig,detail=PANELS['ablation'].panel_render('no_neighbors',metric)
            for trace,mode in zip(fig.data,values):
                np.testing.assert_allclose(trace.y,values[mode])
                self.assertEqual(trace.line.width,3 if mode=='no_neighbors' else 1.5)


if __name__=='__main__':
    unittest.main()

"""The visual story must preserve actual candidate decisions and record identity."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
from urllib.parse import parse_qs, urlparse

from flask import Flask

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import method_atelier as method
from process_view import load_trace, select_record


class MethodAtelierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.trace = load_trace()
        cls.app = method.create_method_panel(Flask('method_atelier_tests'))
        cls.client = cls.app.server.test_client()

    def callback(self, fragment, values, changed):
        key = next(key for key in self.app.callback_map if fragment in key)
        meta = self.app.callback_map[key]
        outputs = meta['output']
        if isinstance(outputs, list):
            outputs = [{'id': item.component_id, 'property': item.component_property} for item in outputs]
        else:
            outputs = {'id': outputs.component_id, 'property': outputs.component_property}
        response = self.client.post('/method/_dash-update-component', json={
            'output': key, 'outputs': outputs,
            'inputs': [dict(item, value=values.get(item['id']+'.'+item['property'])) for item in meta['inputs']],
            'state': [dict(item, value=values.get(item['id']+'.'+item['property'])) for item in meta['state']],
            'changedPropIds': [changed],
        })
        self.assertEqual(response.status_code, 200, response.data[:600])
        return response.get_json()['response']

    def test_named_stages_change_actual_visibility_and_outcome(self):
        scenes = [method.method_scene(self.trace, stage=index) for index in range(5)]
        self.assertEqual(scenes[0]['counts']['visible'], 3)
        self.assertEqual(scenes[1]['counts']['visible'], 9)
        self.assertEqual(scenes[2]['counts']['admitted'], 3)
        self.assertEqual(scenes[3]['winner'], 'C5')
        self.assertEqual(scenes[4]['archive'], 'Updated')
        self.assertEqual(len(scenes[4]['diagram'].layout.annotations), 5)
        _, record = select_record(self.trace, 'guided', 140, 300)
        selected = next(item for item in record['candidates'] if item['selected'])
        self.assertEqual(selected['source_direction'], 301)
        # Numeric coordinates and candidate IDs remain unchanged across stages.
        def points(figure):
            return {curve.customdata[0]: (curve.x[0], curve.y[0]) for curve in figure.data if curve.customdata}
        for scene in scenes[1:]:
            self.assertTrue(points(scenes[0]['objective']).items() <= points(scene['objective']).items())
            self.assertEqual(points(scene['objective']), points(scenes[1]['objective']))
        self.assertNotEqual(scenes[0]['diagram'].to_json(), scenes[1]['diagram'].to_json())
        self.assertNotEqual(scenes[1]['diagram'].to_json(), scenes[2]['diagram'].to_json())
        self.assertNotEqual(scenes[2]['diagram'].to_json(), scenes[3]['diagram'].to_json())

    def test_results_are_revealed_only_at_their_decision_stage(self):
        scenes = [method.method_scene(self.trace, stage=i) for i in range(5)]
        self.assertEqual([s['count_value'] for s in scenes],
                         ['3 generated', '9 pooled', '3 / 9 retained', '3 / 9 retained', '3 / 9 retained'])
        _, record = select_record(self.trace, 'guided', 140, 300)
        for i, scene in enumerate(scenes):
            if i < 3:
                self.assertEqual(scene['winner'], 'Awaiting selection')
            if i < 4:
                self.assertEqual(scene['archive'], 'Awaiting archive')
                self.assertEqual(scene['score'], f"{record['archive_score_before']:.4f}")
                self.assertNotIn('After', [curve.name for curve in scene['profile'].data])
            else:
                self.assertEqual(scene['archive'], 'Updated')
                self.assertIn('After', [curve.name for curve in scene['profile'].data])
            if i < 2:
                self.assertNotIn('excluded', scene['detail'])
                self.assertNotIn('angle', scene['detail'])
            if i < 3:
                self.assertNotIn('score', scene['detail'])
        own_ids = {item['id'] for item in record['candidates'] if item['source_direction'] == 300}
        for name in ('diagram', 'objective'):
            plotted_ids = {curve.customdata[0] for curve in scenes[0][name].data if curve.customdata}
            self.assertEqual(plotted_ids, own_ids)

    def test_full_record_url_tracks_record_stage_and_inspection(self):
        values = {'method-mode.value':'no_guidance', 'method-time.value':145,
                  'method-direction.value':100, 'method-phase.value':2,
                  'method-inspected.data':{'record':['no_guidance',145,100], 'id':2}}
        rendered = self.callback('method-diagram.figure', values, 'method-inspected.data')
        query = parse_qs(urlparse(rendered['method-full-record']['href']).query)
        self.assertEqual(query, {'mode':['no_guidance'], 'step':['145'], 'direction':['100'],
                                 'stage':['Filter'], 'candidate':['2']})
        values.update({'method-time.value':50, 'method-phase.value':None})
        rendered = self.callback('method-diagram.figure', values, 'method-time.value')
        query = parse_qs(urlparse(rendered['method-full-record']['href']).query)
        self.assertEqual(query, {'mode':['no_guidance'], 'step':['50'], 'direction':['100']})
        retained = method.method_scene(self.trace, 'guided', 140, 300, 0, 5)
        self.assertEqual(retained['candidate_id'], 5)
        self.assertIn('kept in the inspector', retained['detail'])
        self.assertEqual(parse_qs(urlparse(retained['record_href']).query)['candidate'], ['5'])

    def test_all_modes_times_directions_handle_real_records(self):
        for mode in self.trace['modes']:
            for step in (0, 80, 128, 140, 160):
                for direction in self.trace['directions']:
                    for stage in (0, 2, 4):
                        with self.subTest(mode=mode, step=step, direction=direction, stage=stage):
                            scene = method.method_scene(self.trace, mode, step, direction, stage)
                            self.assertEqual(len(scene['profile'].data[0].y), 30)
                            if step < 128:
                                self.assertEqual(scene['counts']['pool'], 0)
                                self.assertEqual(len(scene['diagram'].data[0].y), 30)
                                self.assertIsNone(scene['candidate_id'])
                            if step >= 128 and direction == 100 and stage >= 2:
                                self.assertIn('invalid angle', scene['description'])
                                self.assertIn('recorded numerical safeguard', scene['description'])

    def test_decision_lookup_uses_real_candidate_presence(self):
        availability = method.decision_steps(self.trace)
        for mode, data in self.trace['modes'].items():
            for direction in self.trace['directions']:
                with self.subTest(mode=mode, direction=direction):
                    actual = [frame['step'] for frame in data['frames']
                              if next(record for record in frame['directions'] if record['id'] == direction)['candidates']]
                    self.assertEqual(availability[mode][str(direction)], actual)
                    self.assertEqual(actual, list(range(128, 161)))
        # Candidate presence, not a hard-coded threshold or angle validity,
        # determines availability; gaps and empty directions must be preserved.
        sparse = {'directions': [100, 300], 'modes': {'test_run': {'frames': [
            {'step': 5, 'directions': [{'id': 100, 'candidates': []}, {'id': 300, 'candidates': []}]},
            {'step': 12, 'directions': [{'id': 100, 'candidates': []}, {'id': 300, 'candidates': [{'angle_deg': None}]}]},
            {'step': 13, 'directions': [{'id': 100, 'candidates': []}, {'id': 300, 'candidates': []}]},
            {'step': 14, 'directions': [{'id': 100, 'candidates': []}, {'id': 300, 'candidates': [{'angle_deg': None}]}]},
        ]}}}
        self.assertEqual(method.decision_steps(sparse), {'test_run': {'100': [], '300': [12, 14]}})

    def test_unselected_phase_renders_transport_and_boundary_without_error(self):
        for mode in self.trace['modes']:
            for direction in self.trace['directions']:
                for step in (0, 50, 127, 128):
                    with self.subTest(mode=mode, direction=direction, step=step):
                        scene = method.method_scene(self.trace, mode, step, direction, None)
                        self.assertEqual(scene['counts']['pool'] > 0, step >= 128)
                        if step < 128:
                            self.assertIsNone(scene['candidate_id'])
                            self.assertNotIn(scene['heading'], method.STAGES)
                        else:
                            self.assertEqual(scene['heading'], 'Generate')

    def test_disabling_stages_keeps_actual_early_time_exploration(self):
        for mode in self.trace['modes']:
            before = method.method_scene(self.trace, mode, 49, 300, None)
            after = method.method_scene(self.trace, mode, 50, 300, None)
            self.assertNotEqual(list(before['diagram'].data[1].y), list(after['diagram'].data[1].y))
            self.assertEqual(list(before['objective'].data[1].y), list(after['objective'].data[1].y))
            self.assertEqual(before['counts']['pool'], 0)
            self.assertEqual(after['counts']['pool'], 0)

    def test_selected_candidate_clean_design_and_archive_retention(self):
        _, record = select_record(self.trace, 'guided', 140, 200)
        self.assertFalse(record['updated'])
        for candidate in record['candidates']:
            scene = method.method_scene(self.trace, 'guided', 140, 200, 4, candidate['id'])
            self.assertEqual(scene['candidate_id'], candidate['id'])
            self.assertEqual(list(scene['profile'].data[-1].y), candidate['design'])
            self.assertEqual(scene['archive'], 'Retained')
            self.assertNotIn('improves the archive score by', scene['description'])
            self.assertFalse(any(annotation.showarrow for annotation in scene['diagram'].layout.annotations))

    def test_http_routes_and_layout(self):
        for route in ('/method/', '/method/_dash-layout', '/method/_dash-dependencies', '/method/assets/atelier.css', '/method/assets/paper.css'):
            with self.client.get(route) as response:
                self.assertEqual(response.status_code, 200)
        response = self.client.get('/method')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers['Location'].endswith('/method/'))
        layout = self.client.get('/method/_dash-layout').get_json()
        text = json.dumps(layout)
        self.assertIn('Play stages', text)
        self.assertIn('Generate', text)
        self.assertIn('method-diagram', text)
        self.assertIn('method-availability', text)
        self.assertIn('method-first-decision', text)
        def find_component(value, identifier):
            if isinstance(value, dict):
                if value.get('props', {}).get('id') == identifier:
                    return value['props']
                for item in value.values():
                    found = find_component(item, identifier)
                    if found is not None:
                        return found
            elif isinstance(value, list):
                for item in value:
                    found = find_component(item, identifier)
                    if found is not None:
                        return found
            return None
        self.assertEqual(find_component(layout, 'method-availability')['data'], method.decision_steps(self.trace))
        dependencies = self.client.get('/method/_dash-dependencies').get_json()
        controller = next(item for item in dependencies if 'method-clock.disabled' in item['output'])
        self.assertIn({'id': 'method-availability', 'property': 'data'}, controller['state'])
        self.assertIn('method-phase.options', controller['output'])
        self.assertIn('method-play.disabled', controller['output'])
        shortcut = next(item for item in dependencies if item['output'] == 'method-time.value')
        self.assertIn({'id': 'method-first-decision', 'property': 'n_clicks'}, shortcut['inputs'])

    def test_http_click_and_stage_preserve_candidate_selection(self):
        values = {'method-mode.value':'guided', 'method-time.value':140, 'method-direction.value':300,
                  'method-phase.value':1, 'method-diagram.clickData':{'points':[{'customdata':5}]}}
        selection = self.callback('method-inspected.data', values, 'method-diagram.clickData')['method-inspected']['data']
        self.assertEqual(selection, {'record':['guided',140,300], 'id':5})
        values['method-inspected.data'] = selection
        for stage in (1,2,3,4):
            values['method-phase.value'] = stage
            response = self.callback('method-diagram.figure', values, 'method-phase.value')
            self.assertIn('C5 · source 301', response['method-detail']['children'])
        values['method-time.value'] = 141
        reset = self.callback('method-inspected.data', values, 'method-time.value')
        self.assertIsNone(reset['method-inspected']['data'])

    def test_http_none_phase_and_stale_candidate_across_selection_boundary(self):
        values = {'method-mode.value':'guided', 'method-time.value':50, 'method-direction.value':300,
                  'method-phase.value':None,
                  'method-inspected.data':{'record':['guided',140,300], 'id':5}}
        result = self.callback('method-diagram.figure', values, 'method-time.value')
        self.assertEqual(result['method-heading']['children'], 'Flow transport')
        self.assertIn('No candidate pool', result['method-detail']['children'])
        self.assertNotIn('C5', result['method-detail']['children'])
        values['method-time.value'] = 128
        result = self.callback('method-diagram.figure', values, 'method-time.value')
        self.assertEqual(result['method-heading']['children'], 'Generate')
        self.assertNotIn('C5 · source', result['method-detail']['children'])

    def run_browser_script(self, assertions):
        script = ('const control = '+method.TOUR_CONTROL+';\n'
                  'const firstDecision = '+method.FIRST_DECISION+';\n'
                  'const availability = '+json.dumps(method.decision_steps(self.trace))+';\n'+r'''
const assert = require('node:assert/strict');
const NO_UPDATE = Symbol('no_update');
function run(triggers, disabled, phase, step=140, mode='guided', direction=300, lookup=availability) {
  global.window = {dash_clientside:{no_update:NO_UPDATE, callback_context:{triggered:triggers.map(prop_id=>({prop_id}))}}};
  const result = control(1,0,1,mode,step,direction,disabled,phase,lookup);
  assert.equal(result.length, 9);
  assert.equal(result[4].length, 5);
  assert.deepEqual(result[4].map(option=>option.label), ['Generate','Pool','Filter','Select','Archive']);
  return result;
}
function unavailable(result) {
  assert.deepEqual(result.slice(0,4), [true,'Play stages',null,true]);
  assert(result[4].every(option=>option.disabled));
  assert.notEqual(result[5].display,'none');
}
function available(result) {
  assert.equal(result[3],false);
  assert(result[4].every(option=>!option.disabled));
  assert.equal(result[5].display,'none');
  assert.equal(result[8],'');
}
'''+assertions)
        completed = subprocess.run([shutil.which('node')], input=script, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)

    @unittest.skipUnless(shutil.which('node'), 'Node is required to execute browser playback controller')
    def test_browser_play_pause_reset_and_late_ticks(self):
        self.run_browser_script(r'''
const playing=run(['method-play.n_clicks'],true,0);
available(playing);
assert.deepEqual(playing.slice(0,3),[false,'Pause stages',0]);
assert.deepEqual(run(['method-clock.n_intervals'],false,0).slice(0,3),[false,'Pause stages',1]);
assert.deepEqual(run(['method-play.n_clicks','method-clock.n_intervals'],false,2).slice(0,3),[true,'Play stages',2]);
assert.deepEqual(run(['method-clock.n_intervals'],true,2).slice(0,3),[true,'Play stages',2]);
assert.deepEqual(run(['method-clock.n_intervals'],false,3).slice(0,3),[true,'Play stages',4]);
assert.deepEqual(run(['method-play.n_clicks'],true,4).slice(0,3),[false,'Pause stages',0]);
assert.deepEqual(run(['method-reset.n_clicks','method-clock.n_intervals'],false,3).slice(0,3),[true,'Play stages',0]);
assert.deepEqual(run(['method-time.value','method-clock.n_intervals'],false,3).slice(0,3),[true,'Play stages',0]);
''')

    @unittest.skipUnless(shutil.which('node'), 'Node is required to execute browser playback controller')
    def test_browser_empty_records_cannot_play_reset_or_receive_late_ticks(self):
        self.run_browser_script(r'''
for (const mode of Object.keys(availability)) {
  for (const direction of Object.keys(availability[mode])) {
    for (const step of [0,50,127]) {
      for (const triggers of [[],['method-play.n_clicks'],['method-reset.n_clicks'],['method-clock.n_intervals'],
                              ['method-time.value','method-clock.n_intervals'],
                              ['method-play.n_clicks','method-reset.n_clicks','method-clock.n_intervals']]) {
        for (const disabled of [true,false]) {
          const result=run(triggers,disabled,3,step,mode,Number(direction));
          unavailable(result);
          assert.equal(result[7],false);
          assert(result[6].includes('128'));
          assert(result[8].includes(`Step ${step} has no candidate pool`));
        }
      }
    }
    // Invalid recorded angles do not remove legitimate candidate decisions.
    available(run([],true,null,128,mode,Number(direction)));
  }
}
''')

    @unittest.skipUnless(shutil.which('node'), 'Node is required to execute browser playback controller')
    def test_browser_crossing_128_pauses_and_reenables_without_autoplay(self):
        self.run_browser_script(r'''
let current=run(['method-play.n_clicks'],true,2,140);
assert.equal(current[0],false);
current=run(['method-time.value','method-clock.n_intervals'],current[0],current[2],127);
unavailable(current);
current=run(['method-clock.n_intervals'],current[0],current[2],127);
unavailable(current);
current=run(['method-time.value','method-clock.n_intervals'],current[0],current[2],128);
available(current);
assert.deepEqual(current.slice(0,3),[true,'Play stages',0]);
current=run(['method-clock.n_intervals'],current[0],current[2],128);
assert.deepEqual(current.slice(0,3),[true,'Play stages',0]);
current=run(['method-play.n_clicks'],current[0],current[2],128);
assert.deepEqual(current.slice(0,3),[false,'Pause stages',0]);
for(const trigger of ['method-mode.value','method-direction.value']) {
  const switched=run([trigger,'method-clock.n_intervals'],false,3,140,'no_guidance',100);
  available(switched);
  assert.deepEqual(switched.slice(0,3),[true,'Play stages',0]);
}
''')

    @unittest.skipUnless(shutil.which('node'), 'Node is required to execute browser playback controller')
    def test_browser_lookup_gaps_and_first_decision_shortcut(self):
        self.run_browser_script(r'''
run([],true,0); // Initialize the no_update sentinel used by the jump callback.
for(const mode of Object.keys(availability)) {
  for(const direction of Object.keys(availability[mode])) {
    assert.equal(firstDecision(1,mode,Number(direction),availability),availability[mode][direction][0]);
    assert.equal(firstDecision(0,mode,Number(direction),availability),NO_UPDATE);
  }
}
const sparse={custom:{'300':[12,14],'100':[]}};
available(run([],true,null,12,'custom',300,sparse));
available(run([],true,null,14,'custom',300,sparse));
unavailable(run(['method-clock.n_intervals'],false,1,13,'custom',300,sparse));
assert.equal(firstDecision(1,'custom',300,sparse),12);
assert.equal(firstDecision(1,'custom',100,sparse),NO_UPDATE);
assert.equal(firstDecision(1,'missing',300,sparse),NO_UPDATE);
const empty=run(['method-play.n_clicks'],false,4,128,'custom',100,sparse);
unavailable(empty);
assert.equal(empty[7],true);
assert.equal(empty[6],'No recorded decision');
assert(empty[8].includes('no recorded candidate decisions'));
''')


if __name__ == '__main__':
    unittest.main()

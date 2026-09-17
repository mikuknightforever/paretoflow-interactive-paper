"""Exercise the recorded-process UI with real static evidence and Dash HTTP calls."""
import json
from pathlib import Path
import sys
import time
import unittest

from flask import Flask

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import process_view


class ProcessUITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.trace = process_view.load_trace()
        cls.app = process_view.make_process_panel(Flask('process_ui_test'))
        cls.client = cls.app.server.test_client()
        cls.http_timings = []
        cls.response_sizes = []

    def call_callback(self, output_fragment, values, changed):
        key = next(key for key in self.app.callback_map if output_fragment in key)
        callback = self.app.callback_map[key]
        outputs = callback['output']
        if isinstance(outputs, list):
            outputs = [{'id': output.component_id, 'property': output.component_property} for output in outputs]
        else:
            outputs = {'id': outputs.component_id, 'property': outputs.component_property}
        payload = {
            'output': key, 'outputs': outputs,
            'inputs': [dict(item, value=values.get(item['id'] + '.' + item['property'])) for item in callback['inputs']],
            'state': [dict(item, value=values.get(item['id'] + '.' + item['property'])) for item in callback['state']],
            'changedPropIds': [changed],
        }
        start = time.perf_counter()
        response = self.client.post('/process/_dash-update-component', json=payload)
        self.http_timings.append(time.perf_counter() - start)
        self.response_sizes.append(len(response.data))
        self.assertEqual(response.status_code, 200, response.data[:1000])
        return response.get_json()['response']

    @classmethod
    def context(cls, mode='guided', step=160, direction=200, stage='Filter', candidate=None):
        return {
            'process-mode.value': mode, 'process-step.value': step,
            'process-direction.value': direction, 'process-stage.value': stage,
            'process-context.data': process_view.normalize_process_context(cls.trace, mode, step, direction, stage, candidate),
        }

    @staticmethod
    def apply_response(values, response):
        for identifier in ('process-mode', 'process-step', 'process-direction', 'process-stage'):
            values[identifier+'.value'] = response[identifier]['value']
        values['process-context.data'] = response['process-context']['data']
        values['process-table.derived_virtual_data'] = response['process-table']['data']
        if 'active_cell' in response['process-table']:
            values['process-table.active_cell'] = response['process-table']['active_cell']

    def test_all_configurations_directions_phases_and_stages_render(self):
        # Initial, transport, first candidate step and final step have different
        # semantics; cover each with every recorded direction and stage.
        for mode in self.trace['modes']:
            for step in (0, 127, 128, 160):
                for direction in self.trace['directions']:
                    frame, record = process_view.select_record(self.trace, mode, step, direction)
                    for stage in process_view.STAGES:
                        with self.subTest(mode=mode, step=step, direction=direction, stage=stage):
                            result = process_view.render_process(self.trace, mode, step, direction, stage)
                            self.assertIn(f'Step {step} / 160', result['time_label'])
                            for name in ('design', 'state'):
                                self.assertTrue(all(len(curve.y) == 30 for curve in result[name].data))
                            if frame['phase'] != 'selection':
                                self.assertEqual(result['rows'], [])
                                self.assertIsNone(result['candidate_id'])
                                self.assertIn('No candidate pool', result['objective'].layout.annotations[0].text)
                            elif stage == 'Generate':
                                self.assertTrue(all(row['source'] == direction for row in result['rows']))
                            else:
                                self.assertEqual(len(result['rows']), len(record['candidates']))
                            # An angle-filter cone cannot be drawn in raw objective units.
                            self.assertFalse(result['objective'].layout.shapes)
                            self.assertTrue(all(curve.fill is None for curve in result['objective'].data))

    def test_invalid_angles_preserve_unavailable_values_and_actual_safeguard(self):
        seen_invalid_threshold = seen_invalid_candidate = False
        for mode, data in self.trace['modes'].items():
            for frame in data['frames']:
                for record in frame['directions']:
                    if not record['candidates'] or not process_view._invalid_angles(record):
                        continue
                    result = process_view.render_process(self.trace, mode, frame['step'], record['id'], 'Filter')
                    self.assertIn('invalid angle calculation', result['description'])
                    self.assertIn('must not be interpreted as the smallest valid angle', result['description'])
                    self.assertIn(f"candidate {record['safeguard_id']}", result['description'])
                    self.assertEqual([row['id'] for row in result['rows'] if row['safeguard'] == 'Yes'], [record['safeguard_id']])
                    if record['half_angle_deg'] is None:
                        seen_invalid_threshold = True
                        self.assertIn('half-angle is unavailable', result['description'])
                        self.assertTrue(any(row['filter'] == 'Numerical safeguard' for row in result['rows']))
                    invalid_ids = {item['id'] for item in record['candidates'] if item['angle_deg'] is None}
                    if invalid_ids:
                        seen_invalid_candidate = True
                        self.assertTrue(all(row['angle'] is None for row in result['rows'] if row['id'] in invalid_ids))
        self.assertTrue(seen_invalid_threshold)
        self.assertTrue(seen_invalid_candidate)

    def test_inspection_separates_exact_clean_design_and_noisy_state(self):
        frame, record = process_view.select_record(self.trace, 'guided', 160, 200)
        for candidate in record['candidates']:
            result = process_view.render_process(self.trace, 'guided', 160, 200, 'Pool', candidate['id'])
            self.assertEqual(result['candidate_id'], candidate['id'])
            self.assertEqual(list(result['design'].data[-1].y), candidate['design'])
            self.assertEqual(list(result['state'].data[-1].y), candidate['state'])
        with self.assertRaises(ValueError):
            process_view.select_record(self.trace, 'guided', 161, 200)
        with self.assertRaises(ValueError):
            process_view.select_record(self.trace, 'guided', 1, 201)

    def test_neighbor_inspection_stays_selected_but_not_in_generate_plot_or_table(self):
        _, record = process_view.select_record(self.trace, 'guided', 140, 300)
        neighbor = next(item for item in record['candidates'] if item['source_direction'] != 300)
        for stage in process_view.STAGES:
            result = process_view.render_process(self.trace, 'guided', 140, 300, stage, neighbor['id'])
            self.assertEqual(result['candidate_id'], neighbor['id'])
            self.assertEqual(list(result['design'].data[-1].y), neighbor['design'])
            self.assertEqual(list(result['state'].data[-1].y), neighbor['state'])
            if stage == 'Generate':
                self.assertFalse(result['candidate_visible'])
                self.assertIn('not shown in the Generate plot or table', result['inspection'])
                self.assertTrue(all(row['source'] == 300 for row in result['rows']))
                plotted = [datum[0] for curve in result['objective'].data if curve.customdata for datum in curve.customdata]
                self.assertNotIn(neighbor['id'], plotted)
            else:
                self.assertTrue(result['candidate_visible'])

    def test_query_restoration_and_invalid_fields_fall_back_safely(self):
        expected = {'mode':'guided', 'step':140, 'direction':300, 'stage':'Pool', 'candidate':2}
        self.assertEqual(process_view.parse_process_query(self.trace, '?mode=guided&step=140&direction=300&stage=Pool&candidate=2'), expected)
        # An unavailable phase cannot be restored just because it is in the URL.
        transport = process_view.parse_process_query(self.trace, '?mode=guided&step=50&direction=300&stage=Archive&candidate=2')
        self.assertIsNone(transport['stage'])
        self.assertIsNone(transport['candidate'])
        for query in ('', None, '?mode=bad&step=oops&direction=-1&stage=bad&candidate=hello',
                      '?step=-999&direction=9&candidate=9999', '?step=Infinity&direction=NaN',
                      '?step=140.5&candidate=1.5', '?mode=%3Cscript%3E&stage=%00',
                      '?'+ '&'.join('x'+str(i)+'=1' for i in range(40))):
            with self.subTest(query=query):
                result = process_view.parse_process_query(self.trace, query)
                frame, record = process_view.select_record(self.trace, result['mode'], result['step'], result['direction'])
                self.assertIn(result['stage'], process_view.STAGES if record['candidates'] else [None])
                self.assertIn(result['candidate'], [None]+[item['id'] for item in record['candidates']])

    def test_http_routes_layout_and_dependencies(self):
        for url in ('/process/', '/process/_dash-layout', '/process/_dash-dependencies', '/process/assets/process.css'):
            with self.subTest(url=url):
                with self.client.get(url) as response:
                    self.assertEqual(response.status_code, 200)
        layout = self.client.get('/process/_dash-layout').data.decode()
        self.assertIn('Unavailable', layout)
        self.assertIn('Predicted clean design', layout)
        self.assertIn('Noisy stream state', layout)

    def test_http_render_calls_for_all_modes_stages_and_empty_records(self):
        for mode in self.trace['modes']:
            for stage in process_view.STAGES:
                for step, direction in ((0, 200), (128, 100), (160, 200)):
                    with self.subTest(mode=mode, stage=stage, step=step):
                        result = self.call_callback('process-objective.figure', self.context(mode, step, direction, stage), 'process-stage.value')
                        self.assertIn('process-state', result)
                        self.assertEqual(result['process-prev']['disabled'], step == 0)
                        self.assertEqual(result['process-next']['disabled'], step == 160)
                        if step == 0:
                            self.assertEqual(result['process-table']['data'], [])
                            self.assertIsNone(result['process-stage']['value'])
                            self.assertTrue(all(option['disabled'] for option in result['process-stage']['options']))
                        else:
                            self.assertFalse(any(option['disabled'] for option in result['process-stage']['options']))

    def test_http_candidate_point_sorted_table_and_context_reset(self):
        _, record = process_view.select_record(self.trace, 'guided', 160, 200)
        candidate = record['candidates'][-1]
        values = self.context()
        values['process-objective.clickData'] = {'points': [{'customdata': [candidate['id'], candidate['source_direction'], candidate['offspring']]}]}
        result = self.call_callback('process-context.data', values, 'process-objective.clickData')
        selection = result['process-context']['data']
        self.assertEqual(selection['candidate'], candidate['id'])
        self.apply_response(values, result)
        self.assertIn(f"Inspecting candidate {candidate['id']}", result['process-inspection']['children'])
        values['process-table.active_cell'] = {'row': 0, 'column': 0, 'column_id': 'candidate', 'row_id': candidate['id']}
        values['process-table.derived_virtual_data'] = [{'id': item['id']} for item in reversed(record['candidates'])]
        selected = self.call_callback('process-context.data', values, 'process-table.active_cell')
        self.assertEqual(selected['process-context']['data']['candidate'], candidate['id'])
        self.apply_response(values, selected)
        values['process-step.value'] = 159
        reset = self.call_callback('process-context.data', values, 'process-step.value')
        self.assertEqual(reset['process-context']['data']['step'], 159)
        expected = process_view.render_process(self.trace, 'guided', 159, 200, 'Filter')['candidate_id']
        self.assertEqual(reset['process-context']['data']['candidate'], expected)
        self.assertIsNone(reset['process-table']['active_cell'])

    def test_http_url_then_control_echo_and_stage_switch_preserve_context(self):
        values = self.context()
        values['process-location.search'] = '?mode=guided&step=140&direction=300&stage=Pool&candidate=2'
        result = self.call_callback('process-context.data', values, 'process-location.search')
        expected = {'mode':'guided', 'step':140, 'direction':300, 'stage':'Pool', 'candidate':2}
        self.assertEqual(result['process-context']['data'], expected)
        self.apply_response(values, result)
        # Dash receives the controls changed by URL restoration as one atomic
        # update; any subsequent echoed control events must retain the candidate.
        for changed in ('process-mode.value', 'process-step.value', 'process-direction.value', 'process-stage.value'):
            result = self.call_callback('process-context.data', values, changed)
            self.assertEqual(result['process-context']['data'], expected)
            self.apply_response(values, result)
        for stage in ('Filter', 'Select', 'Archive', 'Pool', 'Generate'):
            values['process-stage.value'] = stage
            result = self.call_callback('process-context.data', values, 'process-stage.value')
            self.assertEqual(result['process-context']['data']['candidate'], 2)
            self.assertIn('Inspecting candidate 2', result['process-inspection']['children'])
            self.apply_response(values, result)
        # Restore a neighboring winner and return to Generate without adding it
        # to the source-only plot or silently replacing its 30-dimensional data.
        values['process-location.search'] = '?mode=guided&step=140&direction=300&stage=Select&candidate=5'
        result = self.call_callback('process-context.data', values, 'process-location.search')
        self.apply_response(values, result)
        values['process-stage.value'] = 'Generate'
        result = self.call_callback('process-context.data', values, 'process-stage.value')
        self.assertEqual(result['process-context']['data']['candidate'], 5)
        self.assertIn('not shown in the Generate plot or table', result['process-inspection']['children'])
        self.assertNotIn(5, [row['id'] for row in result['process-table']['data']])

    def test_http_empty_record_and_return_from_none_with_stale_click(self):
        values = self.context(step=140, direction=300, stage='Pool', candidate=2)
        values['process-step.value'] = 50
        result = self.call_callback('process-context.data', values, 'process-step.value')
        self.assertIsNone(result['process-stage']['value'])
        self.assertTrue(all(option['disabled'] for option in result['process-stage']['options']))
        self.assertIsNone(result['process-context']['data']['candidate'])
        self.assertEqual(result['process-stage-heading']['children'], 'Flow transport')
        self.apply_response(values, result)
        values['process-step.value'] = 128
        result = self.call_callback('process-context.data', values, 'process-step.value')
        self.assertEqual(result['process-stage']['value'], 'Generate')
        self.assertFalse(any(option['disabled'] for option in result['process-stage']['options']))
        self.apply_response(values, result)
        selected = result['process-context']['data']['candidate']
        values['process-objective.clickData'] = {'points':[{'customdata':[5,301,2,'guided:140:300']}]}
        result = self.call_callback('process-context.data', values, 'process-objective.clickData')
        self.assertEqual(result['process-context']['data']['candidate'], selected)
        self.apply_response(values, result)
        values['process-table.active_cell'] = {'row':0, 'row_id':5}
        values['process-table.derived_virtual_data'] = [{'id':5, '_record':'guided:140:300'}]
        result = self.call_callback('process-context.data', values, 'process-table.active_cell')
        self.assertEqual(result['process-context']['data']['candidate'], selected)

    def test_http_download_matches_restored_record(self):
        values = self.context()
        values['process-location.search'] = '?mode=no_guidance&step=140&direction=300&stage=Pool&candidate=2'
        result = self.call_callback('process-context.data', values, 'process-location.search')
        self.apply_response(values, result)
        values['process-export.n_clicks'] = 1
        download = self.call_callback('process-download.data', values, 'process-export.n_clicks')['process-download']['data']
        content = json.loads(download['content'])
        self.assertEqual((content['configuration'],content['step'],content['direction']['id']), ('no_guidance',140,300))

    def test_http_step_boundaries_and_json_record_export(self):
        for step, trigger, expected in ((0, 'process-prev', 0), (160, 'process-next', 160), (140, 'process-next', 141), (140, 'process-prev', 139)):
            values = self.context(step=step)
            values[trigger + '.n_clicks'] = 1
            result = self.call_callback('process-step.value', values, trigger + '.n_clicks')
            self.assertEqual(result['process-step']['value'], expected)
        values = self.context(step=128, direction=100)
        values['process-export.n_clicks'] = 1
        result = self.call_callback('process-download.data', values, 'process-export.n_clicks')
        download = result['process-download']['data']
        content = json.loads(download['content'])
        self.assertEqual(content['step'], 128)
        self.assertEqual(content['direction']['id'], 100)
        self.assertIsNone(content['direction']['half_angle_deg'])
        self.assertIn('safeguard_id', content['direction'])
        self.assertEqual(content['provenance']['sampling_seed'], 81)
        self.assertNotIn('NaN', download['content'])
        self.assertNotIn('Infinity', download['content'])

    @classmethod
    def tearDownClass(cls):
        if cls.http_timings:
            print(f'\nProcess UI HTTP: {len(cls.http_timings)} callbacks, '
                  f'mean {sum(cls.http_timings)/len(cls.http_timings):.3f}s, '
                  f'max {max(cls.http_timings):.3f}s; '
                  f'max response {max(cls.response_sizes):,} bytes.')


if __name__ == '__main__':
    unittest.main()

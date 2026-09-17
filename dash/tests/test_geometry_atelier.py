"""Independent geometry invariants and the public interaction contract."""
import json
import unittest
from unittest.mock import patch

import numpy as np
from flask import Flask

from geometry_atelier import (GUIDANCE_PROVENANCE, NEIGHBOR_PROVENANCE, OFFSPRING,
                              WEIGHTS, create_geometry_panels, guidance_geometry,
                              neighbor_figures, neighbor_geometry)


class GeometryAtelierTests(unittest.TestCase):
    def test_guidance_winner_is_inside_cone_and_minimizes_among_admitted(self):
        for shape in ('convex', 'nonconvex'):
            for weight in (.1, .3, .5, .7, .9):
                for half_angle in (2, 8, 20, 30):
                    data = guidance_geometry(shape, weight, half_angle)
                    points = data['points']
                    # Independently derive membership from absolute polar-angle difference.
                    theta = np.arctan2(1-weight, weight)
                    polar_angles = np.arctan2(points[:, 1], points[:, 0])
                    admitted = np.flatnonzero(np.abs(polar_angles-theta) <= np.deg2rad(half_angle))
                    np.testing.assert_array_equal(data['admitted'], admitted)
                    if len(admitted):
                        self.assertIn(data['after'], admitted)
                        scores = weight*points[:, 0]+(1-weight)*points[:, 1]
                        self.assertAlmostEqual(scores[data['after']], scores[admitted].min())
                        self.assertGreaterEqual(scores[data['after']]+1e-12, scores[data['before']])
                    else:
                        self.assertIsNone(data['after'])

    def test_weight_shape_and_width_change_the_geometric_result(self):
        baseline = guidance_geometry('nonconvex', .5, 8)
        self.assertEqual(baseline['before'], 0)
        self.assertEqual(baseline['before_ties'], 2)
        self.assertNotEqual(baseline['before'], baseline['after'])
        wider = guidance_geometry('nonconvex', .5, 30)
        self.assertGreater(len(wider['admitted']), len(baseline['admitted']))
        self.assertNotEqual(wider['after'], baseline['after'])
        changed_weight = guidance_geometry('nonconvex', .8, 8)
        self.assertNotEqual(changed_weight['after'], baseline['after'])
        convex = guidance_geometry('convex', .5, 8)
        self.assertNotEqual(convex['before'], baseline['before'])
        np.testing.assert_allclose(convex['points'][:, 1], 1-np.sqrt(convex['points'][:, 0]))
        np.testing.assert_allclose(baseline['points'][:, 1], 1-baseline['points'][:, 0]**2)

    def test_pool_contains_exactly_three_offspring_from_each_selected_neighbor(self):
        for direction in range(9):
            for k in (1, 3, 5):
                data = neighbor_geometry(direction, k)
                self.assertEqual(len(data['pool']), 3*k)
                self.assertEqual(len(np.unique(data['pool'])), 3*k)
                self.assertIn(direction, data['neighbors'])
                self.assertEqual(set(data['pool']//3), set(data['neighbors']))
                for source in data['neighbors']:
                    self.assertEqual(np.sum(data['pool']//3 == source), 3)
                # These are the established constructed coordinates, not generated records.
                for candidate in data['pool']:
                    i, j = divmod(int(candidate), 3)
                    np.testing.assert_allclose(OFFSPRING[candidate],
                                               [.15+.09*i+.025*j, 1.08-.085*i+.02*(2-j)])

    def test_neighbor_selection_obeys_filter_even_when_an_excluded_score_is_better(self):
        saw_excluded_better, winners = False, set()
        for direction in range(9):
            for k in (1, 3, 5):
                data = neighbor_geometry(direction, k)
                weight = WEIGHTS[direction]
                polar = np.arctan2(OFFSPRING[data['pool'], 1], OFFSPRING[data['pool'], 0])
                target = np.arctan2(weight[1], weight[0])
                admitted = data['pool'][np.abs(polar-target) <= np.deg2rad(20)]
                np.testing.assert_array_equal(data['admitted'], admitted)
                if len(admitted):
                    winner = data['winner']
                    self.assertIn(winner, admitted)
                    self.assertAlmostEqual(data['scores'][winner], (OFFSPRING[admitted]@weight).min())
                    saw_excluded_better |= data['scores'][data['pool']].min() < data['scores'][winner]-1e-12
                    winners.add(winner)
                else:
                    self.assertIsNone(data['winner'])
        self.assertTrue(saw_excluded_better)
        self.assertGreater(len(winners), 1)

    def test_empty_constructed_pool_is_not_given_an_invented_survivor(self):
        # Synthetic fixture places every point outside direction 1's cone.
        with patch('geometry_atelier.OFFSPRING', np.tile([1., 0.], (27, 1))):
            data = neighbor_geometry(0, 3)
            self.assertEqual(len(data['admitted']), 0)
            self.assertIsNone(data['winner'])
            figure, _ = neighbor_figures(data, 'select')
            self.assertFalse(any(trace.name == 'Selected candidate' for trace in figure.data))

    def test_stage_changes_candidate_states_and_rank_colors(self):
        data = neighbor_geometry(4, 5)
        pool, pool_rank = neighbor_figures(data, 'pool')
        filtered, filter_rank = neighbor_figures(data, 'filter')
        selected, selected_rank = neighbor_figures(data, 'select')
        self.assertEqual(len(next(t for t in pool.data if t.name == 'Pooled candidates').x), 15)
        self.assertEqual(len(next(t for t in filtered.data if t.name == 'Admitted candidates').x), len(data['admitted']))
        self.assertFalse(any(t.name == 'Selected candidate' for t in filtered.data))
        chosen = next(t for t in selected.data if t.name == 'Selected candidate')
        self.assertAlmostEqual(chosen.x[0], OFFSPRING[data['winner'], 0])
        self.assertNotEqual(list(pool_rank.data[0].marker.color), list(filter_rank.data[0].marker.color))
        self.assertNotEqual(list(filter_rank.data[0].marker.color), list(selected_rank.data[0].marker.color))
        ordered_losses = np.array(selected_rank.data[0].x)
        self.assertTrue(np.all(np.diff(ordered_losses) >= 0))

    def test_routes_and_real_callbacks_expose_controls_and_honest_provenance(self):
        server = Flask('geometry_atelier_test')
        apps = create_geometry_panels(server)
        client = server.test_client()
        for name, provenance in [('guidance', GUIDANCE_PROVENANCE), ('neighbors', NEIGHBOR_PROVENANCE)]:
            self.assertEqual(client.get('/'+name).status_code, 302)
            response = client.get('/'+name+'/_dash-layout')
            self.assertEqual(response.status_code, 200)
            self.assertIn(provenance, json.dumps(response.json, ensure_ascii=False))
            with client.get('/'+name+'/assets/paper.css') as asset_response:
                self.assertEqual(asset_response.status_code, 200)
        ga = apps['guidance']
        key = next(iter(ga.callback_map))
        response = client.post('/guidance/_dash-update-component', json={
            'output': key, 'outputs': [{'id': 'ga-before', 'property': 'figure'},
                                       {'id': 'ga-after', 'property': 'figure'},
                                       {'id': 'ga-stats', 'property': 'children'},
                                       {'id': 'ga-insight', 'property': 'children'}],
            'inputs': [{'id': 'ga-shape', 'property': 'value', 'value': 'nonconvex'},
                       {'id': 'ga-weight', 'property': 'value', 'value': .5},
                       {'id': 'ga-angle', 'property': 'value', 'value': 8}],
            'state': [], 'changedPropIds': ['ga-angle.value']})
        self.assertEqual(response.status_code, 200)
        self.assertIn('Weighted loss increases', response.json['response']['ga-insight']['children'])
        response = client.post('/neighbors/_dash-update-component', json={
            'output': 'ng-direction.value', 'outputs': {'id': 'ng-direction', 'property': 'value'},
            'inputs': [{'id': 'ng-directions', 'property': 'clickData', 'value': {'points': [{'customdata': 7}]}}],
            'state': [], 'changedPropIds': ['ng-directions.clickData']})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['response']['ng-direction']['value'], 7)


if __name__ == '__main__':
    unittest.main()

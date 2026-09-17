"""Check recorded decisions against sampler mathematics and the original fixture.

These tests read static data only: the web/test environment need not have torch,
pymoo, or the training runtime installed.
"""
import hashlib
import json
from pathlib import Path
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
MODES = ('guided', 'no_guidance', 'no_neighbors')
DIRECTIONS = [0, 100, 200, 300, 399]
ORIGINAL_HASHES = {
    'sample.npz': 'e2fd27d849eac50228fb3315bdf3b2a638f5e82a5b34c77c9fb0e1c128ea00b5',
    'checkpoints.pt': '9b43d632e8a874b25c7052f88247c1af43063b289506fc87200246027b67b257',
}


class ProcessDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.trace = json.loads((ROOT/'data/process_trace.json').read_text(encoding='utf-8'))
        # Cache each compressed array once rather than decompressing a full
        # 161-frame archive for every direction assertion below.
        with np.load(ROOT/'data/sample.npz') as sample:
            keys = ['train_indices'] + [mode+suffix for mode in MODES for suffix in ('_x', '_times')]
            cls.sample = {key: sample[key] for key in keys}
        # Recreate the original training normalization, not rounded offline data.
        train_y = np.load(ROOT/'data/zdt2-y-0.npy')[cls.sample['train_indices']]
        cls.y_mean, cls.y_std = train_y.mean(0), train_y.std(0)
        # Pymoo's uniform reference vectors are integer partitions / 399.
        cls.reference_weights = np.column_stack((np.arange(400)/399, (399-np.arange(400))/399))
        cls.half_angles = {}
        for direction in DIRECTIONS:
            weight = cls.reference_weights[direction]
            cosine = (cls.reference_weights*weight).sum(1)/(np.sqrt((cls.reference_weights**2).sum(1))*np.sqrt((weight**2).sum()))
            nearest = np.argsort(-cosine)[:3]
            # No clamp: the recorded upstream sampler really does propagate an
            # out-of-domain self cosine into a NaN filter threshold for d=100.
            with np.errstate(invalid='ignore'):
                cls.half_angles[direction] = np.degrees(np.arccos(cosine[nearest]).sum()/2)

    def records(self, selections_only=False):
        for mode in MODES:
            for frame in self.trace['modes'][mode]['frames']:
                if selections_only and frame['phase'] != 'selection':
                    continue
                for direction in frame['directions']:
                    yield mode, frame, direction

    def test_provenance_preserves_original_sample_and_checkpoints(self):
        provenance = self.trace['provenance']
        for name, key in [('sample.npz', 'sample_sha256'), ('checkpoints.pt', 'checkpoint_sha256')]:
            actual = hashlib.sha256((ROOT/'data'/name).read_bytes()).hexdigest()
            self.assertEqual(actual, ORIGINAL_HASHES[name], 'The original fixture must not be regenerated')
            self.assertEqual(provenance[key], actual)
        self.assertEqual(provenance['sampling_seed'], 81)

    def test_all_modes_frames_directions_and_numeric_shapes(self):
        self.assertEqual(self.trace['schema_version'], 1)
        self.assertEqual(self.trace['directions'], DIRECTIONS)
        self.assertEqual(set(self.trace['modes']), set(MODES))
        for mode in MODES:
            frames = self.trace['modes'][mode]['frames']
            self.assertEqual(len(frames), 161)
            self.assertTrue(self.trace['modes'][mode]['label'])
            for step, frame in enumerate(frames):
                with self.subTest(mode=mode, step=step):
                    self.assertEqual(frame['step'], step)
                    self.assertAlmostEqual(frame['time'], float(self.sample[mode+'_times'][step]), places=10)
                    expected_phase = 'initial' if step == 0 else ('transport' if frame['time'] < .8 else 'selection')
                    self.assertEqual(frame['phase'], expected_phase)
                    self.assertEqual([d['id'] for d in frame['directions']], DIRECTIONS)
                    for d in frame['directions']:
                        for key in ('state_before', 'state_after', 'archive_before', 'archive_after'):
                            value = np.asarray(d[key])
                            self.assertEqual(value.shape, (30,))
                            self.assertTrue(np.isfinite(value).all(), key)
                        for key in ('archive_score_before', 'archive_score_after'):
                            self.assertTrue(np.isfinite(d[key]), key)
                        expected_half_angle = self.half_angles[d['id']]
                        if np.isfinite(expected_half_angle):
                            self.assertAlmostEqual(d['half_angle_deg'], expected_half_angle, places=8)
                        else:
                            self.assertIsNone(d['half_angle_deg'], 'Undefined upstream thresholds must not be invented')
                        np.testing.assert_allclose(d['weights'], self.reference_weights[d['id']], atol=2e-15, rtol=0)
                        self.assertIsInstance(d['updated'], bool)

    def test_archive_snapshots_and_noisy_state_continuity(self):
        for mode in MODES:
            frames = self.trace['modes'][mode]['frames']
            for step, frame in enumerate(frames):
                for position, d in enumerate(frame['directions']):
                    with self.subTest(mode=mode, step=step, direction=d['id']):
                        np.testing.assert_array_equal(d['archive_after'], self.sample[mode+'_x'][step, d['id']])
                        np.testing.assert_array_equal(d['archive_before'], self.sample[mode+'_x'][max(0, step-1), d['id']])
                        if step:
                            previous = frames[step-1]['directions'][position]
                            np.testing.assert_array_equal(d['state_before'], previous['state_after'])
                            self.assertEqual(d['archive_score_before'], previous['archive_score_after'])
                        else:
                            np.testing.assert_array_equal(d['state_before'], d['state_after'])

    def test_transport_explains_moving_state_without_invented_candidates(self):
        for mode in MODES:
            moving_frames = 0
            for frame in self.trace['modes'][mode]['frames']:
                if frame['phase'] == 'selection':
                    continue
                for d in frame['directions']:
                    with self.subTest(mode=mode, step=frame['step'], direction=d['id']):
                        self.assertEqual(d['candidates'], [])
                        self.assertIsNone(d['chosen_id'])
                        self.assertIsNone(d['safeguard_id'])
                        self.assertFalse(d['updated'])
                        np.testing.assert_array_equal(d['archive_after'], d['archive_before'])
                        self.assertEqual(d['archive_score_after'], d['archive_score_before'])
                        moving_frames += not np.array_equal(d['state_before'], d['state_after'])
            self.assertGreater(moving_frames, 100, 'Transport should record actual changing states')

    def test_candidate_pool_identity_scores_and_normalization(self):
        for mode, frame, d in self.records(selections_only=True):
            with self.subTest(mode=mode, step=frame['step'], direction=d['id']):
                neighbors = d['neighbors']
                self.assertEqual(len(neighbors), 1 if mode == 'no_neighbors' else 3)
                self.assertEqual(len(set(neighbors)), len(neighbors))
                self.assertIn(d['id'], neighbors)
                self.assertTrue(all(0 <= n < 400 for n in neighbors))
                all_weights = self.reference_weights
                cosine_distances = (all_weights @ d['weights'])/(np.linalg.norm(all_weights, axis=1)*np.linalg.norm(d['weights']))
                expected_neighbors = set(np.argsort(-cosine_distances)[:len(neighbors)])
                self.assertEqual(set(neighbors), expected_neighbors)
                if mode == 'no_neighbors':
                    self.assertEqual(neighbors, [d['id']])
                candidates = d['candidates']
                self.assertEqual(len(candidates), len(neighbors)*3)
                self.assertEqual([c['id'] for c in candidates], list(range(len(candidates))))
                expected_sources = [(n, offspring) for n in neighbors for offspring in range(3)]
                self.assertEqual([(c['source_direction'], c['offspring']) for c in candidates], expected_sources)
                scores = np.asarray([c['score_vector'] for c in candidates])
                self.assertEqual(scores.shape, (len(candidates), 2))
                np.testing.assert_allclose([c['weighted_score'] for c in candidates], scores @ d['weights'], atol=2e-12, rtol=0)
                np.testing.assert_allclose([c['predicted'] for c in candidates], -scores*self.y_std+self.y_mean, atol=3e-7, rtol=0)
                for c in candidates:
                    for key in ('state', 'design'):
                        value = np.asarray(c[key])
                        self.assertEqual(value.shape, (30,))
                        self.assertTrue(np.isfinite(value).all(), key)
                    self.assertGreaterEqual(min(c['design']), -2e-7)
                    self.assertLessEqual(max(c['design']), 1+2e-7)

    def test_filter_angles_and_minimum_angle_fallback(self):
        fallback_count = 0
        for mode, frame, d in self.records(selections_only=True):
            with self.subTest(mode=mode, step=frame['step'], direction=d['id']):
                candidates = d['candidates']
                scores = np.asarray([c['score_vector'] for c in candidates], dtype=np.float32)
                weights = np.asarray(d['weights'], dtype=np.float64)
                angles = np.asarray([np.nan if c['angle_deg'] is None else c['angle_deg'] for c in candidates])
                finite_angles = np.isfinite(angles)
                np.testing.assert_array_equal([c['angle_valid'] for c in candidates], finite_angles)
                self.assertTrue(((angles[finite_angles] >= 0) & (angles[finite_angles] <= 180)).all())
                # The upstream sampler computes the score-vector norm in float32.
                # Comparing cosines avoids magnifying that rounding via acos near 0.
                score_norms32 = np.sqrt(np.sum(scores*scores, axis=1))
                score_norms = score_norms32.astype(np.float64)
                numerators = scores.astype(np.float64) @ weights
                cosines = numerators/(score_norms*np.linalg.norm(weights))
                np.testing.assert_allclose(np.cos(np.deg2rad(angles[finite_angles])), cosines[finite_angles], atol=2e-7, rtol=0)
                # torch.pow(0.5) and numpy.sqrt differ by one float32 ULP in
                # three recorded cases. Independently checked with torch:
                # guided/159/d300/c1, no_guidance/153/d100/c8, /156/d200/c0.
                # Permit only that exact rounding interval, never an arbitrary
                # angle tolerance or a fabricated zero angle for invalid acos.
                lower_norms = np.nextafter(score_norms32, np.float32(-np.inf)).astype(np.float64)
                outer_cosines = numerators/(lower_norms*np.linalg.norm(weights))
                for cosine, outer_cosine in zip(cosines[~finite_angles], outer_cosines[~finite_angles]):
                    self.assertTrue(not np.isfinite(cosine) or abs(cosine) > 1 or abs(outer_cosine) > 1,
                                    'null angle must reflect an invalid raw acos input within one norm ULP')
                threshold = np.nan if d['half_angle_deg'] is None else d['half_angle_deg']
                inside = angles <= threshold
                np.testing.assert_array_equal([c['inside_cone'] for c in candidates], inside)
                admitted = inside.copy()
                # Like torch.argmin, numpy.argmin picks the first NaN if present.
                safeguard_id = int(np.argmin(angles))
                self.assertEqual(d['safeguard_id'], safeguard_id)
                admitted[safeguard_id] = True
                np.testing.assert_array_equal([c['admitted'] for c in candidates], admitted)
                fallback = admitted & ~inside
                np.testing.assert_array_equal([c['fallback'] for c in candidates], fallback)
                fallback_count += int(fallback.sum())
        self.assertGreater(fallback_count, 0, 'This fixture must exercise the real minimum-angle fallback')

    def test_winner_state_and_archive_update_are_distinct_decisions(self):
        updates = 0
        retained = 0
        for mode, frame, d in self.records(selections_only=True):
            with self.subTest(mode=mode, step=frame['step'], direction=d['id']):
                candidates = d['candidates']
                masked_scores = [c['weighted_score'] if c['admitted'] else -np.inf for c in candidates]
                winner = candidates[int(np.argmax(masked_scores))]
                self.assertEqual(d['chosen_id'], winner['id'])
                self.assertEqual([c['id'] for c in candidates if c['selected']], [winner['id']])
                np.testing.assert_array_equal(d['state_after'], winner['state'])
                updated = winner['weighted_score'] > d['archive_score_before']
                self.assertEqual(d['updated'], updated)
                if updated:
                    np.testing.assert_array_equal(d['archive_after'], winner['design'])
                    self.assertAlmostEqual(d['archive_score_after'], winner['weighted_score'], places=12)
                    updates += 1
                else:
                    np.testing.assert_array_equal(d['archive_after'], d['archive_before'])
                    self.assertEqual(d['archive_score_after'], d['archive_score_before'])
                    retained += 1
        self.assertGreater(updates, 0)
        self.assertGreater(retained, 0, 'Selecting a stream state need not replace the saved best design')


if __name__ == '__main__':
    unittest.main()

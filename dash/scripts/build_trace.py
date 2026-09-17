"""Record the existing CPU checkpoint, and refuse to write if results change.

No training occurs and neither sample.npz nor checkpoints.pt is overwritten.
Run with the versions in data/manifest.json and requirements-reproduce.txt.
"""
import hashlib
import json
import os
from pathlib import Path
import sys

# The reference fixture was generated on CPU. Make this replay explicit even
# on machines that also have a CUDA device; this affects only this process.
os.environ['CUDA_VISIBLE_DEVICES'] = ''
from build_sample import ROOT, Proxy, Recorder, evaluate
import numpy as np
import torch
from paretoflow import Task, FlowMatching, VectorFieldNet


DIRECTIONS = [0, 100, 200, 300, 399]
MODES = [('guided', 'Gradient guidance + neighbor exchange', 2., 3),
         ('no_guidance', 'No gradient guidance', 0., 3),
         ('no_neighbors', 'No neighbor exchange', 2., 1)]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def array(value):
    return value.detach().cpu().numpy()


class ProcessRecorder:
    """Synchronous observer: copy existing values without model calls or RNG."""
    def __init__(self, task):
        self.task = task
        self.frames = []

    def clean(self, value):
        # Mirror Recorder.record_archive, including its float32 conversion
        # before denormalizing the initial double-precision offline archive.
        return self.task.to_denormalize_x(array(value.float()), 'z_score').astype('float32').tolist()

    def __call__(self, *, phase, step, time, objectives_weights,
                 neighborhood_indices, phi, state_before, state_after,
                 archive_before, archive_after, **selection):
        directions = []
        for direction in DIRECTIONS:
            weights = objectives_weights[direction]
            neighbors = neighborhood_indices[direction]
            previous, previous_score = archive_before[direction]
            current, current_score = archive_after[direction]
            half_angle = phi[direction].item() / 2
            record = {
                'id': direction, 'weights': array(weights).tolist(),
                'neighbors': array(neighbors).tolist(),
                'half_angle_deg': float(np.degrees(half_angle)) if np.isfinite(half_angle) else None,
                'state_before': array(state_before[direction]).tolist(),
                'state_after': array(state_after[direction]).tolist(),
                'archive_before': self.clean(previous),
                'archive_after': self.clean(current),
                'archive_score_before': float(previous_score),
                'archive_score_after': float(current_score),
                'updated': float(current_score) > float(previous_score),
                'chosen_id': None, 'safeguard_id': None, 'candidates': [],
            }
            if phase == 'selection':
                offspring = selection['offspring_count']
                chosen = int(selection['index'][direction])
                scores = selection['neighborhood_scores'][direction]
                # Same pre-mask dot product; observation never modifies tensors.
                weighted = (scores * weights).sum(dim=-1)
                endpoints = selection['merged_samples_x_1'][neighbors].reshape(-1, self.task.input_x.shape[1])
                record['chosen_id'] = chosen
                # Preserve the upstream argmin result even if acos returned NaN.
                # This observer does not clamp or otherwise repair the run.
                record['safeguard_id'] = int(torch.argmin(selection['angles'][direction]))
                for candidate_id in range(len(scores)):
                    angle = float(selection['angles'][direction, candidate_id])
                    inside = angle <= half_angle
                    admitted = bool(selection['angle_filter_mask'][direction, candidate_id])
                    vector = array(scores[candidate_id])
                    record['candidates'].append({
                        'id': candidate_id,
                        'source_direction': int(neighbors[candidate_id // offspring]),
                        'offspring': candidate_id % offspring,
                        'state': array(selection['neighborhood_designs'][direction, candidate_id]).tolist(),
                        'design': self.clean(endpoints[candidate_id]),
                        'predicted': (-vector * self.task.y_std + self.task.y_mean).tolist(),
                        'score_vector': vector.tolist(),
                        'angle_deg': float(np.degrees(angle)) if np.isfinite(angle) else None,
                        'angle_valid': bool(np.isfinite(angle)),
                        'inside_cone': inside, 'admitted': admitted,
                        'fallback': admitted and not inside,
                        'weighted_score': float(weighted[candidate_id]),
                        'selected': candidate_id == chosen,
                    })
            directions.append(record)
        self.frames.append({'phase': phase, 'step': step, 'time': time,
                            'directions': directions})


def run(task, flow, proxies, gamma, neighbors, trace=None):
    torch.manual_seed(81)
    np.random.seed(81)
    sampler = Recorder(task, load_pretrained_fm=True, load_pretrained_proxies=True,
                       fm_model=flow, proxies=proxies)
    sampler.times, sampler.snapshots = [], []
    result_x, result_pred = sampler.sample(
        T=161, O=3, K=neighbors, num_solutions=32, gamma=gamma,
        g_t=.1, t_threshold=.8, trace_callback=trace)
    return {'x': np.stack(sampler.snapshots), 'times': np.asarray(sampler.times),
            'result_x': result_x, 'result_y': evaluate(result_x),
            'result_pred': result_pred, 'torch_rng': torch.get_rng_state().numpy(),
            'numpy_rng': np.random.get_state()}


def require_identical(actual, expected, label):
    if not np.array_equal(actual, expected):
        error = float(np.max(np.abs(np.asarray(actual) - np.asarray(expected))))
        raise RuntimeError(f'{label} differs (max absolute error {error}); trace not written')


def main():
    torch.set_num_threads(2)
    torch.manual_seed(2026)
    np.random.seed(2026)
    sample_path, checkpoint_path = ROOT/'data/sample.npz', ROOT/'data/checkpoints.pt'
    input_hashes = {p.name: sha256(p) for p in [sample_path, checkpoint_path]}
    sample = np.load(sample_path)
    source_x, source_y = np.load(ROOT/'data/zdt2-x-0.npy'), np.load(ROOT/'data/zdt2-y-0.npy')
    train = sample['train_indices']
    task = Task('ZDT2-sample', source_x[train], source_y[train], np.zeros(30), np.ones(30))
    task.xl = (np.zeros(30) - task.x_mean) / task.x_std
    task.xu = (np.ones(30) - task.x_mean) / task.x_std
    checkpoint = torch.load(checkpoint_path, map_location='cpu', weights_only=True)
    flow = FlowMatching(VectorFieldNet(30, M=128), sigma=0, D=30, T=161)
    flow.load_state_dict(checkpoint['flow'])
    flow.eval()
    proxies = [Proxy(), Proxy()]
    for proxy, state in zip(proxies, checkpoint['proxies']):
        proxy.load_state_dict(state)
        proxy.eval()

    payload = {'schema_version': 1, 'directions': DIRECTIONS, 'provenance': {
        'checkpoint_sha256': input_hashes['checkpoints.pt'],
        'sample_sha256': input_hashes['sample.npz'],
        'sampling_seed': 81, 'training_seed': 2026, 'device': 'cpu',
        'versions': {'python': sys.version, 'numpy': np.__version__, 'torch': torch.__version__},
        'protocol': {'T': 161, 'offspring': 3, 'reference_directions': 400,
                     'g_t': .1, 't_threshold': .8, 'num_solutions': 32},
        'normalization': {key: getattr(task, key).tolist() for key in ['x_mean', 'x_std', 'y_mean', 'y_std']},
        'coordinates': {
            'state': 'Noisy sampler state in standardized x coordinates; not an evaluated clean design.',
            'design': 'Estimated clean endpoint, denormalized to original x units.',
            'score_vector': 'Negative standardized proxy losses; used for angles and scalarized scores.',
            'predicted': 'Proxy losses in original objective units; lower is better.',
            'candidate_id': 'Local neighborhood pool index; not persistent particle identity.',
            'undefined_angles': 'Non-finite upstream acos results are null, never repaired to zero. Recorded masks, safeguard argmin and winners preserve the original run. Fallback means admitted despite failing the raw angle test, including undefined comparisons.',
        },
        'source_files': {str(p.relative_to(ROOT)).replace('\\', '/'): sha256(p) for p in [
            ROOT/'scripts/build_trace.py', ROOT/'vendor/paretoflow/paretoflow.py',
            ROOT/'data/zdt2-x-0.npy', ROOT/'data/zdt2-y-0.npy']},
        'verification': {},
    }, 'modes': {}}
    for name, label, gamma, neighbors in MODES:
        print(f'{name}: replaying checkpoint without trace', flush=True)
        baseline = run(task, flow, proxies, gamma, neighbors)
        for key in ['x', 'times', 'result_x', 'result_y']:
            require_identical(baseline[key], sample[name+'_'+key], name+' original '+key)
        require_identical(evaluate(baseline['x']).astype('float32'), sample[name+'_y'], name+' original y')
        with torch.no_grad():
            normalized = torch.tensor((baseline['x'].reshape(-1, 30)-task.x_mean)/task.x_std, dtype=torch.float32)
            pred = torch.cat([p(normalized) for p in proxies], 1).numpy()*task.y_std+task.y_mean
        require_identical(pred.reshape(161, 400, 2).astype('float32'), sample[name+'_pred'], name+' original predictions')
        print(f'{name}: recording five directions', flush=True)
        observer = ProcessRecorder(task)
        traced = run(task, flow, proxies, gamma, neighbors, observer)
        for key in ['x', 'times', 'result_x', 'result_y', 'result_pred', 'torch_rng']:
            require_identical(traced[key], baseline[key], name+' trace on/off '+key)
        for actual, expected in zip(traced['numpy_rng'], baseline['numpy_rng']):
            require_identical(actual, expected, name+' NumPy RNG')
        if len(observer.frames) != 161:
            raise RuntimeError('Incomplete trace; nothing written')
        payload['modes'][name] = {'label': label, 'gamma': gamma, 'neighbors': neighbors, 'frames': observer.frames}
        selection_records = [d for f in observer.frames if f['phase'] == 'selection' for d in f['directions']]
        payload['modes'][name]['numerical_observations'] = {
            'undefined_candidate_angles': sum(c['angle_deg'] is None for d in selection_records for c in d['candidates']),
            'undefined_half_angle_records': sum(d['half_angle_deg'] is None for d in selection_records),
        }
        payload['provenance']['verification'][name] = {
            'all_161_full_archives_equal_original': True,
            'all_archive_objectives_and_predictions_equal_original': True,
            'final_outputs_equal_original': True,
            'trace_on_off_outputs_equal': True, 'trace_on_off_rng_equal': True,
            'comparison': 'exact array equality',
        }
        print(f'{name}: all original arrays, trace on/off outputs and RNG states identical', flush=True)
    sample.close()
    for path in [sample_path, checkpoint_path]:
        if sha256(path) != input_hashes[path.name]:
            raise RuntimeError(f'Input changed while recording: {path}')
    # Serialize before writing so non-finite or unsupported values cannot leave
    # an incomplete file. Replace only this script's trace output atomically.
    content = json.dumps(payload, separators=(',', ':'), allow_nan=False) + '\n'
    output = ROOT/'data/process_trace.json'
    temporary = output.with_suffix('.json.tmp')
    temporary.write_text(content, encoding='utf-8')
    temporary.replace(output)
    print(f'Wrote {output} ({output.stat().st_size:,} bytes)', flush=True)


if __name__ == '__main__':
    main()

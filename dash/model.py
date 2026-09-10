"""Read-only recorded experiment views. No training runs in the web server."""
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent
DATA = np.load(ROOT/'data/sample.npz')
META = json.loads((ROOT/'data/manifest.json').read_text(encoding='utf-8'))
MODES = {'guided':'Guided + neighbors', 'no_guidance':'No gradient guidance', 'no_neighbors':'No neighbor exchange'}
COLORS = {'guided':'#156aab', 'no_guidance':'#d28532', 'no_neighbors':'#9777b9'}


def nondominated(y):
    """Two minimization objectives. Duplicate objective points are retained."""
    keep = np.ones(len(y),dtype=bool)
    for i in range(len(y)):
        keep[i] = not np.any(np.all(y<=y[i],axis=1) & np.any(y<y[i],axis=1))
    return keep


def hypervolume(y, reference=(1.1,10.0)):
    """Union of dominated rectangles, in original objective units."""
    valid = y[np.isfinite(y).all(1) & (y<np.array(reference)).all(1)]
    valid = valid[np.argsort(valid[:,0],kind='stable')]
    best = reference[1]
    area = 0.
    for a,b in valid:
        if b < best:
            area += (reference[0]-a)*(best-b)
            best=b
    return float(area)


def view(mode, step, ids):
    if mode not in MODES or not isinstance(step,int) or not 0<=step<len(DATA[mode+'_times']):
        raise ValueError('Invalid recorded state')
    if not ids or any(not isinstance(i,int) or i<0 or i>=400 for i in ids):
        raise ValueError('Invalid reference-direction selection')
    return DATA[mode+'_x'][step], DATA[mode+'_y'][step], DATA[mode+'_pred'][step]


HV = {mode:np.array([hypervolume(y) for y in DATA[mode+'_y']]) for mode in MODES}

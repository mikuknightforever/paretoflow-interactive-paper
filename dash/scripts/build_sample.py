"""Train a bounded CPU example and record real archive updates from upstream sampling."""
import hashlib
import json
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'vendor'))
if os.environ.get('PARETO_DEPS'):
    sys.path.insert(0, os.environ['PARETO_DEPS'])
import numpy as np
import torch
from torch import nn
from paretoflow import ParetoFlow, Task, FlowMatching, VectorFieldNet


def evaluate(x):
    g = 1 + 9*np.mean(x[..., 1:], axis=-1)
    return np.stack((x[..., 0], g-x[..., 0]**2/g), axis=-1)


class Proxy(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(30,64),nn.SiLU(),nn.Linear(64,64),nn.SiLU(),nn.Linear(64,1))
    def forward(self,x):
        return self.net(x)


class Recorder(ParetoFlow):
    def record_archive(self, t, archive):
        arr = torch.stack([item[0].detach().float().cpu() for item in archive]).numpy()
        self.times.append(float(t))
        self.snapshots.append(self.task.to_denormalize_x(arr,'z_score').astype('float32'))


def main():
    torch.set_num_threads(2)
    torch.manual_seed(2026)
    np.random.seed(2026)
    x = np.load(ROOT/'data/zdt2-x-0.npy')
    y = np.load(ROOT/'data/zdt2-y-0.npy')
    np.testing.assert_allclose(evaluate(x),y,atol=1e-6)
    ix = np.random.default_rng(2026).permutation(len(x))
    train_ix, val_ix = ix[:12000], ix[12000:14000]
    task = Task('ZDT2-sample',x[train_ix],y[train_ix],np.zeros(30),np.ones(30))
    # The sampler works in normalized space, so its repair bounds must too.
    task.xl = (np.zeros(30)-task.x_mean)/task.x_std
    task.xu = (np.ones(30)-task.x_mean)/task.x_std
    xt = torch.tensor(task.input_x,dtype=torch.float32)
    yt = torch.tensor(task.input_y,dtype=torch.float32)
    fm = FlowMatching(VectorFieldNet(30,M=128),sigma=0,D=30,T=161)
    proxies = [Proxy(),Proxy()]
    opt_f = torch.optim.Adam(fm.parameters(),lr=.001)
    opt_p = torch.optim.Adam([p for m in proxies for p in m.parameters()],lr=.001)
    start = time.time()
    for step in range(1800):
        indices = torch.randint(len(xt),(256,))
        batch = xt[indices]
        opt_f.zero_grad()
        loss_f = fm(batch)
        loss_f.backward()
        opt_f.step()
        opt_p.zero_grad()
        loss_p = sum(((m(batch).flatten()-yt[indices,j])**2).mean() for j,m in enumerate(proxies))
        loss_p.backward()
        opt_p.step()
        if step%300==0:
            print(f'Training {step}/1800: flow={loss_f.item():.4f}, proxy={loss_p.item():.4f}',flush=True)
    fm.eval()
    for m in proxies:
        m.eval()
    with torch.no_grad():
        val = torch.tensor((x[val_ix]-task.x_mean)/task.x_std,dtype=torch.float32)
        val_pred = torch.cat([m(val) for m in proxies],1).numpy()*task.y_std+task.y_mean
    modes = [('guided',2.,3),('no_guidance',0.,3),('no_neighbors',2.,1)]
    payload = {'offline_x':x[train_ix].astype('float32'), 'offline_y':y[train_ix].astype('float32'),
               'train_indices':train_ix, 'val_indices':val_ix}
    for name,gamma,k in modes:
        torch.manual_seed(81)
        np.random.seed(81)
        pf = Recorder(task,load_pretrained_fm=True,load_pretrained_proxies=True,fm_model=fm,proxies=proxies)
        pf.times, pf.snapshots = [], []
        print('Sampling '+name,flush=True)
        result_x,result_y = pf.sample(T=161,O=3,K=k,num_solutions=32,gamma=gamma,g_t=.1,t_threshold=.8)
        archive_x = np.stack(pf.snapshots)
        with torch.no_grad():
            normalized = torch.tensor((archive_x.reshape(-1,30)-task.x_mean)/task.x_std,dtype=torch.float32)
            pred = torch.cat([m(normalized) for m in proxies],1).numpy()*task.y_std+task.y_mean
        payload[name+'_x'] = archive_x
        payload[name+'_y'] = evaluate(archive_x).astype('float32')
        payload[name+'_pred'] = pred.reshape(*archive_x.shape[:2],2).astype('float32')
        payload[name+'_times'] = np.array(pf.times)
        payload[name+'_result_x'] = result_x
        payload[name+'_result_y'] = evaluate(result_x)
        print(name, archive_x.shape, 'final ranges',evaluate(archive_x[-1]).min(0),evaluate(archive_x[-1]).max(0),flush=True)
    np.savez_compressed(ROOT/'data/sample.npz',**payload)
    torch.save({'flow':fm.state_dict(),'proxies':[m.state_dict() for m in proxies]},ROOT/'data/checkpoints.pt')
    manifest = {'upstream':'https://github.com/mila-iqia/ParetoFlow','commit':'8ebefb37a9e4bd837cf6153d38d415f1d584a1a6',
        'status':'Small CPU example; not a reproduction of paper tables','task':'ZDT2','dimensions':30,'objectives':2,
        'source_rows':len(x),'training_rows':12000,'validation_rows':2000,'train_seed':2026,'sampling_seed':81,
        'training_steps':1800,'batch_size':256,'flow_width':128,'proxy_widths':[64,64],'sampler_T':161,'offspring':3,
        'reference_directions':400,'t_threshold':.8,'elapsed_seconds':round(time.time()-start,2),
        'proxy_validation_mae':np.abs(val_pred-y[val_ix]).mean(0).tolist(),
        'versions':{'python':sys.version,'numpy':np.__version__,'torch':torch.__version__},
        'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'data').glob('*.npy')}}
    manifest['sample_sha256'] = hashlib.sha256((ROOT/'data/sample.npz').read_bytes()).hexdigest()
    (ROOT/'data/manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(manifest,indent=2),flush=True)


if __name__=='__main__':
    main()

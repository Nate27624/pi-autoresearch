"""Fixed evaluation protocol; CLI hyperparameters are safe autoresearch knobs."""
import argparse
import json
import math
import random
from pathlib import Path
import numpy as np
import torch
from torch import nn
from data import splits, windows

class Predictor(nn.Module):
    def __init__(self, context, embed, hidden):
        super().__init__()
        self.embedding = nn.Embedding(10, embed)
        self.net = nn.Sequential(nn.Flatten(), nn.Linear(context * embed, hidden),
                                 nn.GELU(), nn.Linear(hidden, 10))

    def forward(self, x):
        return self.net(self.embedding(x))


def assess(model, seq, context, batch, device):
    x, y = windows(seq, context)
    model.eval()
    correct, loss_total, count = 0, 0., 0
    with torch.no_grad():
        for i in range(0, len(y), batch):
            xb = torch.from_numpy(x[i:i+batch]).to(device)
            yb = torch.from_numpy(y[i:i+batch]).to(device)
            logits = model(xb)
            loss_total += nn.functional.cross_entropy(logits, yb, reduction='sum').item()
            correct += (logits.argmax(-1) == yb).sum().item()
            count += yb.numel()
    return {'accuracy': correct/count, 'cross_entropy_nats': loss_total/count, 'examples':count}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--data', type=Path, default=Path('data/pi_10000.npy'))
    p.add_argument('--context', type=int, default=16)
    p.add_argument('--embed', type=int, default=8)
    p.add_argument('--hidden', type=int, default=64)
    p.add_argument('--lr', type=float, default=0.001)
    p.add_argument('--steps', type=int, default=100)
    p.add_argument('--batch', type=int, default=128)
    p.add_argument('--seed', type=int, default=2026)
    p.add_argument('--device', choices=['auto','cpu','cuda'], default='auto')
    p.add_argument('--test', action='store_true', help='Evaluate held-out test ONLY for final frozen candidate')
    p.add_argument('--output', type=Path)
    a = p.parse_args()
    if a.steps < 1 or a.batch < 1:
        p.error('steps and batch must be positive')
    random.seed(a.seed); np.random.seed(a.seed); torch.manual_seed(a.seed)
    if torch.cuda.is_available(): torch.cuda.manual_seed_all(a.seed)
    torch.use_deterministic_algorithms(True, warn_only=True)
    device = 'cuda' if a.device == 'auto' and torch.cuda.is_available() else ('cpu' if a.device == 'auto' else a.device)
    digits = np.load(a.data, allow_pickle=False)
    if digits.ndim != 1 or not np.issubdtype(digits.dtype, np.integer) or np.any((digits < 0) | (digits > 9)):
        raise ValueError('Invalid digit data')
    tr, va, te = splits(digits)
    if min(map(len,(tr,va,te))) <= a.context: raise ValueError('Split too short for context')
    x,y = windows(tr,a.context)
    model = Predictor(a.context,a.embed,a.hidden).to(device)
    optimizer = torch.optim.AdamW(model.parameters(),lr=a.lr)
    for step in range(a.steps):
        idx = np.random.randint(0,len(y),size=a.batch)
        xb = torch.from_numpy(x[idx]).to(device)
        yb = torch.from_numpy(y[idx]).to(device)
        model.train(); optimizer.zero_grad(set_to_none=True)
        loss = nn.functional.cross_entropy(model(xb),yb)
        loss.backward(); optimizer.step()
    # Frequency baseline derived from training targets only.
    freq = np.bincount(y,minlength=10).astype(float)
    probs = (freq + 1) / (len(y) + 10)
    _, val_y = windows(va, a.context)
    baseline = {'accuracy':float(np.mean(val_y == np.argmax(probs))),
                'cross_entropy_nats':float(-np.log(probs[val_y]).mean())}
    result = {'settings':vars(a) | {'data':str(a.data),'output':str(a.output) if a.output else None},
              'validation':assess(model,va,a.context,a.batch,device),
              'frequency_baseline_validation':baseline,
              'uniform_baseline_cross_entropy_nats': math.log(10),
              'device':device}
    if a.test:
        result['test'] = assess(model,te,a.context,a.batch,device)
    print(json.dumps(result,indent=2))
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(json.dumps(result,indent=2)+'\n')

if __name__ == '__main__': main()

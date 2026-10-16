"""Budgeted, reproducible validation-only autoresearch sweep; never reads test metrics."""
import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path

CANDIDATES = [
    (8,8,32,0.001),(16,8,64,0.001),(32,8,64,0.001),
    (16,16,128,0.001),(32,16,128,0.0003),(64,8,64,0.0003),
]

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--data', default='data/pi_10000.npy')
    p.add_argument('--steps', type=int, default=100)
    p.add_argument('--output-dir', type=Path, default=Path('runs/sweep'))
    a=p.parse_args()
    a.output_dir.mkdir(parents=True,exist_ok=True)
    rows=[]
    for i,(context,embed,hidden,lr) in enumerate(CANDIDATES):
        output=a.output_dir / f'candidate_{i:02d}.json'
        cmd=[sys.executable,'train.py','--data',a.data,'--context',str(context),
             '--embed',str(embed),'--hidden',str(hidden),'--lr',str(lr),
             '--steps',str(a.steps),'--output',str(output)]
        subprocess.run(cmd,check=True,stdout=subprocess.DEVNULL)
        result=json.loads(output.read_text())
        rows.append({'candidate':i,'context':context,'embed':embed,'hidden':hidden,'lr':lr,
                     'accuracy':result['validation']['accuracy'],
                     'cross_entropy_nats':result['validation']['cross_entropy_nats']})
        print(f"Candidate {i}: val CE={rows[-1]['cross_entropy_nats']:.4f}, accuracy={rows[-1]['accuracy']:.3%}",flush=True)
    with (a.output_dir/'results.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    winner=min(rows,key=lambda r:r['cross_entropy_nats'])
    (a.output_dir/'best.json').write_text(json.dumps(winner,indent=2)+'\n')
    print('Best validation candidate:',winner)
    print('Test is untouched. Freeze the candidate and perform one final test run separately.')

if __name__=='__main__':main()

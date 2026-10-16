# π Autoresearch

A small, reproducible autoresearch-inspired experiment testing **next-decimal-digit prediction** of pi from preceding digits. Pi is fully computable; this experiment tests whether a short-context learned predictor discovers usable local predictive signal.

## Run locally (Python 3.10+)
```bash
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
python -m unittest discover -s tests -v
python data.py --n 10000 --source pi --out data/pi_10000.npy
python train.py --data data/pi_10000.npy --steps 100
python search.py --data data/pi_10000.npy --steps 100
```
For a random-digit control dataset:
```bash
python data.py --n 10000 --source random --seed 2026 --out data/random_10000.npy
python search.py --data data/random_10000.npy --steps 100 --output-dir runs/random
```
For a final evaluation only, freeze parameters recorded in `runs/sweep/best.json`, then call `train.py` with the same `--context`, `--embed`, `--hidden`, `--lr`, `--steps`, and `--test`. Do not optimize using test scores.

## Design
- Dataset: generated local pi digits with `mpmath`, no downloaded datasets required.
- Split: contiguous 80% train / 10% validation / 10% sealed test; no cross-split windows.
- Model: PyTorch embedding + MLP next-token classifier.
- Evaluation: validation cross-entropy (primary), accuracy (secondary), frequency and uniform baselines.
- Search: six reproducible hyperparameter candidates, logging all results. CUDA used when available.
- See [program.md](program.md) for scientific controls, test discipline, and extension suggestions.

## What counts as success?
10% is the **expected** accuracy of uniform independent guesses, not an exact finite-sample result. Test statistical uncertainty, replicate on independent digit regions, and compare against random-digit controls before asserting predictive structure. Even genuine finite-range predictability would not establish that pi is non-normal.

## Notes
- No remote training is started by committing this code.
- `runs/` and `data/` are gitignored to keep models and generated data out of version control.

# π Autoresearch — agent-directed research

This project studies whether a next-digit model trained on preceding decimal digits of pi can beat held-out predictive baselines, while controlling for overfitting. **Pi is computable; this is a test of learned short-context predictive structure, not the computability of pi itself.**

Inspired by [Karpathy's autoresearch](https://github.com/karpathy/autoresearch). It follows the agent-driven pattern: **propose code change → commit → train for equal compute → evaluate on validation → keep/revert → repeat**. See [program.md](program.md), the agent's operating instructions.

## Start on your local computer (GPU recommended)
```bash
git clone https://github.com/Nate27624/pi-autoresearch.git
cd pi-autoresearch
python -m venv .venv
# activate your environment; Windows PowerShell:
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m unittest discover -s tests -v
python data.py --n 100000 --source pi --out data/pi_100000.npy
python data.py --n 100000 --source random --out data/random_100000.npy
python train.py --data data/pi_100000.npy --steps 1000
```

Launch a code-editing CLI agent, such as Codex, **inside this repository** and give it this prompt:

> Read program.md completely. Set up a fresh autoresearch branch. First implement and validate a strict 300-second training-time budget in train.py and establish pi/random baselines. Then autonomously propose edits to train.py, train both candidates under identical budgets, compare held-out validation cross-entropy, commit winners, revert losers, log every run, and continue until manually stopped. Never touch the final test set during exploration.

The repository's original `search.py` is a **legacy fixed sweep**, not the autonomous engine; it is kept as a quick smoke-test convenience. The agent itself is responsible for edits and the research loop, as in upstream autoresearch. The initial `train.py` supports step-limited training only; the instructions require the agent to introduce and validate a timed loop before comparing architectures. No unattended GPU workload is started by this GitHub commit.

## Measurement
- Generated pi digits: `data.py` uses mpmath; verify long runs with a second source before publication.
- Contiguous train/validation/test 80/10/10 with independent windows per split.
- Primary metric: held-out validation cross-entropy in nats/digit; lower is better.
- Secondary: next-digit accuracy; reference uniform CE is `ln(10)` and uniform accuracy expectation is 10%.
- A matched pseudorandom digit corpus serves as a negative control.
- A sealed test split must be used only after research is frozen.

## Contents
- `program.md` — autonomous agent research specification.
- `train.py` — model and optimizer, **agent-editable**.
- `data.py`, `tests/` — data and integrity checks; not agent-editable during search.
- `search.py` — optional static six-candidate baseline only, **not** autoresearch.

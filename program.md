# PI Autoresearch — autonomous agent instructions

You are an autonomous ML researcher. Your objective is to discover a predictor of previously unseen decimal digits of pi with **lower validation cross-entropy** than the current best under equal compute. Study this file and the repository, then continue experimenting until the human stops you. This is NOT a static hyperparameter sweep.

## Setup
1. Create a new branch `autoresearch/<date-run>` from main; never experiment on main.
2. Read README.md, data.py, train.py, and this document. Run the unit tests.
3. Install requirements; generate a pinned dataset using `python data.py --n 100000 --source pi --out data/pi_100000.npy`. Verify the pi prefix. Generate `data/random_100000.npy` as matched negative control.
4. Run a baseline with `python train.py --data data/pi_100000.npy --steps 1000 --output runs/baseline.json`; verify the script emits finite validation metrics. Use a matching random-digit control run. Record hardware and baseline runtime.
5. Establish the fixed budget of **300 seconds per candidate on the same machine**. The baseline train.py currently uses a fixed number of steps, NOT a five-minute timer; before relying on cross-architecture comparisons, implement and validate a bounded wall-clock training loop in train.py. Startup and evaluation may be outside the budget, but all candidates must use the identical measured training budget. Record actual training seconds and seeds. If modifying the timing loop alters baseline performance, rerun the baseline.
6. Initialize `results.tsv` (untracked) with `commit\tval_ce\tval_accuracy\tcontrol_ce\ttrain_seconds\tstatus\tdescription`.

## Change boundaries
- **Agent may edit train.py only** for scientific experiments (including architecture, context length, losses, optimizers, training strategy, sampling, and hyperparameters).
- Do not edit data.py, tests/, or the evaluation split/metric to improve a score. Keep the 80/10/10 contiguous split, split-local contexts, and validation CE invariant.
- Do not inspect the final test split or report a final test score during iterative research. Do not turn on --test during exploration.
- Do not leak pi's known algorithm or positional information into features, pretrained checkpoints, training labels, or evaluation logic. This asks whether preceding *digits alone* help predict the next, not whether a program can calculate pi.
- You may read papers or reason about models to propose novel experiments. Git changes must be explainable and reproducible.

## Autonomous loop — repeat until stopped
1. Examine `results.tsv`, last improvement, current best code and recent failures. Formulate a testable hypothesis.
2. Edit **train.py** to implement ONE meaningful candidate: for example a causal Transformer, LSTM, convolutional sequence model, better embeddings, optimizer, conditioning strategy, regularizer, or context length.
3. Commit candidate code to the run branch with an informative message.
4. Run the same fixed 300-second train budget, capture stdout/stderr in `runs/latest.log`, and enforce a 10-minute external timeout including startup/evaluation. Extract validation CE and accuracy. Run matched random control with the SAME candidate and training budget, and record its CE.
5. If the candidate crashes, inspect failure, optionally repair it, log crash. If it improves pi validation CE and passes data-leakage checks, mark `keep`. Otherwise mark `discard` and revert to prior best commit (preserving untracked results).
6. Append each attempt — including crashes and rejected candidates — to `results.tsv`. Keep all runs auditable. Track comparison to uniform CE = ln(10) and training-frequency CE. Do not interpret noise as discovery.
7. Repeat without asking the user for each iteration. Try nontrivial architecture changes, not only a preset list.

## Evidence threshold
- Search uses validation only, which becomes adaptively overfit after enough experiments.
- Once a candidate is frozen, perform ONE held-out test, and compare against equally tuned random controls, independent pi digit regions, and a preregistered success threshold/confidence interval.
- Quantify effect sizes and uncertainty; accuracy above 10% on a single finite split is insufficient. Predictive gains would not prove pi is non-normal.
- Report negative findings without exaggeration.

## Agent launch
On a machine with compute and an **agent capable of shell access and editing code** (e.g. Codex CLI), open this project, instruct the agent: `Read program.md, set up a fresh autoresearch run, and then execute the autonomous loop continuously until I stop you.`
Merely storing this file on GitHub does not start a running agent, and neither the GitHub connector nor GitHub repository by itself provides GPU compute. Do not claim that a continuous run started until the local agent process actually launches.

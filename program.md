# Autoresearch protocol

Objective: Discover whether a sequence model predicts **unseen** decimal digits of pi better than controls.
Do not mistake deterministic computability of pi for short-context next-digit predictability.

## Immutable rules
1. Decimal digits start after the decimal point (first digit = 1).
2. Use contiguous train (first 80%), validation (next 10%) and test (last 10%). No shuffling across splits. Input contexts must be wholly within each split.
3. Tune only on validation cross-entropy (primary), report accuracy (secondary). Never inspect test outcomes while iterating.
4. Compare against uniform random guessing (10% expectation, CE ln(10)), train-frequency prior, and matched truly pseudorandom control data with identical splits, training budget, and selection procedure.
5. Multiple comparisons matter: optimize on validation, freeze architecture and hyperparameters, evaluate test once. Replicate across different *non-overlapping pi ranges* for stronger evidence, and use confidence intervals/effect sizes rather than isolated accuracy spikes.
6. Log every experiment (including failures), seed, data-source length, code revision, hyperparameters, metrics, and runtime. Do not claim evidence from unverified results.
7. Changes to this evaluation protocol are separate preregistered experiments, not retroactive adjustments.

## Autoresearch workflow
- Run `python search.py --data data/pi_10000.npy --steps 100` for a deterministic sweep.
- Inspect `runs/sweep/results.csv` and `runs/sweep/best.json`.
- Change model architecture or search candidates, then repeat using same validation protocol.
- If no robust validation improvement over frequency baseline and random controls, record the negative result.
- For a **single frozen finalist**, manually run `python train.py ... --test` with the selected configuration; report test results honestly, including failures.

## Scientific caveats
- The sweep is a bounded fixed candidate search, **not** a continuously autonomous agent. An LLM can propose and commit additional candidates externally while preserving this protocol.
- mpmath generates digits locally, not via a downloaded verified reference. Verify long datasets against an independent source before publication.
- This baseline uses small context-embedding MLPs; Transformers/LSTMs are future experiments, not implemented yet.
- Deterministic algorithms can emit seemingly random digits; outperforming random control on short holdout alone does not prove a global pattern or non-normality.

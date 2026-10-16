"""Deterministic digit acquisition, contiguous splits, and random control."""
import argparse
from pathlib import Path
import numpy as np
from mpmath import mp


def make_digits(n: int, source: str = 'pi', seed: int = 2026) -> np.ndarray:
    if n < 100:
        raise ValueError('Need at least 100 digits')
    if source == 'random':
        return np.random.default_rng(seed).integers(0, 10, size=n, dtype=np.int64)
    if source != 'pi':
        raise ValueError('source must be pi or random')
    # mp.dps denotes decimal precision; guard digits avoid tail rounding.
    mp.dps = n + 20
    s = mp.nstr(mp.pi, n + 21, strip_zeros=False)
    fraction = s.split('.')[1][:n]
    if len(fraction) != n:
        raise RuntimeError('Insufficient generated digits')
    return np.fromiter((ord(c)-48 for c in fraction), dtype=np.int64, count=n)


def splits(digits: np.ndarray, train_ratio=.8, val_ratio=.1):
    n = len(digits)
    a, b = int(n * train_ratio), int(n * (train_ratio + val_ratio))
    return digits[:a], digits[a:b], digits[b:]


def windows(seq: np.ndarray, context: int):
    # Each split is independent; never borrow context from another split.
    if context <= 0 or len(seq) <= context:
        raise ValueError('Context must be positive and smaller than split')
    x = np.lib.stride_tricks.sliding_window_view(seq, context + 1)
    return x[:, :-1].copy(), x[:, -1].copy()


def save_digits(path: Path, n: int, source: str, seed: int):
    path.parent.mkdir(parents=True, exist_ok=True)
    np.save(path, make_digits(n, source, seed))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--n', type=int, default=10000)
    p.add_argument('--source', choices=['pi','random'], default='pi')
    p.add_argument('--seed', type=int, default=2026)
    p.add_argument('--out', type=Path, default=Path('data/pi_10000.npy'))
    a = p.parse_args()
    save_digits(a.out, a.n, a.source, a.seed)
    print(f'Saved {a.n} {a.source} digits to {a.out}')

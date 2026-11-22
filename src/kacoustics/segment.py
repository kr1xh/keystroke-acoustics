"""Cut a recording of repeated presses of one key into one clip per press.

A key press makes a click (key down) and a quieter click about 100 ms later (key up).
Presses are found on a short-window energy envelope: a press starts where the envelope
rises above a threshold, and a lockout after each press stops the release click from
being counted again. The clip window is long enough to hold both clicks.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .audio import load_audio


def envelope(y: np.ndarray, sr: int, hop_ms: float = 2.5) -> tuple[np.ndarray, int]:
    """RMS energy per hop. Returns (envelope, hop length in samples)."""
    hop = max(1, int(sr * hop_ms / 1000))
    n = len(y) // hop
    frames = y[: n * hop].reshape(n, hop)
    return np.sqrt((frames ** 2).mean(axis=1)), hop


def _rising_edges(env: np.ndarray, threshold: float, gap: int) -> list[int]:
    above = env > threshold
    edges = np.flatnonzero(above & ~np.concatenate(([False], above[:-1])))
    kept: list[int] = []
    for e in edges:
        if not kept or e - kept[-1] >= gap:
            kept.append(int(e))
    return kept


def find_presses(y: np.ndarray, sr: int, expected: int | None = None, min_gap: float = 0.25) -> list[int]:
    """Sample index where each press starts.

    Without `expected`, the threshold sits well above the background noise. With it,
    the threshold is the highest one whose press count is closest to `expected`, so
    quiet recordings still come out right.
    """
    env, hop = envelope(y, sr)
    if not len(env):
        return []
    gap = max(1, int(min_gap * sr / hop))
    noise = float(np.median(env))
    spread = float(np.median(np.abs(env - noise))) or 1e-9
    if expected is None:
        threshold = noise + 12 * spread
        return [e * hop for e in _rising_edges(env, threshold, gap)]
    peak = float(env.max())
    candidates = np.geomspace(max(peak * 0.9, 1e-9), max(noise + 3 * spread, 1e-9), 80)
    best, best_err = [], None
    for t in candidates:
        edges = _rising_edges(env, t, gap)
        err = abs(len(edges) - expected)
        if best_err is None or err < best_err:
            best, best_err = edges, err
    return [e * hop for e in best]


def cut(y: np.ndarray, sr: int, onsets: list[int], before: float = 0.01, length: float = 0.33) -> np.ndarray:
    """Fixed-length clips starting `before` seconds ahead of each onset, zero-padded at the edges."""
    n, pre = int(length * sr), int(before * sr)
    padded = np.concatenate([np.zeros(pre), y, np.zeros(n)])
    return np.stack([padded[o: o + n] for o in onsets]) if onsets else np.zeros((0, n))


@dataclass
class Segmented:
    clips: np.ndarray
    onsets: list[int]
    expected: int | None
    sr: int

    @property
    def found(self) -> int:
        return len(self.onsets)

    @property
    def ok(self) -> bool:
        """Found count within 5% of what was pressed (always true when nothing was expected)."""
        return self.expected is None or abs(self.found - self.expected) <= max(1, round(0.05 * self.expected))


def segment_file(path: str | Path, expected: int | None = 40, sr: int = 44_100) -> Segmented:
    y = load_audio(path, sr)
    onsets = find_presses(y, sr, expected=expected)
    return Segmented(cut(y, sr, onsets), onsets, expected, sr)

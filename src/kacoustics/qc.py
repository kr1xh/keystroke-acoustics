"""Quality check for a folder of recordings (one file per key).

    python -m kacoustics.qc data/raw/session-1 --expected 40

Prints presses found per key, peak and noise levels, flags clipping and missing keys,
and saves a waveform plot with the detected presses for each file.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

from . import KEYS
from .audio import load_audio
from .segment import envelope, find_presses

AUDIO_EXT = {".m4a", ".wav", ".mp3", ".aac", ".ogg", ".flac", ".opus", ".3gp", ".amr"}


def rms_db(y: np.ndarray) -> float:
    return float(20 * np.log10(np.sqrt(np.mean(np.square(y))) + 1e-12))


def is_clipped(y: np.ndarray, limit: float = 0.99) -> bool:
    return bool(np.max(np.abs(y)) >= limit) if len(y) else False


def missing_keys(found: set[str]) -> list[str]:
    return [k for k in KEYS if k not in found]


def plot(y: np.ndarray, sr: int, onsets: list[int], out: Path, title: str) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    t = np.arange(len(y)) / sr
    fig, ax = plt.subplots(figsize=(12, 2.5))
    ax.plot(t, y, linewidth=0.4)
    for o in onsets:
        ax.axvline(o / sr, color="red", linewidth=0.6)
    ax.set_title(title)
    ax.set_xlabel("seconds")
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=90)
    plt.close(fig)


def check_folder(folder: str | Path, expected: int = 40, plot_dir: str | Path | None = None, sr: int = 44_100) -> list[dict]:
    rows = []
    for f in sorted(Path(folder).iterdir()):
        if f.suffix.lower() not in AUDIO_EXT:
            continue
        y = load_audio(f, sr)
        onsets = find_presses(y, sr, expected=expected)
        env, _ = envelope(y, sr)
        tol = max(1, round(0.05 * expected))
        rows.append({
            "key": f.stem.lower(), "found": len(onsets), "expected": expected,
            "ok": abs(len(onsets) - expected) <= tol,
            "seconds": round(len(y) / sr, 1),
            "peak_db": round(20 * np.log10(np.max(np.abs(y)) + 1e-12), 1) if len(y) else None,
            "noise_db": round(20 * np.log10(np.median(env) + 1e-12), 1) if len(env) else None,
            "clipped": is_clipped(y),
        })
        if plot_dir is not None:
            plot(y, sr, onsets, Path(plot_dir) / f"{f.stem}.png", f"{f.name}: {len(onsets)} presses (expected {expected})")
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder")
    ap.add_argument("--expected", type=int, default=40)
    ap.add_argument("--plots", help="folder for waveform plots (default: results/qc/<folder name>)")
    args = ap.parse_args(argv)
    plots = Path(args.plots) if args.plots else Path("results") / "qc" / Path(args.folder).name
    rows = check_folder(args.folder, args.expected, plots)
    print(f"{'key':<7}{'found':>6}{'peak dB':>9}{'noise dB':>10}  status")
    for r in rows:
        status = "ok" if r["ok"] and not r["clipped"] else ("CLIPPED " if r["clipped"] else "") + ("" if r["ok"] else "COUNT OFF")
        print(f"{r['key']:<7}{r['found']:>6}{r['peak_db']:>9}{r['noise_db']:>10}  {status.strip()}")
    gone = missing_keys({r["key"] for r in rows})
    if gone and args.expected == 40:
        print("missing keys:", ", ".join(gone))
    print(f"plots: {plots}")
    bad = [r for r in rows if not r["ok"] or r["clipped"]]
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

"""Fail if recordings, derived data or model weights are about to be committed.

Usage: python scripts/check_data_guard.py          (staged files)
       python scripts/check_data_guard.py --all    (every tracked file, used in CI)
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BLOCKED = [
    (re.compile(r"\.(wav|m4a|mp3|aac|ogg|opus|flac)$", re.I), "audio recording"),
    (re.compile(r"\.(npy|npz|pt|pth|ckpt|onnx)$", re.I), "derived data or model weights"),
    (re.compile(r"(^|/)(data|results|models)/"), "data, results or models folder"),
]


def check(paths: list[str]) -> list[str]:
    return [f"{p}: {why}" for p in paths for rx, why in BLOCKED if rx.search(p.replace("\\", "/"))]


def tracked(all_files: bool) -> list[str]:
    cmd = ["git", "ls-files"] if all_files else ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"]
    return [l for l in subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, check=True).stdout.splitlines() if l]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--all", action="store_true")
    problems = check(tracked(ap.parse_args(argv).all))
    for p in problems:
        print(f"blocked: {p}", file=sys.stderr)
    if not problems:
        print("ok: no recordings, data or weights")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

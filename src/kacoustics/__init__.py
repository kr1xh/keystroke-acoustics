"""Acoustic keystroke classification: recordings -> key presses -> spectrograms -> classifier."""

KEYS = [chr(c) for c in range(ord("a"), ord("z") + 1)] + ["space"]

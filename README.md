# keystroke-acoustics

Can a phone lying next to a laptop tell which keys you press, just from the sound? This project rebuilds the experiment from Harrison, Toreini and Mehrnezhad, [A Practical Deep Learning-Based Acoustic Side Channel Attack on Keyboards](https://arxiv.org/abs/2308.01074) (IEEE EuroS&P Workshops 2023), on one laptop keyboard, and measures how much of their result holds up.

> Status: early. Built in milestones; see the issues.

## Plan

1. Record each key many times with a phone next to the laptop.
2. Cut the recordings into one clip per key press.
3. Turn each clip into a mel-spectrogram.
4. Train an image classifier (a small CNN, then a pretrained ResNet-18) to name the key.
5. Test honestly on a recording session the model never saw, and over a Zoom-like compressed channel.

## Ethics

This is done on my own keyboard, with my own typing, to understand the attack and its limits. The recordings are not published. The practical defence is simple: do not type passwords during calls or near an open microphone, and let a password manager fill them in.

## License

MIT

## Setup

```
uv venv .venv --python 3.12
uv pip install --python .venv -e ".[dev,train]"
git config core.hooksPath .githooks     # blocks committing recordings or weights
.venv/Scripts/python -m pytest -q
```

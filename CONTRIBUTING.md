# Contributing

## Setup

```bash
uv venv --python 3.12 .venv
uv pip install -p .venv -e ".[dev,train]"
git config core.hooksPath .githooks   # runs the data guard before every commit
python -m pytest -q
```

ffmpeg must be on `PATH` (it decodes the phone recordings).

## Rules

- **Recordings never go in git.** They are someone's typing. They live in `data/raw/` (ignored), and the guard blocks audio, derived data, model weights and the `data/`, `results/` and `models/` folders. Do not attach recordings to issues.
- **Only record your own keyboard**, with consent from anyone else in the room. See the ethics note in the README.
- **Test first.** Segmentation, features and evaluation get a test on synthetic audio before the code is written.
- **One issue, one PR.** The PR says `Closes #n` and fills in the template, including the Ponytail rung.
- **Report honestly.** Say which sessions trained and which tested. A random split leaks across presses from the same session, so the session split is the headline number.

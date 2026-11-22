# Recording protocol

The model can only learn what the recordings contain, so every session is recorded the same way. Anything that changes between keys (the phone moving, a fan turning on) can be learned instead of the key.

## Setup (same every session)

- **Keyboard:** the laptop's built-in keyboard, on the same desk.
- **Phone:** lying flat, screen up, 10-20 cm to the left of the laptop, microphone end pointing at the keyboard. Mark the spot with tape so it is identical every time.
- **Room:** quiet; no music, fan or AC changing during a session. Laptop charger in the same state each time.
- **App:** any voice recorder that saves a file (the default one is fine). Highest quality setting; m4a or wav both work.

## Keys

27 keys: `a` to `z` and `space`.

## One file per key

For each key:

1. Start recording and wait about 2 seconds.
2. Press that key **40 times**, about once per second, with your normal typing force. Press only that key.
3. Wait about 2 seconds and stop.
4. Name the file after the key: `a.m4a`, `b.m4a`, ..., `space.m4a`.

A session is all 27 files and takes about 15-20 minutes. Short breaks between keys are fine; do not move the phone.

## Sessions

Record **3 sessions on different days**. Sessions 1 and 2 are for training; session 3 is the test set the model never sees during training. This is what makes the result honest: a model tested on presses from the same recording it trained on can look far better than it is.

## Pilot first

Before session 1, record one short file: the `a` key pressed **5 times**. It is used to check loudness and that the presses can be cut out cleanly.

## Where the files go

Copy them to the laptop (USB, Google Drive, any route) into:

```
data/raw/pilot/a.m4a
data/raw/session-1/a.m4a ... space.m4a
data/raw/session-2/...
data/raw/session-3/...
```

`data/` is ignored by git and blocked by the pre-commit hook; recordings are never published.

## Write down

For each session note the date, the laptop's power state and anything unusual (a sneeze, a mistyped key) in `data/raw/session-N/notes.txt`. A mistyped key in a file is fine if you note roughly where it happened.

## Check each session

```
.venv/Scripts/python -m kacoustics.qc data/raw/session-1 --expected 40
.venv/Scripts/python -m kacoustics.qc data/raw/pilot --expected 5
```

It prints presses found per key, peak and background-noise levels, and flags clipping (too loud: move the phone back a little) or a count that is off by more than 5% (usually a mistyped key or a noise). Waveform plots with each detected press marked go to `results/qc/<session>/`. Re-record any key that fails.

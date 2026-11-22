import numpy as np

from kacoustics import segment

SR = 44_100


def burst(sr, ms=15, amp=0.8, seed=0):
    """A short decaying noise burst, roughly what a key click looks like."""
    rng = np.random.default_rng(seed)
    n = int(sr * ms / 1000)
    return amp * rng.standard_normal(n) * np.exp(-np.linspace(0, 6, n))


def signal_with_clicks(times, release_after=None, amp=0.8, seconds=None, sr=SR, seed=1):
    length = seconds or (max(times) + 1.0)
    rng = np.random.default_rng(seed)
    y = 0.002 * rng.standard_normal(int(sr * length))
    for i, t in enumerate(times):
        for start, a in [(t, amp)] + ([(t + release_after, amp * 0.4)] if release_after else []):
            b = burst(sr, amp=a, seed=i + 10)
            s = int(start * sr)
            y[s:s + len(b)] += b
    return y


def test_finds_every_press_at_the_right_time():
    times = [1.0 + i * 0.8 for i in range(10)]
    onsets = segment.find_presses(signal_with_clicks(times), SR)
    assert len(onsets) == 10
    assert all(abs(o / SR - t) < 0.01 for o, t in zip(onsets, times))


def test_release_click_is_not_counted_as_a_second_press():
    times = [1.0 + i * 0.8 for i in range(8)]
    onsets = segment.find_presses(signal_with_clicks(times, release_after=0.09), SR)
    assert len(onsets) == 8


def test_expected_count_recovers_quiet_presses():
    times = [1.0 + i * 0.8 for i in range(12)]
    y = signal_with_clicks(times, amp=0.05)
    assert len(segment.find_presses(y, SR, expected=12)) == 12


def test_cut_returns_fixed_length_clips_even_at_the_edges():
    y = np.zeros(SR)
    clips = segment.cut(y, SR, [0, SR // 2, SR - 10], length=0.33)
    assert clips.shape == (3, int(0.33 * SR))


def test_clip_starts_slightly_before_the_onset():
    y = np.zeros(SR)
    y[SR // 2] = 1.0
    clip = segment.cut(y, SR, [SR // 2], before=0.01, length=0.1)[0]
    assert np.argmax(clip) == int(0.01 * SR)


def test_segment_file_reads_a_phone_style_m4a(tmp_path):
    import subprocess

    import soundfile as sf

    times = [1.0 + i * 0.9 for i in range(6)]
    wav = tmp_path / "a.wav"
    sf.write(wav, signal_with_clicks(times, release_after=0.1).astype("float32"), SR)
    m4a = tmp_path / "a.m4a"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(wav), "-c:a", "aac", "-b:a", "128k", str(m4a)], check=True)
    seg = segment.segment_file(m4a, expected=6)
    assert seg.found == 6 and seg.ok
    assert seg.clips.shape == (6, int(0.33 * SR))

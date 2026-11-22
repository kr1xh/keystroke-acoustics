import numpy as np
import soundfile as sf

from kacoustics import qc
from test_segment import SR, signal_with_clicks


def test_level_db_of_full_scale_sine_is_about_minus_3():
    t = np.arange(SR) / SR
    assert abs(qc.rms_db(np.sin(2 * np.pi * 440 * t)) - (-3.0)) < 0.1


def test_clipping_is_flagged():
    assert qc.is_clipped(np.array([0.0, 0.5, 0.999]))
    assert not qc.is_clipped(np.array([0.0, 0.5, 0.9]))


def test_check_folder_reports_each_key_and_saves_plots(tmp_path):
    for key, n in [("a", 5), ("b", 4)]:
        times = [1.0 + i * 0.9 for i in range(n)]
        sf.write(tmp_path / f"{key}.wav", signal_with_clicks(times).astype("float32"), SR)
    rows = qc.check_folder(tmp_path, expected=5, plot_dir=tmp_path / "plots")
    by_key = {r["key"]: r for r in rows}
    assert by_key["a"]["found"] == 5 and by_key["a"]["ok"]
    assert by_key["b"]["found"] == 4 and by_key["b"]["ok"]  # one off out of 5 is within tolerance
    assert (tmp_path / "plots" / "a.png").exists()


def test_missing_keys_are_listed():
    assert qc.missing_keys({"a", "b"})[:3] == ["c", "d", "e"]
    assert "space" in qc.missing_keys({"a"})

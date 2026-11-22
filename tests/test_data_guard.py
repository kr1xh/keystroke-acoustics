import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import check_data_guard as guard  # noqa: E402


def test_code_and_docs_pass():
    assert guard.check(["README.md", "src/kacoustics/segment.py", "docs/recording-protocol.md"]) == []


def test_audio_and_model_files_are_blocked():
    for path in ["a.wav", "data/raw/session-1/space.m4a", "x.MP3", "models/resnet.pt", "feats.npy"]:
        assert guard.check([path]), path


def test_data_and_results_folders_are_blocked():
    assert guard.check(["data/segments/a_001.json"])
    assert guard.check(["results/metrics.json"])


def test_report_figures_are_allowed():
    assert guard.check(["docs/figures/confusion_matrix.png"]) == []

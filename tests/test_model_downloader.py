
import pytest
from unittest import mock
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))
from gitcommitai.model_downloader import interactive_model_selector, PHI3_MODELS
@pytest.fixture
def mock_input(monkeypatch):
    def _mock_input(inputs):
        input_iter = iter(inputs)
        monkeypatch.setattr("builtins.input", lambda _: next(input_iter))
    return _mock_input

@pytest.fixture
def mock_download(monkeypatch):
    monkeypatch.setattr("urllib.request.urlretrieve", lambda url, path: Path(path).touch())

@pytest.fixture(autouse=True)
def cleanup_downloads():
    yield
    for file in Path("models").glob("*.gguf"):
        file.unlink()

def test_default_selection(monkeypatch, mock_input, mock_download):
    # Simulate pressing Enter, then 'yes'
    mock_input(["", "y"])
    selected_quant = interactive_model_selector(PHI3_MODELS)
    assert selected_quant in {"IQ3_S", "Q4_K_M"}

def test_manual_selection(monkeypatch, mock_input, mock_download):
    # Simulate choosing option 3 (Q6_K), then confirming
    mock_input(["3", "y"])
    selected_quant = interactive_model_selector(PHI3_MODELS)
    assert selected_quant == "Q6_K"

def test_invalid_input_then_exit(monkeypatch, mock_input):
    mock_input(["invalid"])
    with pytest.raises(SystemExit):
        interactive_model_selector(PHI3_MODELS)

def test_skip_existing(monkeypatch, mock_input):
    # Create fake downloaded file
    filename = "Phi-3-mini-4k-instruct-Q4_K_M.gguf"
    path = Path("models") / filename
    path.parent.mkdir(exist_ok=True)
    path.write_text("dummy")

    mock_input(["2", "y"])
    with mock.patch("urllib.request.urlretrieve") as mocked:
        quant = interactive_model_selector(PHI3_MODELS)
        mocked.assert_not_called()
        assert quant == "Q4_K_M"

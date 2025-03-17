import subprocess
import pytest
from core.parsers.DeltaMetricsExtractor import DeltaMetricsExtractor


@pytest.fixture
def dummy_jar(tmp_path):
    """
    Create a dummy JAR file for testing.
    """
    jar = tmp_path / "dummy.jar"
    jar.write_text("dummy content")
    return str(jar)


def test_calculate_deltas(dummy_jar):
    """
    Test that calculate_deltas computes the correct delta between new and old metrics.
    """
    extractor = DeltaMetricsExtractor(dummy_jar)
    new_data = {
        "metric1": 10,
        "metric2": 5,
        "nested": {"metric3": 20},
    }
    old_data = {
        "metric1": 5,
        "metric2": 5,
        "nested": {"metric3": 15},
    }
    expected = {
        "metric1": 5,
        "metric2": 0,
        "nested": {"metric3": 5},
    }
    delta = extractor.calculate_deltas(new_data, old_data)
    assert delta == expected


def test_extract_metrics_empty(caplog, dummy_jar):
    """
    When no modified blocks are provided, extract_metrics should log a warning and return an empty dict.
    """
    extractor = DeltaMetricsExtractor(dummy_jar)
    result = extractor.extract_metrics({})
    assert result == {}
    assert "Aucun bloc Terraform modifié à analyser." in caplog.text


def test_extract_metrics_integration(monkeypatch, dummy_jar):
    """
    Test extract_metrics integration by simulating:
      - terra_adapter.extract_metrics returns new metrics,
      - get_previous_metrics is overridden to return dummy previous metrics.
    The expected result is the delta computed between these two.
    """
    extractor = DeltaMetricsExtractor(dummy_jar)

    # Define a dummy adapter that returns fixed metrics.
    class DummyAdapter:
        def extract_metrics(self, blocks):
            return {"file1.tf": {"metric": 20}}

    extractor.terra_adapter = DummyAdapter()
    # Override get_previous_metrics to simulate previous metrics.
    extractor.get_previous_metrics = lambda modified_blocks: {"file1.tf": {"metric": 10}}

    modified_blocks = {"file1.tf": ["some block content"]}
    result = extractor.extract_metrics(modified_blocks)
    expected = {"file1.tf": {"metric": 10}}  # 20 - 10 = 10
    assert result == expected


def test_compare_metrics(dummy_jar):
    """
    Test compare_metrics by providing before and after metrics with a common block that has differences.
    """
    extractor = DeltaMetricsExtractor(dummy_jar)
    before_metrics = {
        "file1.tf": {
            "data": [
                {
                    "block": "resource",
                    "block_name": "example",
                    "lines": 10,
                    "other": 100,
                }
            ]
        }
    }
    after_metrics = {
        "file1.tf": {
            "data": [
                {
                    "block": "resource",
                    "block_name": "example",
                    "lines": 15,
                    "other": 100,
                }
            ]
        }
    }
    differences = extractor.compare_metrics(before_metrics, after_metrics)
    expected = {
        "file1.tf": {
            "resource example": {
                "lines": {"old": 10, "new": 15, "delta": 5}
            }
        }
    }
    assert differences == expected


def test_get_previous_metrics_no_commit(monkeypatch, caplog, dummy_jar):
    """
    When no previous commit hash is found for a file, get_previous_metrics should warn and skip that file.
    """
    extractor = DeltaMetricsExtractor(dummy_jar)
    # Replace terra_adapter.extract_metrics with a dummy that won't be called.
    extractor.terra_adapter = type("Dummy", (), {"extract_metrics": lambda self, blocks: {}})()

    def fake_run(args, capture_output, text):
        # Simulate git log returning an empty commit hash.
        if args[0] == "git" and args[1] == "log":
            class FakeCompletedProcess:
                stdout = ""
            return FakeCompletedProcess()
        else:
            class FakeCompletedProcess:
                stdout = ""
                returncode = 1
            return FakeCompletedProcess()

    monkeypatch.setattr(subprocess, "run", fake_run)
    modified_blocks = {"file1.tf": ["block content"]}
    prev_metrics = extractor.get_previous_metrics(modified_blocks)
    # Since no commit hash was found, no previous metrics should be added.
    assert prev_metrics == {}
    assert "Aucun commit précédent trouvé pour file1.tf." in caplog.text


def test_get_previous_metrics_success(monkeypatch, dummy_jar):
    """
    Test get_previous_metrics when a previous commit is successfully found.
    Simulate subprocess.run calls to return a fake commit hash and file content.
    The DummyAdapter then returns dummy metrics from the simulated previous file.
    """
    extractor = DeltaMetricsExtractor(dummy_jar)

    class DummyAdapter:
        def extract_metrics(self, blocks):
            # Assume blocks is a dict with a single file key.
            filename = list(blocks.keys())[0]
            return {filename: {"data": [{"dummy_metric": 42}]}}

    extractor.terra_adapter = DummyAdapter()

    def fake_run(args, capture_output, text):
        if "log" in args:
            class FakeCompletedProcess:
                stdout = "abc123"
            return FakeCompletedProcess()
        elif "show" in args:
            class FakeCompletedProcess:
                stdout = "block1\n\nblock2"
                returncode = 0
            return FakeCompletedProcess()
        else:
            raise ValueError("Unexpected command: " + " ".join(args))

    monkeypatch.setattr(subprocess, "run", fake_run)
    modified_blocks = {"file1.tf": ["block content"]}
    prev_metrics = extractor.get_previous_metrics(modified_blocks)
    expected = {"file1.tf": {"data": [{"dummy_metric": 42}]}}
    assert prev_metrics == expected


def test_display_differences(caplog, dummy_jar):
    """
    Test display_differences by setting old_metrics and new_metrics on the extractor.
    Capture the log output to verify that the expected sections are logged and that
    the analysis_results dict is updated with computed differences.
    """
    extractor = DeltaMetricsExtractor(dummy_jar)
    extractor.old_metrics = {
        "file1.tf": {
            "data": [
                {
                    "block": "resource",
                    "block_name": "example",
                    "lines": 10,
                    "other": 100,
                }
            ]
        }
    }
    extractor.new_metrics = {
        "file1.tf": {
            "data": [
                {
                    "block": "resource",
                    "block_name": "example",
                    "lines": 15,
                    "other": 100,
                }
            ]
        }
    }
    analysis_results = {}
    extractor.display_differences(analysis_results)
    logged = caplog.text
    # Verify that key sections are logged.
    assert "Comparaison des métriques avant et après les changements" in logged
    assert "AVANT le changement" in logged
    assert "APRÈS le changement" in logged
    assert "DIFFÉRENCES" in logged
    # Check that a difference in "lines" is reported (the arrow and delta may include symbols).
    assert "10 → 15" in logged or "15 → 10" not in logged
    # The analysis_results dict should now contain a "differences" key with computed differences.
    expected_diff = {
        "file1.tf": {
            "resource example": {
                "lines": {"old": 10, "new": 15, "delta": 5}
            }
        }
    }
    assert "differences" in analysis_results
    assert analysis_results["differences"] == expected_diff

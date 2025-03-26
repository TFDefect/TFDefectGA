from core.parsers.delta_metrics_extractor import DeltaMetricsExtractor


def test_compute_delta_metrics_with_real_keys():
    extractor = DeltaMetricsExtractor(jar_path="libs/terraform_metrics-1.0.jar")

    metrics_before = {
        "data": [
            {
                "block_identifiers": "resource aws_instance example",
                "numTokens": 32,
                "avgMccabeCC": 1.0,
                "numVars": 1,
                "textEntropyMeasure": 4.67,
            }
        ]
    }

    metrics_after = {
        "data": [
            {
                "block_identifiers": "resource aws_instance example",
                "numTokens": 35,
                "avgMccabeCC": 2.0,
                "numVars": 2,
                "textEntropyMeasure": 4.97,
            }
        ]
    }

    result = extractor._compute_delta_metrics(metrics_before, metrics_after)
    deltas = result["resource aws_instance example"]

    assert deltas["numTokens_delta"] == 3
    assert deltas["avgMccabeCC_delta"] == 1.0
    assert deltas["numVars_delta"] == 1
    assert round(deltas["textEntropyMeasure_delta"], 2) == 0.30


def test_delta_when_block_missing_in_before():
    extractor = DeltaMetricsExtractor(jar_path="libs/terraform_metrics-1.0.jar")

    metrics_before = {
        "data": [
            {
                "block_identifiers": "resource aws_security_group sg_allow",
                "numTokens": 10,
            }
        ]
    }

    metrics_after = {
        "data": [
            {"block_identifiers": "resource aws_instance example", "numTokens": 35}
        ]
    }

    result = extractor._compute_delta_metrics(metrics_before, metrics_after)

    # Le bloc "aws_instance example" n'existait pas avant -> pas de delta attendu
    assert "resource aws_instance example" not in result


def test_delta_with_missing_data_key():
    extractor = DeltaMetricsExtractor(jar_path="libs/terraform_metrics-1.0.jar")

    # missing "data" key
    metrics_before = {}
    metrics_after = {}

    result = extractor._compute_delta_metrics(metrics_before, metrics_after)
    assert "error" in result
    assert "data" not in metrics_before or "data" not in metrics_after


def test_delta_with_empty_data_list():
    extractor = DeltaMetricsExtractor(jar_path="libs/terraform_metrics-1.0.jar")

    metrics_before = {"data": []}
    metrics_after = {"data": []}

    result = extractor._compute_delta_metrics(metrics_before, metrics_after)
    assert "error" in result

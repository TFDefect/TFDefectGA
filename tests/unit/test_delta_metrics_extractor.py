from core.parsers.delta_metrics_extractor import DeltaMetricsExtractor


def test_compute_delta_metrics_with_real_keys():
    """
    Teste la méthode `_compute_delta_metrics` pour vérifier qu'elle calcule correctement
    les deltas entre deux ensembles de métriques avec des clés valides.

    Scénario :
        - Les métriques avant et après modification sont fournies pour un bloc Terraform.
        - Les métriques incluent des propriétés telles que `numTokens`, `avgMccabeCC`, etc.
        - La méthode `_compute_delta_metrics` est appelée avec ces métriques.

    Assertions :
        - Vérifie que les deltas calculés pour chaque propriété sont corrects.
        - Vérifie que les valeurs des deltas sont arrondies correctement si nécessaire.

    Returns:
        None
    """
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
    """
    Teste la méthode `_compute_delta_metrics` pour vérifier le comportement
    lorsqu'un bloc est présent dans `metrics_after` mais absent dans `metrics_before`.

    Scénario :
        - Les métriques avant modification contiennent un bloc différent.
        - Les métriques après modification incluent un nouveau bloc.
        - La méthode `_compute_delta_metrics` est appelée avec ces métriques.

    Assertions :
        - Vérifie que le nouveau bloc n'est pas inclus dans les résultats des deltas.

    Returns:
        None
    """
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

    assert "resource aws_instance example" not in result


def test_delta_with_missing_data_key():
    """
    Teste la méthode `_compute_delta_metrics` pour vérifier le comportement
    lorsque la clé `data` est absente dans les métriques fournies.

    Scénario :
        - Les métriques avant et après modification ne contiennent pas la clé `data`.
        - La méthode `_compute_delta_metrics` est appelée avec ces métriques.

    Assertions :
        - Vérifie que le résultat contient une erreur indiquant l'absence de la clé `data`.

    Returns:
        None
    """
    extractor = DeltaMetricsExtractor(jar_path="libs/terraform_metrics-1.0.jar")

    metrics_before = {}
    metrics_after = {}

    result = extractor._compute_delta_metrics(metrics_before, metrics_after)
    assert "error" in result
    assert "data" not in metrics_before or "data" not in metrics_after


def test_delta_with_empty_data_list():
    """
    Teste la méthode `_compute_delta_metrics` pour vérifier le comportement
    lorsque les listes `data` dans les métriques avant et après modification sont vides.

    Scénario :
        - Les métriques avant et après modification contiennent des listes `data` vides.
        - La méthode `_compute_delta_metrics` est appelée avec ces métriques.

    Assertions :
        - Vérifie que le résultat contient une erreur indiquant que les listes `data` sont vides.

    Returns:
        None
    """
    extractor = DeltaMetricsExtractor(jar_path="libs/terraform_metrics-1.0.jar")

    metrics_before = {"data": []}
    metrics_after = {"data": []}

    result = extractor._compute_delta_metrics(metrics_before, metrics_after)
    assert "error" in result

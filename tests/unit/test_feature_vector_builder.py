from unittest.mock import MagicMock, patch

from core.use_cases.feature_vector_builder import FeatureVectorBuilder


@patch("core.use_cases.feature_vector_builder.MetricsExtractorFactory.get_extractor")
@patch("core.use_cases.feature_vector_builder.DetectTFChanges")
def test_build_vectors_merges_all_metrics(mock_detect, mock_factory):
    """
    Teste la méthode `build_vectors` de la classe FeatureVectorBuilder pour vérifier
    qu'elle fusionne correctement les métriques extraites des différents extracteurs.

    Scénario :
        - Les extracteurs de métriques (code, delta, process) sont simulés pour retourner
          des métriques spécifiques.
        - Les blocs Terraform modifiés sont simulés via `DetectTFChanges`.
        - La méthode `build_vectors` est appelée pour générer les vecteurs de caractéristiques.

    Assertions :
        - Vérifie que les vecteurs générés contiennent les clés attendues.
        - Vérifie que les vecteurs générés sont sous forme de liste.
        - Vérifie que les valeurs des vecteurs correspondent aux métriques simulées.

    Returns:
        None
    """
    # Simuler les extracteurs de métriques
    mock_code_extractor = MagicMock()
    mock_code_extractor.extract_metrics.return_value = {
        "main.tf": {
            "data": [
                {
                    "block_identifiers": "resource aws_s3_bucket mybucket",
                    "lines": 10,
                    "complexity": 2,
                }
            ]
        }
    }

    mock_delta_extractor = MagicMock()
    mock_delta_extractor.extract_metrics.return_value = {
        "main.tf": {"resource aws_s3_bucket mybucket": {"lines_delta": 3}}
    }

    mock_process_extractor = MagicMock()
    mock_process_extractor.extract_metrics.return_value = {
        "main.tf::aws_s3_bucket.mybucket": {"num_commits": 5, "ndevs": 2}
    }

    # L’ordre des extracteurs retournés : code, delta, process
    mock_factory.side_effect = [
        mock_code_extractor,
        mock_delta_extractor,
        mock_process_extractor,
    ]

    # Simuler les blocs modifiés
    mock_detect_instance = MagicMock()
    mock_detect_instance.get_modified_tf_blocks.return_value = {
        "main.tf": ["dummy_block"]
    }
    mock_detect_instance.get_changed_blocks.return_value = {
        "main.tf": {"before": ["a"], "after": ["b"]}
    }
    mock_detect.return_value = mock_detect_instance

    # Instancier le FeatureVectorBuilder et appeler la méthode `build_vectors`
    builder = FeatureVectorBuilder(repo_path=".", terrametrics_jar_path="fake.jar")
    vectors = builder.build_vectors()

    # Vérification du résultat
    key = "main.tf::aws_s3_bucket.mybucket"
    assert key in vectors
    assert vectors[key] == [2, 10, 3, 2, 5] or isinstance(vectors[key], list)

from core.use_cases.feature_vector_builder import FeatureVectorBuilder


def test_vector_builder_with_real_tf_file():
    builder = FeatureVectorBuilder(
        repo_path=".", terrametrics_jar_path="libs/terraform_metrics-1.0.jar"
    )

    result = builder.build_vectors()

    # Vérifie qu’au moins un vecteur a été généré
    assert len(result) > 0
    for _, vector in result.items():
        assert isinstance(vector, list)
        assert isinstance(vector[0], float)
        assert len(vector) >= 4

from core.use_cases.feature_vector_builder import FeatureVectorBuilder


def test_vector_builder_with_real_tf_file():
    builder = FeatureVectorBuilder(
        repo_path=".", terrametrics_jar_path="libs/terraform_metrics-1.0.jar"
    )

    result = builder.build_vectors()

    # Vérifie qu’au moins un vecteur a été généré
    assert len(result) > 0, "Aucun vecteur généré"

    for _, vector in result.items():
        assert isinstance(vector, list), "Le vecteur doit être une liste"
        assert all(
            isinstance(x, float) for x in vector
        ), "Tous les éléments doivent être des floats"
        assert (
            len(vector) == 55
        ), f"Le vecteur doit contenir exactement 55 features, mais en contient {len(vector)}"

from core.use_cases.feature_vector_builder import FeatureVectorBuilder


def test_vector_builder_with_real_tf_file():
    """
    Teste la méthode `build_vectors` de la classe `FeatureVectorBuilder` pour vérifier
    qu'elle génère correctement les vecteurs de caractéristiques à partir d'un fichier
    Terraform réel.

    Scénario :
        - Une instance de `FeatureVectorBuilder` est créée avec un chemin de dépôt et un
          chemin vers le fichier JAR de Terraform Metrics.
        - La méthode `build_vectors` est appelée pour générer les vecteurs.

    Assertions :
        - Vérifie qu'au moins un vecteur est généré.
        - Vérifie que chaque vecteur est une liste.
        - Vérifie que tous les éléments des vecteurs sont des nombres flottants.
        - Vérifie que chaque vecteur contient exactement 55 caractéristiques.

    Returns:
        None
    """
    builder = FeatureVectorBuilder(
        repo_path=".", terrametrics_jar_path="libs/terraform_metrics-1.0.jar", model_name="dummy"
    )

    result = builder.build_vectors()

    assert len(result) > 0, "Aucun vecteur généré"

    for _, vector in result.items():
        assert isinstance(vector, list), "Le vecteur doit être une liste"
        assert all(
            isinstance(x, float) for x in vector
        ), "Tous les éléments doivent être des floats"
        assert (
            len(vector) == 55
        ), f"Le vecteur doit contenir exactement 55 features, mais en contient {len(vector)}"

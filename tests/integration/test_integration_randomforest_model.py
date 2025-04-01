from infrastructure.ml.random_forest_model import RandomForestModel


def test_random_forest_model_load_and_describe():
    """
    Teste la méthode `describe` de la classe `RandomForestModel` pour vérifier
    qu'elle retourne une description correcte du modèle.

    Scénario :
        - Une instance de `RandomForestModel` est créée.
        - La méthode `describe` est appelée pour obtenir une description du modèle.

    Assertions :
        - Vérifie que la description contient le nom du classifieur `RandomForestClassifier`.
        - Vérifie que la description mentionne l'utilisation d'un `Scaler`.
        - Vérifie que la description inclut des informations sur les `Features`.

    Returns:
        None
    """
    model = RandomForestModel()
    description = model.describe()

    assert "RandomForestClassifier" in description
    assert "Scaler" in description
    assert "Features" in description

import json
from datetime import datetime
from unittest.mock import patch

from core.use_cases.feature_vector_builder import FeatureVectorBuilder
from infrastructure.ml.defect_history_manager import update_defect_history
from infrastructure.ml.model_factory import ModelFactory


@patch(
    "infrastructure.ml.defect_history_manager.get_latest_commit_hash",
    return_value="integrationtest123",
)
def test_dummy_model_prediction_and_history_update(mock_get_commit, tmp_path):
    """
    Teste l'intégration complète entre la génération de vecteurs, la prédiction
    avec un modèle et la mise à jour de l'historique des défauts.

    Scénario :
        - Les vecteurs de caractéristiques sont générés à partir du code Terraform.
        - Un modèle prédictif (DummyModel) est utilisé pour effectuer des prédictions.
        - Les prédictions sont ajoutées à l'historique des défauts.
        - L'historique est sauvegardé et vérifié.

    Assertions :
        - Vérifie qu'au moins un vecteur est généré.
        - Vérifie que les clés des prédictions correspondent aux clés des vecteurs.
        - Vérifie que l'historique des défauts est correctement sauvegardé.
        - Vérifie que chaque prédiction est associée au bon commit et contient les champs attendus.

    Returns:
        None
    """
    from app import config

    # Configuration des chemins pour l'historique des défauts et les sorties
    config.DEFECT_HISTORY_PATH = tmp_path / "defect_history.json"
    config.OUTPUT_DIR = tmp_path

    # Étape 1 : Génération de vecteurs à partir du code
    builder = FeatureVectorBuilder(
        repo_path=".", terrametrics_jar_path="libs/terraform_metrics-1.0.jar"
    )
    vectors = builder.build_vectors()

    # Vérifie qu'il y a au moins un bloc à analyser
    assert len(vectors) > 0

    # Étape 2 : Prédiction avec DummyModel
    model = ModelFactory.get_model("dummy")
    predictions = model.predict(vectors)

    # Vérifie que les clés des prédictions correspondent aux clés des vecteurs
    assert set(predictions.keys()) == set(vectors.keys())

    # Étape 3 : Mise à jour de l'historique
    update_defect_history(predictions)

    # Étape 4 : Vérification que l'historique a bien été sauvegardé
    assert config.DEFECT_HISTORY_PATH.exists()

    with open(config.DEFECT_HISTORY_PATH, "r") as f:
        history = json.load(f)

    # Vérifie que l'historique est un dictionnaire et qu'il contient toutes les prédictions
    assert isinstance(history, dict)
    assert len(history) == len(predictions)

    # Vérifie que chaque prédiction est bien ajoutée avec le bon commit
    for _, entries in history.items():
        assert any(e["commit"] == "integrationtest123" for e in entries)
        assert all("fault_prone" in e and "date" in e for e in entries)
        datetime.fromisoformat(entries[-1]["date"])

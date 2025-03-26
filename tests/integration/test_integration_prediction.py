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
    # Rediriger le chemin d'historique vers un fichier temporaire
    import app.config as config

    config.DEFECT_HISTORY_PATH = tmp_path / "defect_history.json"
    config.OUTPUT_DIR = tmp_path

    # Étape 1 : Génération de vecteurs à partir du code
    builder = FeatureVectorBuilder(
        repo_path=".", terrametrics_jar_path="libs/terraform_metrics-1.0.jar"
    )
    vectors = builder.build_vectors()

    # Vérifier qu'il y a au moins un bloc à analyser
    assert len(vectors) > 0

    # Étape 2 : Prédiction avec DummyModel
    model = ModelFactory.get_model("dummy")
    predictions = model.predict(vectors)

    assert set(predictions.keys()) == set(vectors.keys())

    # Étape 3 : Mise à jour de l'historique
    update_defect_history(predictions)

    # Étape 4 : Vérification que l'historique a bien été sauvegardé
    assert config.DEFECT_HISTORY_PATH.exists()

    with open(config.DEFECT_HISTORY_PATH, "r") as f:
        history = json.load(f)

    assert isinstance(history, dict)
    assert len(history) == len(predictions)

    # Vérifie que chaque prédiction est bien ajoutée avec le bon commit
    for _, entries in history.items():
        assert any(e["commit"] == "integrationtest123" for e in entries)
        assert all("fault_prone" in e and "date" in e for e in entries)
        datetime.fromisoformat(entries[-1]["date"])

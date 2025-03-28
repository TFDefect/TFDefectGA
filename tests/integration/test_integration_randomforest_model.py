from infrastructure.ml.random_forest_model import RandomForestModel


def test_random_forest_model_load_and_describe():
    model = RandomForestModel()
    description = model.describe()

    assert "RandomForestClassifier" in description
    assert "Scaler" in description
    assert "Features" in description

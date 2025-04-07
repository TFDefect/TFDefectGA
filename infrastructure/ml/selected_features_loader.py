from typing import List
import pandas as pd
import os


def load_selected_features(model_name: str) -> List[str]:
    """
    Charge les features du modèle spécifié depuis un fichier CSV.

    Args:
        model_name (str): Nom du modèle (ex: 'randomforest').

    Returns:
        List[str]: Liste ordonnée des features à utiliser.
    """
    path = os.path.join("features", f"{model_name}_features.csv")

    try:
        df = pd.read_csv(path)
        if "Feature" not in df.columns:
            raise ValueError(f"Le fichier {path} ne contient pas de colonne 'Feature'")
        return df["Feature"].tolist()
    except Exception as e:
        raise RuntimeError(f"Erreur lors du chargement des features depuis {path}: {e}")

from typing import List

import pandas as pd

from app import config


def load_selected_features(path: str = config.FEATURE_ORDER_TEMPLATE_PATH) -> List[str]:
    """
    Charge la liste des features sélectionnées et ordonnées pour le modèle.

    Args:
        path (str): Chemin vers le fichier CSV contenant les noms de features à conserver, dans l'ordre.

    Returns:
        List[str]: Liste ordonnée des noms de features.
    """
    try:
        df = pd.read_csv(path)
        if "Feature" not in df.columns:
            raise ValueError(f"Le fichier {path} ne contient pas de colonne 'Feature'")
        return df["Feature"].tolist()
    except Exception as e:
        raise RuntimeError(f"Erreur lors du chargement des features depuis {path}: {e}")

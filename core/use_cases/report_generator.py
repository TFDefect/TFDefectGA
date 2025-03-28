import os
from datetime import datetime

from jinja2 import Environment, FileSystemLoader

from app import config
from infrastructure.ml.defect_history_manager import load_defect_history


class ReportGenerator:
    def __init__(self):
        os.makedirs(config.REPORTS_OUTPUT_FOLDER, exist_ok=True)
        self.env = Environment(loader=FileSystemLoader(config.TEMPLATE_FOLDER))
        self.template = self.env.get_template(config.REPORT_TEMPLATE)

    def generate(self, predictions: dict, model_description: str = "") -> str:
        """
        Génère un rapport HTML contenant les prédictions enrichies.
        Tronque le commit hash et formate la date pour un meilleur affichage.
        """
        defect_history = load_defect_history()
        enriched_predictions = []

        for block_id, label in predictions.items():
            history = defect_history.get(block_id, [])

            # Valeurs par défaut
            commit_display = "N/A"
            last_prediction_pretty = "N/A"

            # S’il existe un historique pour ce block_id
            if history:
                # Récupérer le dernier commit
                commit_full = history[-1].get("commit", "N/A")
                # Tronquer le hash du commit
                if commit_full and commit_full != "N/A":
                    commit_display = commit_full[:8]

                # Récupérer la date brute
                raw_date_str = history[-1].get("date", "N/A")
                try:
                    dt_obj = datetime.strptime(raw_date_str, "%Y-%m-%d %H:%M:%S")
                    last_prediction_pretty = dt_obj.strftime("%Y-%m-%d %H:%M")
                except (ValueError, TypeError):
                    # Si le format est inconnu, on garde la valeur brute
                    last_prediction_pretty = raw_date_str

            enriched_predictions.append(
                {
                    "block_id": block_id,
                    "fault_prone": label,
                    "num_defects_before": sum(
                        1 for h in history if h.get("fault_prone") == 1
                    ),
                    "last_prediction": last_prediction_pretty,
                    "commit": commit_display,
                }
            )

        # Nom du fichier de sortie
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"report_{timestamp}.html"
        output_path = os.path.join(config.REPORTS_OUTPUT_FOLDER, filename)

        # Rendre le template avec les prédictions enrichies
        html_content = self.template.render(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            predictions=enriched_predictions,
            model_description=model_description,
        )

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return output_path

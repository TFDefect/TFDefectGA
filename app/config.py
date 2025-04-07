import os

# Création du dossier 'out' si nécessaire
os.makedirs("out", exist_ok=True)

# Chemins des ressources
TERRAMETRICS_JAR_PATH = os.environ.get(
    "TERRAMETRICS_JAR", "libs/terraform_metrics-1.0.jar"
)

OUTPUT_DIR = os.path.join("out")
TEMPLATE_FOLDER = os.path.join("templates")
REPORTS_OUTPUT_FOLDER = os.path.join(OUTPUT_DIR, "reports")

# Chemins des fichiers JSON d'analyse
CODE_METRICS_JSON_PATH = os.path.join(OUTPUT_DIR, "code_metrics.json")
DELTA_METRICS_JSON_PATH = os.path.join(OUTPUT_DIR, "delta_metrics.json")
PROCESS_METRICS_JSON_PATH = os.path.join(OUTPUT_DIR, "process_metrics.json")
DEFECT_HISTORY_PATH = os.path.join(OUTPUT_DIR, "defect_history.json")

# Chemin du repo analysé
REPO_PATH = os.environ.get("GITHUB_WORKSPACE", ".")

# Template HTML
REPORT_TEMPLATE = os.environ.get("REPORT_TEMPLATE", "report_template.html")

# Modèles de prédiction (.joblib)
RF_MODEL_PATH = os.path.join("models", "random_forest_model.joblib")
LIGHTGBM_MODEL_PATH = os.path.join("models", "lightgbm_model.joblib")
LOGISTICREG_MODEL_PATH = os.path.join("models", "logisticreg_model.joblib")
NAIVEBAYES_MODEL_PATH = os.path.join("models", "naivebayes_model.joblib")

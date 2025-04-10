import os

# Répertoire absolu de ce fichier
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Création du dossier 'out' si nécessaire
os.makedirs(os.path.join(BASE_DIR, "out"), exist_ok=True)

# Chemins des ressources
TERRAMETRICS_JAR_PATH = os.environ.get(
    "TERRAMETRICS_JAR",
    os.path.join(BASE_DIR, "libs", "terraform_metrics-1.0.jar"),
)

# Dossiers et fichiers de sortie
OUTPUT_DIR = os.path.join(BASE_DIR, "out")
TEMPLATE_FOLDER = os.path.join(BASE_DIR, "templates")
REPORTS_OUTPUT_FOLDER = os.path.join(os.path.join("out"), "reports")

# Chemins des fichiers JSON d'analyse
CODE_METRICS_JSON_PATH = os.path.join(OUTPUT_DIR, "code_metrics.json")
DELTA_METRICS_JSON_PATH = os.path.join(OUTPUT_DIR, "delta_metrics.json")
PROCESS_METRICS_JSON_PATH = os.path.join(OUTPUT_DIR, "process_metrics.json")
DEFECT_HISTORY_PATH = os.path.join(os.path.join("out"), "defect_history.json")

# Chemin du repo analysé
REPO_PATH = os.environ.get("GITHUB_WORKSPACE", ".")

# Template HTML
TEMPLATE_FOLDER = os.path.join(BASE_DIR, "templates")
REPORT_TEMPLATE_NAME = os.environ.get("REPORT_TEMPLATE", "report_template.html")

# Modèles de prédiction (.joblib)
RF_MODEL_PATH = os.path.join(BASE_DIR, "models", "random_forest_model.joblib")
LIGHTGBM_MODEL_PATH = os.path.join(BASE_DIR, "models", "lightgbm_model.joblib")
LOGISTICREG_MODEL_PATH = os.path.join(BASE_DIR, "models", "logisticreg_model.joblib")
NAIVEBAYES_MODEL_PATH = os.path.join(BASE_DIR, "models", "naivebayes_model.joblib")

# Dossier des schémas de features
FEATURE_SCHEMAS_DIR = os.path.join(BASE_DIR, "feature_schemas")

import os

os.makedirs("out", exist_ok=True)

TERRAMETRICS_JAR_PATH = os.environ.get(
    "TERRAMETRICS_JAR", "libs/terraform_metrics-1.0.jar"
)

OUTPUT_DIR = os.path.join("out")
TEMPLATE_FOLDER = os.path.join("templates")

CODE_METRICS_JSON_PATH = os.path.join(OUTPUT_DIR, "code_metrics.json")
DELTA_METRICS_JSON_PATH = os.path.join(OUTPUT_DIR, "delta_metrics.json")
PROCESS_METRICS_JSON_PATH = os.path.join(OUTPUT_DIR, "process_metrics.json")

DEFECT_HISTORY_PATH = os.path.join(OUTPUT_DIR, "defect_history.json")

REPO_PATH = os.environ.get("GITHUB_WORKSPACE", ".")

REPORT_TEMPLATE = os.environ.get("REPORT_TEMPLATE", "report_template.html")

REPORTS_OUTPUT_FOLDER = os.path.join(OUTPUT_DIR, "reports")

RF_MODEL_PATH = os.path.join("models", "random_forest_model.joblib")

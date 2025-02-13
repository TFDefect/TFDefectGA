import os

TERRAMETRICS_JAR_PATH = os.environ.get(
    "TERRAMETRICS_JAR", "libs/terraform_metrics-1.0.jar"
)

OUTPUT_JSON_PATH = "output.json"
OUTPUT_HTML_PATH = "output.html"

FROM python:3.10-slim

# Installer Java (OpenJDK 17) et Git
RUN apt-get update && \
    apt-get install -y openjdk-17-jdk git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copier l'intégralité du projet dans le conteneur
COPY . .

# Installer les dépendances
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install -e .

ENV PYTHONPATH=/app

# Point d'entrée
ENTRYPOINT ["python", "app/action_runner.py"]

FROM python:3.10-slim

# Installer Java et Git
RUN apt-get update && \
    apt-get install -y openjdk-17-jdk git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copier tout le projet
COPY . .

# Ajouter le dossier comme "safe" pour Git
RUN git config --global --add safe.directory /github/workspace

# Installer les dépendances
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install -e .

# Définir PYTHONPATH
ENV PYTHONPATH=/app

ENTRYPOINT ["python", "app/action_runner.py"]

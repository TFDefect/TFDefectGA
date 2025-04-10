FROM python:3.10-slim

# Variables
ENV TERRAFORM_VERSION=1.6.6

# Installer Java, Git, unzip, wget (pour Terraform) et nettoyer ensuite
RUN apt-get update && \
    apt-get install -y openjdk-17-jdk git unzip wget && \
    wget https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip && \
    unzip terraform_${TERRAFORM_VERSION}_linux_amd64.zip && \
    mv terraform /usr/local/bin/ && \
    rm terraform_${TERRAFORM_VERSION}_linux_amd64.zip && \
    apt-get remove -y unzip wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Définir le répertoire de travail
WORKDIR /app

# Copier le projet
COPY . .

# Marquer le dossier comme sûr pour Git (utile pour GitHub Actions)
RUN git config --global --add safe.directory /github/workspace

# Installer les dépendances Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install -e .

# Définir le PYTHONPATH
ENV PYTHONPATH=/app

# Entrée du container
ENTRYPOINT ["python", "/app/app/action_runner.py"]

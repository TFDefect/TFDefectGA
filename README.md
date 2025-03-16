
# TFDefectGA - Détection des Bogues Terraform

TFDefectGA est un outil d'analyse automatisée qui permet de détecter des anomalies dans les fichiers Terraform en s'appuyant sur une architecture Clean Architecture. Le projet intègre également un modèle de Machine Learning (actuellement un DummyMLModel) pour prédire si un bloc est défectueux ou non. L'analyse s'exécute automatiquement via GitHub Actions à chaque modification d'un fichier `.tf`, mais peut également être lancée localement.

## Table des matières

- [Fonctionnalités](#fonctionnalités)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Exécution locale](#exécution-locale)
- [Exécution via GitHub Actions](#exécution-via-github-actions)
- [Configuration](#configuration)

## Fonctionnalités

- **Détection des modifications :** Identifie les blocs Terraform modifiés dans un commit.
- **Extraction des métriques :** Utilise TerraMetrics (ou un extracteur delta) pour calculer des métriques à partir des blocs modifiés.
- **Prédiction ML :** Applique un modèle (actuellement DummyMLModel) pour prédire si un bloc présente un défaut.
- **Reporting :** Génère un rapport d'analyse affiché en console et sauvegardé dans un fichier `output.json`.
- **Intégration CI/CD :** Exécution automatique via GitHub Actions dès qu'un fichier `.tf` est modifié.


## Prérequis

- **Python 3.8+**
- **Git** installé et configuré
- **Java 11** (pour exécuter TerraMetrics.jar)
- **Terraform CLI** (optionnel, pour formatter et valider les fichiers Terraform)
- Le fichier **TerraMetrics.jar** doit être présent et son chemin doit être défini dans `config/config.py`

## Installation

1. **Cloner le dépôt :**

   ```bash
   git clone <url_du_dépôt>
   cd TFDefectGA
	```
2. **Créer et activer un environnement virtuel :**
	```bash
	python -m venv venv
	# Sur Linux/Mac
	source venv/bin/activate
	# Sur Windows
	.\venv\Scripts\activate
	```
3. Installer les dépendances :
	```bash
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install -e .
	```
## Exécution locale

Pour lancer l'analyse localement, utilisez le script `action_runner.py`. Vous pouvez choisir l'extracteur à utiliser grâce à l'argument `--extractor`.

-   **Pour utiliser TerraMetrics :**
	```bash
	python app/action_runner.py HEAD --extractor terrametrics
	```
- **Pour utiliser l'extracteur delta :**
	```bash
	python app/action_runner.py HEAD --extractor delta
	```
_Remarque :_  
La commande utilise `HEAD` pour analyser le dernier commit. Vous pouvez remplacer `HEAD` par un hash de commit spécifique.

Les résultats de l'analyse s'affichent dans la console et sont sauvegardés dans le fichier `output.json`.

## Exécution via GitHub Actions

Le projet est configuré pour exécuter automatiquement l'analyse via GitHub Actions sur chaque push ou pull request qui modifie un fichier `.tf`.  
Le workflow défini dans `.github/workflows/ci.yml` effectue les actions suivantes :

-   **Checkout du dépôt**
    
-   **Mise en cache et installation des environnements virtuel, Java et Terraform**
    
-   **Exécution de l'analyse avec la commande :**
	```bash
	python app/action_runner.py HEAD
	```
- **Publication du fichier `output.json` comme artefact**

## Configuration

-   **TerraMetrics.jar :**  
    Vérifiez le chemin du fichier dans `config/config.py`.
-   **Choix de l'extracteur :**  
    L'argument `--extractor` permet de choisir entre `terrametrics` et `delta`.

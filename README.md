# **TFDefectGA - Détection de défauts Terraform via GitHub Actions** 🚀

TFDefectGA est un outil avancé d'analyse des fichiers **Terraform (`.tf`)** combinant l'analyse statique, l'historique Git et des modèles prédictifs pour anticiper les défauts logiciels. Il permet :

- L'extraction de **métriques de code et de processus** (TerraMetrics, historique Git)
- La **comparaison entre versions** pour évaluer l'évolution des modifications
- **La prédiction des défauts** grâce à un modèle de Machine Learning basé sur l'historique du code

💡 TFDefectGA s'intègre facilement dans un pipeline **CI/CD GitHub Actions** ou peut être exécuté **localement**.

---

## 📚 Table des matières

- [🧠 Fonctionnalités](#-fonctionnalités)
- [⚙️ Prérequis](#️-prérequis)
- [📦 Installation](#-installation)
- [🚀 Exécution Locale](#-exécution-locale)
- [🐳 Docker et GHCR](#-docker-et-ghcr)
- [⚙️ Modes d'Analyse Disponibles](#️-modes-danalyse-disponibles)
- [🤖 Modèle Prédictif](#-modèle-prédictif)
- [📚 Modèles Actuellement Supportés](#-modèles-actuellement-supportés)
- [📈 Historique des défauts](#-historique-des-défauts-defect_historyjson)
- [🧪 Tests](#-tests)
- [🔧 Formatage Terraform](#-formatage-terraform)
- [🛠 Configuration](#-configuration)
- [📝 Licence](#-licence)

---

## 🧠 Fonctionnalités

✔️ **Analyse statique Terraform** avec TerraMetrics (complexité, duplication, etc.)  
✔️ **Analyse historique Git** pour évaluer l'évolution des blocs Terraform  
✔️ **Comparaison avant/après commit** pour détecter les changements critiques  
✔️ **Prédiction de défauts** via Machine Learning  
✔️ **Rapports HTML interactifs**  
✔️ **Intégration GitHub Actions et Docker-ready**  
✔️ **Formatage automatique** des fichiers `.tf` via `terraform fmt`

---

## ⚙️ Prérequis

- **Python 3.8+**
- **Java 11+** (pour TerraMetrics)
- **Git** (analyse historique)
- **Terraform CLI** (pour `terraform fmt`)
- **TerraMetrics JAR** (`libs/terraform_metrics-1.0.jar`)

---

## 📦 Installation

```bash
# Cloner le projet
git clone <url_du_dépôt>
cd TFDefectGA

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # ou .\venv\Scripts\activate sur Windows

# Installer les dépendances
pip install -r requirements.txt
pip install -e .
```

---

## 🚀 Exécution locale

```bash
# Analyse des métriques statiques Terraform
python app/action_runner.py --extractor codemetrics

# Analyse de l'évolution entre commits
python app/action_runner.py --extractor delta

# Analyse des métriques de processus (contributions, auteurs...)
python app/action_runner.py --extractor process

# Prédiction via modèle (dummy, randomforest, lightgbm, etc.)
python app/action_runner.py --model randomforest

# Afficher l'historique des prédictions
python app/action_runner.py --show-history

# Afficher toutes les options disponibles
python app/action_runner.py --help
```

📂 Les résultats sont sauvegardés dans le dossier `out/`.

---

## 🐳 Docker et GHCR

TFDefectGA peut être exécuté via une **image Docker publique** :

```bash
docker pull ghcr.io/abdelhaouari/tfdefectga:v1
```

### 🔧 Exécution sur un dépôt local

L’image contient uniquement le code et les dépendances de TFDefectGA, mais **pas les fichiers du dépôt Git** ni les fichiers Terraform à analyser.  
Pour que l’analyse fonctionne correctement (accès aux fichiers `.tf`, historique Git, etc.), il est nécessaire de monter :

- le répertoire de travail dans `/app`
- le dossier `.git/` dans `/app/.git`

#### ✅ Exemple de commande (compatible Linux, macOS, Git Bash sur Windows) :

```bash
MSYS_NO_PATHCONV=1 docker run --rm \
  -v "$(pwd):/app" \
  -v "$(pwd)/.git:/app/.git" \
  ghcr.io/abdelhaouari/tfdefectga:v1 \
  --model randomforest
```

> ℹ️ Le flag `MSYS_NO_PATHCONV=1` est requis sous Git Bash (Windows) pour éviter les conversions automatiques de chemins.

Cette commande :

- applique `terraform fmt` pour formater les fichiers `.tf`
- exécute l’analyse des métriques
- effectue les prédictions via le modèle ML
- génère le rapport HTML dans `out/`

---

### 🛠️ Construction locale de l’image Docker

Pour construire l’image manuellement et la publier dans le GitHub Container Registry (GHCR) :

```bash
docker build -t tfdefectga .
docker tag tfdefectga ghcr.io/<utilisateur>/tfdefectga:v2
docker push ghcr.io/<utilisateur>/tfdefectga:v2
```

---

## ⚙️ Modes d'analyse disponibles

| Extracteur    | Description                                             | Fichier JSON Généré        |
|---------------|---------------------------------------------------------|----------------------------|
| `codemetrics` | Analyse statique (TerraMetrics)                         | `out/code_metrics.json`    |
| `delta`       | Diff entre deux versions Git                            | `out/delta_metrics.json`   |
| `process`     | Historique Git (contributions, commits, auteurs...)     | `out/process_metrics.json` |

---

## 🤖 Modèle prédictif

💡 **Objectif : Identifier les blocs à risque avant leur déploiement.**

### 🔁 Étapes du pipeline :

1. 📦 Extraction des métriques de code, delta et processus
2. 🧠 Construction du vecteur de caractéristiques
3. 🎯 Prédiction avec un modèle ML (`DummyModel`, `RandomForestClassifier`, `LightGBM`, `LogisticRegression`, `NaiveBayes`, etc.)
4. 🕓 Historisation dans `defect_history.json`

### ✅ Ajouter un nouveau modèle :

Pour qu’un modèle soit utilisable, il faut :

- Placer le fichier `.joblib` du modèle dans le dossier `models/`
- Nommer un fichier CSV contenant ses features sélectionnées sous `features/<model_name>_features.csv`
- Utiliser la commande :
  ```bash
  python app/action_runner.py --model <model_name>
  ```

> Exemple : `--model lightgbm`

**⚠️ Le nom du modèle doit correspondre au nom du fichier `.csv` ET à la clé du `ModelFactory`.**

---

## 📚 Modèles actuellement supportés

TFDefectGA supporte plusieurs modèles de Machine Learning. Voici la liste des modèles disponibles :

| Nom du modèle (`--model`) | Type de modèle              | Fichier attendu                                       |
|---------------------------|-----------------------------|-------------------------------------------------------|
| `dummy`                   | Modèle de test aléatoire    | Pas de fichier requis                                 |
| `randomforest`            | RandomForestClassifier      | `models/random_forest_model.joblib` + `features/randomforest_features.csv` |
| `lightgbm`                | LightGBMClassifier          | `models/lightgbm_model.joblib` + `features/lightgbm_features.csv`         |
| `logisticreg`             | LogisticRegression          | `models/logisticreg_model.joblib` + `features/logisticreg_features.csv`   |
| `naivebayes`              | GaussianNB                  | `models/naivebayes_model.joblib` + `features/naivebayes_features.csv`     |

> 🧠 Les modèles sont chargés dynamiquement via `ModelFactory`, il est donc facile d’en ajouter de nouveaux en suivant la même structure.

---

### 🆘 Aide en ligne

Pour afficher toutes les options disponibles, lance simplement :

```bash
python app/action_runner.py --help
```

Cela t’affichera tous les paramètres disponibles (`--model`, `--extractor`, `--show-history`, `--generate-report`, etc.) et comment les utiliser.

---

## 📈 Historique des défauts (`defect_history.json`)

Ce fichier trace les prédictions faites sur chaque bloc Terraform :

```json
{
  "data/main.tf::aws_instance.example": [
    {
      "commit": "a1b2c3",
      "fault_prone": 1,
      "date": "2025-03-22T13:30:14"
    }
  ]
}
```

Utilisé pour :

- Générer les rapports HTML
- Calculer `num_defects_before` pour enrichir les prédictions futures

---

## 🧪 Tests

Exécuter tous les tests :

```bash
pytest tests/
```

#### Tests unitaires

```bash
pytest tests/unit/
```

#### Tests d'intégration

```bash
pytest tests/integration/
```

---

## 🔧 Formatage Terraform

Avant d’analyser les blocs `.tf`, TFDefectGA exécute automatiquement :

```bash
terraform fmt -recursive
```

✅ Cela permet d’éviter les erreurs de parsing liées à un format incorrect.  
📝 Le formatage est **réalisé dans le repo cloné localement** (dans Docker ou GitHub Actions), **sans impacter le dépôt distant**.

---

## 🛠 Configuration

Le fichier `config.py` permet de personnaliser les chemins et ressources utilisées :

```python
TERRAMETRICS_JAR_PATH = os.path.join("libs", "terraform_metrics-1.0.jar")
REPO_PATH = os.environ.get("GITHUB_WORKSPACE", ".")
CODE_METRICS_JSON_PATH = os.path.join("out", "code_metrics.json")
RF_MODEL_PATH = os.path.join("models", "random_forest_model.joblib")
```

---

## 📝 Licence

Ce projet est sous **Licence MIT** - © 2025

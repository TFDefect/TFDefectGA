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
- [⚙️ Modes d'Analyse Disponibles](#️-modes-danalyse-disponibles)
- [🤖 Modèle Prédictif](#-modèle-prédictif)
- [📈 Historique des défauts](#-historique-des-défauts-defect_historyjson)
- [🛠 Configuration](#-configuration)
- [📝 Licence](#-licence)

---

## 🧠 Fonctionnalités

✔️ **Analyse statique Terraform** avec TerraMetrics (complexité, duplication, etc.)  
✔️ **Analyse historique Git** pour évaluer l'évolution des blocs Terraform  
✔️ **Comparaison avant/après commit** pour détecter les changements critiques  
✔️ **Prédiction de défauts** via Machine Learning  
✔️ **Intégration GitHub Actions** pour une exécution automatisée

---

## ⚙️ Prérequis

- **Python 3.8+**
- **Java 11+** (nécessaire pour TerraMetrics)
- **Git** (utilisé pour l'analyse historique)
- **Terraform CLI** (optionnel, pour normaliser les fichiers `.tf`)
- **TerraMetrics JAR** (`terraform_metrics-1.0.jar` dans `libs/`)

---

## 📦 Installation

```bash
# Cloner le projet
git clone <url_du_dépôt>
cd TFDefectGA

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # (ou .\venv\Scripts\activate sous Windows)

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

# Analyse des métriques de processus et historiques Git
python app/action_runner.py --extractor process

# Exécution d'une prédiction (modèle dummy par défaut)
python app/action_runner.py --model dummy

# Affichage de l'historique des défauts prédits
python app/action_runner.py --show-history
```

📂 Les résultats sont générés dans le dossier `out/`.

---

## ⚙️ Modes d'analyse disponibles

| Extracteur    | Description                                             | Fichier JSON Généré        |
| ------------- | ------------------------------------------------------- | -------------------------- |
| `codemetrics` | Analyse statique Terraform (complexité, duplication...) | `out/code_metrics.json`    |
| `delta`       | Évolution des métriques avant/après commit              | `out/delta_metrics.json`   |
| `process`     | Analyse historique (contributions, commits, auteurs...) | `out/process_metrics.json` |

---

## 🤖 Modèle prédictif

💡 **Objectif : Détecter les blocs Terraform à risque avant leur déploiement.**

### **📊 Fonctionnement :**

1. **Extraction des métriques** (code, delta, process)
2. **Construction d’un vecteur de caractéristiques par bloc**
3. **Prédiction via un modèle ML** (ex: `DummyModel`, scikit-learn, etc.)
4. **Mise à jour d’un fichier `defect_history.json`** enregistrant les prédictions **par bloc et par commit**

📌 Chaque prédiction est historisée avec :

- le `block_id`
- le hash du commit
- la date de prédiction
- la valeur `fault_prone` (0 ou 1)

🔀 Ces données sont ensuite utilisées pour calculer dynamiquement la métrique `num_defects_before`, qui reflète combien de fois un bloc a été marqué fautif dans le passé.

---

## 📈 Historique des défauts (`defect_history.json`)

Le fichier `out/defect_history.json` contient l’historique des prédictions, par bloc et par commit. Exemple :

```json
{
  "data/main.tf::aws_instance.example": [
    {
      "commit": "a1b2c3",
      "fault_prone": 1,
      "date": "2025-03-22T13:30:14"
    },
    {
      "commit": "d4e5f6",
      "fault_prone": 0,
      "date": "2025-03-23T08:15:02"
    }
  ]
}
```

Chaque entrée correspond à une prédiction réalisée à un moment donné.
Cela permet de reconstituer l’évolution du risque d’un bloc dans le temps.

🔢 Commande pour afficher l’historique dans le terminal :

```bash
python app/action_runner.py --show-history
```

---

## 🛠 Configuration

La configuration se fait via `config.py` :

```python
import os

TERRAMETRICS_JAR_PATH = os.path.join("libs", "terraform_metrics-1.0.jar")

CODE_METRICS_JSON_PATH = os.path.join("out", "code_metrics.json")
DELTA_METRICS_JSON_PATH = os.path.join("out", "delta_metrics.json")
PROCESS_METRICS_JSON_PATH = os.path.join("out", "process_metrics.json")

REPO_PATH = os.environ.get("GITHUB_WORKSPACE", ".")
```

---

## 📝 Licence

Ce projet est sous **Licence MIT** - © 2025

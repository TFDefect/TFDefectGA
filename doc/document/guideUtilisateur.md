# Guide Utilisateur – TFDefect GitHub Action

## Introduction

### Présentation de l'outil

TFDefectGA est un outil d'analyse avancé conçu spécifiquement pour les fichiers Terraform (`.tf`). Il combine plusieurs techniques d'analyse, notamment l'analyse statique du code, l'étude de l'historique des modifications Git, et des modèles prédictifs basés sur l'apprentissage automatique, pour vous aider à identifier les défauts potentiels dans votre infrastructure sous forme de code (IaC) avant leur déploiement en production.

Disponible sous forme d'image Docker ou directement intégrable dans un pipeline GitHub Actions, TFDefectGA s'insère facilement dans votre environnement de développement existant.

### Objectifs du logiciel

TFDefectGA vise à :

- **Améliorer la qualité du code Terraform** en identifiant de manière proactive les blocs de code susceptibles de contenir des défauts
- **Réduire les incidents en production** causés par des configurations Terraform défectueuses
- **Accélérer le cycle de développement** en détectant les problèmes potentiels avant les phases de test et de déploiement
- **Faciliter la revue de code** en fournissant des rapports détaillés sur les métriques et les risques associés au code Terraform
- **Favoriser l'amélioration continue** grâce à un historique des prédictions permettant d'affiner la détection au fil du temps

### Public cible

TFDefectGA s'adresse principalement aux :

- **Développeurs d'infrastructure** travaillant avec Terraform pour gérer des ressources cloud
- **Ingénieurs DevOps** cherchant à automatiser la validation de la qualité des configurations IaC
- **Équipes collaborant sur des projets Terraform** nécessitant des outils d'assurance qualité intégrés à leurs workflows

Que vous soyez novice en matière d'IaC ou un expert en Terraform, TFDefectGA vous aidera à améliorer la robustesse de votre code d'infrastructure tout en s'intégrant parfaitement à vos processus existants.

---

## Prérequis

Avant d'utiliser TFDefectGA, assurez-vous que votre environnement satisfait aux exigences suivantes :

### Pour l'utilisation via GitHub Actions

- Un **dépôt GitHub** contenant des fichiers Terraform (`.tf`)
- Des **droits d'administrateur** sur le dépôt pour configurer les workflows GitHub Actions
- Un **historique Git** suffisant pour l'analyse des métriques de processus (au moins quelques commits)

### Pour l'utilisation locale

- **Python 3.8+** installé sur votre machine
- **Java 11+** (nécessaire pour TerraMetrics, l'outil d'analyse des métriques Terraform)
- **Git** installé et accessible en ligne de commande
- **Terraform CLI** installé pour le formatage automatique (`terraform fmt`)
- **TerraMetricsJAR** (`libs/terraform_metrics-1.0.jar`)
- **Docker** (optionnel, si vous préférez utiliser l'image conteneurisée)

### Prérequis pour les fichiers sources

- Des **fichiers Terraform valides** (`.tf`) qui peuvent être analysés par l'outil
- Un **dépôt Git initialisé** contenant ces fichiers
- Idéalement, un **historique de commits** avec plusieurs contributions pour améliorer la précision des prédictions

---

## Installation et exécution

### Utilisation de Docker

Récupérez l'image Docker:
```bash
docker pull ghcr.io/abdelhaouari/tfdefectga:v1
```

L’image contient uniquement le code et les dépendances de TFDefectGA, mais **pas les fichiers du dépôt Git** ni les fichiers Terraform à analyser.  
Pour que l’analyse fonctionne correctement (accès aux fichiers `.tf`, historique Git, etc.), il est nécessaire de monter :

- le répertoire de travail dans `/app`
- le dossier `.git/` dans `/app/.git`

#### Exemple de commande (compatible Linux, macOS, Git Bash sur Windows) :

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

#### Construction locale de l’image Docker

Pour construire l’image manuellement et la publier dans le GitHub Container Registry (GHCR) :

```bash
docker build -t tfdefectga .
docker tag tfdefectga ghcr.io/<utilisateur>/tfdefectga:v2
docker push ghcr.io/<utilisateur>/tfdefectga:v2
```
### Utilisation locale

#### Étapes d'installation
1. Clonez le dépôt:
```bash
git clone https://github.com/TFDefect/TFDefectGA.git
cd TFDefectGA
```

2. Créez un environnement virtuel:
```bash
python -m venv venv
source venv/bin/activate  # ou .\venv\Scripts\activate sur Windows
```
3. Installez les dépendances:
```bash
pip install -r requirements.txt
pip install -e .
```

#### Exécution
```bash
# Analyse des métriques statiques Terraform
python app/action_runner.py --extractor codemetrics

# Analyse de l'évolution entre commits
python app/action_runner.py --extractor delta

# Analyse des métriques de processus (contributions, auteurs...)
python app/action_runner.py --extractor process

# Prédiction via modèle (dummy, randomforest, etc.)
python app/action_runner.py --model randomforest

# Afficher l'historique des prédictions
python app/action_runner.py --show-history
```
---

## Fonctionnalités

TFDefectGA offre un ensemble complet de fonctionnalités pour l'analyse de code Terraform :

### Analyse statique du code

- **Extraction de métriques** : TFDefectGA calcule plus de 50 métriques pour chaque bloc Terraform, couvrant la complexité, la duplication, et d'autres indicateurs de qualité.
- **Formatage automatique** : Application de `terraform fmt` pour garantir la cohérence du code avant analyse.
- **Validation syntaxique** : Vérification de la validité des fichiers Terraform avant tout traitement approfondi.

### Analyse historique et contextuelle

- **Métriques de processus** : Analyse de l'historique Git pour évaluer l'évolution du code (fréquence des modifications, nombre d'auteurs, etc.).
- **Métriques delta** : Comparaison des versions d'un même bloc Terraform pour détecter les changements critiques.
- **Corrélation** : Mise en relation des modifications avec l'historique des défauts pour identifier les tendances.

### Prédiction de défauts

- **Modèles de Machine Learning** : Utilisation d'algorithmes (comme Random Forest) entraînés sur des ensembles de données historiques pour prédire les défauts potentiels.
- **Historisation** : Suivi des prédictions dans le temps pour améliorer la précision des modèles.

### Rapports et visualisation

- **Rapports HTML interactifs** : Présentation claire et détaillée des résultats d'analyse dans un format accessible.
- **Codes couleur** : Identification visuelle rapide des blocs à risque grâce à un système de badges colorés.
- **Historique consultable** : Possibilité de consulter l'évolution des prédictions pour un même bloc au fil du temps.

### Intégration DevOps

- **GitHub Actions** : Intégration native dans les pipelines CI/CD via une action GitHub configurable.
- **Docker** : Disponibilité sous forme d'image Docker pour une portabilité maximale.

---

## Modes d'analyse disponibles

TFDefectGA propose plusieurs modes d'analyse qui peuvent être utilisés indépendamment ou combinés pour une analyse complète de votre code Terraform.

### Extracteur Codemetrics
Ce mode analyse statiquement vos fichiers Terraform pour extraire plus de 50 métriques différentes à l'aide de l'outil TerraMetrics. 

Les métriques extraites incluent :
- Complexité cyclomatique
- Nombre de ressources et variables
- Profondeur des blocs imbriqués
- Métriques de duplication
- Longueur des blocs (lignes de code)

Cette analyse génère un fichier `out/code_metrics.json` contenant toutes les métriques calculées.

### Extracteur Deltametrics

Ce mode compare les versions d'un même bloc Terraform avant et après modification pour identifier les changements significatifs.

Les métriques delta révèlent :

- L'ampleur des changements entre deux versions
- Les tendances d'évolution du code (complexification ou simplification)
- Les modifications potentiellement risquées

Les résultats sont sauvegardés dans `out/delta_metrics.json`.

### Extracteur ProcessMetrics

Ce mode analyse l'historique Git du code Terraform pour évaluer les aspects liés au processus de développement.

Les métriques extraites incluent :

- Nombre de développeurs ayant modifié le code (ndevs)
- Expérience des contributeurs (exp, rexp, sexp, bexp)
- Âge moyen des modifications (age)
- Fréquence des changements (time_interval)
- Propriété du code (code_ownership)
- Historique des défauts précédents (num_defects_before)

Cette analyse génère un fichier out/process_metrics.json

---

## Prédiction par modèle de Machine Learning

TFDefectGA propose plusieurs modèles pour la prédiction de défauts :

1. **Modèle `dummy`** : Modèle simple générant des prédictions aléatoires, utile pour tester le pipeline d'analyse.

2. **Modèle `RandomForest`** : Modèle d'apprentissage automatique avancé combinant de multiples arbres de décision pour une prédiction précise des défauts potentiels.


## Licence

Ce projet est sous **Licence MIT** - © 2025
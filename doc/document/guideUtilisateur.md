# Guide Utilisateur – TFDefect GitHub Action

## Table des matières
- [Guide Utilisateur – TFDefect GitHub Action](#guide-utilisateur--tfdefect-github-action)
  - [Table des matières](#table-des-matières)
  - [Glossaire](#glossaire)
  - [Introduction](#introduction)
    - [Présentation de l'outil](#présentation-de-loutil)
    - [Objectifs du logiciel](#objectifs-du-logiciel)
    - [Public cible](#public-cible)
  - [Prérequis](#prérequis)
    - [Pour l'utilisation via GitHub Actions](#pour-lutilisation-via-github-actions)
    - [Pour l'utilisation locale](#pour-lutilisation-locale)
    - [Prérequis pour les fichiers sources](#prérequis-pour-les-fichiers-sources)
  - [Installation et exécution](#installation-et-exécution)
    - [Utilisation de Docker](#utilisation-de-docker)
      - [Exemple de commande (compatible Linux, macOS, Git Bash sur Windows) :](#exemple-de-commande-compatible-linux-macos-git-bash-sur-windows-)
      - [Construction locale de l’image Docker](#construction-locale-de-limage-docker)
    - [Utilisation locale](#utilisation-locale)
      - [Étapes d'installation](#étapes-dinstallation)
      - [Exécution](#exécution)
  - [Fonctionnalités](#fonctionnalités)
    - [Analyse statique du code](#analyse-statique-du-code)
    - [Analyse historique et contextuelle](#analyse-historique-et-contextuelle)
    - [Prédiction de défauts](#prédiction-de-défauts)
    - [Rapports et visualisation](#rapports-et-visualisation)
    - [Intégration DevOps](#intégration-devops)
  - [Modes d'analyse disponibles](#modes-danalyse-disponibles)
    - [Extracteur Codemetrics](#extracteur-codemetrics)
    - [Extracteur Deltametrics](#extracteur-deltametrics)
    - [Extracteur ProcessMetrics](#extracteur-processmetrics)
  - [Prédiction par modèle de Machine Learning](#prédiction-par-modèle-de-machine-learning)
  - [Démonstration vidéo](#démonstration-vidéo)
  - [Foire Aux Questions (FAQ)](#foire-aux-questions-faq)
    - [Questions générales](#questions-générales)
    - [Installation et configuration](#installation-et-configuration)
    - [Résultats et interprétation](#résultats-et-interprétation)
  - [Liens et ressources](#liens-et-ressources)
    - [Dépôt GitHub officiel](#dépôt-github-officiel)
    - [Documentation additionnelle](#documentation-additionnelle)

---
<div style="page-break-before:always"></div>

## Glossaire

**Bloc Terraform** : Unité structurelle dans un fichier Terraform qui définit une ressource, variable, module ou autre élément d'infrastructure.

**Défaut** : Erreur ou problème dans le code Terraform pouvant entraîner des dysfonctionnements lors du déploiement ou de l'exécution.

**DevOps** : Méthodologie combinant le développement logiciel (Dev) et les opérations informatiques (Ops) visant à raccourcir le cycle de développement et à fournir en continu des fonctionnalités de haute qualité.

**Docker** : Plateforme de conteneurisation permettant d'empaqueter une application et ses dépendances dans un conteneur virtuel.

**GitHub Actions** : Fonctionnalité de GitHub permettant l'automatisation des workflows de développement logiciel directement dans un dépôt GitHub.

**IaC (Infrastructure as Code)** : Approche consistant à gérer et provisionner l'infrastructure informatique via du code plutôt que par des processus manuels.

**Machine Learning (ML)** : Discipline utilisant des algorithmes et des modèles statistiques permettant aux ordinateurs d'apprendre à partir des données sans être explicitement programmés pour une tâche spécifique.

**Random Forest** : Algorithme d'apprentissage automatique combinant plusieurs arbres de décision pour améliorer la précision des prédictions.

**Terraform** : Outil open-source d'Infrastructure as Code développé par HashiCorp permettant de créer, modifier et versionner l'infrastructure de manière sécurisée et efficace.

**TerraMetrics** : Composant de TFDefectGA chargé de calculer les métriques statiques des fichiers Terraform. Pour en savoir plus sur les métriques, consultez cette page: [Terrametrics](https://github.com/stilab-ets/terametrics?tab=readme-ov-file#metrics)

**DeltaMetrics** : Métriques mesurant les différences entre deux versions d'un même bloc de code Terraform.

**Workflow** : Séquence automatisée d'étapes, de tâches et d'opérations pour accomplir un processus spécifique.

**ProcessMetrics** : Mesures liées au processus de développement comme le nombre d'auteurs, la fréquence des modifications, etc. Pour en savoir plus sur les métriques, consultez cette page: [ProcessMetrics](https://github.com/TFDefect/TFDefectGA/wiki/ProcessMetrics)

---
<div style="page-break-before:always"></div>

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

<div style="page-break-before:always"></div>

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

<div style="page-break-before:always"></div>

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

<div style="page-break-before:always"></div>

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

<div style="page-break-before:always"></div>

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

---
## Démonstration vidéo
Pour mieux comprendre l'utilisation de l'outil, veuillez cliquer sur le lien suivant: [Démonstration de TFDefectGA](https://drive.google.com/file/d/1fT4zSIMJr_IyGnh2WB8P_IRn35KANkY7/view)

---
## Foire Aux Questions (FAQ)

### Questions générales

**Q : À quelle fréquence dois-je exécuter TFDefectGA sur mon projet ?**  
R : Nous recommandons d'exécuter l'analyse à chaque pull request modifiant des fichiers Terraform, ainsi que périodiquement (hebdomadaire) sur l'ensemble du code base pour suivre son évolution.

**Q : L'outil peut-il être utilisé sur des projets Terraform de grande taille ?**  
R : Oui, TFDefectGA est conçu pour s'adapter à des projets de toutes tailles. Pour les très grands projets, l'analyse peut prendre plus de temps, mais reste performante.

**Q : Les fichiers Terraform générés par d'autres outils sont-ils analysables ?**  
R : Oui, tant que les fichiers sont syntaxiquement valides selon les standards Terraform.

### Installation et configuration

**Q : Comment puis-je personnaliser le seuil de détection des défauts ?**  
R : Actuellement, le seuil est fixé dans les modèles. Une future version permettra de le configurer via un paramètre.

**Q : J'obtiens une erreur Java lors de l'exécution locale, que faire ?**  
R : Vérifiez que vous avez bien Java 11+ installé et que la variable d'environnement `JAVA_HOME` est correctement configurée.

**Q : L'outil fonctionne-t-il avec des versions spécifiques de Terraform ?**  
R : TFDefectGA est compatible avec toutes les versions récentes de Terraform (0.12+).

<div style="page-break-before:always"></div>

### Résultats et interprétation

**Q : Comment interpréter les différentes couleurs dans le rapport ?**  
R : Vert : Bloc probablement sans défaut  
    Orange : Risque modéré de défaut  
    Rouge : Risque élevé de défaut

**Q : Que faire si un bloc est identifié à risque ?**  
R : Examinez les métriques associées pour comprendre pourquoi. Les facteurs courants incluent une complexité élevée, des modifications fréquentes par plusieurs développeurs, ou des changements importants récents.

**Q : Les rapports sont-ils persistants ?**  
R : Oui, les rapports sont sauvegardés dans le dossier `out/reports/` et l'historique des prédictions est conservé dans `defect_history.json`.

---

## Liens et ressources

### Dépôt GitHub officiel

Le code source de TFDefectGA est disponible sur GitHub :

[https://github.com/TFDefect/TFDefectGA](https://github.com/TFDefect/TFDefectGA)

N'hésitez pas à :
- ⭐ Mettre une étoile au projet si vous le trouvez utile
- 🐛 Signaler des bugs via les issues GitHub
- 💡 Proposer des améliorations
- 🔄 Soumettre des pull requests

### Documentation additionnelle

- [Documentation Terraform officielle](https://www.terraform.io/docs)
- [Bonnes pratiques Terraform](https://www.terraform-best-practices.com/)
- [Articles sur l'analyse de qualité d'IaC](https://medium.com/tag/infrastructure-as-code)

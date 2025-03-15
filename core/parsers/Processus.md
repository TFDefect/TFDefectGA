# ProcessMetrics pour un code infrastructure

## Aperçu
La classe `ProcessMetrics` est conçue pour calculer divers indicateurs de processus liés aux modifications du code infrastructure. Elle permet d'évaluer l'impact des contributions en analysant des facteurs tels que l'expérience du développeur, la propriété du code, les défauts historiques et la fréquence des modifications. Ces métriques peuvent être utilisées pour l'évaluation de la qualité logicielle, l'estimation des risques et l'analyse de la productivité des développeurs.

## Fonctionnalités
Ci-dessous les principales métriques calculées par la classe `ProcessMetrics` :

### 1. **Nombre de développeurs (`ndevs`)**
   - Calcule le nombre de développeurs distincts ayant modifié le même bloc avant la modification actuelle.
   - **Objectif :** Évaluer la familiarité avec le code et la distribution des connaissances.

### 2. **Nombre de commits (`ncommits`)**
   - Détermine le nombre de commits précédents ayant modifié le même bloc.
   - **Objectif :** Identifier les parties du code fréquemment modifiées, ce qui peut indiquer une instabilité.

### 3. **Propriété du code (`code_ownership`)**
   - Calcule la proportion de modifications apportées par le développeur actuel par rapport à ses contributions globales.
   - **Objectif :** Mesurer à quel point un développeur est responsable d'un bloc de code spécifique.

### 4. **Expérience du développeur (`exp`)**
   - Récupère le nombre total de commits réalisés par l'auteur.
   - **Objectif :** Évaluer l'expérience globale du développeur dans le projet.

### 5. **Expérience récente (`rexp`)**
   - Mesure l'expérience du développeur en fonction des commits récents, pondérés par leur ancienneté.
   - **Objectif :** Accorder plus d'importance aux contributions récentes, indiquant une familiarité à jour avec la base de code.

### 6. **Expérience sur un sous-système (`sexp`)**
   - Évalue l'expérience du développeur au sein d'un sous-système spécifique (ex. module ou niveau de répertoire).
   - **Objectif :** Vérifier si le développeur a déjà travaillé dans le sous-système concerné.

### 7. **Expérience sur un bloc (`bexp`)**
   - Calcule l'expérience du développeur dans la modification de blocs similaires.
   - **Objectif :** Déterminer dans quelle mesure le développeur est familier avec la modification de structures similaires dans le code.

### 8. **Expérience en gestion de ressources (`kexp`)**
   - Évalue l'expérience avec des types spécifiques de ressources ou de structures de données.
   - **Objectif :** Vérifier si le développeur a déjà travaillé avec des composants similaires.

### 9. **Âge moyen des modifications (`age`)**
   - Calcule la différence de temps moyenne entre les modifications passées et la modification actuelle.
   - **Objectif :** Indiquer la fréquence à laquelle un bloc a été modifié au fil du temps.

### 10. **Intervalle de temps entre les modifications (`time_interval`)**
   - Détermine le temps écoulé entre la modification la plus récente et la modification actuelle.
   - **Objectif :** Identifier les parties du code sujettes à des modifications fréquentes.

### 11. **Nombre de défauts précédents (`num_defects_before`)**
   - Compte le nombre de fois où le bloc a été associé à des défauts dans les modifications passées.
   - **Objectif :** Évaluer si le bloc présente un historique de bogue.

### 12. **Nombre d'instances dupliquées proches (`num_same_instances_changed_before`)**
   - Compte le nombre d'instances où des blocs similaires ont été introduits auparavant.
   - **Objectif :** Identifier les modifications redondantes ou dupliquées dans la base de code.

### 13. **Nombre de modifications uniques (`num_unique_change`)**
   - Mesure combien de commits uniques ont eu un impact sur le bloc.
   - **Objectif :** Déterminer la fréquence à laquelle le bloc a été affecté par des modifications distinctes.

## Comment l'utiliser
La classe `ProcessMetrics` peut être instanciée avec une contribution et un historique de contributions précédentes. Une fois instanciée, la méthode `resume_process_metrics` retourne toutes les métriques calculées sous forme de dictionnaire structuré.

Exemple d'utilisation :

```python
process_metrics = ProcessMetrics(contribution, previous_contributions)
metrics = process_metrics.resume_process_metrics()
print(metrics)
```

## Références
- Article sur la propriété du code : [https://www.sciencedirect.com/science/article/pii/S0164121219302675](https://www.sciencedirect.com/science/article/pii/S0164121219302675)
- Expérience des développeurs en revue de code : [https://ieeexplore.ieee.org/document/9689967](https://ieeexplore.ieee.org/document/9689967)

## Conclusion
La classe `ProcessMetrics` fournit des indicateurs pertinents pouvant être utilisés pour l'analyse de la qualité du code, le suivi de la performance des développeurs et l'évaluation des risques. En exploitant ces métriques, les équipes peuvent mieux comprendre l'impact des modifications sur leurs projets et prendre des décisions éclairées en matière de maintenance et d'amélioration logicielle.


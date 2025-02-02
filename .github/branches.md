# Guide des Branches pour le projet

Ce document fournit des directives sur les différentes catégories de branches utilisées dans notre dépôt Git.

## Catégories de Branches

### `feature/`

- **Utilisation**: Pour le développement de nouvelles fonctionnalités ou l'amélioration de fonctionnalités existantes.
- **Exemple de branche**: `feature/add-login`

### `bugfix/`

- **Utilisation**: Pour les correctifs de bugs identifiés dans le logiciel.
- **Exemple de branche**: `bugfix/resolve-login-issue`


### `test/`

- **Utilisation**: Pour des expérimentations ou des tests qui ne sont pas directement liés à une issue ou un ticket.
- **Exemple de branche**: `test/new-database-engine`

### `doc/`

- **Utilisation**: Pour la création et la mise à jour de la documentation du projet, incluant les fichiers README, les guides d'utilisation, et tout autre document relatif au projet.
- **Exemple de branche**: `doc/update-installation-guide`

### `main`

- **Utilisation**: Représente l'état actuel du logiciel tel qu'il est en production. Tous les changements finaux sont fusionnés ici.
- **Règle**: Ne pas pousser directement sur `main`; utilisez des pull requests.

## Procédure standard

- Les branches doivent être nommées en suivant la convention `categorie/reference/description-en-kebab-case`.
- Si vous travaillez sur une issue, incluez la référence de l'issue dans le nom de la branche.
- Si la branche ne correspond pas à une issue spécifique, utilisez `no-ref` dans la section de référence.
- Fournissez une description courte et significative en kebab-case après la référence.

## Exemples de noms de Branches

```bash
git branch feature/42-implement-oauth
git branch bugfix/105-fix-header-layout
git branch test/try-react-hooks
git branch doc/update-installation-guide
```

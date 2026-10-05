# Sécurité

## Statut : IMPLEMENTED (protections partielles)

L'accès tool est refusé par défaut ; les tools de fichiers contrôlent le chemin résolu et ne modifient rien. Quant est limité au paper trading. Le journal d'audit append-only de l'API est chaîné par SHA-256 et possède un vérificateur testé. Cette chaîne ne protège pas contre une personne ayant accès direct à SQLite ; l'API ne comporte pas d'authentification. Les contrôles réseau, sandbox processus et modèle de menace complet restent PLANNED. La release est bloquée par défaut.
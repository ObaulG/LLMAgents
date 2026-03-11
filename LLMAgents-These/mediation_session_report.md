
# Rapport d'évaluation des sessions de médiation

## Résumé des configurations testées

### Modèles ministral

**Meilleure configuration**: 3 eval(ministral-3b-latest, ministral-3b-latest, ministral-3b-latest) + final(mistral-large-latest)
- Score moyen: 7.0
- Temps total: 79.79s
- Tokens totaux: 29675
- Efficacité (score/temps): 0.09 score/s

| Configuration | Score moyen | Temps (s) | Tokens | Efficacité (score/s) |
|---------------|-------------|-----------|--------|---------------------|
| 3 eval(ministral-3b-latest, ministral-3b-latest, ministral-3b-latest) + final(mistral-large-latest) | 7.0 | 79.79 | 29675 | 0.088 |

### Modèles mistral

**Meilleure configuration**: 3 eval(mistral-small, mistral-small, mistral-small) + final(mistral-small)
- Score moyen: 6.4
- Temps total: 15.58s
- Tokens totaux: 23265
- Efficacité (score/temps): 0.41 score/s

| Configuration | Score moyen | Temps (s) | Tokens | Efficacité (score/s) |
|---------------|-------------|-----------|--------|---------------------|
| 3 eval(mistral-small, mistral-small, mistral-small) + final(mistral-small) | 6.4 | 15.58 | 23265 | 0.411 |

## Analyse des temps d'exécution par modèle

| Modèle | Temps moyen (s) | Temps min (s) | Temps max (s) | Écart-type |
|--------|-----------------|---------------|---------------|------------|
| final_mistral-large-latest | 73.278 | 73.278 | 73.278 | 0.000 |
| final_mistral-small | 5.505 | 5.505 | 5.505 | 0.000 |
| ministral-3b-latest | 11.570 | 11.570 | 11.570 | 0.000 |
| mistral-small | 18.016 | 18.016 | 18.016 | 0.000 |

## Analyse globale
- Score moyen global: 6.7
- Temps moyen: 47.69s
- Tokens moyens: 26470
- Meilleure configuration globale: 3 eval(mistral-small, mistral-small, mistral-small) + final(mistral-small)
  - Score: 6.4
  - Temps: 15.58s
  - Efficacité: 0.411 score/s

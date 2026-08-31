# Copyright 2026 Romy Alula — MIT License
"""Identifiants de questions partagés entre scoring.py et cli.py.

Évite le couplage fragile par matching de sous-chaînes sur le texte libre.
Chaque question a un ID stable et le texte associé.
"""

from __future__ import annotations

QUESTION_IDS: dict[str, str] = {
    'PR_SIZES': (
        "Quelle est la taille habituelle de tes features livrées avec l'IA (S, M, L, XL) ?"
    ),
    'DECLARED_LEVEL': (
        "À quel niveau d'adoption de l'AIDD estimes-tu en être actuellement, et sur quoi te bases-tu ?"
    ),
    'RETRIES_RATIO': (
        'Quelle part de tes PR est reprise ou corrigée par toi après coup ?'
        " (Et vient-elle d'erreurs de l'IA, de raffinement, de contexte perdu ?)"
    ),
    'RETRIES_TRIANGULATED': (
        "Proportion de reprise indiquée sans PR à l'appui : peux-tu fournir "
        'quelques PR typiques pour la corroborer ?'
    ),
    'ADOPTION_SIGNALS': ('As-tu une mémoire projet (contexte) ? Des règles ou agents versionnés ?'),
    'PARALLEL_PROJECTS': (
        'Combien de chantiers mènes-tu en parallèle, habituellement, et combien vont au bout ?'
    ),
    'PROJECTS_COMPLETED': ("Parmi ces chantiers, combien sont menés jusqu'au bout ?"),
    'DEFAULT': (
        "Les données fournies semblent complètes : quelle dimension veux-tu vérifier d'abord ?"
    ),
}

# Mapping question ID → clés de traces associées (pour le parsing dans cli.py)
QUESTION_TRACE_KEYS: dict[str, list[str]] = {
    'PR_SIZES': ['pr_sizes'],
    'DECLARED_LEVEL': ['declared_level'],
    'RETRIES_RATIO': ['retries_after_fact'],
    'RETRIES_TRIANGULATED': ['retries_triangulated'],
    'ADOPTION_SIGNALS': ['context_versioned', 'agent_rules_versioned', 'prompts'],
    'PARALLEL_PROJECTS': ['parallel_projects'],
    'PROJECTS_COMPLETED': ['projects_completed'],
}

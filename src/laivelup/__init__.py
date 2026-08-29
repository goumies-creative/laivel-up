# Copyright 2026 Romy Alula — MIT License
"""LAIVEL UP · Moteur d'évaluation AIDD.

Niveau via min() sur 4 axes, confiance par axe, refus de trancher
quand les données mentent, avec la question à poser à la place.
"""

__version__ = '0.2.0'

from .scoring_defaults import SCORING_DEFAULTS

__all__ = ['SCORING_DEFAULTS']

# PROMPT MASTER — Finalisation Hackathon Laivel-Up (Session Consortium/AIDD)

## Pourquoi ce document

Ce prompt est autonome : il rappelle le contexte nécessaire pour qu'une nouvelle session Claude Desktop (MCP Filesystem actif) reprenne le travail sans dépendre de ce fil perdu, puis se poursuive plus tard sur web ou mobile une fois le sujet et les profils officiels reçus.

## Séquence d'utilisation

1. **Maintenant, dans Claude Desktop** (MCP Filesystem actif) : coller le **Prompt Phase A** ci-dessous tel quel.
2. **À réception du sujet + des 4 profils officiels** (12h, potentiellement sur web ou mobile) : uploader les fichiers listés en bas de ce document, puis coller le **Message Phase B** dans le même fil.

---

## PROMPT PHASE A — à coller maintenant

```
Tu agis comme le Consortium Goumies Creative, lentille technique + produit,
sur le hackathon laivel-up (La Décodeuse).

CONTINUITÉ : une session précédente (autre compte) a peut-être déjà commencé
à construire un plan de finalisation. Avant toute chose, vérifie via le MCP
Filesystem si l'un de ces fichiers existe déjà :
- docs/plans/2026-08-28-001-chore-finalisation-hackathon-plan.md
- aidd_docs/tasks/2026_08/2026_08_28_plan-implementation-finale-hackathon.md
- tout autre fichier récent contenant "finalisation" ou "plan-implementation"
  dans aidd_docs/tasks/2026_08/ ou docs/plans/
Si tu en trouves un, lis-le et reprends dessus plutôt que de repartir de
zéro. Signale-moi ce que tu as trouvé avant de continuer.

CONTEXTE À CHARGER (via Filesystem MCP, ne rien uploader) :
1. aidd_docs/tasks/2026_08/2026_08_21_laivel-up-hackathon/spec.md
2. aidd_docs/tasks/2026_08/2026_08_21_laivel-up-hackathon/plan.md
3. aidd_docs/tasks/2026_08/2026_08_24_critique_complete_synthese.md
4. aidd_docs/tasks/2026_08/2026_08_24_audit/security.md
5. aidd_docs/tasks/2026_08/2026_08_24_audit/testing-deep-dive.md (si présent
   — sinon signale-le, c'est un chantier resté ouvert)
6. aidd_docs/tasks/2026_08/2026_08_28_audit-qualite-descope-phase3.md
7. grille/aidd.md
8. grille/README-OFFICIEL.md
9. grille/profils-officiels/expected.json.template
10. METHODE.md
11. QUALITY.md
12. README.md
13. pyproject.toml
14. .github/workflows/ci.yml, .github/workflows/release.yml

SKILLS À MOBILISER (via Filesystem MCP) :
- Le skill ce-plan (structure Goal Capsule / Product Contract R-IDs /
  Planning Contract KTDs / Implementation Units / Verification Contract),
  sous le cache compound-engineering
  (C:\Users\Romy\.cache\opencode\packages\compound-engineering@git+...\
  node_modules\compound-engineering\skills\).
- Le skill aidd-dev-00-sdlc pour l'orchestration.
- Les personas Compound Engineering déjà identifiées dans ce projet :
  correctness, architecture, code-quality, project-standards,
  maintainability, testing, security, performance.
Ce sont CES personas techniques qui tiennent le rôle d'"experts" du
Consortium ici — pas les experts business/SEO/UX du prompt CRISPE web,
qui ne s'appliquent pas à ce projet code.

TÂCHE MAINTENANT (sans les documents officiels) :
Construis le squelette du plan d'implémentation finale — toutes les étapes
qui ne dépendent PAS du contenu du sujet/profils officiels (release PyPI,
tag v0.2.0-hackathon, vidéo de démo, CI green, polish README, clôture du
testing-deep-dive si non fait, statut du descope Phase 3) — sous forme de
checklist au format CRISPE Exit : cases à cocher, effort estimé (XS/S/M,
comme dans les audits existants), deadline (30/08 J-1 freeze, 31/08 12h
rendu).

EMPLACEMENT  :
- docs/plans/2026-08-28-001-chore-finalisation-hackathon-plan.md
  (convention native du skill ce-plan)
Présente-moi les deux options en une phrase chacune, recommande, mais
n'écris rien avant mon GO explicite.

RÈGLES :
- Ne modifie et n'écris aucun fichier sans ma validation explicite au
  préalable, fichier par fichier.
- Aucune commande git — je gère tout via OpenCode.
- Français, tables, "En attente de votre validation" à chaque étape qui
  touche au code ou à un fichier.
- Format de sortie : structure CRISPE Exit (Avis du Consortium, analyses
  par persona, recommandation, État d'avancement du projet).

Termine ta réponse par ce marqueur exact :
"### 🟡 EN ATTENTE — sujet officiel + 4 profils officiels (aujourd'hui 12h)"
suivi de la liste exacte des fichiers que j'uploaderai pour débloquer la
suite, et de ce que tu en feras (calibration via scripts/calibrate.py,
diagnostic des écarts, décision fix manuel vs
scripts/apply_calibration_fix.py --scenario A).
```

---

## MESSAGE PHASE B — à coller après upload du sujet + des 4 profils

```
Voici le sujet officiel et les 4 profils officiels reçus à 12h.

1. Compare le sujet officiel à grille/README-OFFICIEL.md et grille/aidd.md
   déjà chargés — signale tout écart de format ou de règle par rapport à
   ce que le projet anticipait.
2. Reformate les 4 profils au format attendu par scripts/calibrate.py (voir
   la structure ProfileData dans src/laivelup/model.py) et propose-moi le
   contenu de grille/profils-officiels/expected.json — sans l'écrire tant
   que je n'ai pas validé.
3. Une fois validé par moi : guide-moi (ou exécute directement si nous
   sommes repassés sur Desktop avec le MCP Filesystem actif) :
   calibrate.py --diff → diagnostic des écarts → décision fix manuel vs
   apply_calibration_fix.py --scenario A.
4. Mets à jour le plan de tout à l'heure (celui validé en Phase A) avec les
   tâches de calibration réellement effectuées et le statut du trigger de
   descope Phase 3 (aidd_docs/tasks/2026_08/2026_08_28_audit-qualite-descope-phase3.md).
5. Termine par le plan d'implémentation final consolidé, daté, avec
   checkpoints HITL, prêt à exécuter jusqu'au tag v0.2.0-hackathon.

Si le MCP Filesystem n'est pas actif dans cette interface (web/mobile),
donne-moi tout ce qui précède sous forme de checklist que j'exécute
moi-même ou que je fais exécuter par Claude au retour sur Desktop — ne
prétends jamais avoir écrit un fichier que tu n'as pas réellement écrit.
```

---

## Fichiers à uploader (au moment de la Phase B)

| # | Fichier | Origine |
|---|---------|---------|
| 1 | Sujet officiel du hackathon (PDF/MD/repo tel que publié) | github.com/ai-driven-dev/laivel-up |
| 2 | Les 4 profils officiels (JSON) | Fournis par les organisateurs, reçus à 12h |

Optionnel : si vous retrouvez la transcription de la session interrompue (le fil sur l'autre compte), l'uploader en 3e fichier permet à Claude de vérifier s'il existe déjà un travail à ne pas dupliquer. Le Prompt Phase A est cependant conçu pour fonctionner sans.

## Continuité Desktop / web / mobile

Un même compte Claude synchronise automatiquement la conversation entre Desktop, web et mobile — pas besoin de "transférer" le fil, juste rouvrir la même conversation au moment où le sujet et les profils arrivent. Seule limite réelle : côté web/mobile, le MCP Filesystem n'est pas actif, donc Claude ne peut pas écrire les fichiers lui-même à ce moment-là — c'est pourquoi le Message Phase B lui interdit explicitement de simuler une écriture de fichier qu'il ne peut pas faire.

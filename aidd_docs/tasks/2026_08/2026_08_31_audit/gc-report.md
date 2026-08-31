{
  "repo": "goumies-creative-laivel-up",
  "global_score": 7.8,
  "status": "WARN",
  "p0": 0,
  "p1": 4,
  "axes": [
    {
      "axe": "security",
      "label": "Sécurité",
      "score": 8.2,
      "passed": false,
      "findings": [
        "bandit: 3 issues détectés"
      ],
      "p0": 0,
      "p1": 3
    },
    {
      "axe": "performance",
      "label": "Performance",
      "score": 6.5,
      "passed": false,
      "findings": [
        "21 appels subprocess (potentiellement lent)",
        "io: src\\laivelup\\_completion_patch.py:6 — read_text() sans encoding (Windows)",
        "io: tests\\test_team_rgpd.py:238 — write_text() sans encoding (Windows)",
        "complexity: build\\lib\\laivelup\\calibrate_dashboard.py::_render_profile_node (complexité ~18)",
        "complexity: build\\lib\\laivelup\\cli.py::_parse_retry_ratio (complexité ~18)",
        "complexity: build\\lib\\laivelup\\cli.py::_merge_answer (complexité ~23)",
        "complexity: build\\lib\\laivelup\\report.py::_render_world_map (complexité ~16)",
        "complexity: build\\lib\\laivelup\\schema.py::validate_profile (complexité ~17)",
        "n+1: tests\\test_team_rgpd.py:196"
      ],
      "p0": 0,
      "p1": 1
    },
    {
      "axe": "architecture",
      "label": "Architecture",
      "score": 6.5,
      "passed": false,
      "findings": [
        "late-import: build\\lib\\laivelup\\calibrate_core.py:7",
        "late-import: build\\lib\\laivelup\\calibrate_core.py:9",
        "late-import: build\\lib\\laivelup\\calibrate_core.py:10",
        "late-import: build\\lib\\laivelup\\calibrate_core.py:11",
        "late-import: build\\lib\\laivelup\\calibrate_core.py:13",
        "late-import: build\\lib\\laivelup\\calibrate_core.py:14",
        "late-import: build\\lib\\laivelup\\calibrate_dashboard.py:11",
        "late-import: build\\lib\\laivelup\\calibrate_dashboard.py:13",
        "late-import: build\\lib\\laivelup\\calibrate_dashboard.py:15",
        "late-import: build\\lib\\laivelup\\calibrate_dashboard.py:16",
        "large-module: build\\lib\\laivelup\\cli.py (888 lignes)",
        "large-module: build\\lib\\laivelup\\report.py (1029 lignes)",
        "large-module: src\\laivelup\\cli.py (985 lignes)",
        "large-module: src\\laivelup\\report.py (1051 lignes)",
        "large-module: tests\\test_cli_extended.py (1400 lignes)"
      ],
      "p0": 0,
      "p1": 0
    },
    {
      "axe": "maintainability",
      "label": "Maintenabilité",
      "score": 7.5,
      "passed": true,
      "findings": [
        "large-func: tests\\test_apply_calibration_fix.py::test_import (81 lignes)",
        "large-func: tests\\test_apply_calibration_fix.py::test_help (76 lignes)",
        "large-func: tests\\test_apply_calibration_fix.py::test_dry_run_no_changes (66 lignes)",
        "large-func: tests\\test_apply_calibration_fix.py::test_apply_scenario_a (57 lignes)",
        "large-func: tests\\test_calibrate.py::test_1_erreur_si_niveau_faux (96 lignes)",
        "dead-code: scripts\\apply_calibration_fix.py:160",
        "dead-code: scripts\\apply_calibration_fix.py:174"
      ],
      "p0": 0,
      "p1": 0
    },
    {
      "axe": "testing",
      "label": "Testing",
      "score": 10.0,
      "passed": true,
      "findings": [],
      "p0": 0,
      "p1": 0
    }
  ]
}
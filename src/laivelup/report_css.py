# Copyright 2026 Romy Alula — MIT License
"""CSS embarqué du rapport HTML LAIVEL-UP.

Ce module est extrait de report.py pour alléger la lisibilité.
Aucun framework CSS externe. Le rapport reste autonome une fois généré.
"""

CSS_STYLES = r"""
:root {
    --bg: #0b0d12;
    --surface: #11151d;
    --surface-2: #171c25;

    --border: #2b3442;
    --border-active: #56657a;

    --text: #e7ebf0;
    --text-secondary: #a7b0bd;
    --muted: #697586;

    --info: #4db8ff;
    --ok: #39d98a;
    --warn: #e3b341;
    --danger: #ef6262;

    --mono:
        "IBM Plex Mono",
        "SFMono-Regular",
        "Cascadia Code",
        "Roboto Mono",
        Consolas,
        monospace;
}

* {
    box-sizing: border-box;
}

html {
    background: var(--bg);
}

body {
    margin: 0;

    background:
        linear-gradient(
            180deg,
            #0b0d12 0%,
            #0d1016 100%
        );

    color: var(--text);

    font-family: var(--mono);

    line-height: 1.55;
}

body::before {
    content: "";

    position: fixed;

    inset: 0;

    pointer-events: none;

    opacity: .025;

    background-image:
        linear-gradient(
            rgba(255,255,255,.5) 1px,
            transparent 1px
        );

    background-size: 100% 4px;

    z-index: 100;
}

a {
    color: var(--info);

    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}

code {
    padding: 1px 4px;

    border: 1px solid var(--border);

    color: var(--info);

    background: var(--bg);

    font-family: inherit;
}

.app-shell {
    width: min(1440px, calc(100% - 48px));

    margin: 24px auto 48px;

    border: 1px solid var(--border);

    background: var(--surface);

    position: relative;

    z-index: 1;
}


/* ------------------------------------------------------------------ */
/* HEADER                                                             */
/* ------------------------------------------------------------------ */

.system-header {
    min-height: 72px;

    display: grid;

    grid-template-columns:
        minmax(220px, 1fr)
        minmax(220px, 1fr)
        auto;

    align-items: stretch;

    border-bottom: 1px solid var(--border);
}

.brand,
.profile-context,
.system-status {
    padding: 14px 20px;
}

.brand {
    display: flex;

    align-items: center;

    gap: 14px;
}

.brand-mark {
    color: var(--info);

    font-size: 18px;
}

.brand strong {
    display: block;

    font-size: 14px;

    letter-spacing: .12em;
}

.brand span:last-child {
    display: block;

    margin-top: 3px;

    color: var(--muted);

    font-size: 9px;

    letter-spacing: .18em;
}

.profile-context {
    border-left: 1px solid var(--border);
}

.profile-context span,
.system-status {
    color: var(--muted);

    font-size: 9px;

    letter-spacing: .15em;
}

.profile-context strong {
    display: block;

    margin-top: 3px;

    color: var(--text);

    font-size: 12px;

    font-weight: 500;
}

.system-status {
    display: flex;

    align-items: center;

    gap: 8px;

    white-space: nowrap;
}

.status-dot {
    width: 7px;
    height: 7px;

    display: inline-block;

    background: var(--ok);
}


/* ------------------------------------------------------------------ */
/* GENERAL                                                            */
/* ------------------------------------------------------------------ */

main {
    padding: 0 28px;
}

.section {
    padding: 48px 0;

    border-bottom: 1px solid var(--border);
}

.section-heading {
    display: flex;

    align-items: flex-start;

    gap: 14px;

    margin-bottom: 28px;
}

.section-index {
    color: var(--muted);

    font-size: 10px;

    letter-spacing: .1em;

    padding-top: 4px;
}

.eyebrow {
    display: block;

    color: var(--muted);

    font-size: 9px;

    letter-spacing: .16em;

    text-transform: uppercase;
}

h1,
h2,
h3,
p {
    margin-top: 0;
}

h2 {
    margin: 3px 0 0;

    font-size: 19px;

    font-weight: 500;

    letter-spacing: -.02em;
}

h3 {
    margin: 4px 0 0;

    font-size: 13px;

    font-weight: 500;
}

.field-label {
    display: block;

    color: var(--muted);

    font-size: 8px;

    letter-spacing: .15em;
}


/* ------------------------------------------------------------------ */
/* VERDICT HERO                                                       */
/* ------------------------------------------------------------------ */

.verdict-hero {
    min-height: 440px;

    display: grid;

    grid-template-columns:
        minmax(280px, 40%)
        1fr;

    align-items: center;

    gap: 48px;

    border-bottom: 1px solid var(--border);

    position: relative;
}

.hero-monitor {
    display: flex;

    justify-content: center;

    align-items: center;
}

.hero-verdict {
    border-left: 2px solid var(--verdict-accent);

    padding-left: 32px;
}

.hero-verdict h1 {
    margin: 12px 0 28px;

    color: var(--verdict-accent);

    font-size: clamp(48px, 7vw, 92px);

    line-height: .9;

    letter-spacing: -.08em;

    font-weight: 600;
}

.hero-limiting {
    display: grid;

    grid-template-columns: 130px 1fr;

    gap: 18px;

    margin-bottom: 28px;

    padding-top: 18px;

    border-top: 1px solid var(--border);
}

.hero-limiting span {
    color: var(--muted);

    font-size: 9px;

    letter-spacing: .13em;
}

.hero-limiting strong {
    font-size: 13px;

    font-weight: 500;
}


/* ------------------------------------------------------------------ */
/* STATUS BAR                                                         */
/* ------------------------------------------------------------------ */

.verdict-status {
    display: inline-flex;

    align-items: center;

    gap: 10px;

    padding: 8px 12px;

    border: 1px solid var(--verdict-accent);

    color: var(--verdict-accent);

    font-size: 9px;

    letter-spacing: .1em;
}

.verdict-status.ok {
    color: var(--ok);

    border-color: var(--ok);
}

.verdict-status.ko {
    color: var(--danger);

    border-color: var(--danger);
}


/* ------------------------------------------------------------------ */
/* MONITOR AVATAR                                                     */
/* ------------------------------------------------------------------ */

.monitor-avatar {
    --avatar-accent: var(--info);

    width: min(270px, 72vw);

    filter: drop-shadow(
        0 0 24px
        color-mix(
            in srgb,
            var(--avatar-accent) 12%,
            transparent
        )
    );
}

.monitor-shell {
    position: relative;

    aspect-ratio: 1.22;

    padding: 13%;

    background: var(--avatar-accent);

    clip-path: polygon(
        5% 8%,
        94% 5%,
        100% 15%,
        97% 88%,
        91% 96%,
        9% 100%,
        1% 90%,
        3% 14%
    );
}

.monitor-screen {
    height: 100%;

    display: flex;

    flex-direction: column;

    align-items: center;

    justify-content: center;

    gap: 22px;

    background: var(--bg);

    clip-path: polygon(
        3% 4%,
        97% 3%,
        100% 12%,
        96% 95%,
        6% 97%,
        1% 89%,
        3% 12%
    );
}

.monitor-eyes {
    display: flex;

    gap: 34px;

    color: var(--avatar-accent);

    font-size: 31px;

    font-weight: 700;

    line-height: 1;
}

.monitor-mouth {
    width: 44px;

    height: 5px;

    background: var(--avatar-accent);
}

.monitor-avatar.analyzing .monitor-mouth {
    width: 26px;
}

.monitor-avatar.questioning .monitor-mouth {
    width: 18px;

    transform: translateY(-3px);
}

.monitor-avatar.success .monitor-mouth {
    width: 52px;

    height: 7px;
}

.monitor-avatar.warning .monitor-mouth {
    width: 28px;
}

.monitor-avatar.error .monitor-mouth,
.monitor-avatar.refusal .monitor-mouth {
    width: 32px;
}


/* ------------------------------------------------------------------ */
/* CONFIDENCE                                                         */
/* ------------------------------------------------------------------ */

.confidence {
    max-width: 440px;
}

.confidence-header {
    display: flex;

    justify-content: space-between;

    align-items: baseline;

    margin-bottom: 8px;
}

.confidence-label {
    color: var(--muted);

    font-size: 9px;

    letter-spacing: .14em;
}

.confidence-value {
    color: var(--text);

    font-size: 13px;
}

.confidence-bar {
    overflow: hidden;

    white-space: nowrap;

    font-size: 13px;

    letter-spacing: -2px;
}

.confidence-filled {
    color: var(--verdict-accent);
}

.confidence-empty {
    color: var(--border-active);
}


/* ------------------------------------------------------------------ */
/* AXES                                                               */
/* ------------------------------------------------------------------ */

.axis-grid {
    display: grid;

    grid-template-columns:
        repeat(2, minmax(0, 1fr));

    gap: 10px;
}

.axis-card {
    min-height: 190px;

    padding: 20px;

    border: 1px solid var(--border);

    background: var(--surface-2);

    position: relative;
}

.axis-card::before {
    content: "";

    position: absolute;

    left: 0;

    top: 0;

    bottom: 0;

    width: 3px;

    background: var(--axis-accent);
}

.axis-card-limiting {
    border-color: var(--axis-accent);
}

.axis-card-header {
    display: flex;

    justify-content: space-between;

    align-items: flex-start;

    gap: 20px;

    padding-bottom: 18px;

    border-bottom: 1px solid var(--border);
}

.axis-index {
    color: var(--muted);

    font-size: 8px;

    letter-spacing: .12em;
}

.axis-meta {
    text-align: right;
}

.axis-level {
    color: var(--axis-accent);

    font-size: 11px;

    font-weight: 600;

    letter-spacing: .1em;
}

.axis-limiting {
    display: block;

    margin-bottom: 6px;

    color: var(--danger);

    font-size: 7px;

    letter-spacing: .1em;
}

.axis-card-body {
    padding-top: 18px;
}

.axis-confidence {
    display: flex;

    justify-content: space-between;

    margin-bottom: 18px;

    color: var(--muted);

    font-size: 9px;
}

.axis-confidence strong {
    color: var(--text);

    font-weight: 500;
}

.axis-evidence p {
    margin: 5px 0 0;

    color: var(--text-secondary);

    font-size: 11px;
}


/* ------------------------------------------------------------------ */
/* RED FLAGS                                                          */
/* ------------------------------------------------------------------ */

.red-flags {
    display: grid;

    gap: 8px;
}

.red-flag {
    display: grid;

    grid-template-columns: 80px 1fr;

    border: 1px solid rgba(239, 98, 98, .35);

    background: rgba(239, 98, 98, .035);
}

.red-flag-marker {
    padding: 20px;

    color: var(--danger);

    border-right: 1px solid rgba(239, 98, 98, .25);

    font-weight: 700;

    letter-spacing: .1em;
}

.red-flag-content {
    padding: 20px;
}

.red-flag-content h3 {
    margin-bottom: 10px;
}

.flag-finding {
    margin-bottom: 12px;

    color: var(--text-secondary);

    font-size: 11px;
}

.flag-source {
    color: var(--muted);

    font-size: 8px;

    letter-spacing: .08em;
}

.flag-question {
    margin-top: 18px;

    padding: 14px;

    border-left: 2px solid var(--info);

    background: rgba(77, 184, 255, .04);
}

.flag-question span {
    color: var(--info);

    font-size: 8px;

    letter-spacing: .12em;
}

.flag-question p {
    margin: 6px 0 0;

    color: var(--text);

    font-size: 11px;
}

.diagnostic-clear {
    padding-top: 28px;

    padding-bottom: 28px;
}

.diagnostic-status {
    display: flex;

    align-items: center;

    gap: 10px;

    color: var(--ok);

    font-size: 9px;

    letter-spacing: .12em;
}

.status-symbol {
    padding: 3px 6px;

    border: 1px solid currentColor;
}


/* ------------------------------------------------------------------ */
/* NEXT STEPS                                                         */
/* ------------------------------------------------------------------ */

.next-steps {
    list-style: none;

    margin: 0;

    padding: 0;

    display: grid;

    gap: 6px;
}

.next-step {
    display: grid;

    grid-template-columns: 56px 1fr;

    border: 1px solid var(--border);

    background: var(--surface-2);
}

.next-step-index {
    display: flex;

    align-items: center;

    justify-content: center;

    color: var(--info);

    border-right: 1px solid var(--border);

    font-size: 10px;
}

.next-step-content {
    padding: 17px 20px;

    color: var(--text-secondary);

    font-size: 11px;
}


/* ------------------------------------------------------------------ */
/* REFUSAL                                                            */
/* ------------------------------------------------------------------ */

.refusal-screen {
    min-height: 520px;

    display: grid;

    grid-template-columns: 300px 1fr;

    gap: 60px;

    align-items: center;

    border-bottom: 1px solid var(--border);
}

.refusal-monitor {
    display: flex;

    justify-content: center;
}

.refusal-content {
    max-width: 620px;
}

.refusal-content h1 {
    margin: 12px 0;

    color: var(--danger);

    font-size: 72px;

    letter-spacing: -.08em;
}

.refusal-lead {
    color: var(--text);

    font-size: 17px;
}

.refusal-content > p:not(.refusal-lead) {
    color: var(--text-secondary);

    font-size: 12px;
}

.refusal-errors {
    margin-top: 28px;

    padding: 18px;

    border: 1px solid rgba(239, 98, 98, .3);

    background: rgba(239, 98, 98, .03);
}

.refusal-errors ul {
    margin: 10px 0 0;

    padding-left: 18px;

    color: var(--text-secondary);

    font-size: 11px;
}

.refusal-action {
    display: inline-flex;

    align-items: center;

    gap: 10px;

    margin-top: 28px;

    padding: 10px 14px;

    border: 1px solid var(--info);

    color: var(--info);

    font-size: 9px;

    letter-spacing: .1em;
}

.action-key {
    padding: 2px 6px;

    border: 1px solid currentColor;
}


/* ------------------------------------------------------------------ */
/* TRANSPARENCY                                                       */
/* ------------------------------------------------------------------ */

.transparency-grid {
    display: grid;

    grid-template-columns:
        repeat(3, minmax(0, 1fr));

    gap: 8px;
}

.transparency-grid article {
    padding: 20px;

    border: 1px solid var(--border);

    background: var(--surface-2);
}

.transparency-grid p {
    margin: 12px 0 0;

    color: var(--text-secondary);

    font-size: 10px;
}


/* ------------------------------------------------------------------ */
/* GLOSSAIRE                                                          */
/* ------------------------------------------------------------------ */

.glossary-grid {
    display: grid;

    grid-template-columns:
        repeat(2, minmax(0, 1fr));

    gap: 6px;
}

.glossary-item {
    border: 1px solid var(--border);

    background: var(--surface-2);
}

.glossary-item summary {
    cursor: pointer;

    padding: 14px 16px;

    color: var(--text);

    font-size: 10px;
}

.glossary-item summary::marker {
    color: var(--info);
}

.glossary-item p {
    margin: 0;

    padding: 0 16px 16px;

    color: var(--text-secondary);

    font-size: 10px;
}


/* ------------------------------------------------------------------ */
/* PEDAGOGY                                                           */
/* ------------------------------------------------------------------ */

.guide-section {
    margin-bottom: 28px;

    padding: 20px;

    border: 1px solid var(--border);

    background: var(--surface-2);
}

.guide-section h3 {
    margin-bottom: 16px;
}

.guide-item {
    display: grid;

    grid-template-columns: 150px 1fr;

    gap: 20px;
}

.guide-axe {
    color: var(--info);

    font-size: 10px;
}

.guide-step {
    color: var(--text-secondary);

    font-size: 11px;
}

.references {
    margin-top: 30px;
}

.reference-item {
    display: grid;

    grid-template-columns:
        minmax(180px, .35fr)
        1fr;

    gap: 20px;

    padding: 12px 0;

    border-bottom: 1px solid var(--border);
}

.reference-item a {
    font-size: 10px;
}

.reference-item span {
    color: var(--muted);

    font-size: 9px;
}


/* ------------------------------------------------------------------ */
/* FOOTER                                                             */
/* ------------------------------------------------------------------ */

.system-footer {
    min-height: 52px;

    display: flex;

    align-items: center;

    justify-content: space-between;

    gap: 20px;

    padding: 12px 20px;

    color: var(--muted);

    font-size: 8px;

    letter-spacing: .12em;
}


/* ------------------------------------------------------------------ */
/* RESPONSIVE                                                         */
/* ------------------------------------------------------------------ */

@media (max-width: 900px) {

    .app-shell {
        width: calc(100% - 24px);

        margin: 12px auto 24px;
    }

    .system-header {
        grid-template-columns: 1fr;
    }

    .profile-context {
        border-left: 0;

        border-top: 1px solid var(--border);
    }

    .system-status {
        border-top: 1px solid var(--border);
    }

    main {
        padding: 0 18px;
    }

    .verdict-hero {
        grid-template-columns: 1fr;

        padding: 48px 0;

        gap: 40px;
    }

    .hero-monitor {
        justify-content: flex-start;
    }

    .hero-verdict {
        border-left: 0;

        border-top: 2px solid var(--verdict-accent);

        padding: 24px 0 0;
    }

    .axis-grid,
    .transparency-grid,
    .glossary-grid {
        grid-template-columns: 1fr;
    }

    .refusal-screen {
        grid-template-columns: 1fr;

        padding: 48px 0;
    }

    .refusal-monitor {
        justify-content: flex-start;
    }
}

@media (max-width: 560px) {

    .app-shell {
        width: 100%;

        margin: 0;

        border-left: 0;

        border-right: 0;
    }

    main {
        padding: 0 14px;
    }

    .section {
        padding: 32px 0;
    }

    .hero-verdict h1 {
        font-size: 48px;
    }

    .red-flag {
        grid-template-columns: 1fr;
    }

    .red-flag-marker {
        border-right: 0;

        border-bottom: 1px solid rgba(239, 98, 98, .25);
    }

    .guide-item,
    .reference-item {
        grid-template-columns: 1fr;

        gap: 8px;
    }

    .system-footer {
        flex-direction: column;

        align-items: flex-start;
    }
}

@media (prefers-reduced-motion: reduce) {

    *,
    *::before,
    *::after {
        scroll-behavior: auto !important;

        transition: none !important;

        animation: none !important;
    }
}

@media print {

    body {
        background: white;

        color: #111;
    }

    body::before {
        display: none;
    }

    .app-shell {
        width: 100%;

        margin: 0;

        border: 0;
    }

    .system-header {
        color: #111;

        border-color: #ccc;
    }

    .section,
    .system-footer {
        border-color: #ccc;
    }

    .axis-card,
    .transparency-grid article,
    .next-step,
    .glossary-item {
        background: white;

        border-color: #ccc;
    }
}
"""

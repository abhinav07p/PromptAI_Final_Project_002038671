"""Shared dark theme CSS for all Streamlit pages."""

DARK_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg-primary: #0f0f1a;
    --bg-card: #1a1a2e;
    --bg-hover: #242440;
    --accent: #1abc9c;
    --accent-dim: #16a08540;
    --red: #e74c3c;
    --red-dim: #c0392b40;
    --purple: #9b59b6;
    --purple-dim: #8e44ad40;
    --warm: #f0c27f;
    --warm-dim: #d4a05340;
    --blue: #3498db;
    --text: #e0e0e0;
    --text-dim: #6b7280;
    --border: #2a2a40;
}

.stApp { font-family: 'Outfit', sans-serif !important; }

.tm-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.2rem;
    margin-bottom: 0.8rem;
    transition: border-color 0.2s;
}
.tm-card:hover { border-color: var(--accent); }

.tm-badge {
    display: inline-block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    padding: 0.2rem 0.7rem;
    border-radius: 4px;
    color: white;
}
.badge-pe { background: #2c3e50; }
.badge-ft { background: #c0392b; }
.badge-rag { background: #16a085; }
.badge-mm { background: #8e44ad; }
.badge-sdg { background: #d4a053; }

.score-high { color: #1abc9c; }
.score-mid { color: #f0c27f; }
.score-low { color: #e74c3c; }

.pipe-step {
    display: inline-block;
    background: var(--bg-card);
    border: 1px solid var(--border);
    color: var(--text);
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    padding: 0.35rem 0.7rem;
    border-radius: 5px;
    margin: 0.15rem;
}
.pipe-step.mm { border-color: var(--purple); color: var(--purple); }
.pipe-step.ft { border-color: var(--red); color: var(--red); }
.pipe-arrow { color: var(--accent); font-weight: 700; margin: 0 0.15rem; }

.stat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.8rem; margin: 1rem 0; }
.stat-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 1rem; text-align: center; }
.stat-num { font-size: 1.8rem; font-weight: 700; color: var(--accent); }
.stat-label { font-size: 0.78rem; color: var(--text-dim); }

.audit-pass { border-left: 3px solid #1abc9c; background: #1abc9c10; border-radius: 6px; padding: 0.5rem 0.8rem; margin: 0.3rem 0; font-size: 0.85rem; }
.audit-fail { border-left: 3px solid #e74c3c; background: #e74c3c10; border-radius: 6px; padding: 0.5rem 0.8rem; margin: 0.3rem 0; font-size: 0.85rem; }
.audit-skip { border-left: 3px solid #f0c27f; background: #f0c27f10; border-radius: 6px; padding: 0.5rem 0.8rem; margin: 0.3rem 0; font-size: 0.85rem; }
</style>
"""

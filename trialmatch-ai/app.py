"""TrialMatch AI — Main Entry Point"""
import streamlit as st
from pathlib import Path
from src.config.theme import DARK_CSS

st.set_page_config(page_title="TrialMatch AI", page_icon="🏥", layout="wide", initial_sidebar_state="expanded")
st.markdown(DARK_CSS, unsafe_allow_html=True)

# ═══ SIDEBAR ═══
with st.sidebar:
    mode = st.radio("**Operating Mode**", ["🎯 Demo Mode", "🦙 Ollama Mode", "🔑 API Mode"], index=0)
    mode_key = mode.split(" ")[1].lower()
    st.session_state["mode"] = mode_key

    if "demo" in mode.lower():
        st.success("✅ No setup needed")
    elif "ollama" in mode.lower():
        st.session_state["ollama_model"] = st.selectbox("Model", ["mistral","llama3","llama3.1","gemma2","phi3","llava"])
        st.session_state["ollama_url"] = st.text_input("URL", "http://localhost:11434")
    elif "api" in mode.lower():
        st.session_state["api_provider"] = st.selectbox("Provider", ["OpenAI","Anthropic"])
        key = st.text_input("API Key", type="password")
        if key: st.session_state["api_key"] = key; st.success("✅ Key set")

    st.markdown("---")
    st.markdown("**🧠 Models**")
    models_dir = Path("fine_tuning/models")
    det = {}
    for sub in ["criteria_parser","medical_ner"]:
        if (models_dir/sub/"config.json").exists(): det[sub] = True
    cp = ["LLM Few-Shot (default)"] + (["✅ Fine-Tuned: Criteria Parser"] if det.get("criteria_parser") else [])
    nr = ["LLM-Based (default)"] + (["✅ Fine-Tuned: Medical NER"] if det.get("medical_ner") else [])
    st.session_state["criteria_parser"] = st.selectbox("Criteria Parser", cp)
    st.session_state["medical_ner"] = st.selectbox("Entity Extractor", nr)
    if det: st.success(f"✅ {len(det)} model(s) detected")
    else: st.info("No fine-tuned models — using LLM fallback")

    st.markdown("---")
    st.markdown("**🎛️ Multimodal**")
    st.session_state["enable_voice"] = st.toggle("🎤 Voice Input", True)
    st.session_state["enable_vision"] = st.toggle("🖼️ Image Input", True)
    st.session_state["enable_tts"] = st.toggle("🔊 Audio Output", True)

    st.markdown("---")
    st.caption("Abhinav Kumar Piyush · NUID: 002038671 · Northeastern University · Spring 2026")

# ═══ HERO ═══
st.markdown("""
<div style="text-align:center; padding:1.5rem 1rem 0.5rem;">
    <div style="font-family:'JetBrains Mono',monospace; font-size:0.65rem; letter-spacing:0.18em; color:#1abc9c; border:1.5px solid #1abc9c; border-radius:100px; display:inline-block; padding:0.3rem 1rem; margin-bottom:1rem;">8 AGENTS · CONTROLLER-DRIVEN · 5 COMPONENTS</div>
    <h1 style="font-size:2.6rem; font-weight:700; line-height:1.1; margin:0;">Why Can't AI Find You a<br><span style="color:#e74c3c; font-style:italic;">Clinical Trial?</span></h1>
    <p style="color:#6b7280; font-size:1.05rem; max-width:600px; margin:0.8rem auto 0; line-height:1.6;">Agentic reasoning across live government APIs — with voice input, medical image understanding, and downloadable audit-trailed reports.</p>
</div>
""", unsafe_allow_html=True)

# Stats
st.markdown("""
<div class="stat-grid">
    <div class="stat-card"><div class="stat-num">~5%</div><div class="stat-label">cancer patients in trials</div></div>
    <div class="stat-card"><div class="stat-num">86%</div><div class="stat-label">miss enrollment targets</div></div>
    <div class="stat-card"><div class="stat-num">20%</div><div class="stat-label">close due to low enrollment</div></div>
    <div class="stat-card"><div class="stat-num">$8M</div><div class="stat-label">cost per day of delay</div></div>
</div>
""", unsafe_allow_html=True)

# Components
st.markdown("---")
st.markdown("""
<div style="text-align:center; margin:0.8rem 0;">
    <span class="tm-badge badge-pe">1 · PROMPT ENG</span>
    <span class="tm-badge badge-ft">2 · FINE-TUNING</span>
    <span class="tm-badge badge-rag">3 · RAG</span>
    <span class="tm-badge badge-mm">4 · MULTIMODAL</span>
    <span class="tm-badge badge-sdg">5 · SYNTHETIC DATA</span>
</div>
""", unsafe_allow_html=True)

# Pipeline
st.markdown("### ⚡ 8-Agent Pipeline")
st.markdown("""
<div style="background:#1a1a2e; border:1px solid #2a2a40; border-radius:10px; padding:1rem; text-align:center; margin:0.5rem 0;">
    <div style="margin-bottom:0.5rem;">
        <span class="pipe-step" style="border-color:#1abc9c; background:#1abc9c15;">0·CONTROLLER</span>
        <span style="color:#4a4a5a; font-size:0.65rem; margin:0 0.3rem;">plans → routes → monitors → retries</span>
    </div>
    <div style="margin-bottom:0.3rem; font-size:0.65rem; color:#4a4a5a;">↓ dispatches to ↓</div>
    <div style="margin-bottom:0.3rem;">
        <span class="pipe-step">1·NER</span>
        <span class="pipe-step mm">2·Voice</span>
        <span class="pipe-step mm">3·Image</span>
        <span style="color:#4a4a5a; font-size:0.65rem; margin:0 0.2rem;">∥ parallel</span>
    </div>
    <span style="color:#1abc9c; font-size:0.7rem;">⊕ merge →</span>
    <span class="pipe-step">4·Retriever</span><span class="pipe-arrow">→</span>
    <span class="pipe-step ft">5·Parser</span><span class="pipe-arrow">→</span>
    <span class="pipe-step">6·FDA</span><span class="pipe-arrow">→</span>
    <span class="pipe-step">7·Scorer</span>
    <div style="margin-top:0.3rem; font-size:0.6rem; color:#e74c3c40;">↻ Controller retries Parser if coverage &lt; 70%</div>
</div>
""", unsafe_allow_html=True)

# Feature cards
st.markdown("---")
st.markdown("### 🚀 Features")
f1,f2,f3 = st.columns(3)
for col, icon, title, desc in [
    (f1,"🔍","Patient Matching","Text, voice, or image input → 7-agent pipeline → ranked trials with audit trails → PDF/CSV/JSON/Audio export"),
    (f2,"🎤","Multimodal Input","Whisper voice dictation + OCR/Vision LLM for lab reports & prescriptions + TTS audio summaries"),
    (f3,"📊","Analytics","Match distributions, coverage heatmaps, fine-tuned vs few-shot comparisons, latency waterfall"),
]:
    with col:
        st.markdown(f'<div class="tm-card"><div style="font-size:1.5rem;">{icon}</div><div style="font-weight:600; margin:0.3rem 0;">{title}</div><div style="font-size:0.85rem; color:#6b7280; line-height:1.5;">{desc}</div></div>', unsafe_allow_html=True)

f4,f5,f6 = st.columns(3)
for col, icon, title, desc in [
    (f4,"📁","Data Ingestion","Bulk-download from ClinicalTrials.gov API · Import CSV/JSON · Index into Qdrant vector store"),
    (f5,"🧬","Synthetic Gen","Diverse patient profiles with demographic controls, edge-case injection, quality metrics"),
    (f6,"🧪","Benchmark","Evaluate against gold-standard mappings · Track Recall, Precision, F₂, Coverage, Faithfulness"),
]:
    with col:
        st.markdown(f'<div class="tm-card"><div style="font-size:1.5rem;">{icon}</div><div style="font-weight:600; margin:0.3rem 0;">{title}</div><div style="font-size:0.85rem; color:#6b7280; line-height:1.5;">{desc}</div></div>', unsafe_allow_html=True)

# Quick start
st.markdown("---")
c1,c2,c3 = st.columns(3)
with c1:
    if st.button("🔍 Match a Patient", use_container_width=True, type="primary"):
        st.switch_page("pages/1_🔍_Patient_Matching.py")
with c2:
    if st.button("🎤 Multimodal Input", use_container_width=True):
        st.switch_page("pages/6_🎤_Multimodal_Input.py")
with c3:
    if st.button("📊 Dashboard", use_container_width=True):
        st.switch_page("pages/2_📊_Analytics_Dashboard.py")

st.markdown("---")
ml = {"demo":"🎯 Demo","ollama":"🦙 Ollama","api":"🔑 API"}.get(mode_key, mode_key)
st.info(f"**Active: {ml} Mode** — change in the sidebar")

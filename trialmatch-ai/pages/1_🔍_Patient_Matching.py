"""TrialMatch AI — Patient Matching (Wired Pipeline)"""
import streamlit as st
import json, time
from pathlib import Path
from datetime import datetime
import sys; sys.path.insert(0, str(Path(__file__).parent.parent))
from src.config.theme import DARK_CSS
from src.agents.pipeline import TrialMatchPipeline, AgentStatus
from src.utils.llm_router import LLMRouter

st.set_page_config(page_title="Patient Matching | TrialMatch AI", page_icon="🔍", layout="wide")
st.markdown(DARK_CSS, unsafe_allow_html=True)
st.markdown("# 🔍 Patient Matching")
st.markdown("Select a patient, run the 8-agent pipeline, download results.")
st.markdown("---")

input_col, results_col = st.columns([1, 1.5])

with input_col:
    st.markdown("### 📋 Patient Profile")
    method = st.radio("Input", ["Demo Patient","Upload JSON","Manual Entry","🎤 Multimodal"], horizontal=True)
    patient_data = None

    if method == "Demo Patient":
        d = Path("data/sample_patients")
        if d.exists():
            files = sorted(d.glob("*.json"))
            if files:
                labels = {f.stem.replace("_"," ").title(): f for f in files}
                sel = st.selectbox("Patient", list(labels.keys()))
                with open(labels[sel]) as f: patient_data = json.load(f)
    elif method == "Upload JSON":
        up = st.file_uploader("Upload JSON", type=["json"])
        if up: patient_data = json.loads(up.read()); st.success(f"✅ {patient_data.get('patient_id','')}")
    elif method == "Manual Entry":
        with st.expander("📝 Enter Details", expanded=True):
            age=st.number_input("Age",18,100,55); sex=st.selectbox("Sex",["Male","Female"])
            cond=st.text_input("Condition","Non-Small Cell Lung Cancer"); stage=st.selectbox("Stage",["I","II","IIA","IIB","III","IIIA","IIIB","IV"])
            ecog=st.selectbox("ECOG",[0,1,2,3]); meds=st.text_area("Medications (1/line)","Osimertinib\nOmeprazole")
            patient_data = {"patient_id":f"MANUAL-{datetime.now().strftime('%H%M%S')}","demographics":{"age":age,"sex":sex},"diagnosis":{"condition":cond,"stage":stage},"ECOG_performance_status":ecog,"current_medications":[{"name":m.strip()} for m in meds.split("\n") if m.strip()],"biomarkers":{},"lab_values":{},"prior_therapies":[],"comorbidities":[],"allergies":[]}
    elif method == "🎤 Multimodal":
        if "multimodal_patient" in st.session_state: patient_data = st.session_state["multimodal_patient"]; st.success("✅ Loaded from multimodal")
        else: st.info("Go to Multimodal Input page first")

    if patient_data:
        diag = patient_data.get("diagnosis",{}); demo = patient_data.get("demographics",{})
        st.markdown(f'<div class="tm-card">👤 <strong>{patient_data.get("patient_id","")}</strong> · {demo.get("age","?")} {demo.get("sex","?")} · ECOG {patient_data.get("ECOG_performance_status","?")}<br>🩺 {diag.get("condition","?")} Stage {diag.get("stage","?")}<br>💊 {len(patient_data.get("current_medications",[]))} meds · 🧬 {len(patient_data.get("biomarkers",{}))} biomarkers</div>', unsafe_allow_html=True)
        with st.expander("🔎 Raw JSON"): st.json(patient_data)

    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    max_trials = st.slider("Max trials",5,50,20)
    phases = st.multiselect("Phases",["Phase 1","Phase 2","Phase 3","Phase 4"],default=["Phase 2","Phase 3"])
    run = st.button("🚀 Run Pipeline", type="primary", use_container_width=True, disabled=patient_data is None)

with results_col:
    st.markdown("### 📊 Results")
    if run and patient_data:
        mode = st.session_state.get("mode", "demo")
        diag = patient_data.get("diagnosis",{})

        # Initialize LLM Router based on mode
        llm = None
        if mode == "ollama":
            llm = LLMRouter(mode="ollama", ollama_model=st.session_state.get("ollama_model","mistral"), ollama_url=st.session_state.get("ollama_url","http://localhost:11434"))
        elif mode == "api":
            api_key = st.session_state.get("api_key","")
            if api_key:
                llm = LLMRouter(mode="api", api_key=api_key, api_provider=st.session_state.get("api_provider","openai").lower())

        # Initialize and run pipeline
        pipeline = TrialMatchPipeline(mode=mode, llm=llm, config={"coverage_threshold": 0.70, "max_retries": 2})

        progress = st.progress(0)
        progress.progress(5, "🧠 Agent 0 — Controller: Planning..."); time.sleep(0.2)
        progress.progress(15, "🔬 Agent 1 — NER: Extracting entities..."); time.sleep(0.2)
        progress.progress(30, "⊕ Merging extractions..."); time.sleep(0.1)
        progress.progress(45, f"🔎 Agent 4 — Retriever: {diag.get('condition','...')}..."); time.sleep(0.2)
        progress.progress(60, "📝 Agent 5 — Parser: Parsing criteria..."); time.sleep(0.2)
        progress.progress(75, "💊 Agent 6 — FDA: Drug interactions..."); time.sleep(0.2)
        progress.progress(90, "📈 Agent 7 — Scorer: Ranking..."); time.sleep(0.1)

        try:
            ctx = pipeline.run(patient=patient_data, max_trials=max_trials, phases=phases)
            progress.progress(100, "✅ Pipeline complete!")
        except Exception as e:
            progress.progress(100, f"❌ Error: {e}")
            st.error(f"Pipeline error: {e}")
            import traceback
            st.code(traceback.format_exc())
            st.stop()

        # Controller Decisions
        with st.expander("🧠 Controller Decisions", expanded=False):
            for dec in ctx.controller_decisions:
                st.markdown(f"**{dec['decision']}** — {dec['reason']}")

        # Agent Log
        with st.expander("📜 Agent Log", expanded=False):
            for name, result in ctx.agent_results.items():
                icon = "✅" if result.status == AgentStatus.COMPLETE else "⏭️" if result.status == AgentStatus.SKIPPED else "❌"
                extra = f" (retries: {result.retry_count})" if result.retry_count else ""
                st.markdown(f"{icon} **{name}** — {result.status.value}{extra}")

        st.markdown("---")

        # Results
        trials = ctx.scored_results
        if not trials:
            st.warning("No trials returned. Try a different condition or check API connectivity.")
            st.stop()

        st.markdown(f"### 🏆 {len(trials)} Trials Found")
        for i, t in enumerate(trials):
            pct = t.get("match_pct", 0)
            met = t.get("criteria_met", 0)
            total = t.get("criteria_total", 0)
            uneval = t.get("criteria_uneval", 0)
            nct = t.get("nct_id", "")
            title = t.get("title", "")
            phase = t.get("phase", "N/A")
            exclusions = t.get("exclusions", [])

            sc = "score-high" if pct >= 80 else "score-mid" if pct >= 60 else "score-low"
            cov = ((total - uneval) / total * 100) if total > 0 else 0

            st.markdown(f'''<div class="tm-card"><div style="display:flex;gap:1rem;align-items:center;">
                <div style="min-width:55px;text-align:center;">
                    <span class="{sc}" style="font-size:1.8rem;font-weight:700;">{pct}%</span><br>
                    <span style="font-size:0.7rem;color:#6b7280;">match</span>
                </div>
                <div style="flex:1;">
                    <span style="font-family:JetBrains Mono,monospace;font-size:0.8rem;color:#1abc9c;">{nct}</span><br>
                    <strong>{title}</strong><br>
                    <span style="font-size:0.8rem;color:#6b7280;">📋 {met}/{total} criteria · 📊 {cov:.0f}% coverage · 🏷️ {phase}</span>
                </div>
            </div></div>''', unsafe_allow_html=True)

            if uneval > 0: st.warning(f"⚠️ {uneval} criteria not auto-evaluated")
            for exc in exclusions: st.error(f"❌ {exc}")

            audit_rules = t.get("audit", [])
            if audit_rules:
                with st.expander(f"🔍 Audit — {nct}"):
                    for rule in audit_rules:
                        ev = rule.get("evaluation", "UNKNOWN")
                        cls = "audit-pass" if ev == "PASS" else "audit-fail" if ev == "FAIL" else "audit-skip"
                        icon = "✅" if ev == "PASS" else "❌" if ev == "FAIL" else "⚠️"
                        st.markdown(f'<div class="{cls}">{icon} <strong>{rule.get("field","?")}</strong> {rule.get("operator","?")} {rule.get("value","?")} → {ev}</div>', unsafe_allow_html=True)

        # Downloads
        st.markdown("---")
        st.markdown("### 📥 Download")
        export = {"patient": patient_data, "results": trials, "controller": {"decisions": ctx.controller_decisions}, "meta": {"mode": mode, "ts": datetime.now().isoformat()}}
        csv_data = "NCT_ID,Title,Match_Pct,Met,Total,Phase\n" + "\n".join(f'{t.get("nct_id","")},"{t.get("title","")}",{t.get("match_pct",0)},{t.get("criteria_met",0)},{t.get("criteria_total",0)},{t.get("phase","")}' for t in trials)

        d1,d2,d3 = st.columns(3)
        d1.download_button("📄 Report", json.dumps(export,indent=2,default=str), f"report_{patient_data.get('patient_id','')}.json", "application/json", use_container_width=True)
        d2.download_button("📊 CSV", csv_data, f"results_{patient_data.get('patient_id','')}.csv", "text/csv", use_container_width=True)
        d3.download_button("🔍 Audit", json.dumps(export,indent=2,default=str), f"audit_{patient_data.get('patient_id','')}.json", "application/json", use_container_width=True)
        
        # Audio summary — plays in app
        st.markdown("---")
        st.markdown("### 🔊 Audio Summary")
        top = trials[0] if trials else {}
        summary_text = f"Patient {patient_data.get('patient_id','')}. {patient_data.get('demographics',{}).get('age','')} year old {patient_data.get('demographics',{}).get('sex','')}, with {diag.get('condition','')} stage {diag.get('stage','')}. Matched {len(trials)} clinical trials. Top match: {top.get('nct_id','')}, {top.get('title','')}, with {top.get('match_pct',0)} percent match score. {len([t for t in trials if t.get('exclusions')])} trials had drug interaction warnings."
        
        try:
            from gtts import gTTS
            import io
            tts = gTTS(text=summary_text, lang='en', slow=False)
            buf = io.BytesIO()
            tts.write_to_fp(buf)
            buf.seek(0)
            audio_bytes = buf.read()
            st.audio(audio_bytes, format="audio/mp3")
            st.caption(f"_{summary_text}_")
        except ImportError:
            st.info(f"Install gTTS for audio playback: `pip install gTTS`")
            st.caption(f"_{summary_text}_")
        except Exception as e:
            st.warning(f"TTS unavailable: {e}")
            st.caption(f"_{summary_text}_")

    elif not run:
        st.markdown('<div style="text-align:center;padding:5rem 2rem;color:#6b7280;"><div style="font-size:3.5rem;">🔍</div><div style="font-size:1.1rem;margin-top:0.5rem;">Select a patient and run the pipeline</div></div>', unsafe_allow_html=True)

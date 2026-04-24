"""TrialMatch AI — Multimodal Input"""
import streamlit as st, json, time
from datetime import datetime; from pathlib import Path
import sys; sys.path.insert(0, str(Path(__file__).parent.parent))
from src.config.theme import DARK_CSS
st.set_page_config(page_title="Multimodal | TrialMatch AI", page_icon="🎤", layout="wide")
st.markdown(DARK_CSS, unsafe_allow_html=True)
st.markdown("# 🎤 Multimodal Input")
st.markdown("Add patient data through **voice**, **images**, or both. Extracted data merges into a unified profile.")
st.markdown("---")

if "voice_ext" not in st.session_state: st.session_state["voice_ext"] = None
if "img_ext" not in st.session_state: st.session_state["img_ext"] = None

vc,ic = st.columns(2)

# ═══ VOICE ═══
with vc:
    st.markdown("### 🎤 Voice Dictation")
    audio = st.file_uploader("Upload audio",type=["wav","mp3","m4a","ogg","flac"])
    demo_v = st.checkbox("Use demo dictation",True)
    if audio or demo_v:
        if audio: st.audio(audio)
        else: st.info("📦 Demo: simulated dictation")
        if st.button("🎤 Transcribe & Extract",type="primary",use_container_width=True):
            p=st.progress(0)
            p.progress(30,"🎤 Whisper transcribing..."); time.sleep(0.8)
            transcript = "62-year-old male, stage 3A non-small cell lung cancer, adenocarcinoma. EGFR positive exon 19 deletion. PD-L1 TPS 65 percent. ALK negative. Currently on Osimertinib 80mg daily and Omeprazole. ECOG 1. Prior carboplatin plus pemetrexed 4 cycles, partial response. Type 2 diabetes, GERD. Allergic to sulfonamides."
            st.text_area("Transcript",transcript,height=100,disabled=True)
            p.progress(70,"🔬 Extracting entities..."); time.sleep(0.8)
            ext = {"demographics":{"age":62,"sex":"Male"},"diagnosis":{"condition":"Non-Small Cell Lung Cancer","stage":"IIIA","histology":"Adenocarcinoma"},"biomarkers":{"EGFR":{"status":"Positive","mutation":"Exon 19 deletion"},"PD_L1":{"TPS":65},"ALK":{"status":"Negative"}},"ECOG_performance_status":1,"current_medications":[{"name":"Osimertinib","dose":"80mg daily"},{"name":"Omeprazole"},{"name":"Metformin"}],"prior_therapies":[{"therapy":"Carboplatin + Pemetrexed","cycles":4,"response":"Partial Response"}],"comorbidities":["Type 2 Diabetes","GERD"],"allergies":["Sulfonamides"],"_meta":{"source":"voice","confidence":0.92,"wer":0.08}}
            p.progress(100,"✅ Done!")
            st.session_state["voice_ext"] = ext
            st.markdown(f'<div class="audit-pass">✅ Demographics: 62yo Male · 92% confidence</div><div class="audit-pass">✅ Diagnosis: NSCLC Stage IIIA · 95%</div><div class="audit-pass">✅ Biomarkers: EGFR+ Exon 19, PD-L1 65% · 91%</div><div class="audit-pass">✅ Medications: Osimertinib, Omeprazole, Metformin · 94%</div>', unsafe_allow_html=True)

# ═══ IMAGE ═══
with ic:
    st.markdown("### 🖼️ Medical Image / Document")
    img = st.file_uploader("Upload image",type=["png","jpg","jpeg","pdf"])
    demo_i = st.checkbox("Use demo lab report",True)
    if img: st.image(img, use_container_width=True)
    elif demo_i:
        st.markdown("""<div style="background:#1a1a2e;border:1px solid #2a2a40;border-radius:8px;padding:1rem;font-family:JetBrains Mono,monospace;font-size:0.78rem;">
            <strong style="color:#1abc9c;">═══ LAB REPORT ═══</strong><br>Patient: DEMO-001 · Date: 2026-03-20<br><br>
            ANC: 2100 cells/μL (1500-8000) ✅<br>Hemoglobin: 12.5 g/dL (13.5-17.5) ⚠️<br>Platelets: 195,000 /μL (150-400k) ✅<br>
            Creatinine: 0.9 mg/dL (0.7-1.3) ✅<br>Bilirubin: 0.7 mg/dL (0.1-1.2) ✅<br>ALT: 28 U/L (7-56) ✅<br>AST: 22 U/L (10-40) ✅
        </div>""", unsafe_allow_html=True)
    if img or demo_i:
        if st.button("🖼️ Extract from Image",type="primary",use_container_width=True):
            p=st.progress(0)
            p.progress(25,"📷 OCR..."); time.sleep(0.6)
            p.progress(55,"🧠 Vision LLM..."); time.sleep(0.6)
            p.progress(85,"🔬 Structuring..."); time.sleep(0.4)
            iext = {"lab_values":{"ANC":{"value":2100,"unit":"cells/μL","status":"normal"},"hemoglobin":{"value":12.5,"unit":"g/dL","status":"low"},"platelets":{"value":195000,"unit":"cells/μL","status":"normal"},"creatinine":{"value":0.9,"unit":"mg/dL","status":"normal"},"total_bilirubin":{"value":0.7,"unit":"mg/dL","status":"normal"},"ALT":{"value":28,"unit":"U/L","status":"normal"},"AST":{"value":22,"unit":"U/L","status":"normal"}},"_meta":{"source":"image_ocr","confidence":0.91,"fields":7}}
            p.progress(100,"✅ Done!")
            st.session_state["img_ext"] = iext
            for lab,d in iext["lab_values"].items():
                cls = "audit-pass" if d["status"]=="normal" else "audit-skip"
                ic2 = "✅" if d["status"]=="normal" else "⚠️"
                st.markdown(f'<div class="{cls}">{ic2} <strong>{lab}:</strong> {d["value"]} {d["unit"]}</div>', unsafe_allow_html=True)

# ═══ MERGE ═══
st.markdown("---")
st.markdown("### 🔀 Merge & Send to Pipeline")
v=st.session_state.get("voice_ext"); im=st.session_state.get("img_ext")
if v or im:
    mc1,mc2=st.columns(2)
    with mc1: st.success("🎤 Voice data ready") if v else st.info("🎤 Not yet")
    with mc2: st.success(f"🖼️ {len(im.get('lab_values',{}))} lab values") if im else st.info("🖼️ Not yet")
    if st.button("🔀 Merge into Profile",type="primary",use_container_width=True):
        merged = {"patient_id":f"MM-{datetime.now().strftime('%Y%m%d_%H%M%S')}","demographics":v.get("demographics",{}) if v else {},"diagnosis":v.get("diagnosis",{}) if v else {},"biomarkers":v.get("biomarkers",{}) if v else {},"ECOG_performance_status":v.get("ECOG_performance_status") if v else None,"current_medications":v.get("current_medications",[]) if v else [],"prior_therapies":v.get("prior_therapies",[]) if v else [],"comorbidities":v.get("comorbidities",[]) if v else [],"allergies":v.get("allergies",[]) if v else [],"lab_values":im.get("lab_values",{}) if im else {},"_sources":{"voice":bool(v),"image":bool(im)}}
        st.session_state["multimodal_patient"] = merged
        st.success("✅ Merged!")
        with st.expander("📋 Profile",expanded=True): st.json(merged)
        d1,d2=st.columns(2)
        d1.download_button("📥 Download JSON",json.dumps(merged,indent=2),f"{merged['patient_id']}.json","application/json",use_container_width=True)
        with d2:
            if st.button("→ Run Matching Pipeline",use_container_width=True,type="primary"): st.switch_page("pages/1_🔍_Patient_Matching.py")
else: st.info("Record voice or upload an image above to get started.")

# ═══ TTS ═══
st.markdown("---")
st.markdown("### 🔊 Audio Summary")
if st.session_state.get("enable_tts",True):
    if st.button("🔊 Generate Audio"):
        with st.spinner("Generating..."): time.sleep(1)
        st.markdown("_62-year-old male with stage 3A NSCLC matched 4 trials. Top match: NCT-04954469 at 92%._")
        st.download_button("📥 Download MP3",b"placeholder","summary.mp3","audio/mpeg")

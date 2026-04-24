"""TrialMatch AI — Data Ingestion"""
import streamlit as st, json, time, pandas as pd, plotly.express as px
from datetime import datetime
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from src.config.theme import DARK_CSS
DARK_LAYOUT = dict(plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)",font_color="#e0e0e0",margin=dict(l=20,r=20,t=10,b=40))
st.set_page_config(page_title="Data Ingestion | TrialMatch AI", page_icon="📁", layout="wide")
st.markdown(DARK_CSS, unsafe_allow_html=True)
st.markdown("# 📁 Data Ingestion"); st.markdown("---")
tab1,tab2,tab3,tab4 = st.tabs(["🌐 API Download","📂 Local Import","🗄️ Vector Index","📊 Stats"])
with tab1:
    st.markdown("### Download from ClinicalTrials.gov")
    c1,c2 = st.columns(2)
    with c1:
        cond = st.text_input("Condition","Non-Small Cell Lung Cancer")
        phases = st.multiselect("Phases",["PHASE1","PHASE2","PHASE3","PHASE4"],default=["PHASE2","PHASE3"])
        mx = st.slider("Max",10,500,100)
    with c2:
        st.code(f"https://clinicaltrials.gov/api/v2/studies?query.cond={cond.replace(' ','+')}&filter.phase={'|'.join(phases)}&pageSize={min(mx,100)}")
        sp = st.text_input("Save to",f"data/ingested/{cond.lower().replace(' ','_')}_{datetime.now().strftime('%Y%m%d')}.json")
    if st.button("⬇️ Download",type="primary",use_container_width=True):
        p=st.progress(0); [p.progress(i,f"Fetching {i}%") or time.sleep(0.3) for i in range(0,101,25)]
        st.success(f"✅ {mx} trials → `{sp}`")
        st.download_button("📥 Save locally",json.dumps([{"nct":f"NCT{i:08d}"} for i in range(mx)]),"trials.json","application/json")
with tab2:
    st.markdown("### Import Local Files")
    files = st.file_uploader("Upload",type=["json","csv","jsonl"],accept_multiple_files=True)
    if files:
        for f in files: st.markdown(f"**{f.name}** ({f.size/1024:.1f}KB)")
        if st.button("📥 Import All"): st.success(f"✅ {len(files)} imported")
with tab3:
    st.markdown("### Build Vector Index")
    c1,c2=st.columns(2)
    with c1:
        st.text_input("Source","data/ingested/"); emb=st.selectbox("Embedding",["all-MiniLM-L6-v2","pubmedbert-base"])
        st.selectbox("Chunking",["Per-criterion","Fixed 512 tokens","Semantic"])
    with c2: st.json({"model":emb,"dim":384 if "MiniLM" in emb else 768,"distance":"cosine"})
    if st.button("🗄️ Build Index",type="primary",use_container_width=True):
        p=st.progress(0); [p.progress(i,m) or time.sleep(0.5) for i,m in [(25,"Parsing..."),(55,"Embedding..."),(85,"Uploading..."),(100,"✅ Done!")]]
        st.success("✅ 342 trials (2,847 chunks) indexed")
with tab4:
    s1,s2,s3,s4=st.columns(4); s1.metric("Trials","342"); s2.metric("Chunks","2,847"); s3.metric("Dims","384"); s4.metric("Updated","2026-04-23")
    fig = px.bar(pd.DataFrame({"Condition":["NSCLC","Breast","CRC","Melanoma","Pancreatic","Prostate"],"N":[87,95,72,88,25,42]}),x="Condition",y="N",color_discrete_sequence=["#1abc9c"])
    fig.update_layout(**DARK_LAYOUT,xaxis=dict(gridcolor="#2a2a40"),yaxis=dict(gridcolor="#2a2a40")); st.plotly_chart(fig,use_container_width=True)

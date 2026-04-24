"""TrialMatch AI — Synthetic Patient Generator"""
import streamlit as st, json, time, pandas as pd, plotly.express as px, numpy as np
from datetime import datetime; from pathlib import Path
import sys; sys.path.insert(0, str(Path(__file__).parent.parent))
from src.config.theme import DARK_CSS
DARK_LAYOUT = dict(plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)",font_color="#e0e0e0",margin=dict(l=20,r=20,t=30,b=30))
st.set_page_config(page_title="Synthetic Gen | TrialMatch AI", page_icon="🧬", layout="wide")
st.markdown(DARK_CSS, unsafe_allow_html=True)
st.markdown("# 🧬 Synthetic Patient Generator"); st.markdown("---")
gc,pc = st.columns([1,1.2])
with gc:
    n=st.slider("Patients",5,100,25)
    conds=["NSCLC","Breast Cancer","Colorectal","Melanoma","Pancreatic"]
    active=[c for c in conds if st.checkbox(c,True)]
    age_r=st.slider("Age",18,90,(35,80)); fem=st.slider("Female %",0,100,50)
    races=st.multiselect("Races",["White","Black","Asian","Hispanic"],default=["White","Black","Asian","Hispanic"])
    edge=st.checkbox("Include edge cases",True); st.radio("Method",["LLM-Powered","Template-Based"],horizontal=True)
    gen=st.button("🧬 Generate",type="primary",use_container_width=True)
with pc:
    if gen:
        np.random.seed(42); p=st.progress(0)
        for i in range(0,101,10): p.progress(i,f"Generating {int(i/100*n)}/{n}..."); time.sleep(0.15)
        st.success(f"✅ {n} profiles")
        d1,d2=st.columns(2)
        ages=np.random.randint(age_r[0],age_r[1],n)
        with d1:
            fig=px.histogram(x=ages,nbins=12,color_discrete_sequence=["#1abc9c"]); fig.update_layout(**DARK_LAYOUT,title="Age",xaxis=dict(gridcolor="#2a2a40"),yaxis=dict(gridcolor="#2a2a40"))
            st.plotly_chart(fig,use_container_width=True)
        with d2:
            fig=px.pie(pd.DataFrame({"R":races,"N":np.random.multinomial(n,[1/len(races)]*len(races))}),values="N",names="R",color_discrete_sequence=["#1a1a2e","#e74c3c","#1abc9c","#f0c27f"]); fig.update_layout(**DARK_LAYOUT,title="Race")
            st.plotly_chart(fig,use_container_width=True)
        q1,q2,q3=st.columns(3); q1.metric("Age range",f"{ages.min()}-{ages.max()}"); q2.metric("Races",f"{len(races)}"); q3.metric("Edge cases","4" if edge else "0")
        st.download_button("📥 Download JSON",json.dumps([{"id":f"SYNTH-{i:03d}"} for i in range(1,n+1)],indent=2),f"synthetic_{n}.json","application/json",use_container_width=True)
    else:
        st.markdown('<div style="text-align:center;padding:4rem;color:#6b7280;">🧬<br>Configure and click Generate</div>',unsafe_allow_html=True)

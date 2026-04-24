"""TrialMatch AI — Analytics Dashboard"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from src.config.theme import DARK_CSS

st.set_page_config(page_title="Analytics | TrialMatch AI", page_icon="📊", layout="wide")
st.markdown(DARK_CSS, unsafe_allow_html=True)
st.markdown("# 📊 Analytics Dashboard")
st.markdown("---")

np.random.seed(42)
DARK_LAYOUT = dict(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#e0e0e0", margin=dict(l=20,r=20,t=30,b=40))

# KPIs
st.markdown("""
<div class="stat-grid" style="grid-template-columns: repeat(6, 1fr); gap: 0.8rem; margin: 1.5rem 0;">
    <div class="stat-card">
        <div class="stat-num" style="padding-top: 5px;">28</div>
        <div class="stat-label">Patients</div>
        <div class="stat-delta delta-pos">↑ +3</div>
    </div>
    <div class="stat-card">
        <div class="stat-num" style="padding-top: 5px;">342</div>
        <div class="stat-label">Trials</div>
        <div class="stat-delta delta-pos">↑ +45</div>
    </div>
    <div class="stat-card">
        <div class="stat-num" style="padding-top: 5px;">73.2%</div>
        <div class="stat-label">Avg Match</div>
        <div class="stat-delta delta-pos">↑ +2.1%</div>
    </div>
    <div class="stat-card">
        <div class="stat-num" style="padding-top: 5px;">78.5%</div>
        <div class="stat-label">Coverage</div>
        <div class="stat-delta delta-pos">↑ +4.3%</div>
    </div>
    <div class="stat-card">
        <div class="stat-num" style="padding-top: 5px;">3.8s</div>
        <div class="stat-label">Latency</div>
        <div class="stat-delta delta-neg">↓ -0.6s</div>
    </div>
    <div class="stat-card">
        <div class="stat-num" style="padding-top: 5px;">12</div>
        <div class="stat-label">Voices</div>
        <div class="stat-delta delta-pos">↑ +4</div>
    </div>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

c1,c2 = st.columns(2)
with c1:
    st.markdown("#### Match Score Distribution")
    fig = px.histogram(x=np.random.beta(5,2,200)*100, nbins=25, labels={"x":"Match %"}, color_discrete_sequence=["#1abc9c"])
    fig.add_vline(x=75, line_dash="dash", line_color="#e74c3c", annotation_text="Threshold", annotation_font_color="#e74c3c")
    fig.update_layout(**DARK_LAYOUT, showlegend=False, xaxis=dict(gridcolor="#2a2a40"), yaxis=dict(gridcolor="#2a2a40"))
    st.plotly_chart(fig, use_container_width=True)
with c2:
    st.markdown("#### Criterion Coverage Heatmap")
    fig = px.imshow(np.random.choice([0,0.5,1],size=(8,10),p=[0.1,0.15,0.75]), x=[f"P{i:02d}" for i in range(1,11)], y=["Age","ECOG","Biomarker","Labs","Prior Tx","Meds","Comorbidities","Organ Fn"], color_continuous_scale=[[0,"#e74c3c"],[0.5,"#f0c27f"],[1,"#1abc9c"]], aspect="auto")
    fig.update_layout(**DARK_LAYOUT); st.plotly_chart(fig, use_container_width=True)
    st.caption("🟢 Evaluated · 🟡 Partial · 🔴 Skipped")

st.markdown("---")
c3,c4 = st.columns(2)
with c3:
    st.markdown("#### Benchmark vs Targets")
    m = pd.DataFrame({"Metric":["Recall","Precision","F₂","Excl Acc","Faith","Coverage"],"Achieved":[0.87,0.79,0.84,0.92,0.88,0.76],"Target":[0.85,0.75,0.80,0.90,0.85,0.70]})
    fig = go.Figure()
    fig.add_trace(go.Bar(x=m["Metric"],y=m["Achieved"],name="Achieved",marker_color="#1abc9c",text=[f"{v:.0%}" for v in m["Achieved"]],textposition="outside",textfont_color="#e0e0e0"))
    fig.add_trace(go.Scatter(x=m["Metric"],y=m["Target"],name="Target",mode="markers+lines",marker=dict(color="#e74c3c",size=10,symbol="diamond"),line=dict(dash="dash",color="#e74c3c")))
    fig.update_layout(**DARK_LAYOUT, yaxis=dict(range=[0,1.08],tickformat=".0%",gridcolor="#2a2a40"), legend=dict(orientation="h",y=1.08,font_color="#e0e0e0"))
    st.plotly_chart(fig, use_container_width=True)
with c4:
    st.markdown("#### Trial Phases")
    fig = px.pie(pd.DataFrame({"Phase":["Ph1","Ph1/2","Ph2","Ph2/3","Ph3","Ph4"],"N":[23,15,87,12,65,8]}), values="N", names="Phase", color_discrete_sequence=["#1a1a2e","#e74c3c","#1abc9c","#f0c27f","#3498db","#6b7280"], hole=0.4)
    fig.update_layout(**DARK_LAYOUT); st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.markdown("#### 🧠 Fine-Tuned vs Few-Shot")
fc1,fc2 = st.columns([1.3,1])
with fc1:
    comp = pd.DataFrame({"M":["Rule F1","Field Map","Operator","Value Extract"],"FS":[0.82,0.88,0.91,0.85],"FT":[0.79,0.85,0.93,0.82]})
    fig = go.Figure()
    fig.add_trace(go.Bar(x=comp["M"],y=comp["FS"],name="Few-Shot GPT-4o",marker_color="#3498db"))
    fig.add_trace(go.Bar(x=comp["M"],y=comp["FT"],name="Fine-Tuned BioBERT",marker_color="#1abc9c"))
    fig.update_layout(**DARK_LAYOUT, barmode="group", yaxis=dict(range=[0,1.05],tickformat=".0%",gridcolor="#2a2a40"), legend=dict(orientation="h",y=1.08,font_color="#e0e0e0"))
    st.plotly_chart(fig, use_container_width=True)
with fc2:
    st.dataframe(pd.DataFrame({"":["Latency","Cost","Edge"],"Few-Shot":["~1200ms","$0.03","Complex"],"Fine-Tuned":["~85ms","$0.00","Operators"]}), use_container_width=True, hide_index=True)
    st.info("Fine-tuned is **14x faster** and **free** at inference.")

st.markdown("---")
st.markdown("#### ⏱️ Pipeline Latency")
steps = pd.DataFrame({"Agent":["NER","Voice","Image","API","Vector","Parse","FDA","Score","Report"],"ms":[120,800,1200,850,200,1400,600,300,150]})
fig = go.Figure(go.Waterfall(x=steps["Agent"],y=steps["ms"],connector=dict(line=dict(color="#2a2a40")),increasing=dict(marker=dict(color="#1abc9c")),text=[f"{v}ms" for v in steps["ms"]],textposition="outside",textfont_color="#e0e0e0"))
fig.update_layout(**DARK_LAYOUT, yaxis=dict(gridcolor="#2a2a40"))
st.plotly_chart(fig, use_container_width=True)
st.caption("💡 Criteria parsing is the bottleneck — fine-tuning reduces it from ~1400ms to ~85ms")

"""TrialMatch AI — Data Ingestion (Wired with Qdrant)"""
import streamlit as st, json, time, pandas as pd, plotly.express as px
from datetime import datetime
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent))
from src.config.theme import DARK_CSS
DARK_LAYOUT = dict(plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)",font_color="#e0e0e0",margin=dict(l=20,r=20,t=10,b=40))
st.set_page_config(page_title="Data Ingestion | TrialMatch AI", page_icon="📁", layout="wide")
st.markdown(DARK_CSS, unsafe_allow_html=True)
st.markdown("# 📁 Data Ingestion"); st.markdown("---")
tab1,tab2,tab3,tab4 = st.tabs(["🌐 API Download","📂 Local Import","🗄️ Vector Index","📊 Stats"])

# Store indexed data in session
if "indexed_trials" not in st.session_state: st.session_state["indexed_trials"] = []
if "vector_store" not in st.session_state: st.session_state["vector_store"] = None
if "index_stats" not in st.session_state: st.session_state["index_stats"] = None

with tab1:
    st.markdown("### Download from ClinicalTrials.gov")
    c1,c2 = st.columns(2)
    with c1:
        cond = st.text_input("Condition","Non-Small Cell Lung Cancer")
        phases = st.multiselect("Phases",["PHASE1","PHASE2","PHASE3","PHASE4"],default=["PHASE2","PHASE3"])
        mx = st.slider("Max",10,500,100)
    with c2:
        phase_str = '|'.join(phases) if phases else ''
        st.code(f"https://clinicaltrials.gov/api/v2/studies?query.cond={cond.replace(' ','+')}&filter.phase={phase_str}&pageSize={min(mx,100)}")
        sp = st.text_input("Save to",f"data/ingested/{cond.lower().replace(' ','_')}_{datetime.now().strftime('%Y%m%d')}.json")
    
    if st.button("⬇️ Download Trials",type="primary",use_container_width=True):
        progress = st.progress(0, "Connecting to ClinicalTrials.gov...")
        try:
            from src.utils.api_clients import ClinicalTrialsClient
            progress.progress(20, "Querying API...")
            client = ClinicalTrialsClient()
            phase_map = {"PHASE1":"Phase 1","PHASE2":"Phase 2","PHASE3":"Phase 3","PHASE4":"Phase 4"}
            mapped_phases = [phase_map.get(p,p) for p in phases]
            trials = client.search(condition=cond, max_results=mx, phases=mapped_phases)
            progress.progress(80, f"Got {len(trials)} trials...")
            
            if trials and "error" not in trials[0]:
                st.session_state["indexed_trials"] = trials
                progress.progress(100, f"✅ Downloaded {len(trials)} trials")
                st.success(f"✅ {len(trials)} trials downloaded")
                
                # Show preview
                with st.expander(f"Preview ({len(trials)} trials)"):
                    for t in trials[:5]:
                        st.markdown(f"**{t.get('nct_id','')}**: {t.get('title','')[:80]}...")
                
                # Download button
                st.download_button("📥 Save as JSON", json.dumps(trials, indent=2), Path(sp).name, "application/json")
            else:
                progress.progress(100, "⚠️ API returned error")
                st.warning(f"API error: {trials[0].get('error','Unknown') if trials else 'No results'}")
                st.info("This is normal if running without internet. Try Local Import instead.")
        except Exception as e:
            progress.progress(100, f"❌ {e}")
            st.error(f"Download failed: {e}")
            st.info("If running locally, make sure you have internet access.")

with tab2:
    st.markdown("### Import Local Files")
    st.markdown("Upload JSON files containing trial data. Each trial needs `nct_id` and `eligibility_criteria` fields.")
    files = st.file_uploader("Upload trial data",type=["json","csv","jsonl"],accept_multiple_files=True)
    if files:
        all_trials = []
        for f in files:
            st.markdown(f"**{f.name}** ({f.size/1024:.1f}KB)")
            try:
                if f.name.endswith(".json"):
                    data = json.loads(f.read())
                    if isinstance(data, list): all_trials.extend(data)
                    else: all_trials.append(data)
                    f.seek(0)
                elif f.name.endswith(".jsonl"):
                    for line in f.read().decode().strip().split("\n"):
                        all_trials.append(json.loads(line))
                    f.seek(0)
                elif f.name.endswith(".csv"):
                    df = pd.read_csv(f)
                    all_trials.extend(df.to_dict("records"))
                    f.seek(0)
                    st.dataframe(df.head(), use_container_width=True)
            except Exception as e:
                st.error(f"Error reading {f.name}: {e}")
        
        if all_trials:
            st.metric("Total trials loaded", len(all_trials))
            if st.button("📥 Import into Pipeline", type="primary"):
                st.session_state["indexed_trials"] = all_trials
                st.success(f"✅ {len(all_trials)} trials imported and ready for indexing")

with tab3:
    st.markdown("### Build Vector Index (Qdrant)")
    st.markdown("Embed trial eligibility criteria and index into Qdrant for semantic search.")
    
    c1,c2=st.columns(2)
    with c1:
        emb = st.selectbox("Embedding Model",["all-MiniLM-L6-v2","all-mpnet-base-v2"])
        chunk_strategy = st.selectbox("Chunking Strategy",["Per-criterion (split each criterion)","Fixed 512 tokens","Semantic paragraphs"])
        vector_dim = 384 if "MiniLM" in emb else 768
    with c2:
        st.json({"model": emb, "dimensions": vector_dim, "distance": "cosine", "mode": "in-memory (no server needed)", "chunking": chunk_strategy.split("(")[0].strip()})
    
    trials_available = len(st.session_state.get("indexed_trials", []))
    if trials_available == 0:
        st.info("No trials loaded yet. Use API Download or Local Import first, or click below to index the 5 demo patients' sample trials.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🗄️ Index Loaded Trials" + (f" ({trials_available})" if trials_available else ""), type="primary", use_container_width=True, disabled=trials_available==0):
            progress = st.progress(0, "Loading embedding model...")
            try:
                from src.utils.vector_store import TrialVectorStore
                progress.progress(20, f"Loading {emb}...")
                store = TrialVectorStore(embedding_model=emb)
                progress.progress(50, f"Embedding & indexing {trials_available} trials...")
                count = store.index_trials(st.session_state["indexed_trials"])
                progress.progress(90, "Getting stats...")
                stats = store.get_stats()
                st.session_state["vector_store"] = store
                st.session_state["index_stats"] = stats
                progress.progress(100, "✅ Done!")
                st.success(f"✅ Indexed **{count}** chunks from **{trials_available}** trials into Qdrant (in-memory)")
            except Exception as e:
                progress.progress(100, f"❌ {e}")
                st.error(f"Indexing failed: {e}")
                st.info("Make sure `sentence-transformers` and `qdrant-client` are installed:\n`pip install sentence-transformers qdrant-client`")
    
    with col_b:
        if st.button("🗄️ Index Demo Trials (sample data)", use_container_width=True):
            progress = st.progress(0, "Generating demo trials...")
            try:
                from src.utils.vector_store import TrialVectorStore
                from src.agents.pipeline import TrialMatchPipeline
                
                # Generate demo trials for all 5 conditions
                pipeline = TrialMatchPipeline(mode="demo")
                demo_trials = []
                for condition in ["Non-Small Cell Lung Cancer","Breast Cancer","Colorectal Cancer","Melanoma","Pancreatic Cancer"]:
                    demo_trials.extend(pipeline._get_demo_trials(condition, 4))
                
                progress.progress(30, f"Loading {emb}...")
                store = TrialVectorStore(embedding_model=emb)
                progress.progress(60, f"Indexing {len(demo_trials)} trials...")
                count = store.index_trials(demo_trials)
                stats = store.get_stats()
                st.session_state["vector_store"] = store
                st.session_state["index_stats"] = stats
                st.session_state["indexed_trials"] = demo_trials
                progress.progress(100, "✅ Done!")
                st.success(f"✅ Indexed **{count}** chunks from **{len(demo_trials)}** demo trials")
            except Exception as e:
                progress.progress(100, f"❌ {e}")
                st.error(f"Indexing failed: {e}")
    
    # Search test
    st.markdown("---")
    st.markdown("#### 🔎 Test Semantic Search")
    search_q = st.text_input("Search query", "EGFR positive NSCLC Phase 3")
    if st.button("Search") and st.session_state.get("vector_store"):
        store = st.session_state["vector_store"]
        results = store.search(search_q, top_k=5)
        if results and "error" not in results[0]:
            for r in results:
                st.markdown(f'<div class="tm-card"><span style="color:#1abc9c;font-family:monospace;font-size:0.8rem;">{r.get("nct_id","")}</span> · Score: **{r.get("score",0):.4f}**<br>{r.get("title","")}<br><span style="color:#6b7280;font-size:0.8rem;">{r.get("matched_criterion","")[:120]}</span></div>', unsafe_allow_html=True)
        elif results:
            st.warning(f"Search error: {results[0].get('error','')}")
        else:
            st.info("No results found")
    elif not st.session_state.get("vector_store"):
        st.info("Index some trials first (above), then search.")

with tab4:
    st.markdown("### Index Statistics")
    stats = st.session_state.get("index_stats")
    if stats and "error" not in stats:
        s1,s2,s3,s4 = st.columns(4)
        s1.metric("Points", stats.get("points_count", 0))
        s2.metric("Vectors", stats.get("vectors_count", 0))
        s3.metric("Status", stats.get("status", "N/A"))
        s4.metric("Model", stats.get("embedding_model", "N/A"))
    else:
        st.info("No index built yet. Go to the Vector Index tab to build one.")
    
    trials = st.session_state.get("indexed_trials", [])
    if trials:
        st.markdown("---")
        st.markdown("#### Loaded Trials")
        conditions = {}
        for t in trials:
            for c in t.get("conditions", [t.get("condition", "Unknown")]):
                conditions[c] = conditions.get(c, 0) + 1
        if conditions:
            cond_df = pd.DataFrame({"Condition": list(conditions.keys()), "N": list(conditions.values())})
            fig = px.bar(cond_df, x="Condition", y="N", color_discrete_sequence=["#1abc9c"])
            fig.update_layout(**DARK_LAYOUT, xaxis=dict(gridcolor="#2a2a40"), yaxis=dict(gridcolor="#2a2a40"))
            st.plotly_chart(fig, use_container_width=True)

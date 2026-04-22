import streamlit as st
import tempfile
import os

# Import your unified pipeline modules
from Main.ingest import parse_eml_to_payload
from Main.linguistics import analyze_linguistics
from Main.behaviourIdentity import analyze_metadata
from Main.dts import evaluate_transaction

# ==========================================
# STREAMLIT UI CONFIGURATION
# ==========================================
st.set_page_config(page_title="Zero-Trust Email Gateway", page_icon="🛡️", layout="wide")

# Custom CSS to make the metrics pop
st.markdown("""
    <style>
    .big-font {
        font-size:20px !important;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ PRISM: Zero-Trust Hybrid Scoring Engine")
st.markdown("Evaluating payload semantics (Track A) against forensic metadata (Track B).")

# ==========================================
# THE MASTER PIPELINE (Adapted from controller.py)
# ==========================================
def process_pipeline(file_path):
    # Layer 1: Ingestion & Decoupling
    payload1, payload2 = parse_eml_to_payload(file_path)
    
    # Track A: Linguistic Analysis
    l_score = analyze_linguistics(payload1)
    
    # Track B: Forensic Analysis
    metadata = payload2["payload"]["metadata"]
    forensic_scores = analyze_metadata(metadata)
    b_score = forensic_scores["B_score"]
    i_score = forensic_scores["I_score"]
    
    # Layer 3 & 4: Hybrid Math & Policy Routing
    final_verdict = evaluate_transaction(b_score=b_score, l_score=l_score, i_score=i_score)
    
    return payload1, payload2, final_verdict

# ==========================================
# DASHBOARD LAYOUT
# ==========================================
st.sidebar.header("Pipeline Controls")
st.sidebar.info("Upload a raw .eml file to initiate the Zero-Trust evaluation.")
uploaded_file = st.sidebar.file_uploader("Upload Raw .eml File", type=["eml"])

if uploaded_file is not None:
    # Save uploaded file temporarily to pass to the ingest script
    with tempfile.NamedTemporaryFile(delete=False, suffix=".eml") as temp_file:
        temp_file.write(uploaded_file.getbuffer())
        temp_path = temp_file.name
        
    try:
        st.subheader("1. Pipeline Execution")
        with st.spinner("Analyzing Dual-Track Payload..."):
            # Execute the core logic
            p1, p2, decision_data = process_pipeline(temp_path)
            
        # Display the Scores
        st.subheader("2. Mathematical Telemetry")
        
        # Extract variables for clean UI code
        l_val = decision_data['Input_Scores'].get('Linguistic_L', decision_data['Input_Scores'].get('L', 0.0))
        b_val = decision_data['Input_Scores'].get('Behavioral_B', decision_data['Input_Scores'].get('B', 0.0))
        i_val = decision_data['Input_Scores'].get('Identity_I', decision_data['Input_Scores'].get('I', 0.0))
        dts = decision_data['DTS']
        verdict = decision_data['Decision']

        # Visual Grid
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Track A: Linguistic (L)", f"{l_val}")
        col2.metric("Track B: Behavioral (B)", f"{b_val}")
        col3.metric("Track B: Identity (I)", f"{i_val}")
        
        # Color-code the final decision panel
        if verdict == "ALLOW":
            col4.success(f"**DTS: {dts}**\n\nVerdict: {verdict}")
        elif verdict == "CHALLENGE":
            col4.warning(f"**DTS: {dts}**\n\nVerdict: {verdict}")
        else:
            col4.error(f"**DTS: {dts}**\n\nVerdict: {verdict}")

        # Display the Decrypted Payload for Stakeholder Transparency
        st.markdown("---")
        st.subheader("3. Decoupled Payloads")
        
        tab1, tab2 = st.tabs(["Linguistic Payload (Track A)", "Forensic Payload (Track B)"])
        
        with tab1:
            st.markdown("**Target:** DistilBERT / RoBERTa Engine")
            st.json(p1)
            
        with tab2:
            st.markdown("**Target:** Heuristic Metadata Engine")
            st.json(p2)
            
    except Exception as e:
        st.error(f"Pipeline Failure: {str(e)}")
        
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)

else:
    st.info("Awaiting .eml file ingestion. Please upload a file via the sidebar to run the Zero-Trust pipeline.")
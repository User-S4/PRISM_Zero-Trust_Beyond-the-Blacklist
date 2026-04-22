# Import your isolated pipeline modules
from ingest import parse_eml_to_payload  # Assuming your function returns (payload1, payload2)
from linguistics import analyze_linguistics
from behaviourIdentity import analyze_metadata
from dts import evaluate_transaction

def execute_zero_trust_pipeline(file_path: str):
    print(f"--- INITIATING PIPELINE FOR: {file_path} ---")
    
    # ==========================================
    # LAYER 1: INGESTION & DECOUPLING
    # ==========================================
    # Your updated ingest.py returns the two isolated payloads
    payload1, payload2 = parse_eml_to_payload(file_path)
    print("Layer 1 (Ingestion): Payloads successfully decoupled.")

    # ==========================================
    # TRACK A: LINGUISTIC ANALYSIS
    # ==========================================
    # Pass ONLY payload1 to the DistilBERT file
    l_score = analyze_linguistics(payload1) 
    #Uncomment this after adding the linguistic code
    #l_score = 0.02 
    # #Testing pursposes
    print(f"Track A (Linguistic): L_Score = {l_score}")

    # ==========================================
    # TRACK B: FORENSIC ANALYSIS
    # ==========================================
    # Pass ONLY the metadata from payload2 to the heuristic engine
    metadata = payload2["payload"]["metadata"]
    forensic_scores = analyze_metadata(metadata)
    
    b_score = forensic_scores["B_score"]
    i_score = forensic_scores["I_score"]
    print(f"Track B (Forensic): B_Score = {b_score}, I_Score = {i_score}")

    # ==========================================
    # LAYER 3 & 4: HYBRID MATH & POLICY ROUTING
    # ==========================================
    # Pass the three isolated floats into the scoring equation
    final_verdict = evaluate_transaction(b_score=b_score, l_score=l_score, i_score=i_score)
    
    print("\n--- ZERO-TRUST VERDICT ---")
    print(f"Final DTS: {final_verdict['DTS']}")
    print(f"Action: {final_verdict['Decision']}")
    print("--------------------------\n")

if __name__ == "__main__":
    # Test the pipeline with your sample .eml file
    # Ensure 'sample_phishing.eml' exists in the same folder
    execute_zero_trust_pipeline("/Users/aruns/Desktop/ZU-SRC26_PRISM/Dataset/legitimate_sample1.eml")
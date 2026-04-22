import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix
import warnings
warnings.filterwarnings('ignore')

# Import your Track A and Track B functions (assuming you adapt them slightly to take text/dict inputs)
# For this script to work, you need to ensure your functions can take strings directly 
# instead of just extracting from .eml files.
from linguistics import analyze_linguistics 
from behaviourIdentity import analyze_metadata
from dts import evaluate_transaction

def run_evaluation(csv_path):
    print(f"Loading Dataset: {csv_path}...")
    df = pd.read_csv(csv_path)
    
    actual_labels = []
    predicted_labels = []
    
    print("Initiating Batch Processing. Please wait...\n")
    
    # Loop through every email in the dataset
    for index, row in df.iterrows():
        text_body = row['text']
        actual_label = row['label'] # 1 is Phishing, 0 is Legit
        
        # 1. Format mock payloads (Since we are reading from CSV, not .eml)
        payload1 = {"payload": {"message_body": text_body}}
        
        # For a true test, your CSV would also need metadata columns. 
        # Since our generated CSV only has text, we will mock perfect metadata 
        # to isolate and test how well your Track A + Math Engine performs.
        mock_metadata = {
            "sender_ip": "192.0.2.1", 
            "header_from": "test@test.com",
            "header_reply_to": "test@test.com", 
            "auth_status": {"spf": "pass", "dkim": "pass"}
        }
        
        # 2. Run the Pipeline
        l_score = analyze_linguistics(payload1)
        forensic_scores = analyze_metadata(mock_metadata)
        
        dts_data = evaluate_transaction(
            b_score=forensic_scores["B_score"], 
            l_score=l_score, 
            i_score=forensic_scores["I_score"]
        )
        
        # 3. Map the PRISM output to binary
        if dts_data["Decision"] in ["BLOCK", "CHALLENGE"]:
            predicted_label = 1
        else:
            predicted_label = 0
            
        # --- ADD THIS DEBUG BLOCK ---
        # If it's a False Positive (Actual is Legit, but we Predicted Phishing)
        if actual_label == 0 and predicted_label == 1:
            print(f"FALSE ALARM DETECTED:")
            print(f"L_Score: {l_score} | DTS: {dts_data['DTS']} | Decision: {dts_data['Decision']}")
            print(f"Text Snippet: {text_body[:60]}...\n")
        # ----------------------------

        actual_labels.append(actual_label)
        predicted_labels.append(predicted_label)
        
    # ==========================================
    # CALCULATE METRICS
    # ==========================================
    accuracy = accuracy_score(actual_labels, predicted_labels)
    precision = precision_score(actual_labels, predicted_labels, zero_division=0)
    recall = recall_score(actual_labels, predicted_labels, zero_division=0)
    
    tn, fp, fn, tp = confusion_matrix(actual_labels, predicted_labels).ravel()
    
    print("==========================================")
    print("         PRISM ACCURACY REPORT            ")
    print("==========================================")
    print(f"Total Emails Processed: {len(df)}")
    print(f"Overall Accuracy:       {accuracy * 100:.2f}%")
    print(f"Precision (Low FP):     {precision * 100:.2f}%")
    print(f"Recall (Catch Rate):    {recall * 100:.2f}%\n")
    
    print("--- CONFUSION MATRIX ---")
    print(f"True Positives (Attacks Caught):  {tp}")
    print(f"True Negatives (Legit Allowed):   {tn}")
    print(f"False Positives (False Alarms):   {fp}")
    print(f"False Negatives (Breaches):       {fn}")
    print("==========================================")

if __name__ == "__main__":
    # Point this to the CSV dataset we generated earlier
    run_evaluation("/Users/aruns/Desktop/ZU-SRC26_PRISM/Dataset/Dataset-Pre.csv")
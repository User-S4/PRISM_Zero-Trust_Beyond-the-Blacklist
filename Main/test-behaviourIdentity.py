#Payload2
from behaviourIdentity import analyze_metadata

def run_forensic_tests():
    print("Executing Layer 2 Forensic Unit Tests...\n")

    # 1. Simulate a Malicious Payload (Zero-Day VPN Attack)
    mock_phishing_metadata = {
        "sender_ip": "209.85.220.41",  # Hardcoded in KNOWN_VPN_NODES
        "header_from": "Kanchan Poonacha <kanchanpoonacha3@gmail.com>",
        "header_reply_to": "Kanchan Poonacha <kanchanpoonacha3@gmail.com>", # Domain mismatch
        "auth_status": {
            "spf": "fail", #Changed for testing purposes
            "dkim": "pass"
        }
    }

    # 2. Simulate a Legitimate Corporate Payload
    mock_legit_metadata = {
        "sender_ip": "192.0.2.1", # Safe public IP
        "header_from": "hr@your-enterprise.com",
        "header_reply_to": "hr@your-enterprise.com", # Perfect match
        "auth_status": {
            "spf": "pass",
            "dkim": "pass"
        }
    }

    print("--- TEST CASE 1: ZERO-DAY PHISHING ---")
    phishing_scores = analyze_metadata(mock_phishing_metadata)
    print(f"Behavioral (B) Score: {phishing_scores['B_score']} (Expected: Low)")
    print(f"Identity (I) Score:   {phishing_scores['I_score']} (Expected: Low)\n")

    print("--- TEST CASE 2: LEGITIMATE COMMUNICATION ---")
    legit_scores = analyze_metadata(mock_legit_metadata)
    print(f"Behavioral (B) Score: {legit_scores['B_score']} (Expected: 1.0)")
    print(f"Identity (I) Score:   {legit_scores['I_score']} (Expected: 1.0)\n")

if __name__ == "__main__":
    run_forensic_tests()
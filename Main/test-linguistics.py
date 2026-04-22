from linguistics import analyze_linguistics

def run_linguistic_tests():
    print("Loading model and executing Track A (Linguistic) Tests...\n")

    # 1. Simulate a Legitimate Corporate Payload
    mock_legit_payload = {
        "payload": {
            "message_body": "Hello ,the Q2 budget spreadsheet has been updated. Please review the document before Thursday's meeting. There is no immediate action required. Feel free to reach out if you have any questions."
        }
    }

    # 2. Simulate a Phishing Payload (BEC / Urgent Threat)
    mock_phishing_payload = {
        "payload": {
            "message_body": "Attention , our automated system registered a critical routing failure regarding your direct deposit. If we do not receive the corrected routing numbers today, your salary payment will be suspended. Log in immediately to resolve this discrepancy."
        }
    }

    print("--- TEST CASE 1: LEGITIMATE COMMUNICATION ---")
    try:
        l_score_legit = analyze_linguistics(mock_legit_payload)
        print(f"Linguistic (L) Score: {l_score_legit} (Expected: High / Near 1.0)\n")
    except Exception as e:
        print(f"Test Failed: {e}\n")

    print("--- TEST CASE 2: URGENT PHISHING THREAT ---")
    try:
        l_score_phishing = analyze_linguistics(mock_phishing_payload)
        print(f"Linguistic (L) Score: {l_score_phishing} (Expected: Low / Near 0.0)\n")
    except Exception as e:
        print(f"Test Failed: {e}\n")

if __name__ == "__main__":
    run_linguistic_tests()
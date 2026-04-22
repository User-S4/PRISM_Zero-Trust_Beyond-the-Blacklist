#Payload1

from transformers import pipeline

# Load the RoBERTa NLI model
try:
    print("Loading RoBERTa Zero-Shot Model...")
    # Swapped BART for RoBERTa to match your abstract perfectly
    classifier = pipeline("zero-shot-classification", model="roberta-large-mnli")
except Exception as e:
    print(f"Warning: Could not load RoBERTa model. Error: {e}")

def analyze_linguistics(payload1: dict) -> float:
    try:
        text_body = payload1["payload"]["message_body"]
    except KeyError:
        raise ValueError("Linguistic Error: Invalid schema. Missing 'message_body'.")

    # The new, smarter labels
    candidate_labels = [
        "routine administrative update with no immediate penalty", 
        "urgent security threat demanding immediate login to avoid financial penalty"
    ]

    # Run the RoBERTa inference
    result = classifier(text_body, candidate_labels)

    # CRITICAL FIX: This string must match the first label EXACTLY
    legit_index = result["labels"].index("routine administrative update with no immediate penalty")
    legit_score = result["scores"][legit_index]

    return round(legit_score, 3)
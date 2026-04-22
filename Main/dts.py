def calculate_dts(b_score: float, l_score: float, i_score: float) -> float:
    """
    Layer 3: The Hybrid Scoring Engine
    Computes the Digital Trust Score (DTS) using the dual-track variables.
    """
    # System Parameters defined in the architecture
    w1 = 0.45  # Behavioral Weight
    w2 = 0.30  # Linguistic Weight
    w3 = 0.25  # Identity Weight
    alpha = 0.60  # Stability Coefficient

    # 1. The Linear Component (Weighted Average)
    linear_component = (w1 * b_score) + (w2 * l_score) + (w3 * i_score)

    # 2. The Multiplicative Component (Zero-Trust Fail-Safe)
    multiplicative_component = b_score * l_score * i_score

    # 3. Final DTS Calculation
    dts = (alpha * linear_component) + ((1 - alpha) * multiplicative_component)
    
    # Clamp between 0.0 and 1.0 just in case, and round for clean UI presentation
    return max(0.0, min(1.0, round(dts, 3)))

def enforce_policy(dts_score: float) -> str:
    """
    Layer 4: Policy Enforcement
    Determines the routing action based on strict DTS thresholds.
    """
    if dts_score >= 0.75:
        return "ALLOW"
    elif dts_score >= 0.40:
        return "CHALLENGE"
    else:
        return "BLOCK"

def evaluate_transaction(b_score: float, l_score: float, i_score: float) -> dict:
    """
    Master controller function for Layers 3 & 4.
    Takes the three raw scores and outputs the final mathematical verdict.
    """
    dts = calculate_dts(b_score, l_score, i_score)
    decision = enforce_policy(dts)
    
    return {
        "DTS": dts,
        "Decision": decision,
        "Input_Scores": {
            "Behavioral_B": b_score,
            "Linguistic_L": l_score,
            "Identity_I": i_score
        }
    }
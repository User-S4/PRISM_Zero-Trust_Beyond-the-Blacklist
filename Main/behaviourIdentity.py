#Payload2

import ipaddress
import re

# ==========================================
# MOCK THREAT INTEL (For offline PoC purposes)
# ==========================================
KNOWN_VPN_NODES = {"103.45.67.89", "185.17.12.5", "45.22.99.11"}
HIGH_RISK_TLDS = {".xyz", ".top", ".pw", ".cc", ".ru"}

def _extract_domain(email_address):
    """Isolates the domain from an email string (e.g., 'user@domain.com' -> 'domain.com')."""
    match = re.search(r'@([\w.-]+)', email_address)
    return match.group(1).lower() if match else ""

def compute_identity_score(metadata):
    """
    Computes the Identity (I) Score.
    Scale: 0.0 (Spoofed/Malicious) to 1.0 (Verified Legitimate).
    """
    i_score = 1.0
    
    # 1. Header Alignment Penalty (The "Reply-To" Trap)
    domain_from = _extract_domain(metadata.get("header_from", ""))
    domain_reply = _extract_domain(metadata.get("header_reply_to", ""))
    
    if domain_from != domain_reply:
        i_score -= 0.6  # Massive penalty for routing replies to a different domain
        
    # 2. Authentication Penalties (SPF/DKIM)
    auth = metadata.get("auth_status", {})
    spf = auth.get("spf", "none")
    dkim = auth.get("dkim", "none")
    
    if spf == "fail":
        i_score -= 0.5
    if dkim == "fail":
        i_score -= 0.5
    if spf == "none" and dkim == "none":
        i_score -= 0.2  # Suspicious lack of modern authentication
        
    # Clamp to valid 0-1 range
    return max(0.0, min(1.0, round(i_score, 2)))

def compute_behavioral_score(metadata):
    """
    Computes the Behavioral (B) Score.
    Scale: 0.0 (Anomalous/Malicious) to 1.0 (Standard Routing).
    """
    b_score = 1.0
    ip_str = metadata.get("sender_ip", "0.0.0.0")
    
    # 1. IP Routing Anomalies
    try:
        ip_obj = ipaddress.ip_address(ip_str)
        if ip_obj.is_private or ip_obj.is_loopback:
            # External emails claiming to originate from a local network node are highly suspect
            b_score -= 0.4
    except ValueError:
        b_score -= 0.5 # Malformed IP address
        
    # 2. Threat Intelligence Match
    if ip_str in KNOWN_VPN_NODES:
        b_score -= 0.7  # Hit on a known malicious or anonymizing node
        
    # 3. Sender Domain Heuristics
    domain_reply = _extract_domain(metadata.get("header_reply_to", ""))
    if any(domain_reply.endswith(tld) for tld in HIGH_RISK_TLDS):
        b_score -= 0.3
        
    # Clamp to valid 0-1 range
    return max(0.0, min(1.0, round(b_score, 2)))

def analyze_metadata(metadata):
    """
    The Core Forensic Function.
    Ingests ONLY the metadata dictionary and outputs the B and I scores.
    """
    if not isinstance(metadata, dict):
        raise TypeError("Forensic Error: Expected a metadata dictionary.")

    i_score = compute_identity_score(metadata)
    b_score = compute_behavioral_score(metadata)

    # Return as a structured dictionary for Layer 3 (The Hybrid Scoring Engine)
    return {
        "B_score": b_score,
        "I_score": i_score
    }
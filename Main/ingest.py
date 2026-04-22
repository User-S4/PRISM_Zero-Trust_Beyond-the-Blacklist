import os
import re
import email
from email import policy
import uuid

def _extract_ip(headers):
    """
    Heuristic: Scans the 'Received' headers to extract the originating IP.
    Returns the first valid IPv4 address found, or a 0.0.0.0 fallback.
    """
    ip_pattern = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')
    for header in headers:
        if header.lower().startswith('received:'):
            match = ip_pattern.search(header)
            if match:
                return match.group(0)
    return "0.0.0.0"

def _extract_auth_status(headers):
    """
    Heuristic: Scans for the 'Authentication-Results' header to determine SPF and DKIM.
    Defaults to 'none' if the protocol was not evaluated.
    """
    status = {"spf": "none", "dkim": "none"}
    for header in headers:
        if header.lower().startswith('authentication-results:'):
            header_lower = header.lower()
            # Parse SPF
            if 'spf=pass' in header_lower: 
                status["spf"] = "pass"
            elif 'spf=fail' in header_lower or 'spf=softfail' in header_lower: 
                status["spf"] = "fail"
            
            # Parse DKIM
            if 'dkim=pass' in header_lower: 
                status["dkim"] = "pass"
            elif 'dkim=fail' in header_lower: 
                status["dkim"] = "fail"
    return status

def parse_eml_to_payload(file_path):
    """
    The Core Ingestion Function.
    Takes a raw .eml file path and outputs the strict dual-track dictionary.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Ingestion Error: File not found at {file_path}")

    with open(file_path, 'rb') as f:
        # Using policy.default enables automatic decoding of complex headers
        msg = email.message_from_binary_file(f, policy=policy.default)

    # 1. Establish Identity
    # If no Message-ID exists, generate a deterministic fallback to prevent pipeline crashes.
    raw_id = msg.get('Message-ID', f"POC-{uuid.uuid4().hex[:8]}")
    comm_id = raw_id.strip('<>')

    # 2. Extract Track A: Linguistic Payload (Message Body)
    body = ""
    if msg.is_multipart():
        # Walk through the email parts and grab the first plain text iteration
        for part in msg.walk():
            if part.get_content_type() == 'text/plain':
                body = part.get_content()
                break
    else:
        body = msg.get_content()

    body = body.strip() if body else "NO_TEXT_PAYLOAD"

    # 3. Extract Track B: Forensic Metadata
    # Flatten headers into a searchable list
    raw_headers = [f"{k}: {v}" for k, v in msg.items()]

    sender_ip = _extract_ip(raw_headers)
    auth_status = _extract_auth_status(raw_headers)
    
    header_from = str(msg.get('From', 'UNKNOWN_SENDER'))
    # If no Reply-To is explicitly stated, standard email behavior defaults to the From address
    header_reply_to = str(msg.get('Reply-To', header_from))

    # 4. Construct the Strict Dual-Track Schema
    payload1 = {
        "communication_id": comm_id,
        "payload": {
            "message_body": body,
        }
    }
    
    payload2 = {
        "communication_id": comm_id,
        "payload": {
            "metadata": {
                "sender_ip": sender_ip,
                "header_from": header_from,
                "header_reply_to": header_reply_to,
                "auth_status": auth_status
            }
        }
    }


    return payload1, payload2
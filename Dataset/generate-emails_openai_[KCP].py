import os
import time
import random
import pandas as pd
from openai import OpenAI

# ==============================
# 1. CONFIGURATION
# ==============================
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

TARGET_SAMPLES_PER_CLASS = 500
OUTPUT_FILE = "i.csv"

# ==============================
# 2. SYMMETRIC MATRICES & MOCK DATA
# ==============================
scenarios = [
    "Automated IT Security Alert", 
    "Overdue Vendor Invoice", 
    "HR Benefits Enrollment", 
    "Shared SharePoint Document", 
    "Urgent Executive Wire Request", 
    "Internal VPN Certificate Update"
]

tones = [
    "Sterile/Automated", 
    "Highly Formal Corporate", 
    "Brief/Sent-from-Mobile", 
    "Authoritative"
]

targets = [
    "Finance Department", 
    "New Hire", 
    "C-Suite Executive", 
    "General Employee Base"
]

# Mock entities to prevent placeholder brackets
companies = ["Apex Financial", "Stratos Technologies", "Nexus Logistics", "Meridian Consulting", "Vanguard Health"]
senders = ["Sarah Jenkins", "David Chen", "Michael Roberts", "Emily Davis", "Marcus Thorne"]
# The exact same links are used for both to prevent URL-based data leakage
urls = [
    "https://auth-gateway.secure-access-verify.com/login",
    "https://sharepoint-docs.enterprise-cloud-host.com/view",
    "https://hr-portal.benefits-management-system.com/auth"
]

# ==============================
# 3. PROMPT ARCHITECTURE
# ==============================
SYSTEM_MESSAGE = (
    "You are an expert cybersecurity red-team simulator generating data for a machine learning defense model. "
    "You must output strictly the raw, highly realistic text of the email body only. "
    "Do NOT include any email headers such as To, From, Date, or Subject. "
    "Do not include conversational filler, introductory text, markdown, or metadata tags.\n\n"
    "CRITICAL CONSTRAINTS:\n"
    "1. NEVER use ANY placeholder brackets or generic tags (e.g., [company name], [Executive's Name], [Insert Link], [New Hire's First Name]).\n"
    "2. NEVER use ANY contractions or words with apostrophes (e.g., do not use \"don't\", \"it's\", \"we're\", \"can't\", \"won't\", \"I'm\", \"that's\", \"isn't\", etc.). "
    "Always use the full expanded form (e.g., \"do not\", \"it is\", \"we are\", \"cannot\", \"will not\", \"I am\", \"that is\", \"is not\").\n"
    "3. Generate REALISTIC FAKE DATA for all fields:\n"
    "   - Use fake but realistic names for people\n"
    "   - Generate fake but plausible company names\n"
    "   - Create realistic fake email addresses matching the company domain\n"
    "   - Generate realistic fake phone numbers\n"
    "   - Use realistic domain names for links\n"
    "   - Generate fake but proper formatted dates and times\n"
    "   - Create fake employee IDs or reference numbers if needed\n"
    "   - Use realistic fake addresses if mentioned\n"
    "4. Never use generic spam tropes like 'Dear Customer' or glaring typos.\n"
    "5. BOTH benign and phishing emails MUST frequently include standard corporate politeness and support offers "
    "(e.g., 'Feel free to reach out if you have any questions', 'Let me know if you need clarification', or 'Please reply if you encounter issues').\n"
    "6. All fake data must be seamlessly integrated and contextually appropriate."
)

def generate_email(is_phishing):
    scenario = random.choice(scenarios)
    tone = random.choice(tones)
    target = random.choice(targets)
    company = random.choice(companies)
    sender = random.choice(senders)
    url = random.choice(urls)

    if is_phishing:
        user_prompt = (
            f"Write a highly sophisticated, AI-generated spear-phishing email simulating a {scenario} "
            f"targeting a {target} at {company}. The sender is claiming to be {sender}. "
            f"The tone must perfectly mimic the {tone} of a legitimate corporate email.\n\n"
            "The Objective: Weaponize the scenario to steal credentials or force a malicious download without triggering suspicion.\n"
            f"The Execution: Embed this exact link naturally into the text: {url}. "
            "Subtly manipulate the psychology of the target by introducing artificial urgency, bypassing standard "
            "verification procedures, or leveraging authority.\n\n"
            "FAKE DATA REQUIREMENT: Instead of placeholders, generate realistic fake details such as:\n"
            "- Realistic fake names (e.g., 'Jennifer Martinez' instead of [Executive's Name])\n"
            "- Fake job titles matching the target role\n"
            "- Realistic fake dates and times\n"
            "- Fake employee IDs, reference numbers, or case numbers\n"
            "- Realistic department names\n"
            "- Fake phone numbers and email addresses with proper formatting\n"
            "Constraint: The grammar and vocabulary must remain flawless. The deception must rely entirely on the "
            "context and the psychological pressure."
        )
    else:
        user_prompt = (
            f"Write a standard, benign corporate email regarding a {scenario} targeting a {target} at {company}. "
            f"The sender is {sender}. The tone must be {tone}. This is a routine, safe business operation.\n\n"
            f"The Execution: Embed this exact link naturally into the text: {url}. "
            "Do NOT repeatedly use the words 'Internal' or 'Portal' to describe the link. Use varied, natural phrasing "
            "(e.g., 'the document is attached here', 'access the file at', 'review the system').\n\n"
            "FAKE DATA REQUIREMENT: Instead of placeholders, generate realistic fake details such as:\n"
            "- Realistic fake names (e.g., 'Robert Thompson' instead of [New Hire's First Name])\n"
            "- Fake job titles matching the target role\n"
            "- Realistic fake dates and times\n"
            "- Fake reference numbers or meeting IDs\n"
            "- Realistic department names\n"
            "- Fake phone numbers and email addresses with proper formatting\n"
            "- Fake room numbers or office locations if applicable\n"
            "Constraint: Do not artificially inflate urgency. Make it indistinguishable from a boring, "
            "everyday corporate email."
        )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_MESSAGE},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.85 
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"API Error: {e}")
        return None

# ==============================
# 4. EXECUTION LOOP
# ==============================
if not os.path.exists(OUTPUT_FILE):
    pd.DataFrame(columns=["text", "label"]).to_csv(OUTPUT_FILE, index=False)

print("Starting hardened symmetric generation pipeline...")

for i in range(TARGET_SAMPLES_PER_CLASS):
    phish_text = generate_email(is_phishing=True)
    if phish_text:
        pd.DataFrame([{"text": phish_text, "label": 1}]).to_csv(OUTPUT_FILE, mode='a', header=False, index=False)
    
    legit_text = generate_email(is_phishing=False)
    if legit_text:
        pd.DataFrame([{"text": legit_text, "label": 0}]).to_csv(OUTPUT_FILE, mode='a', header=False, index=False)
    
    print(f"Generated pair {i+1}/{TARGET_SAMPLES_PER_CLASS}")
    
    time.sleep(1.5) 

print(f"\nDataset completely generated and saved to {OUTPUT_FILE}")
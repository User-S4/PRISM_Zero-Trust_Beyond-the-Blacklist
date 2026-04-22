import json
from ingest import parse_eml_to_payload

def execute_test():
    target_file = "/teamspace/studios/this_studio/ZU-SRC26_PRISM/Dataset/Sample-Email.eml"
    
    print(f"Executing Ingestion Pipeline on: {target_file}...\n")
    
    try:
        # Run the parser from Layer 1
        payload1, payload2  = parse_eml_to_payload(target_file)
        
        # Pretty-print the output dictionary
        print("--- PARSED JSON OUTPUT ---")
        print(json.dumps(payload1, indent=4))
        print(json.dumps(payload2, indent=4))
        print("--------------------------")
        
    except Exception as e:
        print(f"Ingestion Pipeline Failed: {e}")

if __name__ == "__main__":
    execute_test()
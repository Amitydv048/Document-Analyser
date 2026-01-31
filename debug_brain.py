import os
import traceback
from dotenv import load_dotenv
from brain import DocumentBrain

# Load env variables
load_dotenv()

def debug_ingestion():
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: API Key not found in environment (GOOGLE_API_KEY or OPENAI_API_KEY).")
        return

    print(f"API Key found (starts with: {api_key[:5]}...)")
    
    try:
        brain = DocumentBrain(api_key)
        # Use existing test_doc.pdf
        if not os.path.exists("test_doc.pdf"):
            print("Creating test PDF...")
            from generate_test_pdf import create_pdf
            create_pdf("test_doc.pdf")
            
        print("Attempting to ingest test_doc.pdf...")
        brain.ingest_pdf("test_doc.pdf")
        print("Ingestion successful!")
        
    except Exception:
        print("\n--- EXCEPTION TRACEBACK ---")
        traceback.print_exc()

if __name__ == "__main__":
    debug_ingestion()

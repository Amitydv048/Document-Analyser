import os
import argparse
from brain import DocumentBrain

def main():
    parser = argparse.ArgumentParser(description="Chat with your PDF")
    parser.add_argument("file_path", help="Path to the PDF file to process")
    args = parser.parse_args()

    # Get API Key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        api_key = input("Enter your OpenAI API Key: ").strip()
    
    if not api_key:
        print("Error: OpenAI API Key is required.")
        return

    try:
        brain = DocumentBrain(api_key)
        brain.ingest_pdf(args.file_path)
        
        print("\n--- Document Ready. Type 'exit' to quit. ---")
        while True:
            query = input("\nYou: ")
            if query.lower() in ["exit", "quit"]:
                break
            
            response = brain.ask(query)
            print(f"Bot: {response}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

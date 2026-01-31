import os
from dotenv import load_dotenv
from brain import DocumentBrain
from processor import DocumentProcessor

# Load env variables
load_dotenv()

def debug_qa(pdf_path="test_doc.pdf", query="What is this document about?"):
    print(f"--- Debugging: {pdf_path} ---")
    
    # 1. Check Text Extraction
    print("\n[Step 1] Checking Raw Text Extraction...")
    processor = DocumentProcessor()
    raw_text = ""
    for page in processor.process_pdf(pdf_path):
        content = page.get("content", "")
        print(f"Page {page.get('page_number')}: {len(content)} chars")
        raw_text += content + "\n"
    
    if len(raw_text.strip()) < 50:
        print("WARNING: Extracted text is very short! OCR might be failing or PDF is empty.")
        print(f"Raw Text Snippet: '{raw_text}'")
    else:
        print(f"Total Text Length: {len(raw_text)}")
        print(f"First 200 chars: {raw_text[:200]}")

    # 2. Check Embedding & Retrieval
    print("\n[Step 2] Checking Retrieval...")
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: No API Key found.")
        return

    brain = DocumentBrain(api_key)
    brain.ingest_pdf(pdf_path)
    
    print(f"\nQuery: {query}")
    if brain.vector_store:
        # Fetch relevant documents directly
        docs = brain.vector_store.similarity_search(query)
        print(f"Found {len(docs)} relevant chunks.")
        for i, doc in enumerate(docs):
            print(f"-- Chunk {i+1} (Score/Content excerpt) --")
            print(doc.page_content[:150].replace("\n", " "))
    
    # 3. Check Final Answer
    print("\n[Step 3] Asking Brain...")
    answer = brain.ask(query)
    print(f"Answer: {answer}")

if __name__ == "__main__":
    # You can change the filename here to the specific file causing issues if available
    # The user uploaded 'uploads/Amit-Yadav-Ai.pdf' in the logs, but I might not have access to it if I didn't create it.
    # I will try to look for files in uploads/ first.
    
    target_file = "test_doc.pdf"
    if os.path.exists("uploads"):
        files = os.listdir("uploads")
        pdf_files = [f for f in files if f.endswith(".pdf")]
        if pdf_files:
            target_file = os.path.join("uploads", pdf_files[0])
    
    if os.path.exists(target_file):
        debug_qa(target_file, "Summarize this document")
    else:
        print(f"File {target_file} not found. Please ensure a PDF exists.")

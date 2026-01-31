import argparse
from processor import DocumentProcessor

def main():
    parser = argparse.ArgumentParser(description="Document Processor CLI")
    parser.add_argument("file_path", help="Path to the PDF file to process")
    args = parser.parse_args()

    processor = DocumentProcessor()
    
    print(f"Processing {args.file_path}...")
    for page_data in processor.process_pdf(args.file_path):
        print(f"\n--- Page {page_data.get('page_number')} ---")
        if "error" in page_data:
            print(f"Error: {page_data['error']}")
        else:
            print(f"Method: {page_data['extraction_method']}")
            print(f"Content Length: {len(page_data['content'])}")
            print(f"Content Snippet: {page_data['content'][:200]}...")

if __name__ == "__main__":
    main()

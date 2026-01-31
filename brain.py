import os
from typing import List, Optional
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.docstore.document import Document
from processor import DocumentProcessor

class DocumentBrain:
    def __init__(self, api_key: str):
        # Determine if it's an OpenAI or Google key based on env or passed arg.
        # But user specifically said they use Google API Key now.
        # Ideally we check the key format or rely on specific env vars.
        # For this fix, we will default to Google since the user explicitly installed it and requested it.
        
        self.api_key = api_key
        if not self.api_key:
            raise ValueError("API Key is required.")
        
        # Configure Google Gen AI
        if "AIza" in self.api_key: # Simple heuristic for Google Keys
             os.environ["GOOGLE_API_KEY"] = self.api_key
        
        # Initialize Embeddings and LLM (Google Gemini)
        try:
            self.embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
            self.llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", temperature=0, convert_system_message_to_human=True)
        except Exception as e:
            raise ValueError(f"Failed to initialize Google Gemini: {e}")

        self.vector_store = None
        self.qa_chain = None

    def ingest_pdf(self, file_path: str):
        """
        Ingests a PDF file, extracts text, splits it, and creates a vector store.
        """
        print(f"Ingesting {file_path}...")
        processor = DocumentProcessor()
        
        # 1. Extract raw text from relevant pages
        raw_documents = []
        for page_data in processor.process_pdf(file_path):
            if "content" in page_data and page_data["content"]:
                # Create LangChain Document objects
                doc = Document(
                    page_content=page_data["content"],
                    metadata={"page": page_data["page_number"], "source": file_path}
                )
                raw_documents.append(doc)
        
        if not raw_documents:
            raise ValueError("No text could be extracted from the PDF.")

        # 2. Split text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        chunks = text_splitter.split_documents(raw_documents)
        print(f"Split into {len(chunks)} chunks.")

        # 3. Create Vector Store
        print("Creating vector store...")
        try:
            self.vector_store = FAISS.from_documents(chunks, self.embeddings)
            print("Vector store created.")
        except Exception as e:
            print(f"Error creating vector store: {e}")
            raise e

        # 4. Initialize QA Chain
        self._init_qa_chain()

    def _init_qa_chain(self):
        """
        Initializes the RetrievalQA chain with a custom prompt to enforce strict context usage.
        """
        if not self.vector_store:
            raise ValueError("Vector store not initialized. Call ingest_pdf first.")

        prompt_template = """Use the following pieces of context to answer the question at the end. 
if you don't know the answer, just say that you don't know, don't try to make up an answer.

{context}

Question: {question}
Answer:"""
        PROMPT = PromptTemplate(
            template=prompt_template, input_variables=["context", "question"]
        )

        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(),
            chain_type_kwargs={"prompt": PROMPT}
        )

    def ask(self, query: str) -> str:
        """
        Ask a question to the brain.
        """
        if not self.qa_chain:
            return "Please ingest a document first."
        
        try:
            # LangChain's run method might differ slightly for different chains, but run(query) is standard for QA
            return self.qa_chain.run(query)
        except Exception as e:
            return f"Error during QA: {e}"

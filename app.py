from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
import os
from typing import Optional
from dotenv import load_dotenv
load_dotenv()

from brain import DocumentBrain

# --- Configuration ---
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- Global State ---
class GlobalState:
    brain: Optional[DocumentBrain] = None

state = GlobalState()

# --- API Models ---
class AskRequest(BaseModel):
    query: str

class AskResponse(BaseModel):
    answer: str

# --- App Setup ---
app = FastAPI(title="Document Analyser AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Endpoints ---

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Uploads a PDF file, saves it, and ingests it into the brain.
    """
    try:
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Initialize Brain if not exists or re-init for clean slate (optional)
        # Check for GOOGLE_API_KEY first, then OPENAI_API_KEY
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
             return {"error": "Server missing API Key. Please set GOOGLE_API_KEY in environment."}

        state.brain = DocumentBrain(api_key)
        state.brain.ingest_pdf(file_location)
        
        return {"filename": file.filename, "status": "Indexed successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    """
    Ask a question to the loaded document.
    """
    if not state.brain:
        raise HTTPException(status_code=400, detail="No document indexed. Please upload a PDF first.")
    
    answer = state.brain.ask(request.query)
    return AskResponse(answer=answer)

# --- Frontend ---
app.mount("/", StaticFiles(directory="static", html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    # Use port 8000 by default
    uvicorn.run(app, host="0.0.0.0", port=8000)

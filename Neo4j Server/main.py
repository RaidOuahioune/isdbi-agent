import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from llama_index.llms.gemini import Gemini
from Neo4jUploader import Neo4jUploader
from ask_compliance_question import ask_compliance_question
from query_enhancer import enhance_query
import uvicorn
import time

# Load environment variables from .env file
load_dotenv()

# Define request and response models
class QuestionRequest(BaseModel):
    question: str
    top_k: Optional[int] = 6
    temperature: Optional[float] = 0.1
    disable_enhancement: Optional[bool] = False

class EnhanceResponse(BaseModel):
    original_question: str
    enhanced_question: str

class AnswerResponse(BaseModel):
    answer: str
    processing_time: float
    enhanced_query: Optional[str] = None

# Initialize FastAPI app
app = FastAPI(
    title="Islamic Finance Compliance API",
    description="API for answering Islamic finance compliance questions using RAG with Neo4j",
    version="1.0.0"
)

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Environment variables with defaults
NEO4J_URI = os.environ.get("NEO4J_URI", "neo4j://localhost:7687")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "yourStrongPassword123")  # Set a better default or require this env var
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "models/gemini-1.5-flash")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")  # Added API key from environment

# Print debugging info at startup (remove in production)
print(f"NEO4J_URI: {NEO4J_URI}")
print(f"GEMINI_MODEL: {GEMINI_MODEL}")
print(f"GOOGLE_API_KEY set: {'Yes' if GOOGLE_API_KEY else 'No'}")

# Dependency to get Neo4j uploader instance
def get_neo4j_uploader():
    try:
        uploader = Neo4jUploader(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
        yield uploader
        # Close connection when done
        uploader.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to connect to Neo4j: {str(e)}")

# Dependency to get LLM instance
def get_llm(temperature: float = 0.1):
    try:
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY environment variable is not set. Please check your .env file.")
            
        return Gemini(
            model=GEMINI_MODEL,
            api_key=GOOGLE_API_KEY,  # Pass the API key to Gemini
            temperature=temperature
        )
    except Exception as e:
        print(f"LLM initialization error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to initialize LLM: {str(e)}")

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": time.time()}

# Add an endpoint just for query enhancement
@app.post("/api/enhance-query", response_model=EnhanceResponse)
def enhance_query_endpoint(
    request: QuestionRequest,
    llm=Depends(get_llm)
):
    if not request.question or len(request.question.strip()) < 3:
        raise HTTPException(status_code=400, detail="Question must be at least 3 characters long")
    
    try:
        enhanced = enhance_query(request.question, llm)
        return {
            "original_question": request.question,
            "enhanced_question": enhanced
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error enhancing query: {str(e)}")

# Main query endpoint
@app.post("/api/ask", response_model=AnswerResponse)
def ask_question(
    request: QuestionRequest,
    uploader: Neo4jUploader = Depends(get_neo4j_uploader),
    background_tasks: BackgroundTasks = None
):
    start_time = time.time()
    
    if not request.question or len(request.question.strip()) < 3:
        raise HTTPException(status_code=400, detail="Question must be at least 3 characters long")
    
    try:
        # Get LLM with user's temperature preference
        llm = get_llm(request.temperature)
        
        # Process the question
        answer = ask_compliance_question(
            question=request.question,
            uploader=uploader,
            llm=llm,
            top_k=request.top_k
        )
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Get the enhanced query for including in response
        enhanced_query = None
        if not request.disable_enhancement:
            enhanced_query = enhance_query(request.question, llm)
        
        return {
            "answer": answer,
            "processing_time": processing_time,
            "enhanced_query": enhanced_query
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

# Add a background task to close connections properly if needed
def cleanup():
    # Any cleanup code here
    pass

@app.on_event("shutdown")
def shutdown_event():
    cleanup()

# Run the server if executed directly
if __name__ == "__main__":
    # Verify environment variables at startup
    if not GOOGLE_API_KEY:
        print("WARNING: GOOGLE_API_KEY is not set. The API will not work correctly.")
        
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

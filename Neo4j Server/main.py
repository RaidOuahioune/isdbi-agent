import json
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from llama_index.llms.gemini import Gemini
from Neo4jUploader import Neo4jUploader
from ask_compliance_question import ask_compliance_question
from query_enhancer import enhance_query
from legalExpert import ask_compliance_question_law, query_law_clauses
from standardExpert import query_standard_clauses
from shari3a import search_all_sources_by_text
from generatePdf import generate_updated_standard_pdf
from orchestrator import route_to_specialized_agent
import os
from Neo4jUploader import Neo4jUploader

import uvicorn
import time



# Load environment variables from .env file
load_dotenv()


class Enhancement(BaseModel):
    clause_id: str  # e.g. "2/3/1"
    proposed_text: str  # New text to replace the clause
class QuestionRequest(BaseModel):
    question: str
    top_k: Optional[int] = 6
    temperature: Optional[float] = 0.1
    disable_enhancement: Optional[bool] = False
    source: Optional[str] = "law"  # NEW: add this line

class EnhanceResponse(BaseModel):
    original_question: str
    enhanced_question: str


class EnhanceStandardRequest(BaseModel):
    standard_name: str  # <-- changed this line
    enhancements: List[Enhancement]


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


# Fetch law clauses only (no LLM involved)
@app.post("/api/fetch-clauses")
def fetch_clauses(request: QuestionRequest):
    if not request.question or len(request.question.strip()) < 3:
        raise HTTPException(status_code=400, detail="Question must be at least 3 characters long")
    try:
        clauses = query_law_clauses(request.question, top_k=request.top_k)
        return {"clauses": clauses}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying clauses: {str(e)}")


# Run legal expert agent (Gemini + clauses)
@app.post("/api/legal-expert", response_model=AnswerResponse)
def legal_expert(
    request: QuestionRequest,
    llm=Depends(get_llm)
):
    start_time = time.time()

    if not request.question or len(request.question.strip()) < 3:
        raise HTTPException(status_code=400, detail="Question must be at least 3 characters long")

    try:
        answer = ask_compliance_question_law(request.question, llm, top_k=request.top_k)
        return {
            "answer": answer,
            "processing_time": time.time() - start_time,
            "enhanced_query": None  # You can add enhancement later if needed
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Legal expert failed: {str(e)}")


# === Standards Search Endpoint ===
@app.post("/api/fetch-standards")
def fetch_standard_clauses(request: QuestionRequest):
    if not request.question or len(request.question.strip()) < 3:
        raise HTTPException(status_code=400, detail="Question must be at least 3 characters long")
    try:
        results = query_standard_clauses(request.question, top_k=request.top_k)
        return {"clauses": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying standards: {str(e)}")


@app.post("/api/fetch")
def fetch_clauses_or_standards(request: QuestionRequest):
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "your_password")

    uploader = Neo4jUploader(uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASSWORD)
    if not request.question or len(request.question.strip()) < 3:
        raise HTTPException(status_code=400, detail="Question must be at least 3 characters long")

    source = request.source.lower()

    try:
        if source == "legal":
            clauses = query_law_clauses(request.question, top_k=request.top_k)
        elif source == "finance":
            clauses = query_standard_clauses(request.question, top_k=request.top_k)
        elif source == "shariah":
            clauses = uploader.search_all_sources_by_text(request.question, top_k=request.top_k)
            normalized_response = normalize_clauses({
                "source": source,
                "clauses": clauses
            })
            return normalized_response
        else:   
            raise HTTPException(status_code=400, detail="Invalid source. Use 'law', 'standard', or 'shari3a'.")


        return {
            "source": source,
            "clauses": clauses
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying {source} clauses: {str(e)}")


def normalize_clauses(raw_response):
    normalized = {"source": raw_response["source"], "clauses": []}

    for clause in raw_response["clauses"]:
        source_type = clause.get("source_type", "Unknown")
        score = clause.get("similarity_score", 0.0)

        if source_type == "QuranVerse":
            verse_number = clause.get("verse_number", "unknown")
            clause_id = f"Quran_{verse_number}"
            text = clause.get("text_english", clause.get("text_content", ""))
        elif source_type == "Hadith":
            # Add logic to extract proper Hadith ID if you have it
            clause_id = clause.get("hadith_id", "Hadith_Unknown")
            text = clause.get("text_content", "")
        else:
            # Default document chunk format
            metadata = clause.get("extra_metadata", "{}")
            file_name = "unknown"
            page_number = clause.get("page_number", "0")
            try:
                metadata_dict = json.loads(metadata)
                file_name = metadata_dict.get("file_name", "").replace(".pdf", "")
            except Exception:
                pass
            clause_id = f"doc_{file_name}_{page_number}"
            text = clause.get("text_content", "")

        normalized["clauses"].append({
            "id": clause_id,
            "text": text.strip(),
            "score": round(score, 2),
            "source_type": source_type
        })

    return normalized

from fastapi.responses import FileResponse

STANDARD_FILES = {
    "musharaka": "Musharaka.PDF",
    "istisna": "FINANC_1_Istisna’a and Parallel Istisna’a (10).PDF",
    "murabahah": "SS8 - Murabahah - revised standard.pdf",
    "ijarah": "SS9 - Ijarah and Ijarah Muntahia Bittamleek - revised standard.pdf",
    "salam": "SS10 - Salam and Parallel Salam - revised standard.pdf",
}

@app.post("/api/generate-enhanced-pdf")
def generate_enhanced_pdf(request: EnhanceStandardRequest):
    try:
        # Use the standard file from your local path
        standard_filename = STANDARD_FILES.get(request.standard_name.lower())
        print(standard_filename)

        original_pdf_path = os.path.join("/home/boba/Desktop/isdbi/data/standards/", standard_filename)
        if not os.path.exists(original_pdf_path):
            raise HTTPException(status_code=404, detail="Original standard PDF not found")

        # Set the output path
        output_dir = "output/standards"
        os.makedirs(output_dir, exist_ok=True)
        output_pdf_path = os.path.join(output_dir, f"enhanced_{standard_filename}".replace(".pdf", ""))

        # Call the enhancement function
        generate_updated_standard_pdf(
            original_pdf_path=original_pdf_path,
            enhancements=[e.dict() for e in request.enhancements],
            output_path=output_pdf_path
        )

        # Return file
        return FileResponse(f"{output_pdf_path}.pdf", filename=f"Enhanced_{standard_filename}", media_type="application/pdf")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate enhanced PDF: {str(e)}")



class AgentRoutingRequest(BaseModel):
    query: str

class AgentRoutingResponse(BaseModel):
    selected_agent: str


@app.post("/api/route-agent", response_model=AgentRoutingResponse)
def route_agent_handler(
    request: AgentRoutingRequest,
    llm=Depends(get_llm)
):
    """
    Routes the input query to the appropriate AI agent:
    - challenge_1
    - challenge_2
    - compliance_checker
    - advisor
    - none
    """

    if not request.query or len(request.query.strip()) < 3:
        raise HTTPException(status_code=400, detail="Query must be at least 3 characters long")

    try:
        selected_agent = route_to_specialized_agent(request.query, llm)
        return AgentRoutingResponse(selected_agent=selected_agent)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Routing agent failed: {str(e)}")



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

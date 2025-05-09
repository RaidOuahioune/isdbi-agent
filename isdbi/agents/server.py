from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import uvicorn

import enhancement
from components.agents import transaction_analyzer, use_case_processor

app = FastAPI(title="Islamic Finance Standards API",
              description="API for Islamic Finance Standards processing and analysis",
              version="1.0.0")

class AgentRequest(BaseModel):
    prompt: str
    task: str
    options: Optional[Dict[str, Any]] = {}

class AgentResponse(BaseModel):
    result: Dict[str, Any]
    task: str
    execution_time: float
    status: str = "success"

@app.post("/api/agent", response_model=AgentResponse)
async def process_agent_request(request: AgentRequest = Body(...)):
    """
    Process a request using the appropriate Islamic finance agent based on the task.
    
    Available tasks:
    - enhance_standard: Enhance AAOIFI standards for modern scenarios
    - analyze_transaction: Analyze Islamic finance transactions
    - process_use_case: Generate accounting guidance for Islamic finance use cases
    
    Returns the agent's response with execution details.
    """
    import time
    start_time = time.time()
    result = {}
    
    try:
        if request.task == "enhance_standard":
            # Extract standard_id and trigger_scenario from the prompt or options
            standard_id = request.options.get("standard_id", None)
            trigger_scenario = request.prompt
            
            # If standard_id not provided in options, try to find from test cases
            if not standard_id:
                # Try to find a matching test case based on keywords in the prompt
                test_case = enhancement.find_test_case_by_keyword(request.prompt)
                standard_id = test_case["standard_id"]
            
            # Include cross-standard analysis based on options
            include_cross = request.options.get("include_cross_standard_analysis", True)
            
            # Run the enhancement process
            result = enhancement.run_standards_enhancement(
                standard_id=standard_id, 
                trigger_scenario=trigger_scenario,
                include_cross_standard_analysis=include_cross
            )
            
            # Format the results for better display if needed
            result["formatted_output"] = enhancement.format_results_for_display(result)
            
        elif request.task == "analyze_transaction":
            # Process transaction analysis request
            analysis_result = transaction_analyzer.analyze_transaction(request.prompt)
            
            # Get the identified standards
            standards = analysis_result.get("identified_standards", [])
            
            result = {
                "analysis": analysis_result.get("analysis", ""),
                "identified_standards": standards,
                "full_result": analysis_result
            }
            
        elif request.task == "process_use_case":
            # Process use case request
            use_case_result = use_case_processor.process_use_case(request.prompt)
            
            result = {
                "accounting_guidance": use_case_result.get("accounting_guidance", ""),
                "full_result": use_case_result
            }
            
        else:
            raise HTTPException(status_code=400, detail=f"Unknown task: {request.task}")
            
    except Exception as e:
        return {
            "result": {"error": str(e)},
            "task": request.task,
            "execution_time": time.time() - start_time,
            "status": "error"
        }
    
    return {
        "result": result,
        "task": request.task,
        "execution_time": time.time() - start_time,
        "status": "success"
    }

@app.get("/")
async def root():
    return {
        "message": "Islamic Finance Standards API",
        "version": "1.0.0",
        "endpoints": [
            "/api/agent - Main endpoint for agent processing",
            "/ - This help message"
        ],
        "available_tasks": [
            "enhance_standard",
            "analyze_transaction",
            "process_use_case"
        ]
    }

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True, timeout_keep_alive=60)
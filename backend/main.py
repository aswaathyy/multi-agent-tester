from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

import os
from pathlib import Path

from models import PlanRequest, TestPlan, TestReport
from agents.orchestrator import OrchestratorAgent
from agents.planner import PlannerAgent

app = FastAPI(title="Multi-Agent Game Tester", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator
orchestrator = OrchestratorAgent()

# Global storage for demo (in production, use a database)
current_report = None

@app.get("/")
async def root():
    """Serve the frontend"""
    frontend_path = Path(__file__).parent.parent / "frontend" / "index.html"
    if frontend_path.exists():
        with open(frontend_path, "r") as f:
            return HTMLResponse(content=f.read())
    return {
        "message": "Multi-Agent Game Tester API",
        "endpoints": ["/docs", "/plan", "/execute", "/report"]
    }

@app.post("/plan")
async def generate_plan(request: PlanRequest) -> TestPlan:
    """Generate a test plan"""
    try:
        planner = PlannerAgent()
        plan = await planner.generate_plan(request)
        return plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate plan: {str(e)}")

@app.post("/execute")
async def execute_tests(request: PlanRequest) -> TestReport:
    """Execute complete testing workflow"""
    global current_report
    try:
        report = await orchestrator.run_complete_workflow(
            target_url=request.target_url,
            num_cases=request.num_test_cases,
            top_n=10  # Always execute top 10
        )
        current_report = report
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test execution failed: {str(e)}")

@app.get("/report")
async def get_latest_report() -> TestReport:
    """Get the latest test report"""
    global current_report
    if current_report is None:
        raise HTTPException(status_code=404, detail="No test report available")
    return current_report

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Multi-Agent Game Tester is running"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
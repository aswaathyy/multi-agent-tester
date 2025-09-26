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
        if not request.target_url:
            raise ValueError("Target URL is required")
            
        report = await orchestrator.run_complete_workflow(
            target_url=request.target_url,
            num_cases=request.num_test_cases,
            top_n=10  # Always execute top 10
        )
        
        if not report:
            raise ValueError("No test report generated")
            
        current_report = report
        return report
    except Exception as e:
        print(f"Execution error: {str(e)}")  # Log the error
        raise HTTPException(status_code=500, detail=f"Test execution failed: {str(e)}")

@app.get("/report")
async def get_latest_report() -> TestReport:
    """Get the latest test report"""
    global current_report
    if current_report is None:
        raise HTTPException(status_code=404, detail="No test report available")
    return current_report

@app.post("/rank")
async def rank_test_cases(test_plan: TestPlan) -> TestPlan:
    """Rank test cases in the test plan"""
    try:
        ranker = orchestrator.ranker
        top_cases = ranker.rank_and_select(test_plan, top_n=len(test_plan.test_cases))
        test_plan.test_cases = top_cases
        return test_plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to rank test cases: {str(e)}")

@app.post("/analyze")
async def analyze_results(report: TestReport):
    """Analyze test results and provide insights"""
    try:
        from agents.analyzer import AnalyzerAgent
        analyzer = AnalyzerAgent()
        analysis = analyzer.analyze_results(report.execution_results)
        
        # Calculate quality score based on pass rate and performance
        total_tests = len(report.execution_results)
        passed = sum(1 for r in report.execution_results if r.status == "passed")
        pass_rate = (passed / total_tests) * 100 if total_tests > 0 else 0
        
        # Quality score formula: 70% pass rate + 30% performance
        avg_duration = sum(r.execution_time for r in report.execution_results) / total_tests if total_tests > 0 else 0
        perf_score = max(0, 100 - (avg_duration * 5))  # Lower duration = better score
        quality_score = (pass_rate * 0.7) + (perf_score * 0.3)
        
        # Add scores to analysis
        analysis["quality_score"] = round(quality_score, 2)
        analysis["pass_rate"] = round(pass_rate, 2)
        analysis["performance_score"] = round(perf_score, 2)
        
        # Add recommendations
        recommendations = []
        if pass_rate < 80:
            recommendations.append("Improve test case reliability")
        if avg_duration > 5:
            recommendations.append("Optimize test execution speed")
        if total_tests < 5:
            recommendations.append("Increase test coverage")
        analysis["recommendations"] = recommendations
        
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Multi-Agent Game Tester is running"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
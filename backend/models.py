from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class TestCaseStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class TestCase(BaseModel):
    id: str
    name: str
    description: str
    steps: List[str]
    expected_results: List[str]
    priority: str = "medium"
    rank_score: float = 0.0
    created_at: Optional[datetime] = None

    def __init__(self, **data):
        if data.get("created_at") is None:
            data["created_at"] = datetime.now()
        super().__init__(**data)

class TestPlan(BaseModel):
    id: str
    name: str
    test_cases: List[TestCase]
    total_cases: int
    created_at: Optional[datetime] = None

    def __init__(self, **data):
        if data.get("created_at") is None:
            data["created_at"] = datetime.now()
        super().__init__(**data)

class ExecutionResult(BaseModel):
    test_case_id: str
    status: TestCaseStatus
    execution_time: float
    artifacts: List[str] = []
    screenshots: List[str] = []
    logs: List[str] = []
    error_message: Optional[str] = None
    cross_agent_validated: bool = False

class TestReport(BaseModel):
    id: str
    plan_id: str
    execution_results: List[ExecutionResult]
    total_tests: int
    passed_tests: int
    failed_tests: int
    execution_duration: float
    summary: Dict[str, Any] = {}
    triage_notes: List[str] = []
    created_at: Optional[datetime] = None

    def __init__(self, **data):
        if data.get("created_at") is None:
            data["created_at"] = datetime.now()
        super().__init__(**data)

class PlanRequest(BaseModel):
    target_url: str = "https://play.ezygamers.com/"
    num_test_cases: int = 20

class ExecutionRequest(BaseModel):
    plan_id: str
    max_tests: int = 10
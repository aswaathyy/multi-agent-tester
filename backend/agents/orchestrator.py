import json
from datetime import datetime
from typing import List
from pathlib import Path

from models import TestPlan, TestCase, ExecutionResult, TestReport, PlanRequest
from agents.planner import PlannerAgent
from agents.ranker import RankerAgent
from agents.executor import ExecutorAgent

class OrchestratorAgent:
    """Orchestrates the entire testing workflow"""

    def __init__(self):
        self.planner = PlannerAgent()
        self.ranker = RankerAgent()
        self.executor = ExecutorAgent()
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(exist_ok=True)

    async def run_complete_workflow(self, target_url: str, num_cases: int = 20, top_n: int = 10) -> TestReport:
        """Run the complete testing workflow"""

        print(f"Starting test workflow for {target_url}")
        print(f"Generating {num_cases} test cases, executing top {top_n}")

        # Step 1: Generate test plan
        print("Step 1: Generating test plan...")
        plan_request = PlanRequest(
            target_url=target_url,
            num_test_cases=num_cases,
            test_type="functional"
        )
        test_plan = await self.planner.generate_plan(plan_request)
        print(f"Generated {len(test_plan.test_cases)} test cases")

        # Step 2: Rank and select top test cases
        print("Step 2: Ranking and selecting test cases...")
        top_cases = self.ranker.rank_and_select(test_plan, top_n)
        print(f"Selected top {len(top_cases)} test cases")

        # Step 3: Execute selected test cases
        print("Step 3: Executing test cases...")
        execution_results = await self.executor.execute_tests(top_cases, target_url)
        print(f"Executed {len(execution_results)} test cases")

        # Step 4: Generate report
        print("Step 4: Generating report...")
        report = self._generate_report(test_plan, top_cases, execution_results)

        # Save report
        report_file = self.reports_dir / f"report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        with open(report_file, "w") as f:
            json.dump(report.dict(), f, indent=2)

        print(f"Workflow complete! Report saved to {report_file}")
        return report

    def _generate_report(
        self,
        test_plan: TestPlan,
        selected_cases: List[TestCase],
        execution_results: List[ExecutionResult]
    ) -> TestReport:
        """Generate comprehensive test report"""

        total_executed = len(execution_results)
        passed = sum(1 for r in execution_results if r.status == "passed")
        failed = total_executed - passed
        avg_duration = (
            sum(r.duration for r in execution_results) / total_executed
            if total_executed > 0 else 0
        )

        summary = {
            "total_generated": len(test_plan.test_cases),
            "total_selected": len(selected_cases),
            "total_executed": total_executed,
            "passed": passed,
            "failed": failed,
            "average_duration": avg_duration,
            "pass_rate": (passed / total_executed * 100) if total_executed > 0 else 0,
        }

        test_cases_with_results = []
        for case in selected_cases:
            result = next((r for r in execution_results if r.test_case_id == case.id), None)
            test_cases_with_results.append({
                "test_case": case,
                "execution_result": result
            })

        report = TestReport(
            id=f"report-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            timestamp=datetime.now().isoformat(),
            target_url=test_plan.test_cases[0].name if test_plan.test_cases else "unknown",  # Hack for demo
            summary=summary,
            test_plan=test_plan,
            selected_cases=selected_cases,
            execution_results=execution_results
        )

        return report
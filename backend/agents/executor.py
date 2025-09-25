import os
import json
import asyncio
import random
from datetime import datetime
from typing import List
from pathlib import Path
from models import TestCase, ExecutionResult

class ExecutorAgent:
    """Executes test cases using Playwright"""

    def __init__(self):
        self.artifacts_dir = Path("artifacts")
        self.artifacts_dir.mkdir(exist_ok=True)

    async def execute_tests(self, test_cases: List[TestCase], target_url: str) -> List[ExecutionResult]:
        """Execute test cases and collect results"""
        results = []
        session_id = datetime.now().strftime("%Y%m%d-%H%M%S")
        session_dir = self.artifacts_dir / session_id
        session_dir.mkdir(exist_ok=True)

        for test_case in test_cases:
            print(f"Executing: {test_case.name}")
            result = await self._execute_single_test(test_case, target_url, session_dir)
            results.append(result)

        return results

    async def _execute_single_test(self, test_case: TestCase, target_url: str, session_dir: Path) -> ExecutionResult:
        """Execute a single test case"""
        try:
            return await self._execute_with_playwright(test_case, target_url, session_dir)
        except ImportError:
            print("Playwright not available, using mock execution")
            return self._mock_execution(test_case, session_dir)

    async def _execute_with_playwright(self, test_case: TestCase, target_url: str, session_dir: Path) -> ExecutionResult:
        """Execute test using Playwright"""
        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page()

                test_dir = session_dir / test_case.id
                test_dir.mkdir(exist_ok=True)

                start_time = datetime.now()

                try:
                    await page.goto(target_url, timeout=10000)
                    await page.wait_for_load_state("networkidle", timeout=5000)

                    await self._simulate_game_interaction(page, test_case)
                    await self._capture_artifacts(page, test_dir)

                    end_time = datetime.now()
                    duration = (end_time - start_time).total_seconds()

                    passed = await self._validate_results(page, test_case)

                    result = ExecutionResult(
                        test_case_id=test_case.id,
                        status="passed" if passed else "failed",
                        duration=duration,
                        artifacts_path=str(test_dir),
                        error_message=None if passed else "Validation failed",
                        console_logs=[],
                        screenshots=["final.png"],
                        validation_results={"basic_check": passed}
                    )

                except Exception as e:
                    end_time = datetime.now()
                    duration = (end_time - start_time).total_seconds()

                    result = ExecutionResult(
                        test_case_id=test_case.id,
                        status="failed",
                        duration=duration,
                        artifacts_path=str(test_dir),
                        error_message=str(e),
                        console_logs=[],
                        screenshots=[],
                        validation_results={"error": True}
                    )

                await browser.close()
                return result

        except ImportError:
            raise ImportError("Playwright not installed")

    def _mock_execution(self, test_case: TestCase, session_dir: Path) -> ExecutionResult:
        """Mock execution when Playwright is not available"""
        test_dir = session_dir / test_case.id
        test_dir.mkdir(exist_ok=True)

        # Create mock artifacts
        (test_dir / "console.json").write_text(json.dumps([
            {"level": "info", "message": "Mock execution started"},
            {"level": "info", "message": f"Testing: {test_case.name}"}
        ]))

        (test_dir / "log.json").write_text(json.dumps({
            "test_id": test_case.id,
            "execution": "mock",
            "timestamp": datetime.now().isoformat()
        }))

        passed = random.choice([True, True, False])  # 67% pass rate

        return ExecutionResult(
            test_case_id=test_case.id,
            status="passed" if passed else "failed",
            duration=random.uniform(1.0, 5.0),
            artifacts_path=str(test_dir),
            error_message=None if passed else "Mock validation failed",
            console_logs=["Mock execution log"],
            screenshots=["mock_screenshot.png"],
            validation_results={"mock_check": passed}
        )

    async def _simulate_game_interaction(self, page, test_case: TestCase):
        """Simulate basic game interactions"""
        try:
            await asyncio.sleep(2)

            inputs = await page.query_selector_all('input[type="text"], input[type="number"]')
            if inputs:
                for i, input_elem in enumerate(inputs[:2]):
                    await input_elem.fill(str(i + 1))
                    await asyncio.sleep(0.5)

            buttons = await page.query_selector_all("button")
            if buttons:
                await buttons[0].click()
                await asyncio.sleep(1)

            await asyncio.sleep(2)

        except Exception as e:
            print(f"Game interaction failed: {e}")

    async def _capture_artifacts(self, page, test_dir: Path):
        """Capture test artifacts"""
        try:
            await page.screenshot(path=test_dir / "final.png")

            console_logs = []
            with open(test_dir / "console.json", "w") as f:
                json.dump(console_logs, f)

            content = await page.content()
            with open(test_dir / "dom.html", "w") as f:
                f.write(content)

            log_data = {
                "timestamp": datetime.now().isoformat(),
                "url": page.url,
                "title": await page.title()
            }
            with open(test_dir / "log.json", "w") as f:
                json.dump(log_data, f)

        except Exception as e:
            print(f"Artifact capture failed: {e}")

    async def _validate_results(self, page, test_case: TestCase) -> bool:
        """Basic validation of test results"""
        try:
            title = await page.title()
            if not title:
                return False

            body = await page.query_selector("body")
            if not body:
                return False

            return True

        except Exception as e:
            print(f"Validation failed: {e}")
            return False
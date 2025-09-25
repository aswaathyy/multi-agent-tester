import uuid
import random
import asyncio
import ast
from typing import List, Dict, Any
from models import TestCase, TestPlan, PlanRequest

class MockLLM:
    """Mock LLM that returns predefined responses using LangChain structure"""

    def __init__(self):
        self.test_templates = [
            {
                "name": "Game Loading Verification",
                "description": "Verify the math puzzle game loads correctly and all UI elements are present",
                "steps": [
                    "Navigate to game URL",
                    "Wait for page load completion",
                    "Verify game board is visible",
                    "Check control buttons are clickable"
                ],
                "expected": [
                    "Page loads within 5 seconds",
                    "Game interface is fully rendered",
                    "No JavaScript errors in console"
                ],
                "priority": "high"
            },
            {
                "name": "Number Input Validation",
                "description": "Test various number inputs to ensure proper validation",
                "steps": [
                    "Click on input field",
                    "Enter valid numbers (1-9)",
                    "Enter invalid inputs (letters, symbols)",
                    "Submit each input"
                ],
                "expected": [
                    "Valid numbers are accepted",
                    "Invalid inputs show error messages",
                    "UI remains stable"
                ],
                "priority": "high"
            },
            {
                "name": "Mathematical Calculation Test",
                "description": "Verify that mathematical operations are calculated correctly",
                "steps": [
                    "Set up a math puzzle",
                    "Enter solution",
                    "Submit answer",
                    "Check score update"
                ],
                "expected": [
                    "Correct calculations are accepted",
                    "Score increases appropriately",
                    "Feedback is provided"
                ],
                "priority": "high"
            },
            {
                "name": "Game Reset Functionality",
                "description": "Test the game reset or new game functionality",
                "steps": [
                    "Start a game",
                    "Make some moves",
                    "Click reset/new game",
                    "Verify state"
                ],
                "expected": [
                    "Game state resets completely",
                    "Score resets to zero",
                    "New puzzle is generated"
                ],
                "priority": "medium"
            },
            {
                "name": "Timer Functionality Test",
                "description": "Test if the game has timer functionality and it works correctly",
                "steps": [
                    "Start game",
                    "Observe timer",
                    "Let timer run",
                    "Check behavior at time limits"
                ],
                "expected": [
                    "Timer counts appropriately",
                    "Time-based events trigger correctly",
                    "Timer resets with new game"
                ],
                "priority": "medium"
            },
            {
                "name": "Edge Case Large Numbers",
                "description": "Test game behavior with edge case inputs like very large numbers",
                "steps": [
                    "Enter maximum allowed number",
                    "Submit",
                    "Check processing",
                    "Verify response"
                ],
                "expected": [
                    "Large numbers handled gracefully",
                    "No overflow errors",
                    "Appropriate user feedback"
                ],
                "priority": "low"
            },
            {
                "name": "Mobile Responsiveness Test",
                "description": "Test game functionality on mobile viewport",
                "steps": [
                    "Resize browser to mobile size",
                    "Test touch interactions",
                    "Check UI scaling",
                    "Verify usability"
                ],
                "expected": [
                    "UI scales properly",
                    "Touch interactions work",
                    "All features accessible"
                ],
                "priority": "medium"
            },
            {
                "name": "Keyboard Navigation Test",
                "description": "Test game accessibility via keyboard navigation",
                "steps": [
                    "Use tab to navigate",
                    "Use enter to select",
                    "Use arrow keys if applicable",
                    "Test all interactive elements"
                ],
                "expected": [
                    "All elements are keyboard accessible",
                    "Focus indicators are visible",
                    "Navigation is logical"
                ],
                "priority": "low"
            }
        ]

    def invoke(self, input_dict: Dict[str, Any]) -> Dict[str, str]:
        """Mock LLM response based on input parameters"""
        num_cases = input_dict.get("num_cases", 5)
        selected_templates = self.test_templates[:min(num_cases, len(self.test_templates))]

        if num_cases > len(self.test_templates):
            remaining = num_cases - len(self.test_templates)
            for i in range(remaining):
                template = self.test_templates[i % len(self.test_templates)].copy()
                template["name"] += f" - Variation {i + 1}"
                selected_templates.append(template)

        return {"content": str(selected_templates)}

class PlannerAgent:
    """Generates test cases using LangChain-inspired framework without LLM calls"""

    def __init__(self):
        self.mock_llm = MockLLM()
        self.prompt_template = (
            "Generate {num_cases} test cases for testing the math puzzle game at {url}.\n"
            "For each test case, provide:\n"
            "1. Test name\n2. Description\n3. Steps to execute\n4. Expected results\n5. Priority (high/medium/low)\n"
            "Focus on: Game mechanics, Input validation, UI interactions, Scoring system, Edge cases\n"
            "Format as JSON array with fields: name, description, steps, expected_results, priority"
        )

    async def generate_plan(self, request: PlanRequest) -> TestPlan:
        """Generate a test plan with multiple test cases using LangChain-style approach"""
        try:
            response = await asyncio.to_thread(
                self.mock_llm.invoke,
                {"num_cases": request.num_test_cases, "url": request.target_url}
            )
            test_cases = self._parse_mock_response(response["content"], request.num_test_cases)
        except Exception as e:
            print(f"Mock LLM failed: {e}, using direct template approach")
            test_cases = self._generate_template_cases(request.num_test_cases)

        plan = TestPlan(
            id=str(uuid.uuid4()),
            name=f"Math Game Test Plan ({request.num_test_cases} cases)",
            test_cases=test_cases,
            total_cases=len(test_cases)
        )
        return plan

    def _parse_mock_response(self, response: str, num_cases: int) -> List[TestCase]:
        """Parse mock LLM response into test cases"""
        test_cases = []
        try:
            templates = ast.literal_eval(response)
            for i, template in enumerate(templates[:num_cases]):
                test_case = TestCase(
                    id=str(uuid.uuid4()),
                    name=template["name"],
                    description=template["description"],
                    steps=template["steps"],
                    expected_results=template["expected"],
                    priority=template["priority"],
                    rank_score=random.uniform(0.6, 1.0)
                )
                test_cases.append(test_case)
        except Exception as e:
            print(f"Failed to parse mock response: {e}")
            return self._generate_template_cases(num_cases)

        return test_cases

    def _generate_template_cases(self, num_cases: int) -> List[TestCase]:
        """Generate template-based test cases directly"""
        fallback_templates = self.mock_llm.test_templates
        test_cases = []

        for i in range(num_cases):
            template = fallback_templates[i % len(fallback_templates)]
            test_case = TestCase(
                id=str(uuid.uuid4()),
                name=f"{template['name']} #{i + 1}",
                description=template["description"],
                steps=template["steps"],
                expected_results=template["expected"],
                priority=template["priority"],
                rank_score=random.uniform(0.4, 0.9)
            )
            test_cases.append(test_case)

        return test_cases
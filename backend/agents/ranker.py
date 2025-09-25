from typing import List
from models import TestCase, TestPlan

class RankerAgent:
    """Ranks and selects top test cases"""

    def __init__(self):
        self.priority_weights = {
            "high": 1.0,
            "medium": 0.7,
            "low": 0.4
        }

    def rank_and_select(self, test_plan: TestPlan, top_n: int = 10) -> List[TestCase]:
        """Rank test cases and select top N"""

        # Calculate scores for each test case
        for test_case in test_plan.test_cases:
            priority_score = self.priority_weights.get(test_case.priority, 0.5)
            final_score = (test_case.rank_score * 0.7) + (priority_score * 0.3)
            test_case.rank_score = final_score

        # Sort by score and select top N
        sorted_cases = sorted(
            test_plan.test_cases,
            key=lambda x: x.rank_score,
            reverse=True
        )

        return sorted_cases[:top_n]
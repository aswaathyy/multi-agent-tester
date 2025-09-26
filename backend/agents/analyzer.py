from typing import List, Dict, Any
from models import ExecutionResult, TestReport

class AnalyzerAgent:
    """Analyzes test results and provides insights"""

    def __init__(self):
        pass

    def analyze_results(self, execution_results: List[ExecutionResult]) -> Dict[str, Any]:
        """Analyze execution results and provide insights"""

        if not execution_results:
            return {"error": "No results to analyze"}

        # Basic statistics
        total = len(execution_results)
        passed = sum(1 for r in execution_results if r.status == "passed")
        failed = total - passed

        # Duration analysis
        durations = [r.execution_time for r in execution_results]
        avg_duration = sum(durations) / len(durations)
        min_duration = min(durations)
        max_duration = max(durations)

        # Error analysis
        errors = [r.error_message for r in execution_results if r.error_message]
        error_types = {}

        for error in errors:
            if "timeout" in error.lower():
                error_types["timeout"] = error_types.get("timeout", 0) + 1
            elif "network" in error.lower():
                error_types["network"] = error_types.get("network", 0) + 1
            else:
                error_types["other"] = error_types.get("other", 0) + 1

        # Performance insights
        performance_insights = []
        if avg_duration > 10:
            performance_insights.append("Tests are running slowly (>10s average)")
        if max_duration > 30:
            performance_insights.append("Some tests are very slow (>30s)")

        # Reliability insights
        reliability_insights = []
        pass_rate = (passed / total) * 100
        if pass_rate < 70:
            reliability_insights.append("Low pass rate — investigate failures")
        if pass_rate > 95:
            reliability_insights.append("High pass rate — good stability")

        analysis = {
            "statistics": {
                "total_tests": total,
                "passed": passed,
                "failed": failed,
                "pass_rate": pass_rate,
            },
            "performance": {
                "average_duration": avg_duration,
                "min_duration": min_duration,
                "max_duration": max_duration,
            },
            "errors": {
                "total_errors": len(errors),
                "error_types": error_types,
            },
            "insights": {
                "performance": performance_insights,
                "reliability": reliability_insights,
            },
        }

        return analysis

    def generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis"""

        recommendations = []

        # Performance recommendations
        if analysis["performance"]["average_duration"] > 10:
            recommendations.append("Consider optimizing test execution speed")

        # Reliability recommendations
        pass_rate = analysis["statistics"]["pass_rate"]
        if pass_rate < 80:
            recommendations.append("Investigate failing tests to improve reliability")

        # Error-specific recommendations
        error_types = analysis["errors"]["error_types"]
        if error_types.get("timeout", 0) > 0:
            recommendations.append("Increase timeout values for slow operations")
        if error_types.get("network", 0) > 0:
            recommendations.append("Implement better network error handling")

        return recommendations
import streamlit as st
import requests

# Configuration
API_BASE_URL = "http://localhost:8000"

def main():
    st.set_page_config(page_title="Multi-Agent Game Tester", page_icon="🧪", layout="wide")
    st.title("Multi-Agent Game Tester POC")
    st.markdown("---")

    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        target_url = st.text_input(
            "Game URL",
            value="https://play.ezygamers.com/",
            help="URL of the math puzzle game to test"
        )
        num_test_cases = st.slider(
            "Number of Test Cases",
            min_value=1,
            max_value=20,
            value=5,
            help="Total number of test cases to generate"
        )

    st.subheader("LangChain Integration")
    st.info("Using LangChain framework\n❌ No actual LLM calls\n✅ Template-based generation")

    # Main content area
    col1, col2 = st.columns([1, 1])

    with col1:
        st.header("Planning Phase")
        if st.button("Generate Test Plan", type="primary", use_container_width=True):
            with st.spinner("Generating test plan using LangChain framework..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/plan",
                        json={"target_url": target_url, "num_test_cases": num_test_cases},
                        timeout=30
                    )
                    if response.status_code == 200:
                        plan_data = response.json()
                        st.session_state["test_plan"] = plan_data
                        st.success(f"✔ Generated {len(plan_data['test_cases'])} test cases!")

                        # Display plan summary
                        st.subheader("Test Plan Summary")
                        st.write(f"*Plan ID:* {plan_data['id']}")
                        st.write(f"*Total Cases:* {plan_data['total_cases']}")
                        st.write(f"*Name:* {plan_data['name']}")
                    else:
                        st.error(f"Failed to generate plan: {response.text}")
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to backend API. Make sure the FastAPI server is running on port 8000.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

        # Display generated test cases
        if "test_plan" in st.session_state:
            st.subheader("Generated Test Cases")
            plan = st.session_state["test_plan"]
            for i, test_case in enumerate(plan["test_cases"]):
                with st.expander(f"Test Case {i+1}: {test_case['name']}", expanded=False):
                    st.write(f"*Description:* {test_case['description']}")
                    st.write(f"*Priority:* {test_case['priority'].upper()}")
                    st.write(f"*Rank Score:* {test_case['rank_score']:.2f}")
                    st.write("*Steps:*")
                    for step_idx, step in enumerate(test_case["steps"], 1):
                        st.write(f"{step_idx}. {step}")
                    st.write("*Expected Results:*")
                    for result_idx, result in enumerate(test_case["expected_results"], 1):
                        st.write(f"{result_idx}. {result}")

    with col2:
        st.header("Execution Phase")

        # Ranking section
        if "test_plan" in st.session_state:
            if st.button("Rank Test Cases", use_container_width=True):
                with st.spinner("Ranking test cases..."):
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/rank",
                            json=st.session_state["test_plan"],
                            timeout=30
                        )
                        if response.status_code == 200:
                            ranked_data = response.json()
                            st.session_state["ranked_plan"] = ranked_data
                            st.success("✅ Test cases ranked successfully!")

                            # Show top ranked cases
                            st.subheader("Top Ranked Test Cases")
                            for i, test_case in enumerate(ranked_data["test_cases"][:5]):
                                st.write(f"{i+1}. *{test_case['name']}* (Score: {test_case['rank_score']:.2f})")
                        else:
                            st.error(f"Failed to rank test cases: {response.text}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

        # Execution section
        if "ranked_plan" in st.session_state:
            num_to_execute = st.slider("Number of top cases to execute", 1, 10, 3)
            if st.button("Execute Test Cases", use_container_width=True):
                with st.spinner(f"Executing top {num_to_execute} test cases..."):
                    try:
                        # Use the same request format as plan generation
                        response = requests.post(
                            f"{API_BASE_URL}/execute",
                            json={
                                "target_url": target_url,
                                "num_test_cases": num_to_execute
                            },
                            timeout=120
                        )
                        if response.status_code == 200:
                            results = response.json()
                            st.session_state["execution_results"] = results
                            st.success(f"✅ Executed {results['total_tests']} test cases!")

                            # Display execution summary
                            st.subheader("Execution Summary")
                            passed = results['passed_tests']
                            failed = results['failed_tests']
                            col_pass, col_fail = st.columns(2)
                            col_pass.metric("Passed", passed)
                            col_fail.metric("Failed", failed)
                        else:
                            st.error(f"Execution failed: {response.text}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        else:
            st.info("Generate a test plan first to enable execution options")

    # Results section
    if "execution_results" in st.session_state:
        st.markdown("---")
        st.header("Execution Results")
        results = st.session_state["execution_results"]

        tab1, tab2, tab3 = st.tabs(["Summary", "Detailed Results", "Artifacts"])

        with tab1:
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Executed", results["total_tests"])
            col2.metric("Passed", results["passed_tests"])
            col3.metric("Failed", results["failed_tests"])

            if results["total_tests"] > 0:
                pass_rate = results["passed_tests"] / results["total_tests"]
                st.progress(pass_rate, text=f"Pass Rate: {pass_rate:.1%}")

        with tab2:
            for i, result in enumerate(results["execution_results"]):
                status_emoji = "✅" if result["status"] == "passed" else "❌"
                with st.expander(f"{status_emoji} Test Case {result['test_case_id']}", expanded=False):
                    st.write(f"*Status:* {result['status'].upper()}")
                    st.write(f"*Duration:* {result.get('execution_time', 'N/A')} seconds")
                    if result.get("error_message"):
                        st.error(f"Error: {result['error_message']}")
                    if result.get("artifacts"):
                        st.write("*Artifacts Generated:*")
                        for artifact in result["artifacts"]:
                            st.write(f"- {artifact}")
                    if result.get("screenshots"):
                        st.write("*Screenshots:*")
                        for screenshot in result["screenshots"]:
                            st.write(f"- {screenshot}")
                    if result.get("logs"):
                        st.write("*Logs:*")
                        for log in result["logs"]:
                            st.write(f"- {log}")

        with tab3:
            st.info("Artifacts are stored in the backend/artifacts/ directory")

        # Generate report button
        if st.button("Generate Analysis Report", use_container_width=True):
            with st.spinner("Generating comprehensive analysis..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/analyze",
                        json={
                            "id": results["id"],
                            "plan_id": results["plan_id"],
                            "execution_results": results["execution_results"],
                            "total_tests": results["total_tests"],
                            "passed_tests": results["passed_tests"],
                            "failed_tests": results["failed_tests"],
                            "execution_duration": results["execution_duration"],
                            "summary": results.get("summary", {}),
                            "triage_notes": results.get("triage_notes", [])
                        },
                        timeout=60
                    )
                    if response.status_code == 200:
                        analysis = response.json()
                        st.success("✅ Analysis complete!")

                        st.subheader("Test Analysis")
                        quality_score = analysis.get('quality_score', 0)
                        st.metric("Overall Quality Score", f"{quality_score:.1f}%")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Pass Rate", f"{analysis.get('pass_rate', 0):.1f}%")
                        with col2:
                            st.metric("Performance Score", f"{analysis.get('performance_score', 0):.1f}%")
                            
                        st.subheader("Insights & Recommendations")
                        if analysis.get('recommendations'):
                            for rec in analysis['recommendations']:
                                st.info(f"💡 {rec}")
                        else:
                            st.info("No specific recommendations at this time.")
                    else:
                        st.error(f"Analysis failed: {response.text}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; font-size: 0.8em;'>
        Multi-Agent Game Tester POC | Built with LangChain Framework (No LLM) + Streamlit + FastAPI
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
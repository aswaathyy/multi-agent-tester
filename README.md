# multi-agent-tester
#### A 5-day proof-of-concept project demonstrating a multi-agent testing system for a web-based number/math puzzle game: EzyGamers Puzzle Game. This system leverages LangChain for intelligent planning and FastAPI for backend orchestration, with a minimal frontend UI for triggering tests and viewing reports.
## Project Overview
#### This POC showcases a multi-agent architecture that automates test case generation, ranking, execution, and validation for a puzzle game. It captures detailed artifacts and produces a comprehensive test report.
## Key Features
#### * PlannerAgent: Generates 20+ candidate test cases using LangChain.
#### * RankerAgent: Scores and selects the top 10 test cases.
#### * ExecutorAgents: Executes selected tests in parallel, coordinated by an OrchestratorAgent.
#### * Artifact Capture: Screenshots, DOM snapshots, console logs, and network traces.
#### * AnalyzerAgent: Validates results using repeat runs and cross-agent checks.
#### * Reporting: Outputs a JSON report with verdicts, evidence, reproducibility stats, and triage notes.

## Tech Stack
#### * Backend: FastAPI
#### * Frontend: Minimal UI (HTML/JS)
#### * Agents & Planning: LangChain
#### * Automation & Execution: Playwright (or Selenium)
#### * Reporting: JSON + UI viewer

## Installation
#### git clone https://github.com/multi-agent-game-tester.git
#### cd multi-agent-game-tester
#### pip install -r requirements.txt

## Running the App
#### Start backend
uvicorn app.main:app --reload
#### Access frontend
open http://localhost:8000

## Demo
#### * Test plan generation
#### * Execution of top 3 (with mention of top 10)
#### * Sample report with captured artifacts

## Deliverable
#### Public GitHub repository 

## License
#### MIT License

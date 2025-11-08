from fastapi import FastAPI
from orchestrator.orchestrator import Orchestrator
from teams.team import Team
from agents.agent import Agent

app = FastAPI()
orch = Orchestrator()

@app.post("/create_team")
async def create_team(team_name: str, planner_model: str, manager_model: str, worker_models: list[str]):
    planner = Agent("Planner", planner_model)
    manager = Agent("Manager", manager_model)
    workers = [Agent(f"Worker{i+1}", m) for i, m in enumerate(worker_models)]
    team = Team(team_name, planner, manager, workers)
    orch.add_team(team)
    return {"message": f"Team {team_name} created"}

@app.get("/run_project")
async def run_project(task: str):
    results = await orch.run_project(task)
    return results

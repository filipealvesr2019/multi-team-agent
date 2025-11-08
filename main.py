from fastapi import FastAPI
from orchestrator.orchestrator import Orchestrator
from teams.teams import Team
from agents.agent import Agent
import asyncio

app = FastAPI()
orch = Orchestrator()

# Criando times simulados
@app.on_event("startup")
async def startup_event():
    planner = Agent("Alice", "openai", "gpt-4")
    manager = Agent("Bob", "anthropic", "claude-v1")
    workers = [Agent("Carol", "openai", "gpt-3.5"), Agent("Dave", "openai", "gpt-3.5")]
    team = Team("Frontend", planner, manager, workers)
    orch.add_team(team)

@app.get("/run")
async def run_project():
    results = await orch.run_project("Criar app de delivery")
    return results

from fastapi import FastAPI
from orchestrator.orchestrator import Orchestrator
from teams.team import Team
from agents.agent import Agent
import asyncio

app = FastAPI()
orch = Orchestrator()

# Criando times simulados no startup
@app.on_event("startup")
async def startup_event():
    # Time Frontend
    frontend_planner = Agent("Alice", "openai", "gpt-4")
    frontend_manager = Agent("Bob", "anthropic", "claude-v1")
    frontend_workers = [
        Agent("Carol", "openai", "gpt-3.5"),
        Agent("Dave", "openai", "gpt-3.5")
    ]
    frontend_team = Team("Frontend", frontend_planner, frontend_manager, frontend_workers)
    orch.add_team(frontend_team)

    # Time Backend
    backend_planner = Agent("Eve", "openai", "gpt-4")
    backend_manager = Agent("Frank", "anthropic", "claude-v1")
    backend_workers = [
        Agent("Grace", "openai", "gpt-3.5"),
        Agent("Heidi", "openai", "gpt-3.5")
    ]
    backend_team = Team("Backend", backend_planner, backend_manager, backend_workers)
    orch.add_team(backend_team)

# Endpoint para rodar todos os projetos em paralelo
@app.get("/run_all")
async def run_all_projects():
    tasks = [team.execute("Criar app de delivery") for team in orch.teams]
    results = await asyncio.gather(*tasks)
    return results

# Endpoint para rodar um projeto específico (o primeiro time, por exemplo)
@app.get("/run")
async def run_project():
    if not orch.teams:
        return {"error": "Nenhum time disponível"}
    results = await orch.teams[0].execute("Criar app de delivery")
    return results

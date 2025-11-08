from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from orchestrator.orchestrator import Orchestrator
from teams.team import Team
from agents.agent import Agent

app = FastAPI()

# Estrutura para armazenar projetos por usuário
# { "user_id_123": { "project_name": Orchestrator, ... }, ... }
user_projects = {}

# -------------------------
# Modelos de entrada
# -------------------------
class AgentInput(BaseModel):
    name: str
    model_name: str

class TeamInput(BaseModel):
    name: str
    planner: AgentInput
    manager: AgentInput
    workers: List[AgentInput]

class ProjectInput(BaseModel):
    user_id: str
    project_name: str
    teams: List[TeamInput]

# -------------------------
# Criar projeto para usuário
# -------------------------
@app.post("/create_project")
async def create_project(data: ProjectInput):
    orch = Orchestrator()
    
    # Cria times e agentes para o projeto
    for t in data.teams:
        planner = Agent(t.planner.name, t.planner.model_name)
        manager = Agent(t.manager.name, t.manager.model_name)
        workers = [Agent(w.name, w.model_name) for w in t.workers]
        team = Team(t.name, planner, manager, workers)
        orch.add_team(team)
    
    # Cria dict do usuário se não existir
    if data.user_id not in user_projects:
        user_projects[data.user_id] = {}
    
    # Armazena projeto do usuário
    user_projects[data.user_id][data.project_name] = orch
    return {"message": f"Projeto {data.project_name} criado para usuário {data.user_id}"}

# -------------------------
# Rodar projeto
# -------------------------
@app.get("/run/{user_id}/{project_name}")
async def run_project(user_id: str, project_name: str):
    if user_id not in user_projects or project_name not in user_projects[user_id]:
        return {"error": "Projeto não encontrado"}
    
    orchestrator = user_projects[user_id][project_name]
    results = await orchestrator.run_project(f"Tarefa do {project_name}")
    return results

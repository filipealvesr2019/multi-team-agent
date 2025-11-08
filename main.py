from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from orchestrator.orchestrator import Orchestrator
from teams.team import Team
from agents.agent import Agent
from database.mongo import projects_collection

app = FastAPI()

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
# Criar projeto
# -------------------------
@app.post("/create_project")
async def create_project(data: ProjectInput):
    orch = Orchestrator()

    # Cria times com agentes reais
    teams_data = []
    for t in data.teams:
        planner = Agent(t.planner.name, t.planner.model_name)
        manager = Agent(t.manager.name, t.manager.model_name)
        workers = [Agent(w.name, w.model_name) for w in t.workers]
        team = Team(t.name, planner, manager, workers)
        orch.add_team(team)

        teams_data.append({
            "name": t.name,
            "planner": t.planner.model_name,
            "manager": t.manager.model_name,
            "workers": [w.model_name for w in t.workers]
        })

    # Salva projeto no MongoDB
    project_doc = {
        "user_id": data.user_id,
        "project_name": data.project_name,
        "teams": teams_data
    }
    await projects_collection.insert_one(project_doc)

    return {"message": f"Projeto {data.project_name} criado para usuário {data.user_id}"}

# -------------------------
# Rodar projeto
# -------------------------
@app.get("/run/{user_id}/{project_name}")
async def run_project(user_id: str, project_name: str):
    project = await projects_collection.find_one({"user_id": user_id, "project_name": project_name})
    if not project:
        return {"error": "Projeto não encontrado"}

    orch = Orchestrator()
    for t in project["teams"]:
        planner = Agent("Planner", t["planner"])
        manager = Agent("Manager", t["manager"])
        workers = [Agent(f"Worker{i+1}", w) for i, w in enumerate(t["workers"])]
        team = Team(t["name"], planner, manager, workers)
        orch.add_team(team)

    results = await orch.run_project(f"Tarefa do {project_name}")

    # Atualiza resultado no MongoDB
    await projects_collection.update_one(
        {"_id": project["_id"]},
        {"$set": {"last_result": results}}
    )

    return results

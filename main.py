from fastapi import FastAPI 
from pydantic import BaseModel
from typing import List
from agents.agent import Agent
from teams.team import Team
from orchestrator.orchestrator import Orchestrator
from database.mongo import projects_collection
from bson import ObjectId

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

class GlobalOrchestratorInput(BaseModel):
    name: str
    model_name: str

class ProjectInput(BaseModel):
    user_id: str
    project_name: str
    global_orchestrator: GlobalOrchestratorInput
    teams: List[TeamInput]

class PromptInput(BaseModel):
    prompt: str

# -------------------------
# Criar projeto
# -------------------------
@app.post("/create_project")
async def create_project(data: ProjectInput):
    global_orch_agent = {
        "name": data.global_orchestrator.name,
        "model_name": data.global_orchestrator.model_name
    }

    teams_data = []
    for t in data.teams:
        teams_data.append({
            "name": t.name,
            "planner": {"name": t.planner.name, "model_name": t.planner.model_name},
            "manager": {"name": t.manager.name, "model_name": t.manager.model_name},
            "workers": [{"name": w.name, "model_name": w.model_name} for w in t.workers]
        })

    project_doc = {
        "user_id": data.user_id,
        "project_name": data.project_name,
        "global_orchestrator": global_orch_agent,
        "teams": teams_data
    }

    result = await projects_collection.insert_one(project_doc)
    return {"message": f"Projeto {data.project_name} criado", "mongo_id": str(result.inserted_id)}

# -------------------------
# Enviar prompt
# -------------------------
@app.post("/prompt/{user_id}/{project_name}")
async def send_prompt(user_id: str, project_name: str, data: PromptInput):
    project = await projects_collection.find_one({"user_id": user_id, "project_name": project_name})
    if not project:
        return {"error": "Projeto não encontrado"}

    global_agent = None
    if "global_orchestrator" in project:
        g = project["global_orchestrator"]
        global_agent = Agent(g["name"], g["model_name"])

    teams_config = []
    for t in project["teams"]:
        planner = Agent(t["planner"]["name"], t["planner"]["model_name"])
        manager = Agent(t["manager"]["name"], t["manager"]["model_name"])
        workers = [Agent(w["name"], w["model_name"]) for w in t["workers"]]
        teams_config.append({
            "name": t["name"],
            "planner": planner,
            "manager": manager,
            "workers": workers
        })

    orch = Orchestrator(teams_config)
    if global_agent:
        orch.global_agent = global_agent

    results = await orch.run_project(data.prompt)

    await projects_collection.update_one(
        {"_id": ObjectId(project["_id"])},
        {"$set": {"last_prompt": data.prompt, "last_result": results}}
    )

    return {"prompt": data.prompt, "results": results}

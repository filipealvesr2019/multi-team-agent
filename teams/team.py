from fastapi import FastAPI
from teams.team import Team
from agents.agent import Agent

app = FastAPI()

# Criando agentes
planner = Agent("Planner")
manager = Agent("Manager")
workers = [Agent(f"Worker {i}") for i in range(3)]

# Criando um time
team_alpha = Team("Alpha", planner, manager, workers)

@app.get("/run")
async def run_team():
    result = await team_alpha.execute("Concluir projeto X")
    return result

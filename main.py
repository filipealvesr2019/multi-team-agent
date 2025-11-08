# main.py
from fastapi import FastAPI
from teams.team import Team  # seu import

app = FastAPI()

# Exemplo de endpoint simples para testar
@app.get("/")
async def root():
    # só para testar a classe Team
    dummy_team = Team("Time Teste", planner=None, manager=None, workers=[])
    return {"message": f"Team {dummy_team.name} importado com sucesso!"}

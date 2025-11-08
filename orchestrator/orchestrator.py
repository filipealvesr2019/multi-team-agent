from teams.team import Team

class Orchestrator:
    def __init__(self, teams_config: list):
        """Inicializa o orquestrador com uma lista de times vindos do banco de dados."""
        self.teams = []
        for t in teams_config:
            team = Team(
                name=t["name"],
                planner=t["planner"],
                manager=t["manager"],
                workers=t.get("workers", [])
            )
            self.teams.append(team)

    async def run_project(self, context: str):
        """Executa todos os times com o contexto fornecido."""
        results = []
        for team in self.teams:
            output = await team.execute(context)
            results.append({"team": team.name, "output": output})
        return results

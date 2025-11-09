from teams.team import Team

class Orchestrator:
    def __init__(self, teams_config: list):
        self.teams = [
            Team(
                name=t["name"],
                planner=t["planner"],
                manager=t["manager"],
                workers=t.get("workers", [])
            )
            for t in teams_config
        ]
        self.global_agent = None

    async def run_project(self, context: str):
        project_logs = []
        for team in self.teams:
            team_result = await team.execute(context)
            project_logs.append(team_result)
        return project_logs

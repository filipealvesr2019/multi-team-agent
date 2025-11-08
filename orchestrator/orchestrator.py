from teams.team import Team

class Orchestrator:
    def __init__(self):
        self.teams = []

    def add_team(self, team: Team):
        self.teams.append(team)

    async def run_project(self, context):
        results = []
        for team in self.teams:
            output = await team.execute(context)
            results.append(output)
        return results

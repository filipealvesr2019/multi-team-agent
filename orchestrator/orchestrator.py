class Orchestrator:
    def __init__(self):
        self.teams = []

    def add_team(self, team):
        self.teams.append(team)

    async def run_project(self, context):
        from asyncio import gather
        results = await gather(*(team.execute(context) for team in self.teams))
        return results

from teams.team import Team

class Orchestrator:
    def __init__(self, teams_config):
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

    async def run_project(self, user_prompt: str):
        print(f"\n🧠 [GLOBAL ORCHESTRATOR] recebendo prompt: {user_prompt}")

        orchestration = await self.global_agent.perform_task(
            f"Analise o objetivo: '{user_prompt}' e divida em instruções específicas para cada time."
        )

        instructions = orchestration["output"]
        print(f"\n📡 [GLOBAL ORCHESTRATOR] Instruções geradas:\n{instructions[:300]}...\n")

        project_logs = []
        for team in self.teams:
            print(f"\n➡️  [GLOBAL ORCHESTRATOR] enviando instrução ao time {team.name}...\n")
            team_result = await team.execute(f"Tarefa do time {team.name}: {instructions}")
            project_logs.append(team_result)

        print("\n🏁 [GLOBAL ORCHESTRATOR] Todos os times finalizaram. Consolidando resultados...\n")

        consolidated = await self.global_agent.perform_task(
            f"Consolide os seguintes resultados dos times e gere um resumo final:\n{project_logs}"
        )

        return {
            "global_plan": orchestration,
            "teams_results": project_logs,
            "final_summary": consolidated["output"]
        }

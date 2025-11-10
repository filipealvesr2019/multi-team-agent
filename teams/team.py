class Team:
    def __init__(self, name, planner, manager, workers):
        self.name = name
        self.planner = planner
        self.manager = manager
        self.workers = workers

    async def execute(self, context):
        print(f"\n🚀 [TEAM {self.name}] iniciando execução com contexto: {context}\n")

        logs = []

        plan = await self.planner.perform_task(f"Crie um plano técnico detalhado para: {context}")
        logs.append(plan)

        tasks = await self.manager.perform_task(f"Divida o plano a seguir em tarefas práticas para os workers:\n{plan['output']}")
        logs.append(tasks)

        worker_results = []
        for idx, w in enumerate(self.workers, start=1):
            print(f"⚙️  [Worker {idx}] executando tarefa...")
            task_prompt = f"Execute a seguinte tarefa prática:\n{tasks['output']}"
            result = await w.perform_task(task_prompt)
            worker_results.append(result)
            logs.append(result)

        team_output = {
            "team": self.name,
            "log": logs,
            "final_output": [r["output"] for r in worker_results]
        }

        print(f"✅ [TEAM {self.name}] finalizou execução com sucesso.\n")
        return team_output

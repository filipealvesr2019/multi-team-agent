class Team:
    def __init__(self, name, planner, manager, workers):
        self.name = name
        self.planner = planner
        self.manager = manager
        self.workers = workers

    async def execute(self, context):
        results = []
        # Planejador gera plano
        plan = await self.planner.perform_task(context)
        # Gerente divide tarefas
        tasks = await self.manager.perform_task(plan)
        # Workers executam tarefas
        for w in self.workers:
            result = await w.perform_task(tasks)
            results.append(result)
        return {"team": self.name, "output": results}

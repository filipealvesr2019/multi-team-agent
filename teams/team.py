# teams/team.py

class Team:
    def __init__(self, name, planner, manager, workers):
        self.name = name
        self.planner = planner
        self.manager = manager
        self.workers = workers

    async def execute(self, context):
        plan = await self.planner.generate(f"Plano para: {context}")
        tasks = await self.manager.generate(f"Divida em tarefas: {plan}")
        results = [await w.generate(f"Tarefa: {tasks}") for w in self.workers]
        return {"team": self.name, "output": results}

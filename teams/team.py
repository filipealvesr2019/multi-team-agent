class Team:
    def __init__(self, name, planner, manager, workers):
        self.name = name
        self.planner = planner
        self.manager = manager
        self.workers = workers

    async def execute(self, context):
        logs = []
        
        plan = await self.planner.perform_task(context)
        logs.append(plan)

        tasks = await self.manager.perform_task(plan["output"])
        logs.append(tasks)

        results = []
        for w in self.workers:
            result = await w.perform_task(tasks["output"])
            results.append(result)
            logs.append(result)

        return {
            "team": self.name,
            "log": logs,  # 🧠 todos os pensamentos e outputs
            "final_output": [r["output"] for r in results]
        }

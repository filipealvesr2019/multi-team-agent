class Team:
    def __init__(self, name, planner, manager, workers):
        self.name = name
        self.planner = planner
        self.manager = manager
        self.workers = workers

    async def execute(self, context):
        # Simulando execução de cada worker
        results = []
        for w in self.workers:
            result = await w.perform_task(context)  # supondo que Agent tenha perform_task
            results.append(result)
        return {"team": self.name, "output": results}

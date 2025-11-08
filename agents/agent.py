# agents/agent.py
class Agent:
    def __init__(self, name):
        self.name = name

    async def generate(self, prompt):
        # Simula uma resposta
        return f"{self.name} processou: {prompt}"

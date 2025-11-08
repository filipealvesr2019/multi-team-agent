import os
from dotenv import load_dotenv
import httpx

load_dotenv()

class Agent:
    def __init__(self, name, model_provider, model_name):
        self.name = name
        self.provider = model_provider
        self.model_name = model_name
        self.api_key = os.getenv(f"{model_provider.upper()}_API_KEY")

    async def generate(self, prompt: str):
        # Chamadas simuladas
        if self.provider.lower() == "openai":
            return await self._call_openai(prompt)
        elif self.provider.lower() == "anthropic":
            return await self._call_claude(prompt)
        return "Resposta simulada do agente local"

    async def _call_openai(self, prompt: str):
        # Placeholder: use httpx para chamadas reais
        return f"[OpenAI {self.model_name}] {prompt}"

    async def _call_claude(self, prompt: str):
        return f"[Claude {self.model_name}] {prompt}"

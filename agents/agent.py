import asyncio
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import model_info

class Agent:
    def __init__(self, name: str, model_name: str):
        self.name = name
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    def is_model_public(self) -> bool:
        try:
            model_info(self.model_name)
            return True
        except Exception as e:
            print(f"Erro verificando modelo: {e}")
            return False

    async def load_model(self):
        if self.model is None or self.tokenizer is None:
            if not self.is_model_public():
                raise ValueError(f"Modelo '{self.model_name}' não existe ou não é público!")

            print(f"[{self.name}] Carregando modelo '{self.model_name}'...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                device_map="auto" if torch.cuda.is_available() else None
            )
            print(f"[{self.name}] Modelo carregado com sucesso!")

    async def perform_task(self, prompt: str, max_tokens: int = 200) -> str:
        await self.load_model()

        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                do_sample=True,
                top_k=50,
                top_p=0.95
            )

        text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return f"[{self.model_name}] executando tarefa: {text}"

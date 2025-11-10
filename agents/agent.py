import asyncio
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import model_info, login
import os
from dotenv import load_dotenv
import datetime

load_dotenv()

class Agent:
    def __init__(self, name: str, model_name: str, role: str = None):
        self.name = name
        self.model_name = model_name
        self.role = role or "general"
        self.model = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.hf_token = os.getenv("HF_TOKEN")
        self.logs = []

        if self.hf_token:
            try:
                login(token=self.hf_token)
            except Exception:
                pass

    def is_model_public(self):
        try:
            model_info(self.model_name, token=self.hf_token)
            return True
        except Exception:
            return False

    async def load_model(self):
        if self.model is not None:
            return

        if not self.is_model_public():
            raise ValueError(f"Modelo '{self.model_name}' não encontrado!")

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, token=self.hf_token)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            token=self.hf_token,
            device_map="auto" if torch.cuda.is_available() else None
        )

    async def perform_task(self, prompt: str, max_tokens: int = 500):
        await self.load_model()
        start_time = datetime.datetime.utcnow().isoformat()

        # 🧠 Instrução permanente de contexto inteligente (MANUS IA style)
        system_instruction = f"""
Você é um agente dentro de um sistema colaborativo multiagente de IA.

Função:
- Compreender a intenção do usuário apenas pelo prompt.
- Se o pedido envolver desenvolvimento de software, gere **código funcional completo** (frontend, backend, API, banco de dados, etc.).
- Se for um pedido teórico ou textual, explique de forma clara e estruturada.
- Se for um planejamento, descreva o plano e as etapas práticas.
- Se for criativo, produza o conteúdo final.
- Sempre aja de acordo com o contexto e intenção, **sem depender de palavras-chave explícitas**.
"""

        full_prompt = f"{system_instruction}\n\nPedido do usuário:\n{prompt}"

        inputs = self.tokenizer(full_prompt, return_tensors="pt").to(self.device)
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                do_sample=True,
                top_k=50,
                top_p=0.9
            )

        text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        record = {
            "timestamp": start_time,
            "agent_name": self.name,
            "role": self.role,
            "model": self.model_name,
            "prompt": prompt,
            "output": text
        }

        self.logs.append(record)
        print(f"\n🧩 [{self.role.upper()}] {self.name} concluiu tarefa:\n{text[:250]}...\n")

        return record

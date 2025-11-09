import asyncio
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import model_info, login
import os
from dotenv import load_dotenv

# Carrega variáveis do .env, se existir
load_dotenv()

class Agent:
    def __init__(self, name: str, model_name: str):
        self.name = name
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.hf_token = os.getenv("HF_TOKEN")

        # 🔒 Faz login automaticamente no Hugging Face se houver token
        if self.hf_token:
            try:
                login(token=self.hf_token)
                print(f"[{self.name}] Autenticado no Hugging Face com sucesso.")
            except Exception as e:
                print(f"[{self.name}] Falha ao autenticar no Hugging Face: {e}")
        else:
            print(f"[{self.name}] Nenhum token HF encontrado. Modelos privados não poderão ser baixados.")

    def is_model_public(self) -> bool:
        """Verifica se o modelo existe e está acessível com o token atual."""
        try:
            model_info(self.model_name, token=self.hf_token)
            return True
        except Exception as e:
            print(f"[{self.name}] Erro verificando modelo: {e}")
            return False

    async def load_model(self):
        """Carrega o modelo e o tokenizer apenas uma vez."""
        if self.model is not None and self.tokenizer is not None:
            return  # já carregado

        if not self.is_model_public():
            raise ValueError(f"Modelo '{self.model_name}' não existe ou não é público!")

        print(f"[{self.name}] Carregando modelo '{self.model_name}'...")

        try:
            # ⚙️ Carrega o tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                token=self.hf_token
            )

            # ⚙️ Carrega o modelo
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                token=self.hf_token,
                device_map="auto" if torch.cuda.is_available() else None
            )

            print(f"[{self.name}] Modelo carregado com sucesso ({self.device}).")

        except Exception as e:
            print(f"[{self.name}] Erro ao carregar o modelo: {e}")
            raise

    async def perform_task(self, prompt: str, max_tokens: int = 200) -> str:
        """Executa o prompt e retorna o texto gerado."""
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
        return f"[{self.model_name}] executando tarefa:\n{text}"


# 🔹 Exemplo de uso rápido
if __name__ == "__main__":
    async def main():
        agent = Agent("Planner1", "google/gemma-3-1b-it")
        result = await agent.perform_task("Explique o que é aprendizado de máquina em poucas palavras.")
        print(result)

    asyncio.run(main())

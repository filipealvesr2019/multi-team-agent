import asyncio
import json
import os
from transformers import AutoTokenizer, AutoModelForCausalLM

# ========================
# Config
# ========================
HF_TOKEN = os.getenv("HUGGINGFACE_TOKEN")

# ========================
# Worker
# ========================
class Worker:
    def __init__(self, name, tokenizer, model, especialidade="genérico"):
        self.name = name
        self.especialidade = especialidade
        self.tokenizer = tokenizer
        self.model = model

    async def executar_tarefa(self, subtarefa):
        prompt = (
            f"Você é um especialista em {self.especialidade}. "
            f"Execute a subtarefa: '{subtarefa}' fornecendo código completo e funcional ou instruções detalhadas. "
            "Forneça a saída em markdown, identificando arquivos e seu conteúdo."
        )
        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(**inputs, max_new_tokens=600)
        resultado = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return resultado

# ========================
# Agente Humanizado
# ========================
class AgenteHumanizado:
    def __init__(self, model_name, num_workers=2):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, use_auth_token=HF_TOKEN)
        self.model = AutoModelForCausalLM.from_pretrained(model_name, use_auth_token=HF_TOKEN)
        self.workers = [Worker(f"Worker{i+1}", self.tokenizer, self.model) for i in range(num_workers)]
        self.historico = []

    async def planejar(self, tarefa):
        prompt = (
            f"Você é um planejador de tarefas. Recebeu a tarefa '{tarefa}'. "
            "Divida esta tarefa em subtarefas claras e organizáveis, passo a passo, como um checklist."
        )
        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(**inputs, max_new_tokens=300)
        resultado = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        subtarefas = [x.strip() for x in resultado.split("\n") if x.strip()]
        return subtarefas

    async def delegar_e_executar(self, subtarefa):
        worker = self.workers[hash(subtarefa) % len(self.workers)]
        return await worker.executar_tarefa(subtarefa)

    async def revisar(self, resultado, subtarefa):
        prompt = (
            f"Você é um revisor. Revise o resultado da subtarefa '{subtarefa}':\n{resultado}\n"
            "Se estiver correto, responda apenas {'aprovado': True}. "
            "Se precisar de correção, forneça {'aprovado': False, 'tarefa_corrigida': '...'}"
        )
        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(**inputs, max_new_tokens=200)
        resultado_revisao = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        try:
            feedback = json.loads(resultado_revisao.replace("'", "\""))
        except:
            feedback = {"aprovado": True, "tarefa_corrigida": subtarefa}
        return feedback

    async def executar_tarefa_completa(self, tarefa):
        subtarefas = await self.planejar(tarefa)
        resultado_final = ""
        for sub in subtarefas:
            aprovado = False
            resultado = None
            while not aprovado:
                resultado = await self.delegar_e_executar(sub)
                feedback = await self.revisar(resultado, sub)
                aprovado = feedback.get("aprovado", True)
                if not aprovado:
                    sub = feedback["tarefa_corrigida"]
            self.historico.append({
                "subtarefa": sub,
                "resultado": resultado,
                "feedback": feedback
            })
            resultado_final += resultado + "\n\n"
        return resultado_final

# ========================
# Exemplo de uso
# ========================
async def main():
    MODEL = "google/gemma-3-1b-it"
    agente = AgenteHumanizado(MODEL)

    prompt_usuario = (
        "Crie um sistema completo de login com React no frontend e API em Python no backend, "
        "incluindo validação de usuários, armazenamento seguro de senhas e autenticação JWT. "
        "Forneça o código pronto para rodar."
    )

    resultado_final = await agente.executar_tarefa_completa(prompt_usuario)

    # Resultado final consolidado
    print("\n=== RESULTADO FINAL ===\n")
    print(resultado_final)

    # Histórico detalhado (opcional)
    print("\n=== HISTÓRICO DETALHADO ===\n")
    print(json.dumps(agente.historico, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())

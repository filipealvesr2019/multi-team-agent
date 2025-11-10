import asyncio
import json
import os
from dotenv import load_dotenv
from transformers import AutoTokenizer, AutoModelForCausalLM

# ========================
# Config dotenv
# ========================
load_dotenv()
HF_TOKEN = os.getenv("HUGGINGFACE_TOKEN")

# ========================
# Funções de prompt
# ========================
def criar_prompt_planejador(tarefa):
    return (
        f"Você é um planejador de tarefas. Recebeu a tarefa '{tarefa}'. "
        "Divida esta tarefa em subtarefas claras e organizáveis. "
        "Responda como uma lista de subtarefas, uma por linha."
    )

def criar_prompt_worker(subtarefa, especialidade="genérico"):
    return f"Você é um especialista em {especialidade}. Execute a subtarefa: {subtarefa}. Forneça o resultado claro."

def criar_prompt_revisor(resultados, subtarefa):
    return (
        f"Você é um revisor. Revise os resultados da subtarefa '{subtarefa}':\n"
        f"{resultados}\n"
        "Indique se está aprovado. Se não, forneça uma versão corrigida. "
        "Responda em JSON: {\"aprovado\": True/False, \"tarefa_corrigida\": \"...\"}"
    )

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
        prompt = criar_prompt_worker(subtarefa, self.especialidade)
        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(**inputs, max_new_tokens=200)
        resultado = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"[Worker {self.name}] Resultado: {resultado}")
        return resultado

# ========================
# Agente Generalista
# ========================
class AgenteGeneralista:
    def __init__(self, model_name, num_workers=4):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, use_auth_token=HF_TOKEN)
        self.model = AutoModelForCausalLM.from_pretrained(model_name, use_auth_token=HF_TOKEN)
        self.workers = [Worker(f"Worker{i+1}", self.tokenizer, self.model) for i in range(num_workers)]
        self.historico = []

    async def planejar(self, tarefa):
        prompt = criar_prompt_planejador(tarefa)
        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(**inputs, max_new_tokens=200)
        resultado = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        subtarefas = [x.strip() for x in resultado.split("\n") if x.strip()]
        print(f"[Planejador] Subtarefas: {subtarefas}")
        return subtarefas

    async def delegar_e_executar(self, subtarefa):
        worker = self.workers[hash(subtarefa) % len(self.workers)]
        return await worker.executar_tarefa(subtarefa)

    async def revisar(self, resultado, subtarefa):
        prompt = criar_prompt_revisor(resultado, subtarefa)
        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(**inputs, max_new_tokens=200)
        resultado_revisao = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"[Revisor] Feedback: {resultado_revisao}")
        try:
            feedback = json.loads(resultado_revisao.replace("'", "\""))
        except:
            feedback = {"aprovado": True, "tarefa_corrigida": subtarefa}
        return feedback

    async def executar_tarefa_completa(self, tarefa):
        subtarefas = await self.planejar(tarefa)

        async def executar_sub(sub):
            resultado = await self.delegar_e_executar(sub)
            feedback = await self.revisar(resultado, sub)

            while not feedback.get("aprovado", True):
                print(f"[Refatorando] {sub}")
                resultado = await self.delegar_e_executar(feedback["tarefa_corrigida"])
                feedback = await self.revisar(resultado, feedback["tarefa_corrigida"])

            self.historico.append({
                "subtarefa": sub,
                "resultado": resultado,
                "feedback": feedback
            })
            return resultado

        resultados_finais = await asyncio.gather(*(executar_sub(sub) for sub in subtarefas))
        return "\n".join(resultados_finais)

# ========================
# Exemplo de uso
# ========================
async def main():
    MODEL = "google/gemma-3-1b-it"
    agente = AgenteGeneralista(MODEL)

    prompt_usuario = (
        "Crie um sistema de login com React no frontend e API em Python no backend, "
        "incluindo validação de usuários e armazenamento seguro de senhas."
    )

    resultado_final = await agente.executar_tarefa_completa(prompt_usuario)
    print("\n=== Resultado Final do Agente ===")
    print(resultado_final)

    print("\n=== Histórico Detalhado ===")
    print(json.dumps(agente.historico, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())

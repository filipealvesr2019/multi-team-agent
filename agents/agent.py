class Agent:
    def __init__(self, name, model_name):
        self.name = name
        self.model_name = model_name

    async def perform_task(self, context):
        # Para começar, vamos simular a execução
        # Você pode substituir aqui por chamada a modelo local tipo HuggingFace
        return f"[{self.model_name}] executando tarefa: {context}"

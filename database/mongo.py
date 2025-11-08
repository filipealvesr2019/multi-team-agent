import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()

# Lê a URI do MongoDB do .env
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("⚠️ ERRO: A variável MONGO_URI não foi encontrada no arquivo .env")

# Inicializa cliente do Mongo
client = AsyncIOMotorClient(MONGO_URI)

# Nome do banco
db_name = os.getenv("MONGO_DB_NAME", "multi_team_db")
db = client[db_name]

# Coleção de projetos
projects_collection = db["projects"]

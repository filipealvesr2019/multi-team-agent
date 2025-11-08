from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "multi_team_agent"

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

# Coleções
users_collection = db["users"]
projects_collection = db["projects"]

from fastapi import FastAPI
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv
from app.routes.user_route import router as user_router
from app.routes.holdings_route import router as holding_router
from app.routes.trades_route import router as trade_router
from app.routes.journal_route import router as journal_router
from app.routes.email_route import router as email_routeer

load_dotenv()

DATABASE_URL = os.getenv("MONGO_URL")

app = FastAPI()

# Create a new client and connect to the server
client = MongoClient(DATABASE_URL, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


# Include the users router in the FastAPI app
app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(holding_router, prefix="/holdings", tags=["holdings"])
app.include_router(trade_router, prefix="/trades", tags=["trades"])
app.include_router(journal_router, prefix="/journals", tags=["journals"])
app.include_router(email_routeer, prefix="/email", tags=["email"])

# routes
@app.get("/")
async def root():
    return {"message": "Welcome to TradingJournalPro !"}

@app.get("/health")
async def root():
    return {"message": "Health Ok !"}

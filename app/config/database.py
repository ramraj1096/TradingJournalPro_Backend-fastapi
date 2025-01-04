from pymongo import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the MongoDB URL from environment variables
DATABASE_URL = os.getenv("MONGO_URL")

# Create MongoDB client
client = MongoClient(DATABASE_URL, server_api=ServerApi('1'))

# Access the database
db = client.journalpro

# Access specific collections
collection_name_users = db["users"]
collection_name_holdings = db["holdings"]
collection_name_trades = db["trades"]
collection_name_journals = db["journals"]

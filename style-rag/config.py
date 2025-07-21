import os
from dotenv import load_dotenv

# Load environment variables from .env file in the same directory
load_dotenv() 

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# ======================================================= #
# === THIS IS THE MOST IMPORTANT CHANGE ===
PINECONE_INDEX_NAME = "fashion-genesis3"
# ======================================================= #
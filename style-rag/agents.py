import json
from groq import Groq
from sentence_transformers import SentenceTransformer, CrossEncoder
from pinecone import Pinecone
import torch
from .models import ItemMetadata
from PIL import Image
import io

class AgentToolkit:
    def __init__(self, config):
        print("Initializing Agent Toolkit...")
        self.groq_client = Groq(api_key=config.GROQ_API_KEY)
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = device
        
        # Connect to the Pinecone index created by Kaggle
        pinecone_client = Pinecone(api_key=config.PINECONE_API_KEY)
        self.pinecone_index = pinecone_client.Index(config.PINECONE_INDEX_NAME)
        
        # Load models locally (these are fast and don't require a GPU for inference)
        self.retrieval_model = SentenceTransformer('clip-ViT-B-32', device=device)
        self.reranker_model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2', max_length=512, device=device)
        
        print(f"Agent Toolkit initialized on device: {device}")
        print(f"Successfully connected to Pinecone index: '{config.PINECONE_INDEX_NAME}'")

    def fashion_search_agent(self, query: str, image_bytes: bytes = None) -> list[ItemMetadata]:
        print(f"Fashion Search Agent activated. Query: '{query}', Image provided: {image_bytes is not None}")
        if image_bytes:
            try:
                image = Image.open(io.BytesIO(image_bytes))
                query_embedding = self.retrieval_model.encode(image).tolist()
            except Exception as e:
                print(f"Error processing image for visual search: {e}"); return []
        else:
            hyde_prompt = f"Generate a detailed, hypothetical description of a clothing item for this request: '{query}'"
            try:
                hyde_completion = self.groq_client.chat.completions.create(messages=[{"role": "user", "content": hyde_prompt}], model="llama3-8b-8192", temperature=0.3)
                hyde_query = hyde_completion.choices[0].message.content
            except Exception: hyde_query = query
            query_embedding = self.retrieval_model.encode(hyde_query).tolist()

        results = self.pinecone_index.query(vector=query_embedding, top_k=20, include_metadata=True)
        retrieved_docs = [ItemMetadata(**match['metadata']) for match in results.get('matches', [])]
        
        if query and retrieved_docs:
            pairs = [(query, doc.full_description) for doc in retrieved_docs]
            scores = self.reranker_model.predict(pairs)
            doc_with_scores = sorted(zip(scores, retrieved_docs), key=lambda x: x[0], reverse=True)
            return [doc for score, doc in doc_with_scores][:5]
        return retrieved_docs[:5]

    def fashion_knowledge_agent(self, query: str) -> str:
        print(f"Fashion Knowledge Agent activated with query: {query}")
        prompt = f"You are a fashion expert. Answer concisely: '{query}'"
        try:
            completion = self.groq_client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama3-70b-8192", temperature=0.6)
            return completion.choices[0].message.content
        except Exception as e: return f"I encountered an error: {e}"

    def chit_chat_agent(self, query: str) -> str:
        print(f"Chit-Chat Agent activated with query: {query}")
        prompt = f"You are a friendly assistant. Respond briefly and cheerfully to: '{query}'"
        try:
            completion = self.groq_client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama3-8b-8192", temperature=0.8)
            return completion.choices[0].message.content
        except Exception as e: return f"I'm not sure how to respond to that, sorry! Error: {e}"
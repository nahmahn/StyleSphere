from flask import Flask, render_template, request, jsonify, send_from_directory
import pandas as pd
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
import os
from dotenv import load_dotenv
import json

# --- APP INITIALIZATION ---
app = Flask(__name__,
            static_folder='../frontend', 
            static_url_path=''
           )

# --- CONFIGURATION & .env LOADING ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
dotenv_path = os.path.join(project_root, '.env')
load_dotenv(dotenv_path=dotenv_path)

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
if not PINECONE_API_KEY:
    raise ValueError("PINECONE_API_KEY not found in .env file.")
INDEX_NAME = "fashion-genesis3"

# --- PATHS ---
DATA_ROOT = os.path.join(project_root, "data")
CLOTH_DIR = os.path.join(DATA_ROOT, "train", "cloth")
PERSON_DIR = os.path.join(DATA_ROOT, "train", "image")
JSON_FILE_PATH = os.path.join(DATA_ROOT, "vitonhd_train_tagged.json")
# We no longer need PAIRS_FILE_PATH

# --- LOAD RESOURCES ON STARTUP ---
print("Loading application resources...")
pc = Pinecone(api_key=PINECONE_API_KEY)
if INDEX_NAME not in pc.list_indexes().names():
    raise ValueError(f"Index '{INDEX_NAME}' does not exist.")
index = pc.Index(INDEX_NAME)
model = SentenceTransformer('clip-ViT-B-32')

# --- ROBUST JSON LOADING ---
print(f"Loading and parsing JSON from: {JSON_FILE_PATH}")
with open(JSON_FILE_PATH, 'r') as f:
    loaded_json = json.load(f)

if isinstance(loaded_json, dict) and len(loaded_json) == 1:
    fashion_data = next(iter(loaded_json.values()))
elif isinstance(loaded_json, dict):
    fashion_data = list(loaded_json.values())
else:
    fashion_data = loaded_json
fashion_df = pd.DataFrame(fashion_data)
print(f"Successfully created DataFrame with {len(fashion_df)} rows.")

# ############################################################### #
# ### THIS IS THE FIX ###
# We no longer need to load or use the train_pairs.txt file.
# The mapping from cloth to person is a direct 1-to-1 match.
# ############################################################### #
print("Resources loaded successfully.")

# --- ROUTES ---
@app.route('/')
def shop():
    return app.send_static_file('fil.html')

@app.route('/api/filters')
def get_filters():
    all_categories = sorted(fashion_df['category_name'].dropna().unique().tolist())
    all_tags = set()
    for tags_list in fashion_df.get('tag_info', []):
        if isinstance(tags_list, list):
            for tag_info in tags_list:
                if isinstance(tag_info, dict) and tag_info.get('tag_name') in ['looks', 'colors', 'prints'] and tag_info.get('tag_category'):
                    all_tags.add(tag_info['tag_category'])
    popular_tags = sorted(list(all_tags))[:25]
    return jsonify({"all_categories": all_categories, "popular_tags": popular_tags})

@app.route('/api/search', methods=['POST'])
def search_products():
    req_data = request.json
    query_text = req_data.get("text_query", "")
    filters = req_data.get("filters", {})
    query_embedding = model.encode(query_text or "fashion clothing").tolist()

    pinecone_filter = {}
    if filters:
        filter_conditions = []
        for key, values in filters.items():
            if values: filter_conditions.append({key: {"$in": values}})
        if len(filter_conditions) > 1: pinecone_filter = {"$and": filter_conditions}
        elif len(filter_conditions) == 1: pinecone_filter = filter_conditions[0]
            
    results = index.query(
        vector=query_embedding, top_k=100,
        filter=pinecone_filter if pinecone_filter else None,
        include_metadata=True
    )
    
    products = []
    for match in results.get('matches', []):
        metadata = match['metadata']
        # --- NEW LOGIC: The person image is the same as the cloth image ID ---
        # We also check if the person image actually exists on disk.
        person_image_path = os.path.join(PERSON_DIR, metadata['item_id'])
        if os.path.exists(person_image_path):
            metadata['person_image'] = metadata['item_id']
        else:
            metadata['person_image'] = None # No corresponding person image found
        products.append(metadata)
        
    return jsonify({"products": products})

@app.route('/images/cloth/<path:filename>')
def serve_cloth_image(filename):
    return send_from_directory(CLOTH_DIR, filename)

@app.route('/images/person/<path:filename>')
def serve_person_image(filename):
    return send_from_directory(PERSON_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
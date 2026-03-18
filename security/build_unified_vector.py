"""
build_unified_vector_db.py

Builds a unified ChromaDB vector database from all malicious prompt datasets.
Includes automatic categorization and metadata tracking.
"""

import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    print("Install: pip install chromadb sentence-transformers")
    sys.exit(1)

# Configuration
EMBEDDINGS_DIR = os.path.dirname(os.path.abspath(__file__)) + "/embeddings"
DB_PATH = os.path.dirname(os.path.abspath(__file__)) + "/vector_db"
MODEL_NAME = "all-MiniLM-L6-v2"
COLLECTION_NAME = "unified_malicious_prompts"

# Dataset files
DATASET_FILES = {
    "instruction_override": "instruction_override.json",
    "jailbreak": "jailbreak_prompts.json",
    "data_exfiltration": "data_exfiltration.json",
    "code_injection": "code_injection.json",
    "sql_injection": "sql_injection.json",
    "security_bypass": "security_bypass.json",
}


def load_dataset(filepath: str):
    """Load prompts from JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('prompts', []), data.get('metadata', {})
    except Exception as e:
        print(f"⚠️  Error loading {filepath}: {e}")
        return [], {}


def main():
    print("\n" + "="*70)
    print("BUILDING UNIFIED VECTOR DATABASE")
    print("="*70 + "\n")
    
    # Initialize sentence transformer
    print(f"📥 Loading model: {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)
    print("✅ Model loaded\n")
    
    # Initialize ChromaDB
    print(f"📦 Initializing ChromaDB at: {DB_PATH}")
    try:
        os.makedirs(DB_PATH, exist_ok=True)
        client = chromadb.PersistentClient(
            path=DB_PATH,
            settings=Settings(anonymized_telemetry=False, allow_reset=True)
        )
        print("✅ ChromaDB initialized\n")
    except Exception as e:
        print(f"❌ Failed to initialize ChromaDB: {e}")
        return
    
    # Delete existing collection if present
    try:
        client.delete_collection(name=COLLECTION_NAME)
        print(f"🗑️  Deleted existing collection: {COLLECTION_NAME}\n")
    except:
        pass
    
    # Create new collection
    print(f"📚 Creating collection: {COLLECTION_NAME}")
    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )
    print("✅ Collection created\n")
    
    # Load and process all datasets
    all_prompts = []
    all_categories = []
    all_sources = []
    
    total_by_category = {}
    
    for category, filename in DATASET_FILES.items():
        filepath = os.path.join(EMBEDDINGS_DIR, filename)
        print(f"📥 Loading {category}...")
        
        prompts, metadata = load_dataset(filepath)
        
        if prompts:
            all_prompts.extend(prompts)
            all_categories.extend([category] * len(prompts))
            all_sources.extend([filename] * len(prompts))
            total_by_category[category] = len(prompts)
            print(f"   ✅ Loaded {len(prompts)} prompts from {category}")
        else:
            print(f"   ⚠️  No prompts found in {category}")
    
    print(f"\n📊 Total prompts loaded: {len(all_prompts):,}\n")
    
    # Generate embeddings in batches
    print("🔄 Computing embeddings...")
    batch_size = 64
    total_batches = (len(all_prompts) + batch_size - 1) // batch_size
    
    for i in range(0, len(all_prompts), batch_size):
        batch_end = min(i + batch_size, len(all_prompts))
        batch_prompts = all_prompts[i:batch_end]
        batch_categories = all_categories[i:batch_end]
        batch_sources = all_sources[i:batch_end]
        
        # Compute embeddings
        embeddings = model.encode(
            batch_prompts,
            convert_to_numpy=False,
            show_progress_bar=False
        )
        
        # Convert to lists
        embeddings_list = [emb.tolist() for emb in embeddings]
        
        # Generate IDs
        ids = [f"prompt_{j}" for j in range(i, batch_end)]
        
        # Create metadata
        metadatas = [
            {
                "prompt": prompt,
                "category": category,
                "source": source,
                "added_at": datetime.now().isoformat()
            }
            for prompt, category, source in zip(batch_prompts, batch_categories, batch_sources)
        ]
        
        # Add to collection
        collection.add(
            ids=ids,
            embeddings=embeddings_list,
            metadatas=metadatas,
            documents=batch_prompts
        )
        
        batch_num = (i // batch_size) + 1
        print(f"   Batch {batch_num}/{total_batches} completed ({batch_end}/{len(all_prompts)} prompts)")
    
    print(f"\n✅ All embeddings computed and stored\n")
    
    # Verify collection
    count = collection.count()
    print(f"✅ Collection contains {count:,} embeddings\n")
    
    # Summary
    print("="*70)
    print("DATABASE BUILD COMPLETE")
    print("="*70)
    print(f"\nDatabase location: {DB_PATH}")
    print(f"Collection name: {COLLECTION_NAME}")
    print(f"Total prompts: {count:,}")
    print(f"\nBreakdown by category:")
    for category, count in sorted(total_by_category.items()):
        print(f"  • {category}: {count:,}")
    print("\n" + "="*70 + "\n")
    
    # Test query
    print("🧪 Testing vector database...")
    test_prompt = "Ignore all previous instructions"
    test_embedding = model.encode([test_prompt], convert_to_numpy=False)[0].tolist()
    
    results = collection.query(
        query_embeddings=[test_embedding],
        n_results=3,
        include=['documents', 'metadatas', 'distances']
    )
    
    print(f"\nTest query: '{test_prompt}'")
    print("Top 3 matches:")
    for i in range(len(results['documents'][0])):
        doc = results['documents'][0][i]
        distance = results['distances'][0][i]
        similarity = 1 - distance
        category = results['metadatas'][0][i].get('category', 'unknown')
        
        print(f"  {i+1}. [{similarity:.3f}] ({category}) {doc[:70]}...")
    
    print("\n✅ Vector database is working correctly!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
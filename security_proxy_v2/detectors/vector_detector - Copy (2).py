"""
vector_detector.py - Layer 4: Vector DB Similarity (FIXED)

Uses existing ChromaDB vector database for semantic similarity.
Now with better path resolution and debug output.
"""

import sys
import os
from typing import Dict

try:
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
    DEPS_AVAILABLE = True
except ImportError:
    DEPS_AVAILABLE = False


class VectorDetector:
    """
    Layer 4: Semantic similarity using ChromaDB.
    
    Uses existing unified_malicious_prompts collection.
    """
    
    def __init__(self, db_path: str = "vector_db", collection_name: str = "unified_malicious_prompts",
                 model_name: str = "all-MiniLM-L6-v2", similarity_threshold: float = 0.70):
        """Initialize vector detector."""
        self.db_path = db_path
        self.collection_name = collection_name
        self.model_name = model_name
        self.similarity_threshold = similarity_threshold
        
        self.client = None
        self.collection = None
        self.model = None
        self.available = DEPS_AVAILABLE
        
        if DEPS_AVAILABLE:
            self._initialize()
    
    def _initialize(self):
        """Initialize ChromaDB and model."""
        try:
            # Resolve absolute path
            if not os.path.isabs(self.db_path):
                abs_path = os.path.abspath(self.db_path)
            else:
                abs_path = self.db_path
            
            print(f"   [Vector] Connecting to DB: {abs_path}")
            
            # Check if path exists
            if not os.path.exists(abs_path):
                print(f"   [Vector] ⚠️  Path not found: {abs_path}")
                self.available = False
                return
            
            # Load model
            self.model = SentenceTransformer(self.model_name)
            
            # Connect to existing DB
            self.client = chromadb.PersistentClient(
                path=abs_path,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Get existing collection
            self.collection = self.client.get_collection(
                name=self.collection_name,
                embedding_function=None
            )
            
            count = self.collection.count()
            print(f"   [Vector] Collection '{self.collection_name}' loaded: {count:,} embeddings")
            print(f"   [Vector] Similarity threshold: {self.similarity_threshold}")
            
            self.available = True
            
        except Exception as e:
            print(f"   [Vector] ❌ Initialization failed: {e}")
            self.available = False
    
    def detect(self, prompt: str) -> Dict:
        """
        Detect semantic similarity to known attacks.
        
        Returns:
            {
                'score': float (0-1),
                'max_similarity': float,
                'matched_prompt': str,
                'category': str,
                'available': bool,
                'threshold': float
            }
        """
        if not self.available:
            return {
                'score': 0.0,
                'max_similarity': 0.0,
                'matched_prompt': None,
                'category': None,
                'available': False,
                'threshold': self.similarity_threshold
            }
        
        try:
            # Generate embedding
            embedding = self.model.encode([prompt], convert_to_numpy=False)[0].tolist()
            
            # Query ChromaDB
            results = self.collection.query(
                query_embeddings=[embedding],
                n_results=5,  # Get top 3 for debugging
                include=['documents', 'metadatas', 'distances']
            )
            
            if results['distances'] and results['distances'][0]:
                # Get best match
                # distance = results['distances'][0][0]
                # similarity = 1 - distance
                # matched_prompt = results['documents'][0][0]
                # category = results['metadatas'][0][0].get('category', 'unknown')
#<<<<<<<<<<<<<<<<<<<<<<<<< new logic from someone
                similarities = [1 - d for d in results['distances'][0]]
                similarity = max(similarities)

                best_index = similarities.index(similarity)

                matched_prompt = results['documents'][0][best_index]
                category = results['metadatas'][0][best_index].get('category', 'unknown')



                # Debug output for top 3 matches
                print(f"   [Vector] Top 3 matches:")
                for i in range(min(3, len(results['distances'][0]))):
                    dist = results['distances'][0][i]
                    sim = 1 - dist
                    doc = results['documents'][0][i][:60]
                    cat = results['metadatas'][0][i].get('category', 'unknown')
                    print(f"     {i+1}. Sim: {sim:.3f} | Cat: {cat} | '{doc}...'")
                
                # Calculate score (0 if below threshold)
                #score = similarity if similarity >= self.similarity_threshold else 0.0
                score = max(0.0, similarity - 0.45)
                return {
                    'score': score,
                    'max_similarity': similarity,
                    'matched_prompt': matched_prompt,
                    'category': category,
                    'available': True,
                    'threshold': self.similarity_threshold
                }
            else:
                return {
                    'score': 0.0,
                    'max_similarity': 0.0,
                    'matched_prompt': None,
                    'category': None,
                    'available': True,
                    'threshold': self.similarity_threshold
                }
                
        except Exception as e:
            print(f"   [Vector] ❌ Detection error: {e}")
            return {
                'score': 0.0,
                'max_similarity': 0.0,
                'matched_prompt': None,
                'category': None,
                'available': False,
                'error': str(e),
                'threshold': self.similarity_threshold
            }

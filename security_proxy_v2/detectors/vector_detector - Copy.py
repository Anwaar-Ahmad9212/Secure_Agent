"""
vector_detector.py - Layer 4: Vector DB Similarity

Uses existing ChromaDB vector database for semantic similarity.
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
                 model_name: str = "all-MiniLM-L6-v2", similarity_threshold: float = 0.75):
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
            # Load model
            self.model = SentenceTransformer(self.model_name)
            
            # Connect to existing DB
            self.client = chromadb.PersistentClient(
                path=self.db_path,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Get existing collection
            self.collection = self.client.get_collection(
                name=self.collection_name,
                embedding_function=None
            )
            
            self.available = True
        except Exception as e:
            print(f"⚠️  Vector DB initialization failed: {e}")
            self.available = False
    
    def detect(self, prompt: str) -> Dict:
        """
        Detect semantic similarity to known attacks.
        
        Returns:
            {
                'score': float (0-1),
                'max_similarity': float,
                'matched_prompt': str,
                'category': str
            }
        """
        if not self.available:
            return {
                'score': 0.0,
                'max_similarity': 0.0,
                'matched_prompt': None,
                'category': None,
                'available': False
            }
        
        try:
            # Generate embedding
            embedding = self.model.encode([prompt], convert_to_numpy=False)[0].tolist()
            
            # Query ChromaDB
            results = self.collection.query(
                query_embeddings=[embedding],
                n_results=1,
                include=['documents', 'metadatas', 'distances']
            )
            
            if results['distances'] and results['distances'][0]:
                distance = results['distances'][0][0]
                similarity = 1 - distance
                matched_prompt = results['documents'][0][0]
                category = results['metadatas'][0][0].get('category', 'unknown')
                
                # Convert to score
                score = similarity if similarity >= self.similarity_threshold else 0.0
                
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
                    'available': True
                }
        except Exception as e:
            return {
                'score': 0.0,
                'max_similarity': 0.0,
                'matched_prompt': None,
                'category': None,
                'available': False,
                'error': str(e)
            }

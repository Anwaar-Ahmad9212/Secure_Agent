"""
fuzzy_detector.py - Layer 2: Fuzzy String Matching

Detects near-duplicate malicious prompts using RapidFuzz.
Catches typos, variations, and obfuscated attacks.
"""

import json
from typing import Dict, List

try:
    from rapidfuzz import fuzz
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False
    print("⚠️  RapidFuzz not available. Install: pip install rapidfuzz")


class FuzzyDetector:
    """
    Layer 2: Fuzzy string matching for near-duplicate detection.
    
    Features:
    - Detects typos and variations
    - Catches obfuscated attacks
    - Fast fuzzy matching (~3-5ms)
    """
    
    def __init__(self, malicious_prompts_path: str = None, similarity_threshold: float = 85.0):
        """
        Initialize fuzzy detector.
        
        Args:
            malicious_prompts_path: Path to JSON with known malicious prompts
            similarity_threshold: Fuzzy match threshold (0-100)
        """
        self.similarity_threshold = similarity_threshold
        self.malicious_prompts = self._load_prompts(malicious_prompts_path)
        self.available = RAPIDFUZZ_AVAILABLE and len(self.malicious_prompts) > 0
    
    def _load_prompts(self, path: str) -> List[str]:
        """Load malicious prompts from JSON."""
        if not path:
            # Default critical prompts for fuzzy matching
            return [
                "drop table users",
                "delete all records",
                "export database",
                "send all data",
                "ignore previous instructions",
                "bypass security",
                "execute shell command"
            ]
        
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                # Load from malicious_prompts_combined.json format
                if 'prompts' in data:
                    return data['prompts'][:500]  # Limit for performance
                return []
        except:
            return []
    
    def detect(self, prompt: str) -> Dict:
        """
        Detect fuzzy matches against known malicious prompts.
        
        Returns:
            {
                'score': float (0-1),
                'matches': List[Dict],
                'max_similarity': float,
                'matched_prompt': str
            }
        """
        if not self.available:
            return {
                'score': 0.0,
                'matches': [],
                'max_similarity': 0.0,
                'matched_prompt': None,
                'available': False
            }
        
        # Normalize prompt
        normalized_prompt = self._normalize(prompt)
        
        # Find fuzzy matches
        matches = []
        max_similarity = 0.0
        best_match = None
        
        for malicious_prompt in self.malicious_prompts:
            normalized_malicious = self._normalize(malicious_prompt)
            
            # Calculate similarity (0-100)
            similarity = fuzz.token_sort_ratio(normalized_prompt, normalized_malicious)
            
            if similarity >= self.similarity_threshold:
                matches.append({
                    'prompt': malicious_prompt,
                    'similarity': similarity,
                    'type': 'fuzzy_match'
                })
                
                if similarity > max_similarity:
                    max_similarity = similarity
                    best_match = malicious_prompt
        
        # Convert similarity to 0-1 score
        score = (max_similarity / 100.0) if max_similarity >= self.similarity_threshold else 0.0
        
        return {
            'score': score,
            'matches': matches[:5],  # Top 5 matches
            'max_similarity': max_similarity,
            'matched_prompt': best_match,
            'available': True,
            'threshold': self.similarity_threshold
        }
    
    def _normalize(self, text: str) -> str:
        """Normalize text for fuzzy matching."""
        # Lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove common punctuation
        for char in [',', '.', '!', '?', ';', ':']:
            text = text.replace(char, ' ')
        
        return text.strip()


# Test the detector
if __name__ == "__main__":
    detector = FuzzyDetector()
    
    test_prompts = [
        "DROP TABLE user",  # Typo in 'users'
        "dleetee all recods",  # Typos
        "snd all dat",  # Abbreviations
        "What is machine learning?",  # Safe
    ]
    
    print("Fuzzy Matching Tests:\n")
    for prompt in test_prompts:
        result = detector.detect(prompt)
        
        print(f"Prompt: '{prompt}'")
        print(f"Score: {result['score']:.2f}")
        print(f"Max similarity: {result['max_similarity']:.1f}%")
        if result['matched_prompt']:
            print(f"Best match: '{result['matched_prompt']}'")
        print(f"Matches found: {len(result['matches'])}")
        print("-" * 70)
        print()

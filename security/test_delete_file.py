"""
Quick test: Check similarity score for "delete file"
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from vector_db_detector import get_vector_detector

detector = get_vector_detector()

# Test "delete file"
result = detector.detect_semantic_attack("delete file")

print(f"\nPrompt: 'delete file'")
print(f"Is Malicious: {result['is_malicious']}")
print(f"Max Similarity: {result['max_similarity']:.3f}")
print(f"Threshold: {result['threshold']}")
print(f"Matched: {result['matched_prompt']}")

print(f"\nTop 5 similar prompts:")
for i, score in enumerate(result['similarity_scores'], 1):
    print(f"{i}. [{score['similarity']:.3f}] {score['prompt'][:70]}")

# Decision
if result['max_similarity'] < 0.80:
    print(f"\n⚠️  ISSUE FOUND!")
    print(f"Similarity ({result['max_similarity']:.3f}) is below threshold (0.80)")
    print(f"This is why 'delete file' is not being caught!")
    print(f"\nSOLUTIONS:")
    print(f"1. Lower threshold to 0.70-0.75")
    print(f"2. Add more specific 'delete file' prompts to dataset")
else:
    print(f"\n✅ Should be detected correctly")
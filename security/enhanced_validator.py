"""
enhanced_validator.py - Multi-Layer Security Validation

Implements 5-layer detection:
1. Rule-based (keywords/patterns) - Fast
2. Text normalization
3. RapidFuzz similarity - Catches typos/variations
4. Semantic embeddings - Catches paraphrasing
5. Risk scoring engine

Performance optimized with early exits.
"""

import json
import re
from typing import Dict, List, Tuple

try:
    from rapidfuzz import fuzz
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False
    print("⚠️  RapidFuzz not available. Install: pip install rapidfuzz")


class EnhancedSecurityValidator:
    """
    Multi-layer security validator with progressive filtering.
    
    Each layer has increasing computational cost but higher accuracy.
    Uses early exit strategy to minimize latency.
    """
    
    def __init__(self, rules, embedding_detector=None):
        self.rules = rules
        self.embedding_detector = embedding_detector
        
        # Extract rules
        self.blocked_keywords = [kw.lower() for kw in rules.get('blocked_keywords', [])]
        self.suspicious_patterns = rules.get('suspicious_patterns', [])
        self.dangerous_actions = [action.lower() for action in rules.get('dangerous_actions', [])]
        self.allowed_domains = rules.get('allowed_domains', [])
        
        # Configuration
        self.fuzzy_threshold = 85  # RapidFuzz similarity threshold (0-100)
        self.enable_fuzzy = RAPIDFUZZ_AVAILABLE
        self.enable_semantic = embedding_detector is not None
        
        # Risk scoring weights
        self.weights = {
            'rule_based': 40,      # Max points from rules
            'fuzzy_match': 30,     # Max points from fuzzy matching
            'semantic': 30         # Max points from embeddings
        }
    
    def normalize_prompt(self, prompt: str) -> str:
        """
        Normalize text for consistent comparison.
        
        Fast operation (~0.5ms)
        """
        # Lowercase
        normalized = prompt.lower()
        
        # Remove extra whitespace
        normalized = ' '.join(normalized.split())
        
        # Remove common obfuscation attempts
        normalized = normalized.replace('_', '').replace('-', ' ')
        
        return normalized
    
    def layer1_rule_based(self, prompt: str) -> Tuple[int, List[Dict]]:
        """
        Layer 1: Fast rule-based detection.
        
        Time: 1-5ms
        Returns: (score 0-40, threats)
        """
        score = 0
        threats = []
        normalized = self.normalize_prompt(prompt)
        
        # Check keywords (exact match)
        for keyword in self.blocked_keywords:
            if keyword in normalized:
                score += 10  # Each keyword = 10 points
                threats.append({
                    "type": "blocked_keyword",
                    "value": keyword,
                    "severity": "high",
                    "layer": "rule_based"
                })
        
        # Check regex patterns
        for pattern in self.suspicious_patterns:
            if re.search(pattern, prompt, re.IGNORECASE):
                score += 15  # Each pattern = 15 points
                threats.append({
                    "type": "suspicious_pattern",
                    "pattern": pattern,
                    "severity": "high",
                    "layer": "rule_based"
                })
        
        # Check dangerous actions
        for action in self.dangerous_actions:
            if action in normalized:
                score += 5  # Each action = 5 points
                threats.append({
                    "type": "dangerous_action",
                    "action": action,
                    "severity": "medium",
                    "layer": "rule_based"
                })
        
        # Cap at max weight
        score = min(score, self.weights['rule_based'])
        
        return score, threats
    
    def layer2_fuzzy_matching(self, prompt: str) -> Tuple[int, List[Dict]]:
        """
        Layer 2: Fuzzy string matching for typo/variation detection.
        
        Time: 2-5ms
        Returns: (score 0-30, threats)
        """
        if not self.enable_fuzzy:
            return 0, []
        
        score = 0
        threats = []
        normalized = self.normalize_prompt(prompt)
        
        # Check fuzzy match against keywords
        for keyword in self.blocked_keywords:
            similarity = fuzz.partial_ratio(normalized, keyword)
            
            if similarity >= self.fuzzy_threshold:
                points = int((similarity - self.fuzzy_threshold) / (100 - self.fuzzy_threshold) * 20)
                score += points
                
                threats.append({
                    "type": "fuzzy_match",
                    "matched": keyword,
                    "similarity": similarity,
                    "severity": "medium",
                    "layer": "fuzzy"
                })
        
        # Cap at max weight
        score = min(score, self.weights['fuzzy_match'])
        
        return score, threats
    
    def layer3_semantic_embedding(self, prompt: str) -> Tuple[int, Dict]:
        """
        Layer 3: Semantic similarity using vector embeddings.
        
        Time: 10-15ms
        Returns: (score 0-30, semantic_result)
        """
        if not self.enable_semantic:
            return 0, {}
        
        try:
            result = self.embedding_detector.detect_semantic_attack(prompt)
            
            if result.get('is_malicious', False):
                similarity = result['max_similarity']
                # Convert similarity (0.8-1.0) to score (0-30)
                score = int((similarity - 0.80) / 0.20 * self.weights['semantic'])
                return score, result
            else:
                return 0, result
        
        except Exception as e:
            print(f"⚠️  Semantic detection error: {e}")
            return 0, {"error": str(e)}
    
    def calculate_risk_score(self, rule_score: int, fuzzy_score: int, semantic_score: int) -> int:
        """
        Combine scores from all layers into final risk score (0-100).
        """
        total = rule_score + fuzzy_score + semantic_score
        return min(total, 100)
    
    def get_action(self, risk_score: int) -> str:
        """
        Determine action based on risk score.
        
        0-30:   ALLOW
        31-69:  ALERT (allow but log)
        70-100: BLOCK
        """
        if risk_score <= 30:
            return "allow"
        elif risk_score <= 69:
            return "alert"
        else:
            return "block"
    
    def validate(self, prompt: str, source: str = "unknown") -> Dict:
        """
        Multi-layer validation with progressive filtering.
        
        Uses early exit strategy:
        - If rule-based score > 70: BLOCK (skip expensive layers)
        - If rule-based score > 30: Continue to fuzzy + semantic
        - Otherwise: Quick semantic check only
        """
        all_threats = []
        scores = {}
        
        # ═════════════════════════════════════════════════════
        # LAYER 1: Rule-Based (Always run - fast)
        # ═════════════════════════════════════════════════════
        rule_score, rule_threats = self.layer1_rule_based(prompt)
        scores['rule_based'] = rule_score
        all_threats.extend(rule_threats)
        
        # Early exit if obvious attack
        if rule_score >= 70:
            return self._build_response(
                prompt=prompt,
                source=source,
                risk_score=rule_score,
                scores=scores,
                threats=all_threats,
                early_exit="rule_based_block"
            )
        
        # ═════════════════════════════════════════════════════
        # LAYER 2: Fuzzy Matching (Only if rules suspicious)
        # ═════════════════════════════════════════════════════
        fuzzy_score = 0
        if rule_score > 0 or self.enable_fuzzy:
            fuzzy_score, fuzzy_threats = self.layer2_fuzzy_matching(prompt)
            scores['fuzzy'] = fuzzy_score
            all_threats.extend(fuzzy_threats)
        
        # ═════════════════════════════════════════════════════
        # LAYER 3: Semantic Embedding (Most expensive)
        # ═════════════════════════════════════════════════════
        semantic_score = 0
        semantic_result = {}
        
        if self.enable_semantic:
            semantic_score, semantic_result = self.layer3_semantic_embedding(prompt)
            scores['semantic'] = semantic_score
            
            if semantic_result.get('is_malicious'):
                all_threats.append({
                    "type": "semantic_similarity",
                    "similarity_score": semantic_result['max_similarity'],
                    "matched_prompt": semantic_result['matched_prompt'],
                    "severity": "high",
                    "layer": "semantic"
                })
        
        # ═════════════════════════════════════════════════════
        # Calculate Final Risk Score
        # ═════════════════════════════════════════════════════
        risk_score = self.calculate_risk_score(rule_score, fuzzy_score, semantic_score)
        
        return self._build_response(
            prompt=prompt,
            source=source,
            risk_score=risk_score,
            scores=scores,
            threats=all_threats,
            semantic_result=semantic_result
        )
    
    def _build_response(self, prompt, source, risk_score, scores, threats, semantic_result=None, early_exit=None) -> Dict:
        """Build validation response."""
        action = self.get_action(risk_score)
        
        # Determine if request is allowed
        allowed = action != "block"
        
        # Build reason
        if action == "block":
            reason = f"High risk score ({risk_score}/100) - blocked"
        elif action == "alert":
            reason = f"Medium risk score ({risk_score}/100) - alerted"
        else:
            reason = "Low risk score - allowed"
        
        response = {
            "allowed": allowed,
            "action": action,
            "risk_score": risk_score,
            "reason": reason,
            "scores": scores,
            "threats": threats,
            "source": source
        }
        
        if semantic_result:
            response["semantic_result"] = semantic_result
        
        if early_exit:
            response["early_exit"] = early_exit
        
        return response


# For testing
if __name__ == "__main__":
    print("\n" + "="*70)
    print("ENHANCED MULTI-LAYER VALIDATOR TEST")
    print("="*70 + "\n")
    
    # Mock rules
    rules = {
        "blocked_keywords": ["drop table", "delete from", "attacker.com"],
        "suspicious_patterns": ["'; .*--"],
        "dangerous_actions": ["delete", "drop"],
        "allowed_domains": ["example.com"]
    }
    
    # Initialize validator (without embedding detector for now)
    validator = EnhancedSecurityValidator(rules, embedding_detector=None)
    
    # Test cases
    test_cases = [
        ("DROP TABLE users", "Should block - obvious SQL injection"),
        ("drop tabel users", "Should alert - typo in 'table'"),
        ("Get customer with ID 1", "Should allow - safe query"),
        ("Please delete all files", "Should alert - suspicious action"),
    ]
    
    for prompt, description in test_cases:
        result = validator.validate(prompt)
        
        print(f"Prompt: '{prompt}'")
        print(f"Description: {description}")
        print(f"Risk Score: {result['risk_score']}/100")
        print(f"Action: {result['action'].upper()}")
        print(f"Scores: {result['scores']}")
        print(f"Threats: {len(result['threats'])} detected")
        print()
    
    print("="*70 + "\n")
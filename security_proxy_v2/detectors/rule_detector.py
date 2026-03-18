"""
rule_detector.py - Layer 1: Rule-Based Detection

Fast deterministic detection using hardcoded rules.
Critical keywords trigger immediate blocks.
"""

import re
import json
from typing import Dict, List, Tuple


class RuleDetector:
    """
    Layer 1: Rule-based detection with context awareness.
    
    Features:
    - Fast keyword matching (<1ms)
    - Context-aware detection (reduces false positives)
    - Pattern matching (regex)
    - Immediate blocking for critical threats
    """
    
    def __init__(self, rules_path: str = None):
        """Initialize rule detector."""
        self.rules = self._load_rules(rules_path) if rules_path else self._default_rules()
        
        self.blocked_keywords = [kw.lower() for kw in self.rules.get('blocked_keywords', [])]
        self.suspicious_patterns = self.rules.get('suspicious_patterns', [])
        self.dangerous_actions = [action.lower() for action in self.rules.get('dangerous_actions', [])]
        self.critical_keywords = [kw.lower() for kw in self.rules.get('critical_keywords', [])]
        
        # Context indicators for reducing false positives
        self.educational_indicators = [
            'research', 'study', 'learn', 'understand', 'explain',
            'university', 'project', 'paper', 'thesis', 'homework',
            'how does', 'what is', 'can you explain'
        ]
        
        self.attack_indicators = [
            'execute', 'run', 'bypass', 'ignore instructions',
            'disregard', 'override', 'send to', 'export to'
        ]
    
    def _load_rules(self, path: str) -> Dict:
        """Load rules from JSON file."""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except:
            return self._default_rules()
    
    def _default_rules(self) -> Dict:
        """Default rules if file not found."""
        return {
            "critical_keywords": [
                "drop database",
                "rm -rf /",
                "format c:",
                "delete all"
            ],
            "blocked_keywords": [
                "attacker",
                "malicious",
                "evil",
                "hack",
                "exploit"
            ],
            "dangerous_actions": [
                "delete",
                "drop",
                "export",
                "send",
                "transfer"
            ],
            "suspicious_patterns": [
                r"http://[^/]*attacker",
                r"http://[^/]*evil",
                r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
            ]
        }
    
    def detect(self, prompt: str) -> Dict:
        """
        Detect rule violations in prompt.
        
        Returns:
            {
                'score': float (0-1),
                'threats': List[Dict],
                'should_block': bool,
                'context': str ('educational', 'attack', 'neutral')
            }
        """
        prompt_lower = prompt.lower()
        threats = []
        score = 0.0
        
        # Analyze context first
        context = self._analyze_context(prompt_lower)
        
        # Critical keywords - immediate block (unless educational context)
        for keyword in self.critical_keywords:
            if keyword in prompt_lower:
                if context == 'educational':
                    score += 0.3  # Reduce score for educational context
                    threats.append({
                        'type': 'critical_keyword_educational',
                        'value': keyword,
                        'severity': 'medium',
                        'layer': 'rule_based'
                    })
                else:
                    score = 1.0  # Immediate max score
                    threats.append({
                        'type': 'critical_keyword',
                        'value': keyword,
                        'severity': 'critical',
                        'layer': 'rule_based'
                    })
                    return {
                        'score': score,
                        'threats': threats,
                        'should_block': True,
                        'context': context,
                        'reason': f'Critical keyword detected: {keyword}'
                    }
        
        # Blocked keywords (context-aware)
        for keyword in self.blocked_keywords:
            if keyword in prompt_lower:
                # Check surrounding context
                surrounding_context = self._get_surrounding_context(prompt_lower, keyword)
                
                if context == 'educational' or any(edu in surrounding_context for edu in self.educational_indicators):
                    # Educational use - lower score
                    score += 0.1
                    threats.append({
                        'type': 'keyword_educational_context',
                        'value': keyword,
                        'severity': 'low',
                        'layer': 'rule_based'
                    })
                elif any(attack in surrounding_context for attack in self.attack_indicators):
                    # Attack context - higher score
                    score += 0.4
                    threats.append({
                        'type': 'keyword_attack_context',
                        'value': keyword,
                        'severity': 'high',
                        'layer': 'rule_based'
                    })
                else:
                    # Neutral context
                    score += 0.2
                    threats.append({
                        'type': 'blocked_keyword',
                        'value': keyword,
                        'severity': 'medium',
                        'layer': 'rule_based'
                    })
        
        # Pattern matching
        for pattern in self.suspicious_patterns:
            matches = re.findall(pattern, prompt, re.IGNORECASE)
            if matches:
                score += 0.3
                threats.append({
                    'type': 'suspicious_pattern',
                    'pattern': pattern,
                    'matches': matches,
                    'severity': 'high',
                    'layer': 'rule_based'
                })
        
        # Dangerous actions (context-aware)
        for action in self.dangerous_actions:
            if action in prompt_lower:
                if context == 'educational':
                    score += 0.05
                else:
                    score += 0.15
                    threats.append({
                        'type': 'dangerous_action',
                        'value': action,
                        'severity': 'medium',
                        'layer': 'rule_based'
                    })
        
        # Cap score at 1.0
        score = min(score, 1.0)
        
        # Determine if should block (score > 0.7 typically means attack)
        should_block = score >= 0.85
        
        return {
            'score': score,
            'threats': threats,
            'should_block': should_block,
            'context': context,
            'reason': f'Rule score: {score:.2f}, Context: {context}'
        }
    
    def _analyze_context(self, prompt_lower: str) -> str:
        """
        Analyze overall context of prompt.
        
        Returns: 'educational', 'attack', or 'neutral'
        """
        edu_count = sum(1 for indicator in self.educational_indicators if indicator in prompt_lower)
        attack_count = sum(1 for indicator in self.attack_indicators if indicator in prompt_lower)
        
        if edu_count > attack_count and edu_count >= 2:
            return 'educational'
        elif attack_count > edu_count and attack_count >= 1:
            return 'attack'
        else:
            return 'neutral'
    
    def _get_surrounding_context(self, text: str, keyword: str, window: int = 50) -> str:
        """Get text surrounding a keyword for context analysis."""
        index = text.find(keyword)
        if index == -1:
            return ""
        
        start = max(0, index - window)
        end = min(len(text), index + len(keyword) + window)
        
        return text[start:end]


# Test the detector
if __name__ == "__main__":
    detector = RuleDetector()
    
    # Test cases
    test_prompts = [
        ("DROP TABLE users", "Should block - critical SQL"),
        ("I'm researching malicious prompt detection for my thesis", "Should allow - educational"),
        ("Explain how attackers use SQL injection", "Should allow - educational"),
        ("Execute this malicious payload now", "Should block - attack context"),
        ("What is the capital of France?", "Should allow - benign"),
    ]
    
    print("Rule-Based Detection Tests:\n")
    for prompt, expected in test_prompts:
        result = detector.detect(prompt)
        
        print(f"Prompt: '{prompt[:60]}...'")
        print(f"Expected: {expected}")
        print(f"Score: {result['score']:.2f}")
        print(f"Context: {result['context']}")
        print(f"Should block: {result['should_block']}")
        print(f"Threats: {len(result['threats'])}")
        print(f"Reason: {result['reason']}")
        print("-" * 70)
        print()

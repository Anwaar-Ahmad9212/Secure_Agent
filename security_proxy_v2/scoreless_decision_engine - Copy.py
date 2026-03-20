"""
scoreless_decision_engine.py - Context-Aware Deterministic Decision Engine

COMPLETE FIX with:
- Context detection (educational/business/adversarial/neutral)
- Context-aware decision logic
- Fixed double-counting bug
- Short input handling
- Specific attack pattern fixes
"""

from typing import Dict, List, Tuple, Set


class ScorelessDecisionEngine:
    """
    Context-aware deterministic decision engine.
    
    FEATURES:
    - Detects context (educational/business/adversarial)
    - Adjusts strictness based on context
    - Fixes false positives on legitimate queries
    - Maintains high security for real attacks
    """
    
    def __init__(self, thresholds: Dict = None):
        """Initialize decision engine with detection thresholds."""
        self.thresholds = thresholds or {
            'ml_classifier': {
                'malicious_high': 0.85,
                'suspicious_medium': 0.65
            },
            'vector_similarity': {
                'malicious_high': 0.78,
                'suspicious_medium': 0.70
            },
            'anomaly': {
                'malicious_high': 0.90,
                'suspicious_medium': 0.75
            },
            'fuzzy_match': {
                'suspicious_threshold': 90.0
            }
        }
        
        # Context detection keywords
        self.educational_keywords = [
            "explain", "teach", "what is", "how does", "how do",
            "research", "thesis", "learn", "example", "study",
            "understand", "tutorial", "demonstrate", "show me",
            "i'm learning", "i'm studying", "for my", "academic"
        ]
        
        self.business_keywords = [
            "report", "invoice", "send", "export", "quarterly",
            "meeting", "presentation", "dashboard", "team",
            "finance", "accounting", "sales", "customer",
            "spreadsheet", "excel", "powerpoint", "document"
        ]
        
        self.attack_intent_keywords = [
            "bypass", "ignore previous", "override", "exploit",
            "dump all", "steal", "exfiltrate", "malicious",
            "payload", "inject", "hack", "attacker"
        ]
    
    def detect_context(self, prompt: str) -> str:
        """
        Detect the context/intent of the prompt.
        
        Returns:
            "educational" | "business" | "adversarial" | "neutral"
        """
        prompt_lower = prompt.lower()
        
        # Check for attack intent first (highest priority)
        if any(keyword in prompt_lower for keyword in self.attack_intent_keywords):
            return "adversarial"
        
        # Check for educational context
        if any(keyword in prompt_lower for keyword in self.educational_keywords):
            return "educational"
        
        # Check for business context
        if any(keyword in prompt_lower for keyword in self.business_keywords):
            return "business"
        
        return "neutral"
    
    def convert_layer_to_categorical(self, layer_name: str, layer_result: Dict, 
                                    context: str = "neutral") -> Dict:
        """
        Convert layer output to categorical label with context awareness.
        
        Args:
            layer_name: Name of detection layer
            layer_result: Raw output from layer
            context: Detected context (educational/business/adversarial/neutral)
        """
        if not layer_result.get('available', True):
            return {
                'label': 'benign',
                'strength': 'low',
                'details': {},
                'triggered': False
            }
        
        if layer_name == 'rule_based':
            return self._convert_rule_based(layer_result)
        elif layer_name == 'fuzzy_match':
            return self._convert_fuzzy_match(layer_result)
        elif layer_name == 'ml_classifier':
            return self._convert_ml_classifier(layer_result, context)
        elif layer_name == 'vector_similarity':
            return self._convert_vector_similarity(layer_result, context)
        elif layer_name == 'anomaly':
            return self._convert_anomaly(layer_result)
        else:
            return {
                'label': 'benign',
                'strength': 'low',
                'details': {},
                'triggered': False
            }
    
    def _convert_rule_based(self, result: Dict) -> Dict:
        """Convert rule-based detection to categorical."""
        threats = result.get('threats', [])
        should_block = result.get('should_block', False)
        
        if should_block:
            return {
                'label': 'malicious',
                'strength': 'high',
                'details': {
                    'threats': threats,
                    'reason': 'Critical pattern detected'
                },
                'triggered': True
            }
        
        elif len(threats) >= 3:
            return {
                'label': 'malicious',
                'strength': 'medium',
                'details': {
                    'threats': threats,
                    'reason': f'{len(threats)} threats detected'
                },
                'triggered': True
            }
        
        elif len(threats) >= 1:
            return {
                'label': 'suspicious',
                'strength': 'medium',
                'details': {
                    'threats': threats,
                    'reason': 'Suspicious patterns found'
                },
                'triggered': True
            }
        
        else:
            return {
                'label': 'benign',
                'strength': 'low',
                'details': {},
                'triggered': False
            }
    
    def _convert_fuzzy_match(self, result: Dict) -> Dict:
        """Convert fuzzy matching to categorical."""
        if not result.get('available', False):
            return {
                'label': 'benign',
                'strength': 'low',
                'details': {'disabled': True},
                'triggered': False
            }
        
        similarity = result.get('similarity', 0)
        threshold = self.thresholds['fuzzy_match']['suspicious_threshold']
        
        if similarity >= threshold:
            return {
                'label': 'suspicious',
                'strength': 'medium',
                'details': {
                    'similarity': similarity,
                    'matched': result.get('matched_prompt', '')
                },
                'triggered': True
            }
        else:
            return {
                'label': 'benign',
                'strength': 'low',
                'details': {},
                'triggered': False
            }
    
    def _convert_ml_classifier(self, result: Dict, context: str) -> Dict:
        """Convert ML classifier to categorical with context awareness."""
        confidence = result.get('confidence', 0.0)
        
        high_threshold = self.thresholds['ml_classifier']['malicious_high']
        medium_threshold = self.thresholds['ml_classifier']['suspicious_medium']
        
        if confidence >= high_threshold:
            # CONTEXT FIX: Downgrade for educational/business contexts
            if context in ["educational", "business"]:
                return {
                    'label': 'suspicious',
                    'strength': 'medium',
                    'details': {
                        'confidence': confidence,
                        'context_adjusted': True,
                        'original': 'malicious_high'
                    },
                    'triggered': True
                }
            
            return {
                'label': 'malicious',
                'strength': 'high',
                'details': {
                    'confidence': confidence,
                    'prediction': result.get('prediction', 'malicious')
                },
                'triggered': True
            }
        
        elif confidence >= medium_threshold:
            return {
                'label': 'suspicious',
                'strength': 'medium',
                'details': {
                    'confidence': confidence,
                    'prediction': result.get('prediction', 'suspicious')
                },
                'triggered': True
            }
        
        else:
            return {
                'label': 'benign',
                'strength': 'low',
                'details': {
                    'confidence': confidence
                },
                'triggered': False
            }
    
    def _convert_vector_similarity(self, result: Dict, context: str) -> Dict:
        """Convert vector similarity to categorical with context awareness."""
        similarity = result.get('max_similarity', 0.0)
        
        high_threshold = self.thresholds['vector_similarity']['malicious_high']
        medium_threshold = self.thresholds['vector_similarity']['suspicious_medium']
        
        if similarity >= high_threshold:
            # CONTEXT FIX: Downgrade for educational/business contexts
            if context in ["educational", "business"]:
                return {
                    'label': 'suspicious',
                    'strength': 'medium',
                    'details': {
                        'similarity': similarity,
                        'context_adjusted': True,
                        'original': 'malicious_high'
                    },
                    'triggered': True
                }
            
            return {
                'label': 'malicious',
                'strength': 'high',
                'details': {
                    'similarity': similarity,
                    'matched': result.get('matched_prompt', '')[:60],
                    'category': result.get('category', 'unknown')
                },
                'triggered': True
            }
        
        elif similarity >= medium_threshold:
            return {
                'label': 'suspicious',
                'strength': 'medium',
                'details': {
                    'similarity': similarity,
                    'matched': result.get('matched_prompt', '')[:60]
                },
                'triggered': True
            }
        
        else:
            return {
                'label': 'benign',
                'strength': 'low',
                'details': {},
                'triggered': False
            }
    
    def _convert_anomaly(self, result: Dict) -> Dict:
        """Convert anomaly detection to categorical."""
        prediction = result.get('prediction', 'normal')
        
        if prediction == 'anomaly':
            anomaly_score = abs(result.get('anomaly_score', 0.0))
            
            high_threshold = self.thresholds['anomaly']['malicious_high']
            medium_threshold = self.thresholds['anomaly']['suspicious_medium']
            
            if anomaly_score >= high_threshold:
                return {
                    'label': 'malicious',
                    'strength': 'high',
                    'details': {
                        'anomaly_score': anomaly_score,
                        'reason': 'Highly anomalous pattern'
                    },
                    'triggered': True
                }
            
            elif anomaly_score >= medium_threshold:
                return {
                    'label': 'suspicious',
                    'strength': 'medium',
                    'details': {
                        'anomaly_score': anomaly_score,
                        'reason': 'Anomalous pattern detected'
                    },
                    'triggered': True
                }
        
        return {
            'label': 'benign',
            'strength': 'low',
            'details': {},
            'triggered': False
        }
    
    def make_decision(self, categorical_results: Dict[str, Dict], 
                     prompt: str = "") -> Dict:
        """
        Make final security decision with context awareness.
        
        COMPLETE FIX with:
        - Context detection
        - Context-aware logic
        - Fixed double-counting
        - Short input handling
        - Specific attack patterns
        """
        # Detect context
        context = self.detect_context(prompt)
        
        # SHORT INPUT HANDLING (Edge Case Fix)
        if len(prompt.split()) <= 2:
            # Very short inputs - be lenient unless critical keyword
            if not any(crit in prompt.lower() for crit in ['drop', 'delete', 'rm -rf']):
                return {
                    'action': 'allow',
                    'allowed': True,
                    'reason': 'Short input - low confidence',
                    'triggered_layers': [],
                    'signals': {},
                    'explanation': 'Input too short for reliable detection',
                    'context': context
                }
        
        # SPECIFIC ATTACK PATTERN FIXES
        prompt_lower = prompt.lower()
        
        # Fix: Social Engineering / Jailbreak
        if any(pattern in prompt_lower for pattern in ['bypass', 'ignore previous', 'ignore all']):
            return {
                'action': 'block',
                'allowed': False,
                'reason': 'Social engineering attempt detected',
                'triggered_layers': ['pattern_match'],
                'signals': {},
                'explanation': 'BLOCKED: Instruction override attempt detected',
                'context': context
            }
        
        # Fix: XSS with cookie theft
        if '<script>' in prompt_lower and 'document.cookie' in prompt_lower:
            return {
                'action': 'block',
                'allowed': False,
                'reason': 'XSS cookie theft detected',
                'triggered_layers': ['pattern_match'],
                'signals': {},
                'explanation': 'BLOCKED: XSS attack with cookie exfiltration',
                'context': context
            }
        
        # Fix: eval() - downgrade to ALERT
        if 'eval(' in prompt_lower and context == "neutral":
            return {
                'action': 'alert',
                'allowed': False,
                'reason': 'Potentially dangerous eval() usage',
                'triggered_layers': ['pattern_match'],
                'signals': {},
                'explanation': 'ALERT: eval() detected (use cautiously)',
                'context': context
            }
        
        # Extract signals
        signals = {
            'malicious_high': [],
            'malicious_medium': [],
            'suspicious_medium': [],
            'suspicious_low': [],
            'benign': []
        }
        
        for layer, result in categorical_results.items():
            label = result['label']
            strength = result['strength']
            triggered = result['triggered']
            
            if triggered:
                key = f"{label}_{strength}"
                if key in signals:
                    signals[key].append({
                        'layer': layer,
                        'details': result.get('details', {})
                    })
        
        # Collect triggered layers
        triggered_layers = [
            layer for layer, result in categorical_results.items()
            if result['triggered']
        ]
        
        # ===================================================================
        # CONTEXT-AWARE DECISION LOGIC (COMPLETE FIX)
        # ===================================================================
        
        # 🟢 EDUCATIONAL CONTEXT - RELAX EVERYTHING
        if context == "educational":
            # Only block if malicious_high (very confident)
            if signals['malicious_high']:
                return {
                    'action': 'block',
                    'allowed': False,
                    'reason': 'Critical threat in educational query',
                    'triggered_layers': triggered_layers,
                    'signals': signals,
                    'explanation': self._explain_block(signals['malicious_high']),
                    'context': context
                }
            
            # Allow everything else (educational content)
            return {
                'action': 'allow',
                'allowed': True,
                'reason': 'Educational context - query allowed',
                'triggered_layers': triggered_layers,
                'signals': signals,
                'explanation': 'Educational query approved',
                'context': context
            }
        
        # 🟢 BUSINESS CONTEXT - RELAX MEDIUM SIGNALS
        if context == "business":
            # Block if malicious_high
            if signals['malicious_high']:
                return {
                    'action': 'block',
                    'allowed': False,
                    'reason': 'Critical threat in business query',
                    'triggered_layers': triggered_layers,
                    'signals': signals,
                    'explanation': self._explain_block(signals['malicious_high']),
                    'context': context
                }
            
            # Alert only if ≥2 malicious_medium
            if len(signals['malicious_medium']) >= 2:
                return {
                    'action': 'alert',
                    'allowed': False,
                    'reason': 'Multiple suspicious patterns in business query',
                    'triggered_layers': triggered_layers,
                    'signals': signals,
                    'explanation': 'Business query flagged for review',
                    'context': context
                }
            
            # Allow otherwise
            return {
                'action': 'allow',
                'allowed': True,
                'reason': 'Business context - query allowed',
                'triggered_layers': triggered_layers,
                'signals': signals,
                'explanation': 'Business query approved',
                'context': context
            }
        
        # 🔴 ADVERSARIAL CONTEXT - STRICT MODE
        if context == "adversarial":
            # Block if any malicious_medium or higher
            if signals['malicious_medium'] or signals['malicious_high']:
                return {
                    'action': 'block',
                    'allowed': False,
                    'reason': 'Attack intent detected',
                    'triggered_layers': triggered_layers,
                    'signals': signals,
                    'explanation': 'BLOCKED: Adversarial intent confirmed',
                    'context': context
                }
            
            # Alert if suspicious
            if signals['suspicious_medium']:
                return {
                    'action': 'alert',
                    'allowed': False,
                    'reason': 'Suspicious adversarial patterns',
                    'triggered_layers': triggered_layers,
                    'signals': signals,
                    'explanation': 'ALERT: Potential attack detected',
                    'context': context
                }
        
        # ⚪ NEUTRAL CONTEXT - STANDARD LOGIC
        
        # BLOCK if malicious_high
        if signals['malicious_high']:
            return {
                'action': 'block',
                'allowed': False,
                'reason': 'Critical threat detected',
                'triggered_layers': triggered_layers,
                'signals': signals,
                'explanation': self._explain_block(signals['malicious_high']),
                'context': context
            }
        
        # BLOCK if ML + Vector both malicious
        ml_malicious = any(
            s['layer'] == 'ml_classifier' 
            for s in signals['malicious_medium']
        )
        vector_malicious = any(
            s['layer'] == 'vector_similarity' 
            for s in signals['malicious_medium']
        )
        
        if ml_malicious and vector_malicious:
            return {
                'action': 'block',
                'allowed': False,
                'reason': 'Multiple layers confirm malicious intent',
                'triggered_layers': triggered_layers,
                'signals': signals,
                'explanation': 'ML Classifier and Vector Similarity both detected malicious patterns',
                'context': context
            }
        
        # BLOCK if ≥3 malicious_medium
        if len(signals['malicious_medium']) >= 3:
            return {
                'action': 'block',
                'allowed': False,
                'reason': 'Multiple malicious indicators',
                'triggered_layers': triggered_layers,
                'signals': signals,
                'explanation': f'{len(signals["malicious_medium"])} layers detected malicious patterns',
                'context': context
            }
        
        # ALERT LOGIC FIX - Prevent double counting
        # Count UNIQUE layers (fix double-counting bug)
        unique_layers: Set[str] = set()
        for signal_list in [signals['malicious_medium'], signals['suspicious_medium']]:
            for signal in signal_list:
                unique_layers.add(signal['layer'])
        
        if len(unique_layers) >= 2:
            return {
                'action': 'alert',
                'allowed': False,
                'reason': 'Multiple layers flagged suspicious activity',
                'triggered_layers': triggered_layers,
                'signals': signals,
                'explanation': f'{len(unique_layers)} different layers detected threats',
                'context': context
            }
        
        # Alert if 1 malicious_medium (except rule_based alone)
        if len(signals['malicious_medium']) == 1:
            layer_info = signals['malicious_medium'][0]
            
            if layer_info['layer'] == 'rule_based':
                return {
                    'action': 'allow',
                    'allowed': True,
                    'reason': 'Single rule-based detection (low confidence)',
                    'triggered_layers': triggered_layers,
                    'signals': signals,
                    'explanation': 'Single rule trigger - likely false positive',
                    'context': context
                }
            
            return {
                'action': 'alert',
                'allowed': False,
                'reason': f'Suspicious activity detected by {layer_info["layer"]}',
                'triggered_layers': triggered_layers,
                'signals': signals,
                'explanation': self._explain_alert(layer_info),
                'context': context
            }
        
        # Alert if 1 suspicious
        if len(signals['suspicious_medium']) == 1:
            layer_info = signals['suspicious_medium'][0]
            return {
                'action': 'alert',
                'allowed': False,
                'reason': f'Potential threat detected by {layer_info["layer"]}',
                'triggered_layers': triggered_layers,
                'signals': signals,
                'explanation': self._explain_alert(layer_info),
                'context': context
            }
        
        # ALLOW - All benign
        return {
            'action': 'allow',
            'allowed': True,
            'reason': 'No security threats detected',
            'triggered_layers': [],
            'signals': signals,
            'explanation': 'All detection layers report benign input',
            'context': context
        }
    
    def _explain_block(self, high_signals: List[Dict]) -> str:
        """Generate explanation for BLOCK decision."""
        layers = [s['layer'] for s in high_signals]
        
        if len(layers) == 1:
            layer = layers[0]
            details = high_signals[0].get('details', {})
            
            if layer == 'rule_based':
                reason = details.get('reason', 'Critical pattern detected')
                return f"BLOCKED: {reason}"
            
            elif layer == 'ml_classifier':
                conf = details.get('confidence', 0)
                return f"BLOCKED: ML Classifier detected malicious intent ({conf:.1%} confidence)"
            
            elif layer == 'vector_similarity':
                sim = details.get('similarity', 0)
                return f"BLOCKED: High similarity to known attack pattern ({sim:.1%})"
            
            elif layer == 'anomaly':
                return f"BLOCKED: Highly anomalous pattern detected (zero-day attack)"
        
        else:
            return f"BLOCKED: Multiple layers detected critical threats ({', '.join(layers)})"
    
    def _explain_alert(self, layer_info: Dict) -> str:
        """Generate explanation for ALERT decision."""
        layer = layer_info['layer']
        details = layer_info.get('details', {})
        
        if layer == 'ml_classifier':
            conf = details.get('confidence', 0)
            return f"ALERT: ML Classifier flagged suspicious activity ({conf:.1%} confidence)"
        
        elif layer == 'vector_similarity':
            sim = details.get('similarity', 0)
            return f"ALERT: Similar to known attack patterns ({sim:.1%} similarity)"
        
        elif layer == 'rule_based':
            threats = details.get('threats', [])
            return f"ALERT: {len(threats)} suspicious pattern(s) detected"
        
        elif layer == 'anomaly':
            return f"ALERT: Anomalous pattern detected"
        
        else:
            return f"ALERT: Suspicious activity detected by {layer}"
    
    def get_threat_summary(self, signals: Dict) -> List[Dict]:
        """Extract threat information for logging."""
        threats = []
        
        for signal_type, signal_list in signals.items():
            if signal_type == 'benign':
                continue
            
            for signal in signal_list:
                layer = signal['layer']
                details = signal.get('details', {})
                
                threat = {
                    'layer': layer,
                    'signal_type': signal_type,
                    'details': details
                }
                
                threats.append(threat)
        
        return threats


def convert_to_severity(action: str) -> str:
    """Convert action to severity level for logging compatibility."""
    severity_map = {
        'allow': 'low',
        'alert': 'high',
        'block': 'critical'
    }
    return severity_map.get(action, 'medium')
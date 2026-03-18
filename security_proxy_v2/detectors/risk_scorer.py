"""
risk_scorer.py - Layer 6: Hybrid Risk Scoring

Combines all detection layers into final risk score.
"""

from typing import Dict, List


class RiskScorer:
    """
    Layer 6: Hybrid risk scoring and decision making.
    
    Combines:
    - Rule-based score
    - Fuzzy matching score
    - ML probability score
    - Vector similarity score
    - Anomaly detection score
    
    Into final risk score (0-100).
    """
    
    def __init__(self, weights: Dict[str, float] = None):
        """
        Initialize risk scorer.
        
        Args:
            weights: Layer weights (default if None)
        """
        self.weights = weights or {
            'rule_based': 30.0,      # Fast, deterministic
            'fuzzy_match': 15.0,     # Typo detection
            'ml_classifier': 25.0,   # ML probability
            'vector_similarity': 25.0,  # Semantic similarity
            'anomaly': 5.0           # Zero-day detection
        }
        
        # Decision thresholds
        self.block_threshold = 70.0
        self.alert_threshold = 40.0
    
    def calculate_risk(self, layer_results: Dict) -> Dict:
        """
        Calculate final risk score from all layers.
        
        Args:
            layer_results: {
                'rule_based': {...},
                'fuzzy_match': {...},
                'ml_classifier': {...},
                'vector_similarity': {...},
                'anomaly': {...}
            }
            
        Returns:
            {
                'risk_score': float (0-100),
                'action': str ('allow', 'alert', 'block'),
                'layer_scores': Dict,
                'threats': List,
                'explanation': str
            }
        """
        layer_scores = {}
        total_risk = 0.0
        all_threats = []
        
        # Calculate weighted score for each layer
        for layer_name, weight in self.weights.items():
            result = layer_results.get(layer_name, {})
            
            if result.get('available', True):
                score = result.get('score', 0.0)
                layer_scores[layer_name] = score * weight
                total_risk += layer_scores[layer_name]
                
                # Collect threats
                if 'threats' in result:
                    all_threats.extend(result['threats'])
            else:
                layer_scores[layer_name] = 0.0
        
        # Determine action
        if total_risk >= self.block_threshold:
            action = 'block'
        elif total_risk >= self.alert_threshold:
            action = 'alert'
        else:
            action = 'allow'
        
        # Generate explanation
        explanation = self._generate_explanation(layer_scores, total_risk, action)
        
        return {
            'risk_score': total_risk,
            'action': action,
            'layer_scores': layer_scores,
            'threats': all_threats,
            'explanation': explanation,
            'thresholds': {
                'block': self.block_threshold,
                'alert': self.alert_threshold
            }
        }
    
    def _generate_explanation(self, layer_scores: Dict, total_risk: float, action: str) -> str:
        """Generate human-readable explanation."""
        # Find dominant layer
        dominant_layer = max(layer_scores, key=layer_scores.get)
        dominant_score = layer_scores[dominant_layer]
        
        explanations = []
        
        if action == 'block':
            explanations.append(f"HIGH RISK ({total_risk:.1f}/100)")
        elif action == 'alert':
            explanations.append(f"MEDIUM RISK ({total_risk:.1f}/100)")
        else:
            explanations.append(f"LOW RISK ({total_risk:.1f}/100)")
        
        # Add dominant layer info
        if dominant_score > 0:
            layer_readable = dominant_layer.replace('_', ' ').title()
            explanations.append(f"Primary detection: {layer_readable} ({dominant_score:.1f} points)")
        
        # Add layer breakdown
        active_layers = [name for name, score in layer_scores.items() if score > 0]
        if len(active_layers) > 1:
            explanations.append(f"Active layers: {len(active_layers)}")
        
        return " | ".join(explanations)

"""
ml_classifier.py - Layer 3: ML Classification

Uses trained XGBoost model to predict malicious probability.
"""

import os
import pickle
import numpy as np
from typing import Dict

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("⚠️  XGBoost not available. Install: pip install xgboost")


class MLClassifier:
    """
    Layer 3: ML-based classification using XGBoost.
    
    Predicts probability that a prompt is malicious based on features.
    """
    
    def __init__(self, model_path: str = None):
        """Initialize ML classifier."""
        self.model = None
        self.available = XGBOOST_AVAILABLE
        
        if model_path and os.path.exists(model_path):
            self._load_model(model_path)
        else:
            self.available = False
    
    def _load_model(self, path: str):
        """Load trained model from disk."""
        try:
            with open(path, 'rb') as f:
                self.model = pickle.load(f)
            self.available = True
        except Exception as e:
            print(f"⚠️  Failed to load ML model: {e}")
            self.available = False
    
    def detect(self, features: np.ndarray) -> Dict:
        """
        Classify prompt using ML model.
        
        Args:
            features: Feature array from FeatureExtractor
            
        Returns:
            {
                'score': float (0-1),
                'probability': float,
                'confidence': float,
                'prediction': int (0 or 1)
            }
        """
        if not self.available or self.model is None:
            return {
                'score': 0.0,
                'probability': 0.0,
                'confidence': 0.0,
                'prediction': 0,
                'available': False
            }
        
        try:
            # Predict probability
            features_reshaped = features.reshape(1, -1)
            probability = self.model.predict_proba(features_reshaped)[0][1]
            
            # Binary prediction
            prediction = 1 if probability >= 0.5 else 0
            
            # Confidence (distance from 0.5)
            confidence = abs(probability - 0.5) * 2
            
            return {
                'score': probability,
                'probability': probability,
                'confidence': confidence,
                'prediction': prediction,
                'available': True
            }
        except Exception as e:
            return {
                'score': 0.0,
                'probability': 0.0,
                'confidence': 0.0,
                'prediction': 0,
                'available': False,
                'error': str(e)
            }

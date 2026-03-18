"""
anomaly_detector.py - Layer 5: Anomaly Detection

Detects zero-day attacks using Isolation Forest.
"""

import os
import pickle
import numpy as np
from typing import Dict

try:
    from sklearn.ensemble import IsolationForest
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class AnomalyDetector:
    """
    Layer 5: Anomaly detection for zero-day attacks.
    
    Uses Isolation Forest trained on benign prompts.
    """
    
    def __init__(self, model_path: str = None):
        """Initialize anomaly detector."""
        self.model = None
        self.available = SKLEARN_AVAILABLE
        
        if model_path and os.path.exists(model_path):
            self._load_model(model_path)
        else:
            self.available = False
    
    def _load_model(self, path: str):
        """Load trained model."""
        try:
            with open(path, 'rb') as f:
                self.model = pickle.load(f)
            self.available = True
        except:
            self.available = False
    
    def detect(self, features: np.ndarray) -> Dict:
        """
        Detect if prompt is anomalous.
        
        Returns:
            {
                'score': float (0-1),
                'is_anomaly': bool,
                'anomaly_score': float
            }
        """
        if not self.available or self.model is None:
            return {
                'score': 0.0,
                'is_anomaly': False,
                'anomaly_score': 0.0,
                'available': False
            }
        
        try:
            features_reshaped = features.reshape(1, -1)
            
            # Predict (-1 = anomaly, 1 = normal)
            prediction = self.model.predict(features_reshaped)[0]
            is_anomaly = prediction == -1
            
            # Get anomaly score
            anomaly_score = self.model.score_samples(features_reshaped)[0]
            
            # Normalize score to 0-1
            score = 0.5 if is_anomaly else 0.0
            
            return {
                'score': score,
                'is_anomaly': is_anomaly,
                'anomaly_score': anomaly_score,
                'available': True
            }
        except:
            return {
                'score': 0.0,
                'is_anomaly': False,
                'anomaly_score': 0.0,
                'available': False
            }

"""
security_proxy_v2.py - Advanced ML-Based Security Proxy (JSON SERIALIZATION FIXED)

Multi-layer hybrid detection system with logging support.
"""

import json
import sys
import os
import numpy as np  # ← Added for type conversion
from flask import Flask, request, jsonify
from flask_cors import CORS

# Add paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# Import logging utility (from old security folder)
try:
    security_dir = os.path.join(os.path.dirname(BASE_DIR), 'security')
    sys.path.insert(0, security_dir)
    from log_utils import log_event
    LOGGING_AVAILABLE = True
    print("✅ Logging module loaded")
except ImportError as e:
    LOGGING_AVAILABLE = False
    print(f"⚠️  Logging not available: {e}")
    def log_event(*args, **kwargs):
        pass  # Dummy function

# Import detectors
from detectors import (
    RuleDetector,
    FuzzyDetector,
    MLClassifier,
    VectorDetector,
    AnomalyDetector,
    RiskScorer
)
from utils import FeatureExtractor

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


# ============================================================================
# JSON SERIALIZATION HELPER
# ============================================================================

def convert_to_json_serializable(obj):
    """
    Convert NumPy types to native Python types for JSON serialization.
    
    Fixes: TypeError: Object of type float32 is not JSON serializable
    """
    if isinstance(obj, (np.integer, np.int8, np.int16, np.int32, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float16, np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_to_json_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_to_json_serializable(item) for item in obj]
    else:
        return obj


# ============================================================================
# SECURITY PROXY CLASS
# ============================================================================

class SecurityProxyV2:
    """Advanced security proxy with multi-layer detection and logging."""
    
    def __init__(self, config_path: str = None):
        """Initialize security proxy with all detectors."""
        print("\n" + "="*70)
        print("🔧 Initializing Advanced Security Proxy V2")
        print("="*70 + "\n")
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Initialize feature extractor
        print("📊 Initializing feature extractor...")
        self.feature_extractor = FeatureExtractor()
        print("✅ Feature extractor ready\n")
        
        # Initialize all detection layers
        self._initialize_detectors()
        
        print("="*70)
        print("✅ Security Proxy V2 Initialized Successfully")
        print("="*70 + "\n")
    
    def _load_config(self, path: str) -> dict:
        """Load configuration from JSON."""
        default_config = {
            "vector_db": {
                "path": "../security/vector_db",
                "collection_name": "unified_malicious_prompts",
                "model_name": "all-MiniLM-L6-v2",
                "similarity_threshold": 0.65  # Lowered threshold
            },
            "fuzzy_matching": {
                "enabled": True,
                "threshold": 85.0,
                "malicious_prompts_path": "../security/embeddings/malicious_prompts_combined.json"
            },
            "ml_classifier": {
                "enabled": True,
                "model_path": "models/xgboost_model.pkl"
            },
            "anomaly_detection": {
                "enabled": True  # Enabled anomaly detection
            },
            "risk_thresholds": {
                "block": 70.0,
                "alert": 40.0
            }
        }
        
        config_file = path or os.path.join(BASE_DIR, 'config', 'detection_config.json')
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    loaded = json.load(f)
                    # Merge with defaults
                    for key in default_config:
                        if key in loaded:
                            if isinstance(default_config[key], dict):
                                default_config[key].update(loaded[key])
                            else:
                                default_config[key] = loaded[key]
            except Exception as e:
                print(f"⚠️  Error loading config: {e}, using defaults")
        
        return default_config
    
    def _initialize_detectors(self):
        """Initialize all detection layers."""
        # Layer 1: Rule-based
        print("⚙️  Layer 1: Rule-Based Detector...")
        self.rule_detector = RuleDetector()
        print("   ✅ Rule-based detection ready")
        
        # Layer 2: Fuzzy matching
        print("⚙️  Layer 2: Fuzzy Matching Detector...")
        fuzzy_config = self.config.get('fuzzy_matching', {})
        fuzzy_path = fuzzy_config.get('malicious_prompts_path')
        if fuzzy_path and not os.path.isabs(fuzzy_path):
            fuzzy_path = os.path.join(BASE_DIR, fuzzy_path)
        
        self.fuzzy_detector = FuzzyDetector(
            malicious_prompts_path=fuzzy_path,
            similarity_threshold=fuzzy_config.get('threshold', 85.0)
        )
        if self.fuzzy_detector.available:
            print("   ✅ Fuzzy matching ready")
        else:
            print("   ⚠️  Fuzzy matching unavailable (install rapidfuzz)")
        
        # Layer 3: ML Classifier
        print("⚙️  Layer 3: ML Classifier...")
        ml_config = self.config.get('ml_classifier', {})
        ml_path = ml_config.get('model_path')
        if ml_path and not os.path.isabs(ml_path):
            ml_path = os.path.join(BASE_DIR, ml_path)
        
        self.ml_classifier = MLClassifier(model_path=ml_path)
        if self.ml_classifier.available:
            print("   ✅ ML classifier ready")
        else:
            print("   ⚠️  ML classifier unavailable (model not trained)")
        
        # Layer 4: Vector similarity
        print("⚙️  Layer 4: Vector Similarity Detector...")
        vector_config = self.config.get('vector_db', {})
        db_path = vector_config.get('path', '../security/vector_db')
        
        # Resolve path
        if not os.path.isabs(db_path):
            db_path = os.path.join(BASE_DIR, db_path)
        
        print(f"   Vector DB path: {db_path}")
        
        self.vector_detector = VectorDetector(
            db_path=db_path,
            collection_name=vector_config.get('collection_name', 'unified_malicious_prompts'),
            model_name=vector_config.get('model_name', 'all-MiniLM-L6-v2'),
            similarity_threshold=vector_config.get('similarity_threshold', 0.65)
        )
        if self.vector_detector.available:
            try:
                count = self.vector_detector.collection.count()
                print(f"   ✅ Vector similarity ready ({count:,} embeddings)")
            except:
                print("   ✅ Vector similarity ready")
        else:
            print("   ⚠️  Vector similarity unavailable (ChromaDB not found)")
        
        # Layer 5: Anomaly detection (optional)
        print("⚙️  Layer 5: Anomaly Detector...")
        anomaly_config = self.config.get('anomaly_detection', {})
        if anomaly_config.get('enabled', False):
            anomaly_path = anomaly_config.get('model_path')
            if anomaly_path and not os.path.isabs(anomaly_path):
                anomaly_path = os.path.join(BASE_DIR, anomaly_path)
            self.anomaly_detector = AnomalyDetector(model_path=anomaly_path)
            if self.anomaly_detector.available:
                print("   ✅ Anomaly detection ready")
            else:
                print("   ⚠️  Anomaly detection unavailable (model not trained)")
        else:
            self.anomaly_detector = None
            print("   ⊝  Anomaly detection disabled")
        
        # Layer 6: Risk scorer
        print("⚙️  Layer 6: Risk Scorer...")
        weights_path = os.path.join(BASE_DIR, 'config', 'weights.json')
        weights = None
        if os.path.exists(weights_path):
            try:
                with open(weights_path, 'r') as f:
                    data = json.load(f)
                    weights = data.get('layer_weights')
            except:
                pass
        
        self.risk_scorer = RiskScorer(weights=weights)
        print("   ✅ Risk scorer ready\n")
    
    def validate(self, prompt: str, source: str = "unknown") -> dict:
        """Validate prompt through all detection layers."""
        import time
        start_time = time.time()
        
        layer_results = {}
        
        # Layer 1: Rule-based detection
        layer_results['rule_based'] = self.rule_detector.detect(prompt)
        
        # Early exit if critical threat detected
        if layer_results['rule_based'].get('should_block', False):
            elapsed_ms = (time.time() - start_time) * 1000
            result = {
                'allowed': False,
                'action': 'block',
                'risk_score': 100.0,
                'layer_scores': {'rule_based': 100.0},
                'threats': layer_results['rule_based'].get('threats', []),
                'explanation': 'Critical threat detected by rules',
                'detection_time_ms': float(elapsed_ms),
                'early_exit': 'rule_based',
                'source': source
            }
            
            # Log the event
            if LOGGING_AVAILABLE:
                self._log_validation(prompt, result, source)
            
            return convert_to_json_serializable(result)  # ← Convert before return
        
        # Layer 2: Fuzzy matching
        layer_results['fuzzy_match'] = self.fuzzy_detector.detect(prompt)
        
        # Extract features for ML layers
        features_dict = self.feature_extractor.extract_all_features(prompt)
        features_array = self.feature_extractor.features_to_array(features_dict)
        
        # Layer 3: ML classification
        layer_results['ml_classifier'] = self.ml_classifier.detect(features_array)
        
        # Layer 4: Vector similarity
        vector_result = self.vector_detector.detect(prompt)
        layer_results['vector_similarity'] = vector_result
        
        # Debug output
        if vector_result.get('available', False):
            sim = vector_result.get('max_similarity', 0)
            threshold = vector_result.get('threshold', 0.65)
            print(f"[DEBUG] Vector similarity: {sim:.3f} (threshold: {threshold:.2f})")
            if sim >= threshold:
                print(f"[DEBUG] Vector match: {vector_result.get('matched_prompt', '')[:60]}...")
        
        # Layer 5: Anomaly detection (if enabled)
        if self.anomaly_detector:
            layer_results['anomaly'] = self.anomaly_detector.detect(features_array)
        else:
            layer_results['anomaly'] = {'score': 0.0, 'available': False}
        
        # Layer 6: Calculate final risk score
        risk_result = self.risk_scorer.calculate_risk(layer_results)
        
        # Calculate detection time
        elapsed_ms = (time.time() - start_time) * 1000
        
        # Build final result (CONVERT ALL NUMPY TYPES!)
        result = {
            'allowed': risk_result['action'] == 'allow',
            'action': risk_result['action'],
            'risk_score': float(risk_result['risk_score']),  # ← Convert to native float
            'layer_scores': convert_to_json_serializable(risk_result['layer_scores']),  # ← Convert dict
            'threats': convert_to_json_serializable(risk_result['threats']),  # ← Convert list
            'explanation': risk_result['explanation'],
            'detection_time_ms': float(elapsed_ms),  # ← Convert to native float
            'thresholds': convert_to_json_serializable(risk_result['thresholds']),  # ← Convert dict
            'source': source
        }
        
        # Log the event
        if LOGGING_AVAILABLE:
            self._log_validation(prompt, result, source)
        
        return result  # Already converted above
    
    def _log_validation(self, prompt: str, result: dict, source: str):
        """Log validation event to logs.json."""
        try:
            action = 'blocked' if result['action'] == 'block' else 'allowed'
            
            # Ensure all values are JSON-serializable
            metadata = {
                'risk_score': float(result['risk_score']),
                'layer_scores': convert_to_json_serializable(result['layer_scores']),
                'threats': convert_to_json_serializable(result['threats']),
                'detection_time_ms': float(result['detection_time_ms'])
            }
            
            log_event(
                source=source,
                prompt=prompt,
                action=action,
                reason=result['explanation'],
                tool=source,
                severity=self._get_severity_from_risk(float(result['risk_score'])),
                metadata=metadata
            )
        except Exception as e:
            print(f"⚠️  Logging error: {e}")
            import traceback
            traceback.print_exc()
    
    def _get_severity_from_risk(self, risk_score: float) -> str:
        """Convert risk score to severity level."""
        if risk_score >= 70:
            return 'critical'
        elif risk_score >= 40:
            return 'high'
        elif risk_score >= 20:
            return 'medium'
        else:
            return 'low'


# Initialize global proxy instance
proxy = SecurityProxyV2()


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "security-proxy-v2",
        "version": "2.0.0"
    })


@app.route('/validate', methods=['POST'])
def validate_endpoint():
    """Validate a prompt through all detection layers."""
    data = request.get_json()
    
    if not data or 'prompt' not in data:
        return jsonify({"error": "Missing 'prompt' in request"}), 400
    
    prompt = data['prompt']
    source = data.get('source', 'unknown')
    
    # Validate through all layers
    result = proxy.validate(prompt, source)
    
    return jsonify(result)  # Result already converted to JSON-serializable


@app.route('/secure/agent', methods=['POST'])
def secure_agent():
    """Validate AI agent request."""
    data = request.get_json()
    
    if not data or 'prompt' not in data:
        return jsonify({"error": "Missing 'prompt' in request"}), 400
    
    prompt = data['prompt']
    result = proxy.validate(prompt, source='ai_agent')
    
    if result['action'] == 'block':
        return jsonify({
            "status": "blocked",
            "message": "Request blocked by security policy",
            "validation": result
        }), 403
    elif result['action'] == 'alert':
        return jsonify({
            "status": "alerted",
            "message": "Request flagged as suspicious but allowed",
            "validation": result
        }), 200
    else:
        return jsonify({
            "status": "allowed",
            "message": "Request validated",
            "validation": result
        }), 200


@app.route('/secure/n8n', methods=['POST'])
def secure_n8n():
    """Validate n8n workflow request."""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Missing request body"}), 400
    
    prompt = data.get('message') or data.get('prompt') or data.get('text') or str(data)
    result = proxy.validate(prompt, source='n8n')
    
    if result['action'] == 'block':
        return jsonify({
            "status": "blocked",
            "message": "Request blocked by security policy",
            "validation": result
        }), 403
    else:
        return jsonify({
            "status": "allowed",
            "message": "Request validated",
            "validation": result
        }), 200


@app.route('/stats', methods=['GET'])
def stats():
    """Get detector statistics."""
    vector_count = 0
    try:
        if proxy.vector_detector.available:
            vector_count = proxy.vector_detector.collection.count()
    except:
        pass
    
    return jsonify({
        "detectors": {
            "rule_based": {"available": True},
            "fuzzy_match": {"available": proxy.fuzzy_detector.available},
            "ml_classifier": {"available": proxy.ml_classifier.available},
            "vector_similarity": {
                "available": proxy.vector_detector.available,
                "embeddings_count": vector_count
            },
            "anomaly": {"available": proxy.anomaly_detector.available if proxy.anomaly_detector else False}
        },
        "config": proxy.config,
        "logging": {"available": LOGGING_AVAILABLE}
    })


if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════╗
║         Advanced Security Proxy V2.0                       ║
║         Multi-Layer ML-Based Detection System              ║
║                                                            ║
║  Running on: http://localhost:5001                         ║
║                                                            ║
║  Detection Layers:                                         ║
║  ├─ Layer 1: Rule-Based (1-2ms)                            ║
║  ├─ Layer 2: Fuzzy Matching (3-5ms)                        ║
║  ├─ Layer 3: ML Classification (5-8ms)                     ║
║  ├─ Layer 4: Vector Similarity (10-15ms)                   ║
║  ├─ Layer 5: Anomaly Detection (2-3ms, optional)           ║
║  └─ Layer 6: Risk Scoring (1ms)                            ║
║                                                            ║
║  Endpoints:                                                ║
║  - POST /validate      : Validate any prompt               ║
║  - POST /secure/agent  : Validate AI agent requests        ║
║  - POST /secure/n8n    : Validate n8n workflow requests    ║
║  - GET  /stats         : Detector statistics               ║
║  - GET  /health        : Health check                      ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    app.run(host='0.0.0.0', port=5001, debug=False)  # ← debug=False for stability
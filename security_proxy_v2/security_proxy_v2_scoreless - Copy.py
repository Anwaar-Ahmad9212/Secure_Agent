"""
security_proxy_v2_scoreless.py - Security Proxy with Scoreless Decision Engine (FIXED)

Uses deterministic categorical decision making instead of weighted risk scoring.
All other functionality (logging, layers, etc.) remains intact.

FIXED: JSON serialization error for NumPy float32 types
"""

import json
import sys
import os
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS

# Add paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# Import logging utility
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
        pass

# Import detectors (reusing existing ones)
from detectors import (
    RuleDetector,
    FuzzyDetector,
    MLClassifier,
    VectorDetector,
    AnomalyDetector
)
from utils import FeatureExtractor

# Import scoreless decision engine
from scoreless_decision_engine import (
    ScorelessDecisionEngine,
    convert_to_severity
)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


# JSON serialization helper - ENHANCED
def convert_to_json_serializable(obj):
    """Convert NumPy types and other non-serializable objects to native Python types."""
    if obj is None:
        return None
    elif isinstance(obj, (np.integer, np.int8, np.int16, np.int32, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float16, np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_to_json_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_to_json_serializable(item) for item in obj]
    elif isinstance(obj, set):
        return [convert_to_json_serializable(item) for item in obj]
    elif hasattr(obj, '__dict__'):
        # For custom objects, try to convert their __dict__
        return convert_to_json_serializable(obj.__dict__)
    else:
        return obj


class SecurityProxyV2Scoreless:
    """Security proxy with scoreless decision engine."""
    
    def __init__(self, config_path: str = None):
        """Initialize security proxy with all detectors."""
        print("\n" + "="*70)
        print("🔧 Initializing Security Proxy V2 (Scoreless)")
        print("="*70 + "\n")
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Initialize feature extractor
        print("📊 Initializing feature extractor...")
        self.feature_extractor = FeatureExtractor()
        print("✅ Feature extractor ready\n")
        
        # Initialize all detection layers
        self._initialize_detectors()
        
        # Initialize scoreless decision engine
        print("🧠 Initializing Scoreless Decision Engine...")
        self.decision_engine = ScorelessDecisionEngine(
            thresholds=self.config.get('categorical_thresholds', None)
        )
        print("✅ Scoreless decision engine ready\n")
        
        print("="*70)
        print("✅ Security Proxy V2 (Scoreless) Initialized Successfully")
        print("="*70 + "\n")
    
    def _load_config(self, path: str) -> dict:
        """Load configuration from JSON."""
        default_config = {
            "vector_db": {
                "path": "../security/vector_db",
                "collection_name": "unified_malicious_prompts",
                "model_name": "all-MiniLM-L6-v2",
                "similarity_threshold": 0.68
            },
            "fuzzy_matching": {
                "enabled": False,
                "threshold": 85.0,
                "malicious_prompts_path": "../security/embeddings/malicious_prompts_combined.json"
            },
            "ml_classifier": {
                "enabled": True,
                "model_path": "models/xgboost_model.pkl"
            },
            "anomaly_detection": {
                "enabled": True,
                "model_path": "models/anomaly_model.pkl"
            },
            "categorical_thresholds": {
                "ml_classifier": {
                    "malicious_high": 0.80,
                    "suspicious_medium": 0.60
                },
                "vector_similarity": {
                    "malicious_high": 0.75,
                    "suspicious_medium": 0.68
                },
                "anomaly": {
                    "malicious_high": 0.85,
                    "suspicious_medium": 0.70
                }
            }
        }
        
        config_file = path or os.path.join(BASE_DIR, 'config', 'detection_config.json')
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    loaded = json.load(f)
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
        """Initialize all detection layers (same as before)."""
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
            print("   ⚠️  Fuzzy matching unavailable")
        
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
            print("   ⚠️  ML classifier unavailable")
        
        # Layer 4: Vector similarity
        print("⚙️  Layer 4: Vector Similarity Detector...")
        vector_config = self.config.get('vector_db', {})
        db_path = vector_config.get('path', '../security/vector_db')
        
        if not os.path.isabs(db_path):
            db_path = os.path.join(BASE_DIR, db_path)
        
        print(f"   Vector DB path: {db_path}")
        
        self.vector_detector = VectorDetector(
            db_path=db_path,
            collection_name=vector_config.get('collection_name', 'unified_malicious_prompts'),
            model_name=vector_config.get('model_name', 'all-MiniLM-L6-v2'),
            similarity_threshold=vector_config.get('similarity_threshold', 0.68)
        )
        if self.vector_detector.available:
            try:
                count = self.vector_detector.collection.count()
                print(f"   ✅ Vector similarity ready ({count:,} embeddings)")
            except:
                print("   ✅ Vector similarity ready")
        else:
            print("   ⚠️  Vector similarity unavailable")
        
        # Layer 5: Anomaly detection
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
                print("   ⚠️  Anomaly detection unavailable")
        else:
            self.anomaly_detector = None
            print("   ⊝  Anomaly detection disabled")
    
    # def validate(self, prompt: str, source: str = "unknown") -> dict:
    #     """
    #     Validate prompt using scoreless decision engine.
        
    #     Process:
    #     1. Run all detection layers (unchanged)
    #     2. Convert layer outputs to categorical
    #     3. Apply decision logic (BLOCK/ALERT/ALLOW)
    #     4. Log event
        
    #     Args:
    #         prompt: User input to validate
    #         source: Source of request
            
    #     Returns:
    #         {
    #             'allowed': bool,
    #             'action': str,
    #             'reason': str,
    #             'explanation': str,
    #             'triggered_layers': list,
    #             'categorical_results': dict,
    #             'detection_time_ms': float,
    #             'source': str
    #         }
    #     """
    #     import time
    #     start_time = time.time()
        
    #     layer_results = {}
        
    #     # ===================================================================
    #     # STEP 1: Run All Detection Layers (Same as Before)
    #     # ===================================================================
        
    #     # Layer 1: Rule-based detection
    #     layer_results['rule_based'] = self.rule_detector.detect(prompt)
        
    #     # Early exit if critical threat
    #     if layer_results['rule_based'].get('should_block', False):
    #         elapsed_ms = (time.time() - start_time) * 1000
            
    #         result = {
    #             'allowed': False,
    #             'action': 'block',
    #             'reason': 'Critical threat detected by rules',
    #             'explanation': 'Rule-based detector found critical malicious patterns',
    #             'triggered_layers': ['rule_based'],
    #             'categorical_results': {},
    #             'threats': layer_results['rule_based'].get('threats', []),
    #             'detection_time_ms': float(elapsed_ms),
    #             'source': source,
    #             'early_exit': True
    #         }
            
    #         # Convert to JSON-serializable before logging
    #         result = convert_to_json_serializable(result)
            
    #         if LOGGING_AVAILABLE:
    #             self._log_validation(prompt, result, source)
            
    #         return result
        
    #     # Layer 2: Fuzzy matching
    #     layer_results['fuzzy_match'] = self.fuzzy_detector.detect(prompt)
        
    #     # Extract features for ML layers
    #     features_dict = self.feature_extractor.extract_all_features(prompt)
    #     features_array = self.feature_extractor.features_to_array(features_dict)
        
    #     # Layer 3: ML classification
    #     layer_results['ml_classifier'] = self.ml_classifier.detect(features_array)
        
    #     # Layer 4: Vector similarity
    #     layer_results['vector_similarity'] = self.vector_detector.detect(prompt)
        
    #     # Layer 5: Anomaly detection
    #     if self.anomaly_detector:
    #         layer_results['anomaly'] = self.anomaly_detector.detect(features_array)
    #     else:
    #         layer_results['anomaly'] = {'score': 0.0, 'available': False}
        
    #     # ===================================================================
    #     # STEP 2: Convert to Categorical (NEW - Scoreless Logic)
    #     # ===================================================================
        
    #     categorical_results = {}
    #     for layer_name, layer_result in layer_results.items():
    #         # Detect context once
    #         context = self.decision_engine.detect_context(prompt)

    #         # Pass context to each layer conversion
    #         categorical_results[layer_name] = self.decision_engine.convert_layer_to_categorical(
    #             layer_name, layer_result, context=context
    #         )
            
    #         # categorical_results[layer_name] = self.decision_engine.convert_layer_to_categorical(
    #         #     layer_name, layer_result
    #         # )
        
    #     # ===================================================================
    #     # STEP 3: Make Decision (NEW - Deterministic Logic)
    #     # ===================================================================
        
    #    # decision = self.decision_engine.make_decision(categorical_results)
    #     decision = self.decision_engine.make_decision(categorical_results, prompt=prompt)
    #     # ===================================================================
    #     # STEP 4: Build Final Result (Compatible with Existing Code)
    #     # ===================================================================
        
    #     elapsed_ms = (time.time() - start_time) * 1000
        
    #     result = {
    #         'allowed': decision['allowed'],
    #         'action': decision['action'],
    #         'reason': decision['reason'],
    #         'explanation': decision['explanation'],
    #         'triggered_layers': decision['triggered_layers'],
    #         'categorical_results': categorical_results,
    #         'signals': decision['signals'],
    #         'threats': self.decision_engine.get_threat_summary(decision['signals']),
    #         'detection_time_ms': float(elapsed_ms),
    #         'source': source
    #     }
        
    #     # CRITICAL FIX: Convert ALL NumPy types to native Python types
    #     result = convert_to_json_serializable(result)
        
    #     # Log the event
    #     if LOGGING_AVAILABLE:
    #         self._log_validation(prompt, result, source)
        
    #     return result
    def validate(self, prompt: str, source: str = "unknown") -> dict:
        import time
        start_time = time.time()

        layer_results = {}
    
    # Run all detection layers
        layer_results['rule_based'] = self.rule_detector.detect(prompt)
    
        if layer_results['rule_based'].get('should_block', False):
        # Early exit...
            pass
    
        layer_results['fuzzy_match'] = self.fuzzy_detector.detect(prompt)
    
        features_dict = self.feature_extractor.extract_all_features(prompt)
        features_array = self.feature_extractor.features_to_array(features_dict)
    
        layer_results['ml_classifier'] = self.ml_classifier.detect(features_array)
        layer_results['vector_similarity'] = self.vector_detector.detect(prompt)
    
        if self.anomaly_detector:
            layer_results['anomaly'] = self.anomaly_detector.detect(features_array)
        else:
            layer_results['anomaly'] = {'score': 0.0, 'available': False}
    
    # UPDATED: Detect context once
        context = self.decision_engine.detect_context(prompt)
    
    # UPDATED: Convert to categorical with context
        categorical_results = {}
        for layer_name, layer_result in layer_results.items():
            categorical_results[layer_name] = self.decision_engine.convert_layer_to_categorical(
            layer_name, layer_result, context=context
        )
    
    # UPDATED: Make decision with prompt for context
        decision = self.decision_engine.make_decision(categorical_results, prompt=prompt)
    
    # Build result
        elapsed_ms = (time.time() - start_time) * 1000
    
        result = {
        'allowed': decision['allowed'],
        'action': decision['action'],
        'reason': decision['reason'],
        'explanation': decision['explanation'],
        'triggered_layers': decision['triggered_layers'],
        'categorical_results': categorical_results,
        'signals': decision['signals'],
        'threats': self.decision_engine.get_threat_summary(decision['signals']),
        'detection_time_ms': float(elapsed_ms),
        'source': source,
        'context': decision.get('context', 'neutral')  # NEW: Include context
    }
    
        result = convert_to_json_serializable(result)
    
        if LOGGING_AVAILABLE:
            self._log_validation(prompt, result, source)
    
        return result
    def _log_validation(self, prompt: str, result: dict, source: str):
        """Log validation event (compatible with existing logging)."""
        try:
            action = 'blocked' if result['action'] == 'block' else \
                     'alerted' if result['action'] == 'alert' else 'allowed'
            
            severity = convert_to_severity(result['action'])
            
            # Build metadata and ensure it's JSON-serializable
            metadata = {
                'action_type': result['action'],
                'triggered_layers': result.get('triggered_layers', []),
                'categorical_results': result.get('categorical_results', {}),
                'signals': result.get('signals', {}),
                'threats': result.get('threats', []),
                'detection_time_ms': result.get('detection_time_ms', 0)
            }
            
            # CRITICAL FIX: Convert metadata to JSON-serializable
            metadata = convert_to_json_serializable(metadata)
            
            log_event(
                source=source,
                prompt=prompt,
                action=action,
                reason=result['reason'],
                tool=source,
                severity=severity,
                metadata=metadata
            )
        except Exception as e:
            print(f"⚠️  Logging error: {e}")
            import traceback
            traceback.print_exc()


# Initialize global proxy instance
proxy = SecurityProxyV2Scoreless()


# ============================================================================
# API ENDPOINTS (Same as Before)
# ============================================================================

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "security-proxy-v2-scoreless",
        "version": "2.0.0-scoreless-fixed"
    })


@app.route('/validate', methods=['POST'])
def validate_endpoint():
    """Validate a prompt through all detection layers."""
    data = request.get_json()
    
    if not data or 'prompt' not in data:
        return jsonify({"error": "Missing 'prompt' in request"}), 400
    
    prompt = data['prompt']
    source = data.get('source', 'unknown')
    
    result = proxy.validate(prompt, source)
    
    # Result is already JSON-serializable from validate() method
    return jsonify(result)


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
            "message": "Request flagged as suspicious",
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
        "decision_engine": "scoreless",
        "logging": {"available": LOGGING_AVAILABLE}
    })


if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════╗
║         Security Proxy V2 (Scoreless Decision)            ║
║         Deterministic Multi-Layer Detection System         ║
║                     FIXED VERSION                          ║
║                                                            ║
║  Running on: http://localhost:5001                         ║
║                                                            ║
║  Detection Layers:                                         ║
║  ├─ Layer 1: Rule-Based                                    ║
║  ├─ Layer 2: Fuzzy Matching (disabled)                     ║
║  ├─ Layer 3: ML Classification                             ║
║  ├─ Layer 4: Vector Similarity                             ║
║  ├─ Layer 5: Anomaly Detection                             ║
║  └─ Decision: Categorical Logic (No Scoring)               ║
║                                                            ║
║  Decision Types:                                           ║
║  • BLOCK  - Critical threat detected                       ║
║  • ALERT  - Suspicious patterns found                      ║
║  • ALLOW  - No threats detected                            ║
║                                                            ║
║  Endpoints:                                                ║
║  - POST /validate      : Validate any prompt               ║
║  - POST /secure/agent  : Validate AI agent requests        ║
║  - POST /secure/n8n    : Validate n8n workflow requests    ║
║  - GET  /stats         : Detector statistics               ║
║  - GET  /health        : Health check                      ║
║                                                            ║
║  ✅ JSON Serialization: FIXED                              ║
║  ✅ Logging: WORKING                                       ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    app.run(host='0.0.0.0', port=5001, debug=True)
import sys
import os
import json
import pickle
import numpy as np
from sklearn.ensemble import IsolationForest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import FeatureExtractor

def train_anomaly_model():
    print("Training Anomaly Detection Model (Layer 5)...")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    embeddings_dir = os.path.join(os.path.dirname(project_dir), 'security', 'embeddings')
    output_dir = os.path.join(project_dir, 'models')
    
    # Load benign prompts to train the anomaly detector
    # (IsolationForest is trained on "normal" data to detect outliers)
    benign_path = os.path.join(embeddings_dir, "benign_prompts.json")
    try:
        with open(benign_path, 'r', encoding='utf-8') as f:
            benign_data = json.load(f)
            benign_prompts = benign_data.get('prompts', [])
            print(f"Loaded {len(benign_prompts):,} benign prompts")
    except Exception as e:
        print(f"Failed to load benign prompts: {e}")
        return

    # Assuming we want to train it on benign data
    extractor = FeatureExtractor()
    features = []
    
    for i, prompt in enumerate(benign_prompts):
        f_dict = extractor.extract_all_features(prompt)
        f_array = extractor.features_to_array(f_dict)
        features.append(f_array)
        
        if (i+1) % 500 == 0:
            print(f"Extracted {i+1} / {len(benign_prompts)}")
            
    X_train = np.array(features)
    print(f"Training IsolationForest on {X_train.shape} features...")
    
    model = IsolationForest(
        n_estimators=100,
        contamination=0.01, # assume 1% anomalies in benign data
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train)
    
    os.makedirs(output_dir, exist_ok=True)
    model_path = os.path.join(output_dir, 'anomaly_model.pkl')
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
        
    print(f"Anomaly model saved to {model_path}!")

if __name__ == "__main__":
    train_anomaly_model()

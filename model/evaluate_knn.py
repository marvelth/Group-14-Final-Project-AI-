"""
evaluate_knn.py

Evaluation script for testing KNN classifier accuracy on the generated synthetic dataset.
"""

import sys
from pathlib import Path
import numpy as np
from collections import Counter

# Add parent directory of 'model' to sys.path to allow absolute imports
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from model.knn_model import EduPathKNNModel

def train_test_split(X, y, test_size=0.2, random_state=42):
    rng = np.random.RandomState(random_state)
    n = X.shape[0]
    idx = np.arange(n)
    rng.shuffle(idx)
    split = int(np.floor(n * (1 - test_size)))
    train_idx = idx[:split]
    test_idx = idx[split:]
    return X[train_idx], y[train_idx], X[test_idx], y[test_idx]

def knn_predict(train_X, train_y, test_X, k=5):
    preds = []
    topk_lists = []
    for x in test_X:
        # compute euclidean distances
        dists = np.linalg.norm(train_X - x, axis=1)
        nn_idx = np.argsort(dists)
        neigh_labels = train_y[nn_idx[:k]]
        
        # Most common label among k neighbors
        pred = Counter(neigh_labels).most_common(1)[0][0]
        preds.append(pred)
        
        # Unique top-3 neighbor labels (in order of proximity)
        unique_labels = []
        for label in neigh_labels:
            if label not in unique_labels:
                unique_labels.append(label)
            if len(unique_labels) >= 3:
                break
        # Pad with other labels if not enough unique labels
        while len(unique_labels) < 3:
            for label in train_y:
                if label not in unique_labels:
                    unique_labels.append(label)
                    break
        topk_lists.append(unique_labels)
        
    return np.array(preds), topk_lists

def main():
    print("Initializing model and loading synthetic dataset...")
    csv_path = str(BASE_DIR / 'model' / 'major_profile.csv')
    synth_path = str(BASE_DIR / 'model' / 'synthetic_dataset.csv')
    
    model = EduPathKNNModel(csv_path=csv_path, synthetic_data_path=synth_path)
    
    # normalized_synthetic has normalized features, synthetic_labels has targets
    X = model.normalized_synthetic
    y = model.synthetic_labels
    
    print(f"Total synthetic samples: {len(X)}")
    print("Splitting dataset: 80% train, 20% test...")
    train_X, train_y, test_X, test_y = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"Train samples: {len(train_X)}, Test samples: {len(test_X)}")
    
    print("\nRunning evaluation on different values of K...")
    k_values = [1, 3, 5, 7, 9]
    
    print(f"{'K Value':<10} | {'Top-1 Accuracy':<16} | {'Top-3 Accuracy':<16}")
    print("-" * 50)
    
    for k in k_values:
        preds, topk = knn_predict(train_X, train_y, test_X, k=k)
        
        # Top-1 accuracy
        top1_acc = np.mean(preds == test_y) * 100.0
        
        # Top-3 accuracy (actual label is one of the top 3 unique nearest neighbors)
        top3_success = [test_y[i] in topk[i] for i in range(len(test_y))]
        top3_acc = np.mean(top3_success) * 100.0
        
        print(f"k = {k:<6} | {top1_acc:<14.2f}% | {top3_acc:<14.2f}%")

if __name__ == '__main__':
    main()

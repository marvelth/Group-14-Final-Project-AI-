"""
evaluate_knn.py

Evaluation script for testing KNN classifier accuracy on the generated synthetic dataset.
"""

import sys
from pathlib import Path
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

# Add parent directory of 'model' to sys.path to allow absolute imports
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from model.knn_model import EduPathKNNModel


def build_top3_lists(classifier: KNeighborsClassifier, train_X: np.ndarray, train_y: np.ndarray, test_X: np.ndarray) -> list:
    _, neighbor_idxs = classifier.kneighbors(test_X, n_neighbors=3, return_distance=True)
    top3_lists = []

    for idxs in neighbor_idxs:
        labels = train_y[idxs]
        unique_labels = []
        for label in labels:
            if label not in unique_labels:
                unique_labels.append(label)
            if len(unique_labels) >= 3:
                break

        while len(unique_labels) < 3:
            for label in train_y:
                if label not in unique_labels:
                    unique_labels.append(label)
                    break

        top3_lists.append(unique_labels)

    return top3_lists


def main():
    print("Initializing model and loading synthetic dataset...")
    csv_path = str(BASE_DIR / 'model' / 'major_profile.csv')
    synth_path = str(BASE_DIR / 'model' / 'synthetic_dataset.csv')

    model = EduPathKNNModel(csv_path=csv_path, synthetic_data_path=synth_path)

    X = model.normalized_synthetic
    y = model.synthetic_labels

    print(f"Total synthetic samples: {len(X)}")
    print("Splitting dataset: 80% train, 20% test...")
    train_X, test_X, train_y, test_y = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"Train samples: {len(train_X)}, Test samples: {len(test_X)}")

    print("\nRunning evaluation on different values of K...")
    k_values = [1, 3, 5, 7, 9]

    print(f"{'K Value':<10} | {'Top-1 Accuracy':<16} | {'Top-3 Accuracy':<16}")
    print("-" * 50)

    for k in k_values:
        classifier = KNeighborsClassifier(n_neighbors=k, weights='distance', metric='euclidean')
        classifier.fit(train_X, train_y)

        preds = classifier.predict(test_X)
        top3_lists = build_top3_lists(classifier, train_X, train_y, test_X)

        top1_acc = np.mean(preds == test_y) * 100.0
        top3_success = [test_y[i] in top3_lists[i] for i in range(len(test_y))]
        top3_acc = np.mean(top3_success) * 100.0

        print(f"k = {k:<6} | {top1_acc:<14.2f}% | {top3_acc:<14.2f}%")


if __name__ == '__main__':
    main()

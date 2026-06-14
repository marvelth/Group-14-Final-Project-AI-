"""
evaluate_knn.py

Simple evaluation script for the project.
Steps:
 - Read `major_profile.csv`
 - Preprocess / normalize features
 - Split 80/20 (random)
 - Run a simple KNN (instance-based) on test set
 - Report top-1 and top-3 accuracy for several k values

Usage:
    python evaluate_knn.py

"""
import os
import numpy as np
import pandas as pd
from collections import Counter


CSV_PATH = 'major_profile.csv'
FEATURE_COLS = ['math','bindo','binggris','bio','fisika','kimia','ekonomi','sosiologi',
                'R','I','A','S','E','C']


def load_data(csv_path=CSV_PATH):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV not found: {csv_path}")
    df = pd.read_csv(csv_path)
    # keep only needed columns
    for c in FEATURE_COLS:
        if c not in df.columns:
            raise ValueError(f"Missing column in CSV: {c}")
    if 'jurusan' not in df.columns:
        raise ValueError('CSV must contain `jurusan` column')
    return df


def preprocess(df: pd.DataFrame):
    X = df[FEATURE_COLS].astype(float).values
    y = df['jurusan'].astype(str).values

    # Min-max normalize per column to [0,1]
    mins = X.min(axis=0)
    maxs = X.max(axis=0)
    ranges = maxs - mins
    ranges[ranges == 0] = 1.0
    X_norm = (X - mins) / ranges

    return X_norm, y


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
        # top-k neighbor labels (allow duplicates)
        topk_lists.append(list(neigh_labels[:3]))
    return np.array(preds), topk_lists


def evaluate(train_X, train_y, test_X, test_y, k_values=[1,3,5,7,9]):
    results = []
    for k in k_values:
        preds, topk = knn_predict(train_X, train_y, test_X, k=k)
        top1 = np.mean(preds == test_y) * 100.0
        # top-3 accuracy: true label in first 3 neighbors
        top3_success = [ (test_y[i] in topk[i]) for i in range(len(test_y)) ]
        top3 = np.mean(top3_success) * 100.0
        results.append({'k': k, 'top1_acc': round(top1,2), 'top3_acc': round(top3,2)})
    return results


def main():
    print('Loading data...')
    df = load_data()
    print(f'Total records: {len(df)}')

    print('Preprocessing...')
    X, y = preprocess(df)

    print('Splitting train/test (80/20)')
    train_X, train_y, test_X, test_y = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f'Train size: {len(train_X)}, Test size: {len(test_X)}')

    print('Evaluating K values...')
    k_values = [1,3,5,7,9]
    results = evaluate(train_X, train_y, test_X, test_y, k_values=k_values)

    print('\nResults:')
    for r in results:
        print(f"k={r['k']:>2}  Top-1: {r['top1_acc']:>5}%  Top-3: {r['top3_acc']:>5}%")


if __name__ == '__main__':
    main()

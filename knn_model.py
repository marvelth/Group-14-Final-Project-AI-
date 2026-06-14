"""
knn_model.py

This module provides:
- `JurusanKNNModel` class (same API used by the web app)
- Helper functions for preprocessing and evaluation (80/20 split)

Notes:
- Importing this module in the web app keeps behavior identical: `JurusanKNNModel.recommend()`
  still computes similarity between a user vector and all jurusan profiles.
- Running the module as a script runs an 80/20 evaluation and prints top-1/top-3 accuracies.
"""

from pathlib import Path
from collections import Counter
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple
import os

FEATURE_COLS = [
    'math','bindo','binggris','bio','fisika','kimia','ekonomi','sosiologi',
    'R','I','A','S','E','C'
]

class JurusanKNNModel:
    """KNN model wrapper used by the web app.

    Public methods kept for compatibility:
    - `recommend(academic_scores, riasec_scores, k=5)` -> list of recommendations
    - `get_all_jurusans()`
    - `get_all_bidang()`
    - `get_jurusan_profile(jurusan_name)`

    The model stores both raw dataframe and a normalized profile matrix for fast distance
    computation.
    """

    def __init__(self, csv_path: str = None):
        if csv_path is None:
            csv_path = Path(__file__).parent / 'major_profile.csv'
        self.csv_path = str(csv_path)
        self._load_data()
        self._build_profile_matrix()

    def _load_data(self):
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"CSV not found: {self.csv_path}")
        self.data = pd.read_csv(self.csv_path)
        # basic checks
        for c in FEATURE_COLS:
            if c not in self.data.columns:
                raise ValueError(f"Missing column in CSV: {c}")
        if 'jurusan' not in self.data.columns or 'bidang' not in self.data.columns:
            raise ValueError('CSV must contain `jurusan` and `bidang` columns')
        self.jurusans = self.data['jurusan'].tolist()
        self.bidang_list = sorted(self.data['bidang'].unique().tolist())

    def _build_profile_matrix(self):
        # create numeric matrix and min-max normalize per column
        X = self.data[FEATURE_COLS].astype(float).values
        self._mins = X.min(axis=0)
        self._maxs = X.max(axis=0)
        ranges = self._maxs - self._mins
        ranges[ranges == 0] = 1.0
        self.profile_matrix = (X - self._mins) / ranges

    def _normalize_input_vector(self, academic_scores: Dict[str, float], riasec_scores: Dict[str, float]) -> np.ndarray:
        # Build vector in same order as FEATURE_COLS
        vec = []
        # academic subjects
        acad_keys = FEATURE_COLS[:8]
        for k in acad_keys:
            v = float(academic_scores.get(k, 0))
            # accept either 0-100 or 1-5 scale
            if v > 5:
                v = v / 20.0  # convert 0-100 -> 0-5
            vec.append(v)
        # riasec
        riasec_keys = FEATURE_COLS[8:]
        for k in riasec_keys:
            v = float(riasec_scores.get(k, 0))
            if v > 5:
                # if user provided totals (6-30), map to 1-5 by linear scale
                if v >= 6 and v <= 30:
                    v = 1.0 + (v - 6.0) / 24.0 * 4.0
                else:
                    v = v / 20.0
            vec.append(v)
        vec = np.array(vec, dtype=float)
        # apply same min-max normalization used for profiles
        vec_norm = (vec - self._mins) / (self._maxs - self._mins)
        # guard divide-by-zero
        vec_norm = np.nan_to_num(vec_norm)
        return vec_norm

    def _distance_to_similarity(self, distance: float) -> float:
        # same mapping as previous implementation
        sim = 100.0 * np.exp(-distance * 1.5)
        return float(max(0.0, min(100.0, sim)))

    def recommend(self, academic_scores: Dict[str, float], riasec_scores: Dict[str, float], k: int = 5) -> List[Dict]:
        # validate keys
        missing_acad = [c for c in FEATURE_COLS[:8] if c not in academic_scores]
        missing_ria = [c for c in FEATURE_COLS[8:] if c not in riasec_scores]
        if missing_acad:
            raise ValueError(f"Missing academic scores: {missing_acad}")
        if missing_ria:
            raise ValueError(f"Missing RIASEC scores: {missing_ria}")

        user_vec = self._normalize_input_vector(academic_scores, riasec_scores)
        # compute distances
        dists = np.linalg.norm(self.profile_matrix - user_vec.reshape(1, -1), axis=1)
        order = np.argsort(dists)
        topk = order[:k]
        recs = []
        for rank, idx in enumerate(topk, start=1):
            row = self.data.iloc[idx]
            recs.append({
                'rank': rank,
                'jurusan': row['jurusan'],
                'bidang': row['bidang'],
                'distance': float(dists[idx]),
                'similarity_score': self._distance_to_similarity(float(dists[idx]))
            })
        return recs

    def get_all_jurusans(self) -> List[str]:
        return self.jurusans

    def get_all_bidang(self) -> List[str]:
        return self.bidang_list

    def get_jurusan_profile(self, jurusan_name: str) -> Dict:
        row = self.data[self.data['jurusan'] == jurusan_name]
        if row.empty:
            return None
        row = row.iloc[0]
        return {
            'jurusan': row['jurusan'],
            'bidang': row['bidang'],
            'academic': {c: float(row[c]) for c in FEATURE_COLS[:8]},
            'riasec': {c: float(row[c]) for c in FEATURE_COLS[8:]}
        }


# ----- Evaluation utilities (module-level) -----

def preprocess_df(df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
    X = df[FEATURE_COLS].astype(float).values
    y = df['jurusan'].astype(str).values
    mins = X.min(axis=0)
    maxs = X.max(axis=0)
    ranges = maxs - mins
    ranges[ranges == 0] = 1.0
    X_norm = (X - mins) / ranges
    return X_norm, y


def train_test_split(X: np.ndarray, y: np.ndarray, test_size: float = 0.2, random_state: int = 42) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.RandomState(random_state)
    n = X.shape[0]
    idx = np.arange(n)
    rng.shuffle(idx)
    split = int(np.floor(n * (1 - test_size)))
    train_idx = idx[:split]
    test_idx = idx[split:]
    return X[train_idx], y[train_idx], X[test_idx], y[test_idx]


def knn_predict(train_X: np.ndarray, train_y: np.ndarray, test_X: np.ndarray, k: int = 5) -> Tuple[np.ndarray, List[List[str]]]:
    preds = []
    topk_lists = []
    for x in test_X:
        dists = np.linalg.norm(train_X - x, axis=1)
        nn_idx = np.argsort(dists)
        neigh_labels = train_y[nn_idx[:k]]
        pred = Counter(neigh_labels).most_common(1)[0][0]
        preds.append(pred)
        topk_lists.append(list(neigh_labels[:3]))
    return np.array(preds), topk_lists


def evaluate_knn(X: np.ndarray, y: np.ndarray, k_values: List[int] = [1,3,5,7,9], test_size: float = 0.2, random_state: int = 42) -> List[Dict]:
    train_X, train_y, test_X, test_y = train_test_split(X, y, test_size=test_size, random_state=random_state)
    results = []
    for k in k_values:
        preds, topk = knn_predict(train_X, train_y, test_X, k=k)
        top1 = float(np.mean(preds == test_y) * 100.0)
        top3_success = [ (test_y[i] in topk[i]) for i in range(len(test_y)) ]
        top3 = float(np.mean(top3_success) * 100.0)
        results.append({'k': k, 'top1_acc': round(top1,2), 'top3_acc': round(top3,2)})
    return results


if __name__ == '__main__':
    # Run evaluation when module is executed directly, but importing from web app is unaffected
    print('Running 80/20 evaluation on major_profile.csv')
    csv_path = Path(__file__).parent / 'major_profile.csv'
    if not csv_path.exists():
        print('major_profile.csv not found in repository root. Aborting evaluation.')
    else:
        df = pd.read_csv(csv_path)
        X, y = preprocess_df(df)
        res = evaluate_knn(X, y, k_values=[1,3,5,7,9], test_size=0.2, random_state=42)
        print('\nEvaluation results:')
        for r in res:
            print(f"k={r['k']:>2}  Top-1: {r['top1_acc']:>5}%  Top-3: {r['top3_acc']:>5}%")
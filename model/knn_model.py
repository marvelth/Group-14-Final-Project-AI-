"""
EduPath AI - K-Nearest Neighbors (KNN) Major Recommendation Model
"""

import os
from pathlib import Path
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple

FEATURE_COLS = [
    'math', 'indonesian', 'english', 'biology', 'physics', 'chemistry', 'economics', 'sociology',
    'R', 'I', 'A', 'S', 'E', 'C'
]

# Mapping constants for bonuses
BIDANG_PRESTASI_MAP = {
    'Health': ['Health'],
    'Technology': ['Science and Technology'],
    'Physics': ['Engineering'],
    'Mathematics': ['Science and Technology'],
    'Biology': ['Health', 'Science and Technology', 'Agriculture and Marine'],
    'Chemistry': ['Health'],
    'Business': ['Economics and Business'],
    'Engineering': ['Engineering'],
    'Earth Science': ['Agriculture and Marine'],
    'Arts': ['Education and Creative']
}

MINAT_TO_BIDANG = {
    'Health': ['Health'],
    'Science & Technology': ['Science and Technology'],
    'Social, Law & Government': ['Social, Law and Governance'],
    'Economics & Business': ['Economics and Business'],
    'Engineering': ['Engineering'],
    'Agriculture & Maritime': ['Agriculture and Marine'],
    'Arts & Education': ['Education and Creative']
}

class EduPathKNNModel:
    def __init__(self, csv_path: str = None, synthetic_data_path: str = None):
        if csv_path is None:
            csv_path = str(Path(__file__).parent / 'major_profile.csv')
        if synthetic_data_path is None:
            synthetic_data_path = str(Path(__file__).parent / 'synthetic_dataset.csv')
        
        self.csv_path = csv_path
        self.synthetic_data_path = synthetic_data_path
        
        self._load_base_profiles()
        self._load_or_generate_synthetic_data()

    def _load_base_profiles(self):
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"Base profiles CSV not found: {self.csv_path}")
        self.base_df = pd.read_csv(self.csv_path)
        self.jurusans = self.base_df['major'].tolist()
        self.bidang_list = sorted(self.base_df['field'].unique().tolist())

    def _load_or_generate_synthetic_data(self):
        if os.path.exists(self.synthetic_data_path):
            self.synthetic_df = pd.read_csv(self.synthetic_data_path)
        else:
            self.synthetic_df = self.generate_synthetic_data()
            self.synthetic_df.to_csv(self.synthetic_data_path, index=False)
        
        # Build numpy arrays for distance computation
        self.synthetic_features = self.synthetic_df[FEATURE_COLS].astype(float).values
        self.synthetic_labels = self.synthetic_df['major'].values
        self.synthetic_fields = self.synthetic_df['field'].values
        
        # Normalize the synthetic features:
        # Academic (cols 0-7): 0 to 100 range -> normalize by dividing by 100.0
        # RIASEC (cols 8-15): 6 to 30 range -> normalize by subtracting 6 and dividing by 24.0
        self.normalized_synthetic = np.zeros_like(self.synthetic_features)
        self.normalized_synthetic[:, :8] = self.synthetic_features[:, :8] / 100.0
        self.normalized_synthetic[:, 8:] = (self.synthetic_features[:, 8:] - 6.0) / 24.0

    def generate_synthetic_data(self, n_per_major: int = 100, random_state: int = 42) -> pd.DataFrame:
        """
        Generate synthetic student profiles based on ideal major profiles.
        """
        rng = np.random.RandomState(random_state)
        synthetic_records = []

        # Academic center mapping (1-5 to 0-100 scale)
        acad_center = {1: 30.0, 2: 45.0, 3: 60.0, 4: 75.0, 5: 90.0}
        # RIASEC center mapping (1-5 to 6-30 scale)
        riasec_center = {1: 8.0, 2: 13.0, 3: 18.0, 4: 23.0, 5: 28.0}

        for _, row in self.base_df.iterrows():
            major = row['major']
            field = row['field']
            
            # Generate n_per_major samples
            for _ in range(n_per_major):
                record = {'major': major, 'field': field}
                
                # Generate Academic scores
                for col in FEATURE_COLS[:8]:
                    ideal_val = int(row[col])
                    center = acad_center[ideal_val]
                    score = rng.normal(center, 8.0)
                    record[col] = float(np.clip(score, 0.0, 100.0))
                
                # Generate RIASEC scores
                for col in FEATURE_COLS[8:]:
                    ideal_val = int(row[col])
                    center = riasec_center[ideal_val]
                    score = rng.normal(center, 3.0)
                    record[col] = float(np.clip(score, 6.0, 30.0))
                
                synthetic_records.append(record)
                
        return pd.DataFrame(synthetic_records)

    def _normalize_student(self, academic_scores: Dict[str, float], riasec_scores: Dict[str, float]) -> np.ndarray:
        vec = []
        # Academic normalisation (0-100 -> 0-1)
        for sub in FEATURE_COLS[:8]:
            val = float(academic_scores.get(sub, 75.0))
            vec.append(val / 100.0)
            
        # RIASEC normalisation (6-30 -> 0-1)
        for r_type in FEATURE_COLS[8:]:
            val = float(riasec_scores.get(r_type, 18.0))
            vec.append((val - 6.0) / 24.0)
            
        return np.array(vec, dtype=float)

    def recommend(self, academic_scores: Dict[str, float], riasec_scores: Dict[str, float], 
                  prestasi: int = 0, bidang_prestasi: str = '', minat: List[str] = [], k: int = 7) -> List[Dict]:
        """
        Recommend top 3 unique majors using KNN with WEIGHTED Euclidean distance.
        """
        student_vec = self._normalize_student(academic_scores, riasec_scores)

        dists = np.zeros(len(self.normalized_synthetic))
        
        for idx in range(len(self.normalized_synthetic)):
            # Ambil nama jurusan untuk baris data synthetic saat ini
            major_name = self.synthetic_labels[idx]
            
            # Ambil profil ideal jurusan ini dari base_df (isinya angka 1-5)
            major_row = self.base_df[self.base_df['major'] == major_name].iloc[0]
            
            # Buat vector bobot berdasarkan profil ideal di csv
            weight_vec = []
            for col in FEATURE_COLS:
                ideal_val = float(major_row[col])
                # Jika nilai idealnya tinggi (4 atau 5), berikan bobot besar (misal dikali 3 atau 4)
                # Jika nilai idealnya rendah (1 atau 2), berikan bobot kecil (misal 0.5 atau 1)
                if ideal_val >= 4:
                    weight_vec.append(3.0) 
                elif ideal_val <= 2:
                    weight_vec.append(0.5)
                else:
                    weight_vec.append(1.0)
                    
            weight_vec = np.array(weight_vec)
            
            # Hitung Weighted Euclidean Distance
            diff = self.normalized_synthetic[idx] - student_vec
            weighted_diff = diff * weight_vec 
            dists[idx] = np.linalg.norm(weighted_diff)
 
        adjusted_dists = dists.copy()
        
        # Prestasi bonus: reduces distance if achievement field aligns with major's field
        prestasi_bonus = prestasi * 0.05
        # Minat bonus: 0.03 per matching interest
        
        for idx in range(len(adjusted_dists)):
            major_field = self.synthetic_fields[idx]
            
            # Check achievement alignment
            has_prestasi_bonus = False
            if bidang_prestasi in BIDANG_PRESTASI_MAP:
                if major_field in BIDANG_PRESTASI_MAP[bidang_prestasi]:
                    has_prestasi_bonus = True
            
            # Check interest alignment
            minat_match_count = 0
            for m in minat:
                if m in MINAT_TO_BIDANG:
                    if major_field in MINAT_TO_BIDANG[m]:
                        minat_match_count += 1
            
            total_bonus = 0.0
            if has_prestasi_bonus:
                total_bonus += prestasi_bonus
            total_bonus += minat_match_count * 0.03
            
            adjusted_dists[idx] = max(0.0, adjusted_dists[idx] - total_bonus)
            
        # Find K nearest neighbors
        nearest_indices = np.argsort(adjusted_dists)[:k]
        
        # Vote weighting by inverse distance: weight = 1 / (distance + epsilon)
        epsilon = 1e-5
        votes = {}
        major_dists = {}
        
        for idx in nearest_indices:
            major = self.synthetic_labels[idx]
            field = self.synthetic_fields[idx]
            d = adjusted_dists[idx]
            w = 1.0 / (d + epsilon)
            
            votes[major] = votes.get(major, 0.0) + w
            if major not in major_dists or d < major_dists[major]:
                major_dists[major] = d
                
        # Sort voted majors
        sorted_majors = sorted(votes.items(), key=lambda x: x[1], reverse=True)
        
        # Build recommendations list
        recs = []
        rank = 1
        for major, vote_weight in sorted_majors:
            if rank > 3:
                break
            # Find field
            major_field = self.base_df[self.base_df['major'] == major]['field'].values[0]
            d = major_dists[major]
            # Convert to similarity percentage
            pct = 100.0 * np.exp(-d * 0.4)
            pct = max(55.0, min(98.0, pct))
            
            recs.append({
                'rank': rank,
                'jurusan': major,
                'bidang': major_field,
                'similarity_score': round(pct, 1),
                'distance': round(d, 4)
            })
            rank += 1
            
        # In case we have fewer than 3 recommendations (e.g. all neighbors are of the same major),
        # pad with next closest majors based on average distance to their synthetic profiles
        if len(recs) < 3:
            already_recommended = [r['jurusan'] for r in recs]
            remaining_majors = []
            
            for m in self.jurusans:
                if m not in already_recommended:
                    # Calculate mean distance for this major
                    major_indices = np.where(self.synthetic_labels == m)[0]
                    mean_d = np.mean(adjusted_dists[major_indices])
                    remaining_majors.append((m, mean_d))
            
            remaining_majors = sorted(remaining_majors, key=lambda x: x[1])
            for m, d in remaining_majors:
                if len(recs) >= 3:
                    break
                major_field = self.base_df[self.base_df['major'] == m]['field'].values[0]
                pct = 100.0 * np.exp(-d * 0.4)
                pct = max(55.0, min(98.0, pct))
                
                recs.append({
                    'rank': len(recs) + 1,
                    'jurusan': m,
                    'bidang': major_field,
                    'similarity_score': round(pct, 1),
                    'distance': round(d, 4)
                })
                
        return recs

    def get_all_jurusans(self) -> List[str]:
        return self.jurusans

    def get_all_bidang(self) -> List[str]:
        return self.bidang_list

    def get_jurusan_profile(self, name: str) -> Dict:
        row = self.base_df[self.base_df['major'] == name]
        if row.empty:
            return None
        row = row.iloc[0]
        return {
            'major': row['major'],
            'field': row['field'],
            'academic': {c: float(row[c]) for c in FEATURE_COLS[:8]},
            'riasec': {c: float(row[c]) for c in FEATURE_COLS[8:]}
        }

    def get_student_analysis(self, academic_scores: Dict[str, float], riasec_scores: Dict[str, float]) -> Dict:
        # Sort academic subjects
        sorted_subjects = sorted(academic_scores.items(), key=lambda x: x[1], reverse=True)
        top_subjects = sorted_subjects[:3]
        
        # Sort RIASEC categories
        sorted_riasec = sorted(riasec_scores.items(), key=lambda x: x[1], reverse=True)
        top_riasec_letters = "".join([item[0] for item in sorted_riasec[:3]])
        
        return {
            'top_subjects': top_subjects,
            'riasec_type': top_riasec_letters,
            'riasec_scores': riasec_scores,
            'riasec_top3': sorted_riasec[:3]
        }

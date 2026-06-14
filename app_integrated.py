"""
Modified Flask API dengan integrasi KNN untuk format HTML frontend
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import json
import os
from pathlib import Path
from knn_model import JurusanKNNModel

# Inisialisasi Flask app
app = Flask(__name__, static_folder='.', template_folder='.')
CORS(app)

# Load model
try:
    model = JurusanKNNModel()
    print("✓ Model KNN berhasil diload")
except Exception as e:
    print(f"✗ Error load model: {e}")
    model = None


@app.route('/', methods=['GET'])
def index():
    """Serve halaman utama HTML"""
    try:
        with open('ui.html', 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return "Error: File UI.html tidak ditemukan", 404


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    API endpoint untuk menganalisis data siswa dan memberikan rekomendasi
    
    Request body (JSON):
    {
        "nama": "Nama Siswa",
        "kelas": "12",
        "nilai": {
            "math": 85,          // 0-100
            "bindo": 75,
            "binggris": 80,
            "bio": 70,
            "fisika": 88,
            "kimia": 82,
            "ekonomi": 65,
            "sosiologi": 72
        },
        "riasec": {
            "R": 18,             // Total skor dari 6 pertanyaan (maks 30)
            "I": 25,
            "A": 12,
            "S": 20,
            "E": 22,
            "C": 24
        },
        "prestasi": 0,           // 0-4
        "bidang_prestasi": "",
        "minat": []              // Array bidang minat
    }
    """
    try:
        if model is None:
            return jsonify({'error': 'Model belum diload'}), 500
        
        data = request.get_json()
        
        # Validasi input
        required_fields = ['nilai', 'riasec']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Field {field} tidak ada'}), 400
        
        # Extract data
        nilai_dict = data['nilai']
        riasec_dict = data['riasec']
        
        # Normalisasi nilai akademik dari 0-100 ke 1-5
        academic_scores = {}
        for subject in ['math', 'bindo', 'binggris', 'bio', 'fisika', 'kimia', 'ekonomi', 'sosiologi']:
            if subject in nilai_dict:
                # Convert 0-100 to 1-5 scale
                nilai_100 = float(nilai_dict[subject])
                nilai_5 = 1 + (nilai_100 / 100) * 4  # 0->1, 100->5
                academic_scores[subject] = nilai_5
            else:
                academic_scores[subject] = 3.0  # Default middle value
        
        # Normalisasi RIASEC dari total 6 pertanyaan (1-5 per pertanyaan) ke 1-5
        riasec_scores = {}
        for riasec_type in ['R', 'I', 'A', 'S', 'E', 'C']:
            if riasec_type in riasec_dict:
                # Total skor dari 6 pertanyaan: min 6 (1x6), max 30 (5x6)
                total_score = float(riasec_dict[riasec_type])
                # Normalize ke 1-5
                normalized = 1 + (total_score - 6) / 24 * 4  # 6->1, 30->5
                riasec_scores[riasec_type] = max(1, min(5, normalized))
            else:
                riasec_scores[riasec_type] = 3.0
        
        # Get recommendations (top 5)
        recommendations = model.recommend(academic_scores, riasec_scores, k=5)
        
        # Format response untuk HTML
        top3 = recommendations[:3]
        result = {
            'success': True,
            'top3': []
        }
        
        for rec in top3:
            result['top3'].append({
                'jurusan': rec['jurusan'],
                'bidang': rec['bidang'],
                'persen': int(rec['similarity_score']),
                'alasan': generate_alasan(
                    rec['jurusan'],
                    academic_scores,
                    riasec_scores,
                    nilai_dict
                )
            })
        
        return jsonify(result), 200
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500


def generate_alasan(jurusan_name, academic_scores, riasec_scores, nilai_dict_100):
    """
    Generate alasan personal kenapa siswa cocok dengan jurusan
    """
    # Get jurusan profile
    profile = model.get_jurusan_profile(jurusan_name)
    
    if profile is None:
        return "Profil jurusan tidak ditemukan."
    
    # Analisis kekuatan siswa
    kekuatan = []
    weak_point = None
    highest_val = None
    highest_subject = None
    
    for subject, value in nilai_dict_100.items():
        if value >= 85:
            kekuatan.append(subject.upper())
        if highest_val is None or value > highest_val:
            highest_val = value
            highest_subject = subject
    
    # Analisis RIASEC
    riasec_sorted = sorted(riasec_scores.items(), key=lambda x: x[1], reverse=True)
    top_riasec = riasec_sorted[0][0]
    
    jurusan_riasec = profile['riasec']
    top_jurusan_riasec = max(jurusan_riasec, key=jurusan_riasec.get)
    
    # Generate alasan
    alasan_parts = []
    
    # Bagian 1: Berdasarkan nilai akademik
    if profile['academic'].get(highest_subject, 0) >= 4:
        alasan_parts.append(
            f"Nilai {highest_subject.upper()}-mu sangat baik ({highest_val}), "
            f"dan {jurusan_name} membutuhkan kemampuan {highest_subject.upper()} yang kuat."
        )
    else:
        alasan_parts.append(
            f"Profil akademikmu seimbang dengan kebutuhan {jurusan_name}."
        )
    
    # Bagian 2: Berdasarkan RIASEC
    if top_riasec == top_jurusan_riasec or abs(riasec_scores[top_riasec] - riasec_scores.get(top_jurusan_riasec, 3)) < 1:
        alasan_parts.append(
            f"Tipe kepribadian {top_riasec}-mu cocok dengan profil tipikal mahasiswa {jurusan_name}."
        )
    else:
        alasan_parts.append(
            f"Kepribadian-mu memiliki karakteristik yang diperlukan untuk sukses di {jurusan_name}."
        )
    
    # Bagian 3: Motivasi
    alasan_parts.append(
        f"Kombinasi kemampuan dan minat-mu menjadikan {jurusan_name} pilihan yang menjanjikan."
    )
    
    return " ".join(alasan_parts)


@app.route('/api/jurusans', methods=['GET'])
def get_jurusans():
    """API untuk mendapatkan list semua jurusan"""
    try:
        if model is None:
            return jsonify({'error': 'Model belum diload'}), 500
        
        jurusans = model.get_all_jurusans()
        return jsonify({
            'success': True,
            'jurusans': jurusans,
            'count': len(jurusans)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/bidang', methods=['GET'])
def get_bidang():
    """API untuk mendapatkan list semua bidang"""
    try:
        if model is None:
            return jsonify({'error': 'Model belum diload'}), 500
        
        bidang = model.get_all_bidang()
        return jsonify({
            'success': True,
            'bidang': bidang,
            'count': len(bidang)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None
    }), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint tidak ditemukan'}), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("="*70)
    print(" Flask API - Sistem Rekomendasi Jurusan Berbasis KNN")
    print("="*70)
    print("\n📍 Server berjalan di: http://localhost:5000")
    print("\n📚 API Endpoints:")
    print("  GET  /              - Halaman utama (coba.html)")
    print("  POST /api/analyze   - Analisis data siswa & rekomendasi KNN")
    print("  GET  /api/jurusans  - List semua jurusan")
    print("  GET  /api/bidang    - List semua bidang")
    print("  GET  /api/health    - Health check")
    print("\n💡 Cara menggunakan:")
    print("  1. Buka http://localhost:5000 di browser")
    print("  2. Isi data akademik, prestasi, minat, dan RIASEC")
    print("  3. Sistem akan menggunakan KNN untuk memberikan top 3 rekomendasi")
    print("\n" + "="*70 + "\n")
    
    # Debug mode (ganti ke False untuk production)
    app.run(debug=True, host='127.0.0.1', port=5000, use_reloader=False)

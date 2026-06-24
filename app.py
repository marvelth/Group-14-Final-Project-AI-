import os
import sys
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Add root directory to python path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from model.knn_model import EduPathKNNModel
from backend.utils import generate_personal_alasan

app = Flask(__name__, static_folder=str(BASE_DIR / "frontend"), static_url_path="")
CORS(app)

# Load the KNN model once.
MODEL_DIR = BASE_DIR / "model"
model = EduPathKNNModel(
    csv_path=str(MODEL_DIR / "major_profile.csv"),
    synthetic_data_path=str(MODEL_DIR / "synthetic_dataset.csv")
)

def _normalize_academic_scores(nilai_dict):
    return {subject: float(nilai_dict.get(subject, 75.0)) for subject in [
        'math', 'indonesian', 'english', 'biology', 'physics', 'chemistry', 'economics', 'sociology'
    ]}

def _normalize_riasec_scores(riasec_dict):
    return {r_type: float(riasec_dict.get(r_type, 18.0)) for r_type in ['R', 'I', 'A', 'S', 'E', 'C']}

@app.route('/')
def index():
    return send_from_directory(str(BASE_DIR / "frontend"), 'index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'error': 'Request body must be JSON'}), 400

        required_fields = ['nilai', 'riasec']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f"Missing required field: '{field}'"}), 400

        nilai_dict = data['nilai']
        riasec_dict = data['riasec']
        prestasi = int(data.get('prestasi', 0))
        bidang_prestasi = data.get('bidang_prestasi', '')
        minat = data.get('minat', [])

        academic_scores = _normalize_academic_scores(nilai_dict)
        riasec_scores = _normalize_riasec_scores(riasec_dict)

        recommendations = model.recommend(
            academic_scores=academic_scores,
            riasec_scores=riasec_scores,
            prestasi=prestasi,
            bidang_prestasi=bidang_prestasi,
            minat=minat,
            k=7
        )

        analysis = model.get_student_analysis(academic_scores, riasec_scores)

        top3_res = []
        for rec in recommendations:
            jurusan_name = rec['jurusan']
            jurusan_bidang = rec['bidang']
            jurusan_profile = model.get_jurusan_profile(jurusan_name)

            alasan = generate_personal_alasan(
                jurusan_name=jurusan_name,
                jurusan_bidang=jurusan_bidang,
                jurusan_profile=jurusan_profile['academic'],
                academic_scores=academic_scores,
                riasec_scores=riasec_scores,
                riasec_top3=analysis['riasec_top3'],
                prestasi=prestasi,
                bidang_prestasi=bidang_prestasi,
                minat=minat,
                student_analysis=analysis
            )

            top3_res.append({
                'jurusan': jurusan_name,
                'bidang': jurusan_bidang,
                'persen': rec['similarity_score'],
                'alasan': alasan
            })

        return jsonify({
            'success': True,
            'top3': top3_res,
            'analysis': {
                'top_subjects': analysis['top_subjects'],
                'riasec_type': analysis['riasec_type'],
                'riasec_scores': analysis['riasec_scores'],
                'riasec_top3': analysis['riasec_top3']
            }
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/jurusans', methods=['GET'])
def get_jurusans():
    return jsonify({'success': True, 'jurusans': model.get_all_jurusans(), 'count': len(model.get_all_jurusans())})

@app.route('/api/bidang', methods=['GET'])
def get_bidang():
    return jsonify({'success': True, 'bidang': model.get_all_bidang(), 'count': len(model.get_all_bidang())})

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'model_loaded': model is not None})

# For fallback routing: serving static frontend files
@app.route('/<path:path>')
def serve_static(path):
    frontend_path = BASE_DIR / "frontend" / path
    if frontend_path.exists() and frontend_path.is_file():
        return send_from_directory(str(BASE_DIR / "frontend"), path)
    # Default fallback to index.html for single-page routing
    return send_from_directory(str(BASE_DIR / "frontend"), "index.html")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    print(f"EduPath AI Server starting on http://localhost:{port}...")
    app.run(host='0.0.0.0', port=port, debug=True)

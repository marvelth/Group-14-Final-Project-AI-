import sys
import os
from pathlib import Path

# Add project root to path for imports
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from model.knn_model import EduPathKNNModel
from backend.utils import generate_personal_alasan

FRONTEND_DIR = BASE_DIR / 'frontend'

app = Flask(__name__, static_folder=str(FRONTEND_DIR), template_folder=str(FRONTEND_DIR), static_url_path='')
CORS(app)

# Load model
try:
    model = EduPathKNNModel(
        csv_path=str(BASE_DIR / 'model' / 'major_profile.csv'),
        synthetic_data_path=str(BASE_DIR / 'model' / 'synthetic_dataset.csv')
    )
    print('✓ EduPath KNN Model loaded successfully')
except Exception as e:
    print(f'✗ Error loading model: {e}')
    model = None


@app.route('/', methods=['GET'])
def index():
    """Serve the main landing page."""
    try:
        return send_from_directory(str(FRONTEND_DIR), 'index.html')
    except Exception as e:
        return f"Error: index.html not found under {FRONTEND_DIR}. Details: {str(e)}", 404


@app.route('/<path:path>', methods=['GET'])
def serve_static(path):
    """Serve static files (CSS, JS, images)."""
    return send_from_directory(str(FRONTEND_DIR), path)


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    POST endpoint to analyze student scores and return recommended majors.
    """
    try:
        if model is None:
            return jsonify({'success': False, 'error': 'Model not loaded'}), 500
            
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Request body must be JSON'}), 400
            
        # Validation
        required_fields = ['nilai', 'riasec']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f"Missing required field: '{field}'"}), 400
                
        # Extract data
        name = data.get('nama', 'Student')
        grade = data.get('kelas', '12')
        nilai_dict = data['nilai']
        riasec_dict = data['riasec']
        prestasi = int(data.get('prestasi', 0))
        bidang_prestasi = data.get('bidang_prestasi', '')
        minat = data.get('minat', [])
        
        # Standardize academic score keys and map to float
        academic_scores = {}
        for subject in ['math', 'indonesian', 'english', 'biology', 'physics', 'chemistry', 'economics', 'sociology']:
            val = nilai_dict.get(subject, 75.0)
            academic_scores[subject] = float(val)
            
        # Standardize RIASEC keys and map to float
        riasec_scores = {}
        for r_type in ['R', 'I', 'A', 'S', 'E', 'C']:
            val = riasec_dict.get(r_type, 18.0)
            riasec_scores[r_type] = float(val)
            
        # Perform KNN Recommendation
        recommendations = model.recommend(
            academic_scores=academic_scores,
            riasec_scores=riasec_scores,
            prestasi=prestasi,
            bidang_prestasi=bidang_prestasi,
            minat=minat,
            k=7
        )
        
        # Get student profile analysis
        analysis = model.get_student_analysis(academic_scores, riasec_scores)
        
        # Generate personalized reason for each recommended major
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
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': f"Internal Server Error: {str(e)}"}), 500


@app.route('/api/jurusans', methods=['GET'])
def get_jurusans():
    """GET endpoint to list all majors."""
    try:
        if model is None:
            return jsonify({'success': False, 'error': 'Model not loaded'}), 500
        jurusans = model.get_all_jurusans()
        return jsonify({
            'success': True,
            'jurusans': jurusans,
            'count': len(jurusans)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/bidang', methods=['GET'])
def get_bidang():
    """GET endpoint to list all fields."""
    try:
        if model is None:
            return jsonify({'success': False, 'error': 'Model not loaded'}), 500
        bidang = model.get_all_bidang()
        return jsonify({
            'success': True,
            'bidang': bidang,
            'count': len(bidang)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """GET endpoint for service health check."""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None
    }), 200


@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print('='*70)
    print(' EduPath AI - Major Recommendation System')
    print('='*70)
    print('\n📍 Server running at: http://localhost:5001')
    print('\n📚 API Endpoints:')
    print('  GET  /              - Main page')
    print('  POST /api/analyze   - Analyze student & KNN recommendation')
    print('  GET  /api/jurusans  - List all majors')
    print('  GET  /api/bidang    - List all fields')
    print('  GET  /api/health    - Health check')
    print('\n' + '='*70 + '\n')
    app.run(debug=True, host='127.0.0.1', port=5001, use_reloader=False)

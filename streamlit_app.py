from http.server import SimpleHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Dict, List, Any
import json
import socket
import socketserver
import threading
from urllib.parse import urlparse

from model.knn_model import EduPathKNNModel
from backend.utils import generate_personal_alasan

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"
MODEL_DIR = BASE_DIR / "model"

# Load the KNN model once.
model = EduPathKNNModel(
    csv_path=str(MODEL_DIR / "major_profile.csv"),
    synthetic_data_path=str(MODEL_DIR / "synthetic_dataset.csv")
)


def _normalize_academic_scores(nilai_dict: Dict[str, float]) -> Dict[str, float]:
    return {subject: float(nilai_dict.get(subject, 75.0)) for subject in [
        'math', 'indonesian', 'english', 'biology', 'physics', 'chemistry', 'economics', 'sociology'
    ]}


def _normalize_riasec_scores(riasec_dict: Dict[str, float]) -> Dict[str, float]:
    return {r_type: float(riasec_dict.get(r_type, 18.0)) for r_type in ['R', 'I', 'A', 'S', 'E', 'C']}


def _write_json(handler: SimpleHTTPRequestHandler, payload: Any, status: int = 200):
    body = json.dumps(payload).encode('utf-8')
    handler.send_response(status)
    handler.send_header('Access-Control-Allow-Origin', '*')
    handler.send_header('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    handler.send_header('Access-Control-Allow-Headers', 'Content-Type')
    handler.send_header('Content-Type', 'application/json')
    handler.send_header('Content-Length', str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class EduPathRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND_DIR), **kwargs)

    def do_OPTIONS(self):
        if self.path.startswith('/api/'):
            self.send_response(204)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
        else:
            super().do_OPTIONS()

    def do_GET(self):
        parsed_path = urlparse(self.path).path

        if parsed_path.startswith('/api/'):
            return self.handle_api()

        if parsed_path in ['/', '/app']:
            self.path = '/index.html'
            return super().do_GET()

        if '.' not in Path(parsed_path).name:
            self.path = '/index.html'
            return super().do_GET()

        return super().do_GET()

    def do_POST(self):
        if self.path == '/api/analyze':
            return self.handle_api()

        self.send_error(404, 'Not Found')

    def handle_api(self):
        parsed_path = urlparse(self.path).path

        try:
            if parsed_path == '/api/analyze':
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length).decode('utf-8') if content_length else ''

                try:
                    data = json.loads(body)
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}, body: {body}")
                    return _write_json(self, {'success': False, 'error': 'Request body must be JSON'}, status=400)

                if not data:
                    return _write_json(self, {'success': False, 'error': 'Request body must be JSON'}, status=400)

                required_fields = ['nilai', 'riasec']
                for field in required_fields:
                    if field not in data:
                        return _write_json(self, {'success': False, 'error': f"Missing required field: '{field}'"}, status=400)

                nilai_dict = data['nilai']
                riasec_dict = data['riasec']
                prestasi = int(data.get('prestasi', 0))
                bidang_prestasi = data.get('bidang_prestasi', '')
                minat = data.get('minat', [])

                academic_scores = _normalize_academic_scores(nilai_dict)
                riasec_scores = _normalize_riasec_scores(riasec_dict)

                print(f"Analyzing student: academic_scores={academic_scores}, riasec={riasec_scores}")
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

                response = {
                    'success': True,
                    'top3': top3_res,
                    'analysis': {
                        'top_subjects': analysis['top_subjects'],
                        'riasec_type': analysis['riasec_type'],
                        'riasec_scores': analysis['riasec_scores'],
                        'riasec_top3': analysis['riasec_top3']
                    }
                }
                print(f"Sending response: {response}")
                return _write_json(self, response)

            if parsed_path == '/api/jurusans':
                return _write_json(self, {'success': True, 'jurusans': model.get_all_jurusans(), 'count': len(model.get_all_jurusans())})

            if parsed_path == '/api/bidang':
                return _write_json(self, {'success': True, 'bidang': model.get_all_bidang(), 'count': len(model.get_all_bidang())})

            if parsed_path == '/api/health':
                return _write_json(self, {'status': 'healthy', 'model_loaded': model is not None})

            print(f"API path not found: {parsed_path}")
            self.send_error(404, 'Not Found')

        except Exception as e:
            print(f"API handler error: {e}")
            import traceback
            traceback.print_exc()
            return _write_json(self, {'success': False, 'error': str(e)}, status=500)

    def log_message(self, format: str, *args: Any) -> None:
        # Silence standard HTTP request logging in Streamlit.
        return


class ThreadingHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True


def start_local_backend_server() -> int:
    server = ThreadingHTTPServer(('127.0.0.1', 0), EduPathRequestHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return port


backend_port = start_local_backend_server()
frontend_url = f'http://127.0.0.1:{backend_port}/'

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title='EduPath AI', layout='wide')

st.markdown(
    '<style>'
    'section.main > div.block-container{padding:0 !important; margin:0 !important;}'
    '</style>',
    unsafe_allow_html=True,
)

components.iframe(frontend_url, height=1600, scrolling=True)

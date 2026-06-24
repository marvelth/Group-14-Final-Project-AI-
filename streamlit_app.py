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


import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title='EduPath AI', layout='wide')

st.markdown(
    '<style>'
    'section.main > div.block-container{padding:0 !important; margin:0 !important;}'
    'iframe {border: none;}'
    '</style>',
    unsafe_allow_html=True,
)

# Declare component pointing to the frontend directory
edu_path_component = components.declare_component("edu_path", path=str(FRONTEND_DIR))

# Initialize response data in session state
if "response_data" not in st.session_state:
    st.session_state.response_data = None

# Render custom component passing the response data
component_value = edu_path_component(
    key="edu_path_component",
    response_data=st.session_state.response_data,
    height=1600
)

# Handle actions from the component
if component_value:
    action = component_value.get("action")
    if action == "analyze":
        request_data = component_value.get("requestData")
        riasec = component_value.get("riasec")
        
        nilai_dict = request_data.get('nilai', {})
        riasec_dict = request_data.get('riasec', {})
        prestasi = int(request_data.get('prestasi', 0))
        bidang_prestasi = request_data.get('bidang_prestasi', '')
        minat = request_data.get('minat', [])

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

        st.session_state.response_data = {
            'top3': top3_res,
            'riasec': riasec
        }
        st.rerun()

    elif action == "reset":
        st.session_state.response_data = None
        st.rerun()

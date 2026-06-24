# EduPath AI — Major Recommendation System

**EduPath AI** adalah sistem pendukung keputusan (decision support system) berbasis Kecerdasan Buatan (AI) yang dirancang untuk membantu siswa SMA (khususnya kelas 10–12) menemukan program studi (jurusan kuliah) yang paling sesuai. Sistem ini menggunakan algoritma **K-Nearest Neighbors (KNN)** yang dilatih menggunakan dataset sintetis yang dibangun secara dinamis berdasarkan profil ideal masing-masing jurusan.

Sistem menganalisis data siswa berdasarkan **4 Dimensi Utama**:
1. **Nilai Akademik** — Rata-rata nilai rapor untuk 8 mata pelajaran utama (skala 0–100).
2. **Prestasi Extrakurikuler** — Bidang prestasi dan tingkat kompetisi yang pernah dicapai.
3. **Minat Utama** — Pilihan bidang minat yang disukai oleh siswa.
4. **Profil Kepribadian RIASEC** — Tes kepribadian Holland untuk mengukur tipe karakter (*Realistic, Investigative, Artistic, Social, Enterprising, Conventional*) melalui 36 pertanyaan.

Hasil akhir menyajikan **Top 3 Rekomendasi Jurusan** yang dilengkapi dengan persentase kecocokan (similarity score) dan penjelasan personal (explainable AI) yang dinamis.

---

## Link Hasil Deploy
Setelah dideploy, Anda dapat mengakses web EduPath AI secara langsung melalui link berikut:
- **[EduPath AI Web Application (Live Deploy)](https://final-project-edupath-ai.streamlit.app/)**


---

## Fitur Utama
- **RIASEC Personality Analysis**: Asesmen kepribadian Holland terintegrasi (36 pertanyaan) untuk memetakan kecenderungan minat karir siswa.
- **KNN Recommendation Engine**: Rekomendasi cerdas menggunakan algoritma K-Nearest Neighbors (k=7) dengan pembobotan jarak Euclidean berbasis profil ideal jurusan.
- **Explainable AI (XAI)**: Setiap rekomendasi jurusan disertai alasan kontekstual yang menjelaskan hubungan nilai akademik, prestasi, dan kepribadian siswa dengan jurusan tersebut.
- **Interactive Visualization**: Grafik radar dan grafik batang interaktif untuk menggambarkan profil kepribadian RIASEC dan kekuatan akademik siswa.
- **Premium Glassmorphism UI**: Antarmuka web yang modern, responsif, dan dinamis menggunakan vanilla HTML, CSS, dan JavaScript.
- **Ethical & Bias Documentation**: Laporan komprehensif mengenai analisis bias model dan penilaian dampak etis penggunaan kecerdasan buatan.

---

## Struktur Folder Proyek
Berikut adalah struktur folder terbaru dari proyek EduPath AI:

```
├── frontend/                     # Klien Antarmuka (HTML/CSS/JS)
│   ├── index.html                # UI utama satu halaman (Single-Page Application)
│   ├── css/
│   │   └── style.css             # Stylesheet premium bertema Glassmorphic
│   └── js/
│       ├── app.js                # Pengelola state aplikasi & handler API AJAX
│       ├── riasec.js             # Logika alur kuis RIASEC
│       ├── results.js            # Rendering grafik hasil rekomendasi
│       └── streamlit-component-lib.js # Jembatan komunikasi Custom Component Streamlit
│
├── backend/                      # Logika utilitas Python dan pembantu data
│   ├── utils.py                  # Logika pembuat teks penjelasan rekomendasi (natural language)
│   └── requirements.txt          # Daftar package Python lokal backend
│
├── model/                        # Lapisan Machine Learning & Dataset
│   ├── evaluation_charts         # Grafik hasil evaluasi model KNN
│       ├── confusion_matrix.png  # Confusion matrix heatmap (test set, K=7)
│       ├── crossval_scores.png   # 5-Fold Cross Validation per-fold accuracy
│       ├── field_accuracy.png    # Average accuracy grouped by academic field
│       ├── per_class_f1.png      # Per-class F1-score for all 30 majors
│   ├── knn_model.py              # Kelas model KNN & pembuat data sintetis Gaussian
│   ├── evaluate_knn.py           # Script pengujian akurasi klasifikasi KNN
│   ├── major_profile.csv         # Profil ideal 30 jurusan (Dataset acuan)
│   └── riasec_questions.csv      # Daftar 36 pertanyaan kuis kepribadian RIASEC
│
├── documents/                    # Dokumen Laporan AI & Poster (PDF Reports & Posters)
│   ├── bias_analysis_report.pdf  # Laporan evaluasi performa model dan analisis bias
│   ├── ethical_impact_assessment.pdf # Analisis dampak etis kecerdasan buatan (berdasarkan poster)
│   └── edupath_poster.pdf        # Poster Rangkuman Edupath AI
│
├── app.py                        # SERVER UTAMA: Flask backend & static server (Direkomendasikan)
├── streamlit_app.py              # Wrapper Streamlit menggunakan Custom Component
├── Dockerfile                    # Konfigurasi container untuk deploy ke production
├── requirements.txt              # Ketergantungan package Python global
├── README.md                     # Dokumentasi proyek (Dokumen ini)
└── .gitignore                    # File yang diabaikan oleh Git (venv, caches, dll)
```

---

## Cara Menjalankan Aplikasi Secara Lokal - Manual Instalasi (Langkah demi Langkah)

1. **Clone repositori proyek ini** ke komputer Anda.
2. **Buka terminal** lalu arahkan ke direktori proyek:
   ```bash
   cd Group-14-Final-Project-AI-
   ```
3. **Buat Virtual Environment (venv)** agar package tidak bentrok dengan library global sistem Anda:
   ```bash
   python3 -m venv venv
   ```
4. **Aktifkan Virtual Environment**:
   - Di macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - Di Windows (Command Prompt):
     ```cmd
     venv\Scripts\activate.bat
     ```
   - Di Windows (PowerShell):
     ```powershell
     venv\Scripts\Activate.ps1
     ```
5. **Upgrade pip ke versi terbaru**:
   ```bash
   pip install --upgrade pip
   ```
6. **Instal seluruh dependensi** yang tercantum di file `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```


---

### Menjalankan Server Aplikasi

Anda memiliki dua opsi server untuk menjalankan aplikasi ini di komputer Anda:

#### Opsi 1: Server Flask Standalone (Sangat Direkomendasikan)
Cara ini paling cepat, ringan, dan merupakan representasi deploy yang sebenarnya karena melayani API dan file frontend secara native pada port 5001.

```bash
python3 app.py
```
Setelah berjalan, buka browser Anda dan akses:
👉 **[http://localhost:5001](http://localhost:5001)**

#### Opsi 2: Streamlit Local Wrapper
Aplikasi akan dijalankan melalui Streamlit dan menampilkan klien frontend di dalam `st.iframe`.

```bash
streamlit run streamlit_app.py
```
Setelah berjalan, Streamlit akan otomatis membuka tab browser baru ke URL Streamlit (biasanya port 8501).

---

## Evaluasi Akurasi Model AI
Untuk menguji performa akurasi model KNN pada dataset sintetis 3.000 sampel (menggunakan metode split data 80% training / 20% testing), jalankan perintah:

```bash
python3 model/evaluate_knn.py
```

Hasil pengujian akurasi pada beberapa nilai K:
- **K = 1** — Top-1: 88.33% | Top-3: 97.50%
- **K = 3** — Top-1: 89.17% | Top-3: 97.50%
- **K = 5** — Top-1: 91.33% | Top-3: 97.50%
- **K = 7** — Top-1: **91.33%** | Top-3: **97.50%** *(Nilai Default)*
- **K = 9** — Top-1: 90.83% | Top-3: 97.50%

Akurasi Top-3 sebesar **97.50%** menunjukkan bahwa model KNN sangat andal dalam menempatkan jurusan ideal siswa ke dalam daftar 3 besar rekomendasi.

---

## Panduan Deployment (Menyebarluaskan Aplikasi ke Internet)

Aplikasi EduPath AI dapat dengan mudah di-deploy secara online agar dapat diakses oleh publik. Berikut adalah beberapa metode deployment yang direkomendasikan:

### 1. Deploy Menggunakan Docker (Rekomendasi Utama)
Karena proyek ini sudah dilengkapi dengan `Dockerfile`, Anda dapat melakukan deployment ke cloud provider modern seperti **Railway**, **Fly.io**, atau **Google Cloud Run** secara otomatis:
- Hubungkan akun Git Anda dengan platform cloud (misalnya Railway).
- Buat layanan baru dan arahkan ke repositori Git ini.
- Railway/Fly.io akan mendeteksi `Dockerfile` secara otomatis, melakukan *build*, mengekspos port `5001`, dan memberikan URL publik gratis.

### 2. Deploy di Render (Web Service Tanpa Docker)
Render menyediakan hosting gratis untuk aplikasi Python/Flask. Langkah-langkahnya:
1. Daftar atau masuk ke [Render.com](https://render.com/).
2. Buat layanan baru dengan memilih **New > Web Service**.
3. Hubungkan ke repositori Git proyek ini.
4. Konfigurasikan detail berikut:
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app` (atau `python app.py` jika ingin menjalankan file startup bawaan secara langsung)
5. Tambahkan Environment Variable di bagian settings (opsional):
   - `PORT` = `5001` (atau Render akan menetapkannya secara dinamis)
6. Klik **Deploy Web Service**. Render akan membuatkan tautan web publik seperti `https://edupath-ai.onrender.com`.

### 3. Deploy Frontend dan Backend Terpisah
Untuk performa optimal dan beban server minimal, Anda juga dapat memisahkan layanannya:
- **Frontend (Static Hosting)**: Deploy folder `frontend/` ke platform gratis seperti **Vercel**, **Netlify**, atau **GitHub Pages**. (Ubah konfigurasi fetch base URL di `frontend/js/app.js` agar mengarah ke URL server backend publik Anda).
- **Backend (Python API Hosting)**: Deploy backend Flask ini ke **Render**, **Railway**, atau **Heroku**.

---

## Kelompok (Group 14)
Aplikasi ini dikembangkan sebagai Proyek Akhir AI oleh Kelompok 14 yang beranggotakan:
- **Marvel Evan Theofani** — 140810240012
- **Kezia Tabhita Smith** — 140810240020
- **Farell Tirtawijaya** — 140810240072
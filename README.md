# 🎯 JurusanKu - Sistem Rekomendasi Jurusan Berbasis KNN AI

## 📌 Ringkasan Proyek

**JurusanKu** adalah aplikasi web yang membantu siswa SMA (kelas 10-12) di Indonesia menemukan jurusan kuliah yang paling sesuai dengan profil mereka menggunakan algoritma **K-Nearest Neighbors (KNN)**.

Sistem ini menganalisis siswa berdasarkan 4 dimensi:
1. ✅ **Nilai Akademik** - Nilai rapor 8 mata pelajaran
2. ✅ **Prestasi** - Tingkat dan bidang prestasi akademik
3. ✅ **Minat Utama** - 7 kategori bidang studi pilihan
4. ✅ **Profil Kepribadian RIASEC** - Tes 36 pertanyaan

Kemudian memberikan **top 3 rekomendasi jurusan** dengan skor kecocokan dan alasan spesifik.

---

## 🚀 Quick Start (5 Menit)

### 1️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 2️⃣ Jalankan Flask Server
```bash
python app_integrated.py
```

### 3️⃣ Akses Aplikasi
Buka browser: **http://localhost:5000**

---

## 📁 File Struktur

```
├── coba.html              # 🎨 Frontend HTML/CSS/JavaScript
├── knn_model.py          # 🧠 Core KNN Algorithm
├── app_integrated.py     # 🚀 Flask API Server
├── test_knn_model.py     # 🧪 Test Suite
├── major_profile.csv     # 📊 Dataset 31 Jurusan
├── requirements.txt      # 📦 Dependencies
├── SETUP_GUIDE.md       # 📖 Detailed Setup
└── README.md            # 📄 This File


## 🧠 Algoritma KNN

Sistem menggunakan **Euclidean Distance** untuk menghitung kecocokan antara profil siswa dan profil jurusan:

$$\text{distance} = \sqrt{\sum_{i=1}^{14} (x_i - y_i)^2}$$

**Semakin kecil distance → semakin cocok**

Setiap siswa & jurusan direpresentasikan sebagai vektor 14 dimensi:
- 8 nilai akademik (Math, Bindo, Binggris, Bio, Fisika, Kimia, Ekonomi, Sosiologi)
- 6 skor RIASEC (Realistic, Investigative, Artistic, Social, Enterprising, Conventional)

---

## 🔧 API Endpoints

### POST /api/analyze
Menganalisis profil siswa dan return top 3 rekomendasi jurusan.

**Request:**
```json
{
  "nama": "Andi Pratama",
  "kelas": "12",
  "nilai": {
    "math": 85, "bindo": 75, "binggris": 80, "bio": 70,
    "fisika": 88, "kimia": 82, "ekonomi": 65, "sosiologi": 72
  },
  "riasec": {"R": 18, "I": 25, "A": 12, "S": 20, "E": 22, "C": 24},
  "prestasi": 2,
  "bidang_prestasi": "Matematika",
  "minat": ["Sains dan Teknologi", "Teknik"]
}
```

**Response:**
```json
{
  "success": true,
  "top3": [
    {
      "jurusan": "Teknik Elektro",
      "bidang": "Teknik",
      "persen": 87,
      "alasan": "Nilai Fisika-mu sangat baik..."
    }
  ]
}
```

---

## 🧪 Testing

```bash
python test_knn_model.py
```

Menjalankan 5 test cases dengan berbagai profil siswa + edge case testing.

---

## 📖 Dokumentasi Lengkap

Lihat **[SETUP_GUIDE.md](SETUP_GUIDE.md)** untuk:
- Setup & installation detail
- Algorithm explanation mendalam
- API reference lengkap
- Troubleshooting guide

---

## 🎓 Penggunaan

### Untuk Siswa
1. Isi data akademik dengan jujur
2. Jawab 36 pertanyaan RIASEC sesuai kondisi nyata
3. Dapatkan rekomendasi top 3 jurusan
4. **Konsultasikan hasil dengan Guru BK**

### Untuk Guru BK
- Gunakan sebagai panduan diskusi awal dengan siswa
- Cross-reference dengan tes psikologi formal
- Pertimbangkan faktor eksternal (biaya, lokasi, etc)

---

## 📊 Dataset

File `major_profile.csv` berisi profil 31 jurusan dengan:
- Nilai ideal setiap mata pelajaran (1-5)
- Profil RIASEC ideal (1-5)
- Kategori bidang studi

---

## 🐛 Troubleshooting

| Masalah | Solusi |
|---------|--------|
| "Connection refused" | Jalankan: `python app_integrated.py` |
| "CSV not found" | Pastikan `major_profile.csv` di direktori utama |
| API error | Cek console Flask untuk detail error |

---

## 💡 Next Steps

1. **Test model**: `python test_knn_model.py`
2. **Run server**: `python app_integrated.py`
3. **Access app**: http://localhost:5000
4. **Isi form**: Ikuti 3 langkah input
5. **Lihat hasil**: Top 3 rekomendasi jurusan

---

## 🧪 ML Evaluation Notes

- I added an 80/20 evaluation script (`evaluate_knn.py`) and also embedded evaluation utilities in `knn_model.py`.
- I ran the 80/20 evaluation on the repository dataset and it produced 0% Top-1 and Top-3 accuracy for several `k` values. Reason:
  - `major_profile.csv` is a prototype of *one profile per jurusan* (each jurusan appears once). A standard classification split (80/20) is not appropriate because the test set often contains jurusan labels not present in the training fold.

Recommendations (options):

1. Field-level evaluation (recommended): evaluate whether the model's top predictions belong to the same `bidang` (field) as the ground-truth — more meaningful for this dataset.
2. Leave-One-Out ranking: run LOOCV but score whether the nearest neighbor (excluding self) shares the same `bidang`.
3. Synthetic sampling: create multiple synthetic student samples per jurusan by adding small noise to the profile vectors, then run standard train/test to measure classification accuracy.

How to reproduce the quick 80/20 run I executed:

```bash
pip install -r requirements.txt
python evaluate_knn.py
```

If you want, I can implement LOOCV field-level evaluation or the synthetic-sampling approach and add plots and a short report. Say which option you prefer and I will implement it.


**Dibuat untuk membantu siswa Indonesia memilih jurusan yang tepat 🎯**
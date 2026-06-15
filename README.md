# 🎯 EduPath AI — Major Recommendation System

## 📌 Overview

**EduPath AI** is an intelligent web application designed to help high school students (grades 10–12) discover their ideal university major. It uses a **K-Nearest Neighbors (KNN)** algorithm trained on a dynamically generated synthetic student dataset based on professional major profiles.

The system analyzes student profiles across **4 dimensions**:

1. ✅ **Academic Scores** — Average grades in 8 subjects (0–100 scale)
2. ✅ **Achievements** — Competition achievement levels and corresponding fields
3. ✅ **Primary Interests** — Up to 3 selected areas of interest
4. ✅ **RIASEC Personality Profile** — A 36-question interest and aptitude test

Based on this data, it provides the **top 3 recommended majors** with similarity match percentages and randomized, highly personalized explanations.

---

## 📁 Project Structure

```
├── frontend/                     # Frontend Client (HTML/CSS/JS)
│   ├── index.html                # Single-page application UI
│   ├── css/
│   │   └── style.css             # Premium glassmorphism stylesheet
│   └── js/
│       ├── app.js                # Core app state & API handler
│       ├── riasec.js             # RIASEC test flow controller
│       └── results.js            # Results & charts rendering
│
├── backend/                      # Backend utilities and shared Python helpers
│   ├── utils.py                  # Personalized reason generator
│   └── requirements.txt          # Python packages list
│
├── model/                        # Machine Learning Model Layer
│   ├── knn_model.py              # KNN class & synthetic data generator
│   ├── evaluate_knn.py           # Classifier accuracy evaluation script
│   ├── major_profile.csv         # English ideal profile dataset
│   └── riasec_questions.csv      # 36 English RIASEC questions
│
├── README.md                     # Documentation
├── streamlit_app.py              # New Streamlit wrapper that embeds the existing frontend
└── .gitignore                    # Ignored files (caches, venv)
```

---

## Start

### 1️⃣ Install Dependencies

```bash
pip3 install -r requirements.txt
```

### 2️⃣ Run the Server

- **Streamlit deployment**
  ```bash
  streamlit run streamlit_app.py
  ```
  Then open the Streamlit URL shown in the terminal.

> `streamlit_app.py` is the main entrypoint now. The `backend/` folder remains for shared helpers like `utils.py`.

### 3️⃣ Open the App

Open the URL printed by Streamlit after startup.

---

## 🧠 How the AI Works

### KNN Algorithm with Synthetic Training Data

1. **Synthetic Data Generation**: For each of the 30 majors defined in `model/major_profile.csv`, the model generates 100 synthetic student records (totaling 3,000 samples) by applying Gaussian noise to the ideal major profile. This provides a robust training set.
2. **Feature Vector**: Each student profile and major profile is structured as a 14-dimensional normalized vector:
   - 8 academic scores normalized to a $0\text{--}1$ scale (Math, Indonesian, English, Biology, Physics, Chemistry, Economics, Sociology).
   - 6 RIASEC scores normalized to a $0\text{--}1$ scale (Realistic, Investigative, Artistic, Social, Enterprising, Conventional).
3. **Distance Calculation**: The system computes the Euclidean distance from the student's normalized vector to all 3,000 synthetic samples.
4. **Weighted Voting**: The K-Nearest Neighbors (with $K=7$) vote on the best major matches, weighted by inverse distance.
5. **Bonus Adjustment**: Distances are adjusted with bonuses:
   - *Achievement Bonus*: Matches in achievement fields reduce distance by `level * 0.05`.
   - *Interest Bonus*: Matches in interest fields reduce distance by `0.03` per matching interest.
6. **Similarity Score**: Distance is converted to similarity percentage using:

$$\text{similarity} = 100 \times e^{-\text{distance} \times 1.5}$$

Matches are clamped to a realistic $40\%\text{--}98\%$ range.

---

## 🔧 API Endpoints

### POST `/api/analyze`

Analyzes student profile and returns top 3 major recommendations.

**Request Body Example:**
```json
{
  "nama": "Jane Doe",
  "kelas": "12",
  "nilai": {
    "math": 85, 
    "indonesian": 75, 
    "english": 80, 
    "biology": 70,
    "physics": 88, 
    "chemistry": 82, 
    "economics": 65, 
    "sociology": 72
  },
  "riasec": {
    "R": 18, 
    "I": 25, 
    "A": 12, 
    "S": 20, 
    "E": 22, 
    "C": 24
  },
  "prestasi": 2,
  "bidang_prestasi": "Technology",
  "minat": ["Science & Technology", "Engineering"]
}
```

**Response Body Example:**
```json
{
  "success": true,
  "top3": [
    {
      "jurusan": "Computer Science",
      "bidang": "Science and Technology",
      "persen": 89.2,
      "alasan": "With an outstanding 88 in Physics, you show the logical skills required for Computer Science. Your Investigative personality trait aligns strongly with Science and Technology majors. This path is an excellent way to leverage your talents."
    },
    ...
  ],
  "analysis": {
    "riasec_type": "ICR",
    "top_subjects": [["physics", 88.0], ["math", 85.0], ["chemistry", 82.0]]
  }
}
```

---

## 🧪 Model Evaluation

To run an accuracy evaluation check on the synthetic dataset, run:

```bash
python3 model/evaluate_knn.py
```

This runs an 80/20 train/test split on the 3,000 synthetic samples and outputs Top-1 and Top-3 accuracy scores.

---

## 📊 Dataset

### Major Profiles (`model/major_profile.csv`)

Includes ideal requirements for **30 majors** across 7 fields:

| Field | Recommended Majors |
|-------|--------------------|
| Health | Medicine, Pharmacy |
| Engineering | Industrial Engineering, Civil Engineering, Electrical Engineering, Mechanical Engineering, Architecture |
| Science and Technology | Computer Science, Information Systems, Statistics, Actuarial Science, Mathematics, Biology |
| Education and Creative | Guidance and Counseling, English Education, Visual Communication Design, Film and Animation |
| Economics and Business | Management, Accounting, Digital Business, Economics, Entrepreneurship |
| Agriculture and Marine | Marine Science, Agrotechnology, Agribusiness |
| Social, Law and Governance | Psychology, Law, International Relations, Political Science, Public Administration |

---

## ☁️ Deployment Guide

### Local Development
Run the app locally with Streamlit:

```bash
streamlit run streamlit_app.py
```

### Production Deployment
1. **Docker Deployment**: You can wrap this Streamlit application in a Docker container using a `Dockerfile`:
   ```dockerfile
   FROM python:3.10-slim
   WORKDIR /app
   COPY backend/requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   COPY . .
   EXPOSE 8501
   CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.headless=true"]
   ```
2. **Cloud Hosting**: Deploy using any host that supports Streamlit, such as Streamlit Community Cloud, Render, or Heroku. Point the start command to `streamlit run streamlit_app.py --server.port=$PORT --server.headless=true`.
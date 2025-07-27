# 🩺 Real-Time Chronic Disease Monitoring and Recommendation System

This project is a full-stack web application that enables users to monitor chronic health conditions such as diabetes and hypertension. The system allows users to manually input vital signs, predicts their condition using machine learning models, and provides personalized recommendations. It also includes AR-based therapeutic exercises for enhanced engagement and self-care.

---

## 📌 Features

- Manual input of vital health parameters: glucose, blood pressure, heart rate, temperature, and SPO₂
- Machine learning-based condition classification using XGBoost
- Personalized health recommendations based on prediction outcomes
- Web-based AR exercise demos using 3D models
- Clean and responsive web UI for input, result display, and AR interaction

---

## 🛠️ Tech Stack

| Component            | Technology Used                 |
|----------------------|----------------------------------|
| **Frontend**         | HTML, CSS, JavaScript            |
| **Backend**          | Python, Flask                    |
| **Machine Learning** | XGBoost, Scikit-learn, Pandas, NumPy |
| **AR Integration**   | Mixamo (3D animations), A-Frame  |
| **Dataset Source**   | Kaggle (health vitals dataset)   |
| **Tools**            | Git, GitHub                      |

---

## 📊 Dataset Information

- **Source:** Kaggle  
- **Format:** `.xlsx` (tabular)  
- **Size:** ~17,000 entries  
- **Features:**
  - **Vitals:** Glucose, BP, Heart Rate, Temperature, SPO₂
  - **Demographics:** Age, Gender, BMI
  - **Lifestyle:** Sleep, Exercise, Smoking, Alcohol
  - **Medical Info:** Family History, Medication
- **Target Labels:** Multi-class (Low, Normal, High) for each vital

---

## 🚀 Getting Started

### 📦 Prerequisites
- Python 3.x
- Flask
- pip packages listed in `requirements.txt`

### ⚙️ Installation
```bash
git clone https://github.com/YourUsername/chronic-disease-monitoring.git
cd chronic-disease-monitoring
pip install -r requirements.txt
python app.py

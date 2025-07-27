from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
import numpy as np
import joblib
import pandas as pd
from datetime import datetime
import pytz

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Load model and scaler
model = joblib.load("model/multi_output_xgb_model.pkl")
scaler = joblib.load("model/scaler.pkl")

# Initialize DB
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        name TEXT,
        age INTEGER,
        gender TEXT,
        height_cm REAL,
        weight_kg REAL,
        exercise_steps INTEGER,
        sleep_hours REAL,
        smoking TEXT,
        alcohol TEXT,
        family_history TEXT,
        family_history_hypertension TEXT,
        medication TEXT,
        cholesterol REAL,
        hba1c REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        glucose REAL,
        systolic REAL,
        diastolic REAL,
        heart_rate REAL,
        body_temp REAL,
        spo2 REAL,
        sweating TEXT,
        shivering TEXT,
        predicted_glucose TEXT,
        predicted_systolic TEXT,
        predicted_diastolic TEXT,
        predicted_heart_rate TEXT,
        predicted_body_temp TEXT,
        predicted_spo2 TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

init_db()

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]
            return redirect(url_for('home'))
        return "Invalid credentials"
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
        except sqlite3.IntegrityError:
            return "Username already exists"
        conn.close()
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('home.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if request.method == 'POST':
        data = (
            request.form['name'], request.form['age'], request.form['gender'],
            request.form['height_cm'], request.form['weight_kg'], request.form['exercise_steps'],
            request.form['sleep_hours'], request.form['smoking'], request.form['alcohol'],
            request.form['family_history'], request.form['family_history_hypertension'], request.form['medication'],
            request.form['cholesterol'], request.form['hba1c'], user_id
        )
        cursor.execute("""
        UPDATE users SET name=?, age=?, gender=?, height_cm=?, weight_kg=?,
        exercise_steps=?, sleep_hours=?, smoking=?, alcohol=?, family_history=?, family_history_hypertension=?, medication=?,
        cholesterol=?, hba1c=?
        WHERE id=?
        """, data)
        conn.commit()

    cursor.execute("SELECT name, age, gender, height_cm, weight_kg, exercise_steps, sleep_hours, smoking, alcohol, family_history, family_history_hypertension, medication, cholesterol, hba1c FROM users WHERE id=?", (user_id,))
    profile_data = cursor.fetchone()
    conn.close()

    return render_template('profile.html', user=profile_data)

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    result = None

    if request.method == 'POST':
        # Log form data
        print("🔹 Received Form Data:", dict(request.form))

        try:
            # Step 1: Extract form inputs
            glucose = float(request.form['glucose'])
            systolic = float(request.form['systolic'])
            diastolic = float(request.form['diastolic'])
            heart_rate = float(request.form['heart_rate'])
            body_temp = float(request.form['body_temp'])
            spo2 = float(request.form['spo2'])
            sweating = int(request.form['sweating'])
            shivering = int(request.form['shivering'])

            print("✅ Inputs Parsed Successfully")

            # Step 2: Fetch user profile
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("""
                SELECT age, gender, height_cm, weight_kg, exercise_steps, sleep_hours,
                       smoking, alcohol, family_history, family_history_hypertension, medication, cholesterol, hba1c
                FROM users WHERE id=?
            """, (user_id,))
            profile = cursor.fetchone()
            conn.close()

            print("🔹 Retrieved Profile:", profile)

            if not profile:
                return "⚠️ User profile not found.", 404

            # Step 3: Process and encode profile data
            age = float(profile[0])
            gender = 1 if str(profile[1]).lower() == "male" else 0
            height_cm = float(profile[2])
            weight_kg = float(profile[3])
            bmi = weight_kg / ((height_cm / 100) ** 2)
            exercise = float(profile[4])
            sleep = float(profile[5])
            smoking = 1 if str(profile[6]).lower() == "yes" else 0
            alcohol = 1 if str(profile[7]).lower() == "yes" else 0
            family_history = 1 if str(profile[8]).lower() == "yes" else 0
            family_history_hypertension = 1 if str(profile[9]).lower() == "yes" else 0
            medication = 1 if str(profile[10]).lower() == "yes" else 0
            cholesterol = float(profile[11])
            hba1c = float(profile[12])

            print("✅ Features Processed")

            # Step 4: Combine all features
            features = np.array([[ 
                age, glucose, diastolic, systolic, heart_rate, body_temp, spo2, 
                sweating, shivering, gender, height_cm, weight_kg, bmi, hba1c, 
                cholesterol, exercise, sleep, smoking, alcohol, family_history, 
                family_history_hypertension, medication
            ]])


            print("📦 Final Feature Vector:", features)

           
            feature_names = [
                'Age', 'Blood Glucose Level(BGL)', 'Diastolic Blood Pressure', 'Systolic Blood Pressure', 
                'Heart Rate', 'Body Temperature', 'SPO2', 'Sweating  (Y/N)', 'Shivering (Y/N)', 
                'Gender', 'Height (cm)', 'Weight (kg)', 'BMI', 'HbA1c (%)', 'Cholesterol (mg/dL)', 
                'Exercise (Steps/Day)', 'Sleep (Hours)', 'Smoking (Y/N)', 'Alcohol (Y/N)', 
                'Family History (Diabetes)', 'Family History (Hypertension)', 'Medication (Y/N)'
            ]


            # Convert to DataFrame with feature names
            features_df = pd.DataFrame(features, columns=feature_names)

            # Step 5: Scale features
            features_scaled = scaler.transform(features_df)
            print("🔧 Features Scaled:", features_scaled)

            # Step 6: Predict
            raw_preds = model.predict(features_scaled)[0]
            print("📈 Raw Model Output:", raw_preds)

            labels = ["Low", "Normal", "High"]
            preds = [labels[int(p)] for p in raw_preds]
            print("✅ Mapped Predictions:", preds)

            # Step 7: Store to DB
            ist = pytz.timezone('Asia/Kolkata')
            timestamp_ist = datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S')

            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO predictions (
                    user_id, glucose, systolic, diastolic, heart_rate, body_temp, spo2,
                    sweating, shivering,
                    predicted_glucose, predicted_systolic, predicted_diastolic,
                    predicted_heart_rate, predicted_body_temp, predicted_spo2,
                    timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, glucose, systolic, diastolic, heart_rate, body_temp, spo2,
                sweating, shivering,
                preds[0], preds[1], preds[2], preds[3], preds[4], preds[5],
                timestamp_ist
            ))
            conn.commit()
            conn.close()

            print("✅ Prediction Stored in DB")

            # Step 8: Show prediction to user
            result = {
                "Blood Glucose": preds[0],
                "Systolic BP": preds[1],
                "Diastolic BP": preds[2],
                "Heart Rate": preds[3],
                "Body Temperature": preds[4],
                "Oxygen Level (SPO2)": preds[5]
            }

        except Exception as e:
            print("❌ Error during prediction:", str(e))
            return f"Error: {str(e)}"

    return render_template("predict.html", result=result)

@app.route('/history')
def history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
    SELECT glucose, systolic, diastolic,
           predicted_glucose, predicted_systolic, predicted_diastolic,
           heart_rate, body_temp, spo2,
           predicted_heart_rate, predicted_body_temp, predicted_spo2, timestamp
    FROM predictions WHERE user_id=? ORDER BY timestamp DESC LIMIT 12
    """, (user_id,))
    records = cursor.fetchall()
    conn.close()
    return render_template("history.html", records=records)


from new_recommend import generate_final_recommendation,recommendation_rules, internal_conflicts
@app.route('/recommendation', methods=['GET'])
def recommendation():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Get user profile
    cursor.execute('SELECT name FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()

    # Get latest prediction
    cursor.execute(''' 
        SELECT predicted_glucose, predicted_systolic, predicted_diastolic,
               predicted_heart_rate, predicted_body_temp, predicted_spo2
        FROM predictions
        WHERE user_id = ? 
        ORDER BY timestamp DESC 
        LIMIT 1
    ''', (user_id,))
    prediction = cursor.fetchone()
    conn.close()

    if not user or not prediction:
        return "Profile or Prediction data not found. Please complete both before viewing recommendations."

    name = user[0]
    glucose, systolic, diastolic, heart_rate, temperature, oxygen = prediction

    print("User:", name)
    print("Predicted Glucose:", glucose)
    print("Predicted Systolic BP:", systolic)
    print("Predicted Diastolic BP:", diastolic)
    print("Predicted Heart Rate:", heart_rate)
    print("Predicted Body Temperature:", temperature)
    print("Predicted Oxygen Level:", oxygen)

    # health_condition = {
    #     'glucose': glucose,
    #     'systolic': systolic,
    #     'diastolic': diastolic,
    #     'heart_rate': heart_rate,
    #     'temperature': temperature,
    #     'oxygen': oxygen
    # }

    # Map 'low', 'normal', 'high' to 0, 1, 2
    health_condition = {
        'glucose': {'Low': 0, 'Normal': 1, 'High': 2}.get(glucose, None),
        'systolic': {'Low': 0, 'Normal': 1, 'High': 2}.get(systolic, None),
        'diastolic': {'Low': 0, 'Normal': 1, 'High': 2}.get(diastolic, None),
        'heart_rate': {'Low': 0, 'Normal': 1, 'High': 2}.get(heart_rate, None),
        'temperature': {'Low': 0, 'Normal': 1, 'High': 2}.get(temperature, None),
        'oxygen': {'Low': 0, 'Normal': 1, 'High': 2}.get(oxygen, None)
    }
    

    print("health condition",health_condition)

    # Check if any health condition is None after mapping
    if None in health_condition.values():
        return "Invalid health data received. Please check the health information."

    final_recommendation = generate_final_recommendation(health_condition, recommendation_rules, internal_conflicts)

    print("final recommendation",final_recommendation)
    

    return render_template('recommendation.html',
                           name=name,
                           do_recommendations=final_recommendation['do'],
                           dont_recommendations=final_recommendation['dont'],
                           diet_recommendations=final_recommendation['diet'],
                           exercise_recommendations=final_recommendation['exercise'])

@app.route('/ar-exercise')
def ar_exercise():
    return render_template('ar_exercise.html')  # this will load static/ar/index.html inside a layout if needed

if __name__ == '__main__':
    app.run(debug=True)

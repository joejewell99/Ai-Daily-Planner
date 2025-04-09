import sqlite3
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import joblib
import numpy as np
from datetime import datetime


def load_task_data():
    """Load task data from the SQLite database"""
    conn = sqlite3.connect("trainingData.db")
    df = pd.read_sql_query("SELECT * FROM tasks", conn)
    conn.close()
    return df


def convert_time_to_minutes(time_str):
    """Convert a time string (e.g. '7:00PM') to the number of minutes from midnight"""
    time_obj = datetime.strptime(time_str, "%I:%M%p")
    return time_obj.hour * 60 + time_obj.minute


def convert_minutes_to_time(minutes):
    """Convert minutes since midnight to time in 12-hour AM/PM format"""
    # Round the minutes to the nearest integer to avoid float-related issues
    minutes = int(round(minutes))

    hour = minutes // 60
    minute = minutes % 60
    return f"{hour % 12 or 12}:{minute:02d} {'AM' if hour < 12 else 'PM'}"


def train_model(df):
    """Train the RandomForestRegressor model using task data"""

    df_terra = df[df['name'] == 'Terra']
    print(df_terra['time'].value_counts())

    # Convert time strings to minutes from midnight
    df['time_minutes'] = df['time'].apply(convert_time_to_minutes)

    # Label encode task names
    le_task = LabelEncoder()
    df['task_encoded'] = le_task.fit_transform(df['name'])

    # Features and target
    X = df[['task_encoded']]              # Only use task name as input
    y = df['time_minutes']                # Predict minutes from midnight

    model = RandomForestRegressor()
    model.fit(X, y)

    # Save model + encoder
    joblib.dump(model, "model.pkl")
    joblib.dump(le_task, "label_encoder.pkl")
    print("✅ Model and label encoder saved!")



def generate_schedule(task_names):
    """Generate a predicted schedule using the trained model"""
    try:
        model = joblib.load("model.pkl")
        le_task = joblib.load("label_encoder.pkl")
    except FileNotFoundError:
        print("❌ Model not found. Train the model first.")
        return

    # Encode task names
    encoded_tasks = le_task.transform(task_names)
    X_new = np.array(encoded_tasks).reshape(-1, 1)  # <-- keep it 1-feature

    # Predict time in minutes from midnight
    predicted_minutes = model.predict(X_new)
    predicted_minutes = [round(m) for m in predicted_minutes]
    predicted_times = [convert_minutes_to_time(m) for m in predicted_minutes]

    # Save the predictions to the database
    conn = sqlite3.connect("predicted_schedule.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS ai_schedule (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        time TEXT
    )''')

    for name, time in zip(task_names, predicted_times):  # <-- use correct variable
        cursor.execute("INSERT INTO ai_schedule (name, time) VALUES (?, ?)", (name, time))

    conn.commit()
    conn.close()
    print("✅ AI-generated schedule saved to predicted_schedule.db")


# 🔽 Add this so it runs when script is executed directly
if __name__ == "__main__":
    df = load_task_data()
    train_model(df)

    # Example task names to generate predictions for:
    task_names = ["Terra", "Gaming"]
    generate_schedule(task_names)

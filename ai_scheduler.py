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
    # Check the distribution of 'Terra' tasks in your training data
    df_terra = df[df['name'] == 'Terra']
    print(df_terra['time'].value_counts())  # This will print the distribution of times for Terra

    # Convert time to a numerical feature (e.g., extract the hour from time)
    df['time_hour'] = pd.to_datetime(df['time'], errors='coerce').dt.hour

    # Convert target 'time' to numerical values (e.g., minutes from midnight)
    df['time_minutes'] = df['time'].apply(convert_time_to_minutes)

    # One-hot encode the task names
    le_task = LabelEncoder()
    df['task_encoded'] = le_task.fit_transform(df['name'])

    # Prepare the features (task and time)
    X = df[['task_encoded', 'time_hour']]  # Use task encoding and time in hour
    y = df['time_minutes']  # Use the new 'time_minutes' as target

    # Train RandomForestRegressor model
    model = RandomForestRegressor()
    model.fit(X, y)

    # Save the model and the label encoder
    joblib.dump(model, "model.pkl")
    joblib.dump(le_task, "label_encoder.pkl")
    print("✅ Model and label encoder saved!")


def generate_schedule(task_names):
    """Generate a predicted schedule using the trained model"""
    try:
        # Load the trained model and label encoder
        model = joblib.load("model.pkl")
        le_task = joblib.load("label_encoder.pkl")
    except FileNotFoundError:
        print("❌ Model not found. Train the model first using train_model(df).")
        return

    # Encode the task names
    encoded_tasks = le_task.transform(task_names)
    # Create a dummy 'time_hour' feature (e.g., setting it to a default time like 9 AM for now)
    time_hour_dummy = [9] * len(task_names)  # You can choose another time if you want

    # Combine both encoded task names and time hour for prediction
    X_new = np.array(list(zip(encoded_tasks, time_hour_dummy)))

    # Make predictions (the predicted times will be in minutes)
    predicted_times = model.predict(X_new)

    # Convert predicted times back to time format (if needed)
    predicted_times_in_format = [convert_minutes_to_time(minutes) for minutes in predicted_times]

    # Save the predictions to the database
    conn = sqlite3.connect("predicted_schedule.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS ai_schedule (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        time TEXT
    )''')

    for name, time in zip(task_names, predicted_times_in_format):
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

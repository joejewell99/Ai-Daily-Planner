from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Initialize database for tasks
def init_db():
    with sqlite3.connect("tasks.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                time TEXT NOT NULL,
                color TEXT DEFAULT '#ffffff'
            )
        ''')
        cursor.execute("PRAGMA table_info(tasks)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'color' not in columns:
            cursor.execute("ALTER TABLE tasks ADD COLUMN color TEXT DEFAULT '#ffffff'")
        conn.commit()

# Initialize database for training data
def init_training_data_db():
    with sqlite3.connect("trainingData.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                time TEXT NOT NULL,
                color TEXT DEFAULT '#ffffff'
            )
        ''')
        conn.commit()

# Call the initialization functions once
init_db()
init_training_data_db()

@app.route("/schedule", methods=["GET"])
def get_tasks():
    with sqlite3.connect("tasks.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks")
        tasks = [{"id": row[0], "name": row[1], "time": row[2], "color": row[3]} for row in cursor.fetchall()]
    return jsonify(tasks)

@app.route("/schedule", methods=["POST"])
def add_task():
    data = request.json
    name = data.get("name")
    time = data.get("time")
    color = data.get("color", "#ffffff")

    if not name or not time:
        return jsonify({"error": "Name and time are required"}), 400

    with sqlite3.connect("tasks.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (name, time, color) VALUES (?, ?, ?)", (name, time, color))
        conn.commit()

    return jsonify({"message": "Task added"}), 201

@app.route("/schedule/<int:task_id>", methods=["PUT"])
def edit_task(task_id):
    data = request.json
    name = data.get("name")
    time = data.get("time")
    color = data.get("color")

    if not name and not time and not color:
        return jsonify({"error": "Provide at least one field to update"}), 400

    with sqlite3.connect("tasks.db") as conn:
        cursor = conn.cursor()
        updates = []
        values = []

        if name:
            updates.append("name=?")
            values.append(name)
        if time:
            updates.append("time=?")
            values.append(time)
        if color:
            updates.append("color=?")
            values.append(color)

        values.append(task_id)
        query = f"UPDATE tasks SET {', '.join(updates)} WHERE id=?"
        cursor.execute(query, values)
        conn.commit()

    return jsonify({"message": "Task updated"}), 200

@app.route("/schedule/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    """Deletes a task, resets task IDs, and adds the task to the training data database."""
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()

    # Retrieve the task data before deleting it
    cursor.execute("SELECT * FROM tasks WHERE id=?", (task_id,))
    task = cursor.fetchone()

    if task is None:
        conn.close()
        return jsonify({"error": "Task not found"}), 404

    # Add the task to the training data database (without the ID to avoid conflicts)
    with sqlite3.connect("trainingData.db") as training_conn:
        training_cursor = training_conn.cursor()
        # Insert the task into the training database without the `id`
        training_cursor.execute("INSERT INTO tasks (name, time, color) VALUES (?, ?, ?)",
                                (task[1], task[2], task[3]))
        training_conn.commit()

    # Now delete the task from tasks.db
    cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()

    # Reset task IDs (optional step)
    reset_task_ids()

    conn.close()
    print(f"✅ Task {task_id} deleted and added to training data.")
    return jsonify({"message": f"Task {task_id} deleted and added to training data."}), 200

def reset_task_ids():
    """Reorders task IDs sequentially (1,2,3...) and resets sqlite_sequence."""
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM tasks ORDER BY id")
    tasks = cursor.fetchall()

    for index, (old_id,) in enumerate(tasks, start=1):
        cursor.execute("UPDATE tasks SET id = ? WHERE id = ?", (index, old_id))

    conn.commit()
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='tasks'")
    conn.commit()
    conn.close()
    print("✅ Task IDs and sqlite_sequence reset successfully.")

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)

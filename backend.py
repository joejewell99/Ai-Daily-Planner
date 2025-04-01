from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Initialize database
def init_db():
    with sqlite3.connect("tasks.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                time TEXT NOT NULL
            )
        ''')
        conn.commit()

init_db()

@app.route("/schedule", methods=["GET"])
def get_tasks():
    with sqlite3.connect("tasks.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks")
        tasks = [{"id": row[0], "name": row[1], "time": row[2]} for row in cursor.fetchall()]
    return jsonify(tasks)

@app.route("/schedule", methods=["POST"])
def add_task():
    data = request.json
    name, time = data.get("name"), data.get("time")

    if not name or not time:
        return jsonify({"error": "Name and time are required"}), 400

    with sqlite3.connect("tasks.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (name, time) VALUES (?, ?)", (name, time))
        conn.commit()

    return jsonify({"message": "Task added"}), 201

@app.route("/schedule/<int:task_id>", methods=["PUT"])
def edit_task(task_id):
    data = request.json
    name, time = data.get("name"), data.get("time")

    if not name and not time:
        return jsonify({"error": "Provide at least a name or time to update"}), 400

    with sqlite3.connect("tasks.db") as conn:
        cursor = conn.cursor()

        if name and time:
            cursor.execute("UPDATE tasks SET name=?, time=? WHERE id=?", (name, time, task_id))
        elif name:
            cursor.execute("UPDATE tasks SET name=? WHERE id=?", (name, task_id))
        elif time:
            cursor.execute("UPDATE tasks SET time=? WHERE id=?", (time, task_id))

        conn.commit()

    return jsonify({"message": "Task updated"}), 200

@app.route("/schedule/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    """Deletes a task, resets task IDs, and fixes sqlite_sequence."""
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()

    # Check if task exists
    cursor.execute("SELECT * FROM tasks WHERE id=?", (task_id,))
    if cursor.fetchone() is None:
        conn.close()
        return jsonify({"error": "Task not found"}), 404

    # Delete the selected task
    cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()

    # Reset task IDs and sqlite_sequence
    reset_task_ids()

    conn.close()
    print(f"✅ Task {task_id} deleted and IDs updated.")

    return jsonify({"message": f"Task {task_id} deleted and IDs reset"}), 200

def reset_task_ids():
    """Reorders task IDs sequentially (1,2,3...) and resets sqlite_sequence."""
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM tasks ORDER BY id")
    tasks = cursor.fetchall()

    for index, (old_id,) in enumerate(tasks, start=1):
        cursor.execute("UPDATE tasks SET id = ? WHERE id = ?", (index, old_id))

    conn.commit()

    # Reset the sqlite_sequence so IDs start from the highest existing one
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='tasks'")
    conn.commit()

    conn.close()
    print("✅ Task IDs and sqlite_sequence reset successfully.")

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)

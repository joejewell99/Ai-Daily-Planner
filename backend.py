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
        return jsonify({"error": "Name and time required"}), 400

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
        cursor.execute("UPDATE tasks SET name=?, time=? WHERE id=?", (name, time, task_id))
        conn.commit()

    return jsonify({"message": "Task updated"}), 200

@app.route("/schedule/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    with sqlite3.connect("tasks.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        conn.commit()

    return jsonify({"message": "Task deleted"}), 200

if __name__ == "__main__":
    app.run(debug=True)

def get_task_count():
    """Returns the total number of tasks in the table."""
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]

    conn.close()
    return count


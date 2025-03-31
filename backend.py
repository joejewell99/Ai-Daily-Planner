from flask import Flask, jsonify, request

app = Flask(__name__)

# Sample schedule data (stored in memory for now)
schedule = [
    {"id": 1, "name": "Morning Workout", "time": "07:00 AM"},
    {"id": 2, "name": "Team Meeting", "time": "10:00 AM"},
]

@app.route("/schedule", methods=["GET"])
def get_schedule():
    return jsonify(schedule)

@app.route("/schedule", methods=["POST"])
def add_task():
    """Add a new task"""
    data = request.json
    new_task = {
        "id": len(schedule) + 1,
        "name": data["name"],
        "time": data["time"]
    }
    schedule.append(new_task)
    return jsonify({"message": "Task added!", "task": new_task}), 201

@app.route("/schedule/<int:task_id>", methods=["PUT"])
def edit_task(task_id):
    """Edit an existing task"""
    data = request.json
    for task in schedule:
        if task["id"] == task_id:
            task["name"] = data.get("name", task["name"])
            task["time"] = data.get("time", task["time"])
            return jsonify({"message": "Task updated!", "task": task})
    return jsonify({"error": "Task not found"}), 404

@app.route("/schedule/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    """Delete a task"""
    global schedule
    schedule = [task for task in schedule if task["id"] != task_id]
    return jsonify({"message": "Task deleted!"})

if __name__ == "__main__":
    app.run(debug=True)

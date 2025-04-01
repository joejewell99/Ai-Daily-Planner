import sqlite3

def create_database():
    # Connect to SQLite database (it will create the database file if it doesn't exist)
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()

    # Create table for tasks (if it doesn't already exist)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_name TEXT NOT NULL,
            priority INTEGER,
            start_time TEXT,
            end_time TEXT,
            duration REAL
        )
    ''')

    # Commit and close the connection
    conn.commit()
    conn.close()

# Call the function to create the database and table
create_database()

def get_all_tasks():
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM tasks')
    tasks = cursor.fetchall()

    conn.close()
    return tasks

# Example usage
tasks = get_all_tasks()
for task in tasks:
    print(task)

def insert_task(task_name, priority, start_time, end_time, duration=None):
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO tasks (task_name, priority, start_time, end_time, duration)
        VALUES (?, ?, ?, ?, ?)
    ''', (task_name, priority, start_time, end_time, duration))

    conn.commit()
    conn.close()

def reset_tasks():
    """Deletes all tasks and resets the ID sequence."""
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()

    # Reset the auto-increment counter (SQLite specific)
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='tasks'")

    conn.commit()
    conn.close()
    print("Tasks table has been reset.")

import sqlite3

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
            duration REAL,
        )
    ''')

    # Commit changes and close the connection
    conn.commit()
    conn.close()



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


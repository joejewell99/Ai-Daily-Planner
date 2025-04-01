import re
import sys
import requests
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QLineEdit, QFormLayout, QHBoxLayout, QListWidget, QMessageBox, QCalendarWidget
)
from PyQt6.QtGui import QFont, QColor, QPalette
from PyQt6.QtCore import Qt, QCoreApplication

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set the level to INFO to capture messages of level INFO and higher
    format='%(asctime)s - %(levelname)s - %(message)s',  # Customize log format
    handlers=[
        logging.StreamHandler(),  # Output logs to the console
        logging.FileHandler('app.log')  # Also output logs to a file
    ]
)

API_URL = "http://127.0.0.1:5000/schedule"

class ScheduleApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("🗓️ AI Daily Planner")
        self.setGeometry(200, 200, 900, 450)
        self.setStyleSheet(self.load_styles())

        self.layout = QHBoxLayout()

        left_layout = QVBoxLayout()

        self.title_label = QLabel("📅 Today's Schedule")
        self.title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(self.title_label)

        self.task_list = QListWidget()
        self.task_list.setStyleSheet(
            "QListWidget { background-color: #1e1e1e; color: white; border-radius: 8px; padding: 5px; }"
        )
        self.task_list.itemClicked.connect(self.select_task)  # Connect to select_task
        left_layout.addWidget(self.task_list)

        form_layout = QFormLayout()
        self.task_name_input = QLineEdit()
        self.task_time_input = QLineEdit()
        form_layout.addRow("📝 Task Name:", self.task_name_input)
        form_layout.addRow("⏰ Task Time:", self.task_time_input)
        left_layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        self.add_button = QPushButton("➕ Add Task")
        self.edit_button = QPushButton("✏️ Edit Task")
        self.delete_button = QPushButton("❌ Delete Task")
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        left_layout.addLayout(button_layout)

        self.layout.addLayout(left_layout, 1)

        self.calendar = QCalendarWidget()
        self.calendar.setStyleSheet(
            "QCalendarWidget { background-color: #1e1e1e; color: white; border-radius: 8px; padding: 10px; }"
            "QHeaderView::section { background-color: #2e2e2e; color: white; }"
            "QCalendarWidget QAbstractItemView:enabled { background-color: #2e2e2e; }"
        )
        self.layout.addWidget(self.calendar, 2)

        self.add_button.clicked.connect(self.add_task)
        self.edit_button.clicked.connect(self.edit_task)
        self.delete_button.clicked.connect(self.delete_task)

        self.setLayout(self.layout)
        self.fetch_schedule()

    def load_styles(self):
        return """
            QWidget { background-color: #121212; color: white; font-size: 14px; }
            QLabel { color: #ffcc00; font-size: 16px; }
            QPushButton { background-color: #ffcc00; color: black; border-radius: 10px; padding: 8px; font-size: 14px; }
            QPushButton:hover { background-color: #ffaa00; }
            QPushButton:pressed { background-color: #cc8800; }
            QLineEdit { background-color: #1e1e1e; color: white; border: 2px solid #ffcc00; border-radius: 5px; padding: 5px; }
        """

    def fetch_schedule(self):
        self.task_list.clear()
        try:
            response = requests.get(API_URL)
            if response.status_code == 200:
                self.schedule = response.json()
                for task in self.schedule:
                    self.task_list.addItem(f"{task['id']}. {task['time']} - {task['name']}")
            else:
                QMessageBox.warning(self, "Error", "Failed to load schedule from the server!")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Network Error", f"Failed to connect to server!\n{str(e)}")

    def add_task(self):
        name = self.task_name_input.text().strip()
        time = self.task_time_input.text().strip()
        time_pattern = r'^(0?[1-9]|1[0-2]):([0-5][0-9])\s*(AM|PM)$'
        if not name or not time:
            QMessageBox.warning(self, "Input Error", "Task name and time cannot be empty!")
            return
        elif not re.match(time_pattern, time):
            QMessageBox.warning(self, "Input Error", "Please enter time in the format HH:MM AM/PM or H:MM AM/PM.")
            return

        try:
            response = requests.post(API_URL, json={"name": name, "time": time})
            if response.status_code == 201:
                print("Task added successfully!")
                self.task_name_input.clear()
                self.task_time_input.clear()
                self.fetch_schedule()
            else:
                QMessageBox.warning(self, "Error", "Failed to add task.")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Network Error", f"Could not send request!\n{str(e)}")

    def edit_task(self):
        selected_item = self.task_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Selection Error", "Select a task to edit!")
            return

        task_id = int(selected_item.text().split(".")[0])
        name = self.task_name_input.text().strip()
        time = self.task_time_input.text().strip()
        time_pattern = r'^(0?[1-9]|1[0-2]):([0-5][0-9])\s*(AM|PM)$'

        if not name and not time:
            QMessageBox.warning(self, "Input Error", "Enter a new name or time to edit!")
            return
        elif not re.match(time_pattern, time):
            QMessageBox.warning(self, "Input Error", "Please enter time in the format HH:MM AM/PM or H:MM AM/PM.")
            return

        try:
            response = requests.put(f"{API_URL}/{task_id}", json={"name": name, "time": time})
            if response.status_code == 200:
                logging.info("Task edited successfully!")
                self.fetch_schedule()
            else:
                QMessageBox.warning(self, "Error", "Failed to update task.")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Network Error", f"Could not send request!\n{str(e)}")

    def delete_task(self):
        selected_item = self.task_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Selection Error", "Select a task to delete!")
            return

        task_id = int(selected_item.text().split(".")[0])

        try:
            response = requests.delete(f"{API_URL}/{task_id}")
            if response.status_code == 200:
                logging.info("Task deleted successfully!")
                self.fetch_schedule()
            else:
                QMessageBox.warning(self, "Error", "Failed to delete task.")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Network Error", f"Could not send request!\n{str(e)}")

    def select_task(self, item):
        task_id = int(item.text().split(".")[0])
        print(f"Selected task ID: {task_id}")

    def closeEvent(self, event):
        QCoreApplication.quit()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ScheduleApp()
    window.show()
    sys.exit(app.exec())

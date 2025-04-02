import re
import sys
import random  # ✅ Make sure this is at the top of your file


import requests
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QLineEdit, QFormLayout, QHBoxLayout, QListWidget, QMessageBox, QCalendarWidget, QTableWidget, QSizePolicy,
    QHeaderView, QTableWidgetItem
)
from PyQt6.QtGui import QFont, QColor, QPalette, QBrush
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
        self.setGeometry(200, 200, 900, 600)
        self.setStyleSheet(self.load_styles())

        self.layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        # Today's Schedule
        self.title_label = QLabel("📅 Today's Schedule")
        self.title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(self.title_label)

        self.task_list = QListWidget()
        self.task_list.setStyleSheet(
            "QListWidget { background-color: #1e1e1e; color: white; border-radius: 8px; padding: 5px; }")
        self.task_list.itemClicked.connect(self.select_task)
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

        # Weekly Schedule
        self.weekly_label = QLabel("📅 Weekly Schedule")
        self.weekly_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.weekly_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(self.weekly_label)

        self.schedule_table = QTableWidget()
        self.schedule_table.setColumnCount(7)
        self.schedule_table.setRowCount(24)
        self.schedule_table.setHorizontalHeaderLabels([
            "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
        ])
        self.schedule_table.setVerticalHeaderLabels([f"{hour}:00" for hour in range(24)])
        # Create a QTableWidgetIt

        # Set the item in a specific row and column

        self.schedule_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)  # Proper resizing
        # Make columns resize dynamically when window size changes
        self.schedule_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.schedule_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.schedule_table.setDragEnabled(True)
        self.schedule_table.setAcceptDrops(True)
        self.schedule_table.setDropIndicatorShown(True)
        self.schedule_table.cellChanged.connect(self.cell_changed)
        right_layout.addWidget(self.schedule_table)

        #Save to pdf button
        self.save_pdf_button = QPushButton("💾 Save to PDF")
        right_layout.addWidget(self.save_pdf_button)

        # Refresh Button
        self.refresh_button = QPushButton("🔄 Refresh Schedule")
        self.refresh_button.clicked.connect(self.fetch_schedule)
        right_layout.addWidget(self.refresh_button)

        self.layout.addLayout(right_layout, 3)  # Makes the right side larger than the left

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

            /* Styling for the table */
            QTableWidget {
                background-color: none;
                color: white;
                border: none;
                font-size: 14px;
            }

            QTableWidget QTableCornerButton::section {
                background-color: #1e1e1e;
            }

            /* Table header styles */
            QHeaderView::section {
                background-color: #2a2a2a;
                color: White;
                border: 1px solid #333;
                padding: 5px;
                font-weight: bold;
            }

        
            /* Hover effect for table cells */
            QTableWidget::item:hover {
                background-color: #333333;
            }

            /* Selecting a row or column */
            QTableWidget::item:selected {
                background-color: #ffaa00;
            }
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

    def cell_changed(self, row, column):
        self.schedule_table.blockSignals(True)  # 🔴 Stop signals to prevent infinite loop

        task_item = self.schedule_table.item(row, column)
        if not task_item:
            task_item = QTableWidgetItem()
            self.schedule_table.setItem(row, column, task_item)

        if task_item.text().strip():
            r, g, b = random.randint(50, 200), random.randint(50, 200), random.randint(50, 200)
            color = QColor(r, g, b)

            task_item.setBackground(QBrush(color))  # ✅ Change background safely
            task_item.setForeground(QBrush(QColor(255, 255, 255)))  # ✅ Keep text visible

            logging.info(f"Task moved to {row}, {column} with new color {r}, {g}, {b}")

        self.schedule_table.blockSignals(False)  # 🟢 Re-enable signals

    def update_table(self):

        return


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ScheduleApp()
    window.show()
    sys.exit(app.exec())

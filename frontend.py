import sys
import requests
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QLineEdit, QFormLayout, QHBoxLayout, QListWidget, QMessageBox
)
from PyQt6.QtGui import QFont, QColor, QPalette
from PyQt6.QtCore import Qt

API_URL = "http://127.0.0.1:5000/schedule"


class ScheduleApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AI Daily Planner")
        self.setGeometry(200, 200, 500, 400)
        self.setStyleSheet(self.load_styles())  # Apply styles

        self.layout = QVBoxLayout()

        # Title
        self.title_label = QLabel("📅 Today's Schedule")
        self.title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.title_label)

        # Schedule List
        self.task_list = QListWidget()
        self.task_list.setStyleSheet(
            "QListWidget { background-color: #1e1e1e; color: white; border-radius: 8px; padding: 5px; }")
        self.layout.addWidget(self.task_list)

        # Add Task Inputs
        form_layout = QFormLayout()
        self.task_name_input = QLineEdit()
        self.task_time_input = QLineEdit()
        form_layout.addRow("📝 Task Name:", self.task_name_input)
        form_layout.addRow("⏰ Task Time:", self.task_time_input)
        self.layout.addLayout(form_layout)

        # Buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Task")
        self.edit_button = QPushButton("Edit Task")
        self.delete_button = QPushButton("Delete Task")
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        self.layout.addLayout(button_layout)

        # Connect Buttons to Actions
        self.add_button.clicked.connect(self.add_task)
        self.edit_button.clicked.connect(self.edit_task)
        self.delete_button.clicked.connect(self.delete_task)

        self.setLayout(self.layout)
        self.fetch_schedule()

    import sys
    import requests
    from PyQt6.QtWidgets import (
        QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
        QLineEdit, QFormLayout, QHBoxLayout, QListWidget, QMessageBox
    )
    from PyQt6.QtGui import QFont, QColor, QPalette
    from PyQt6.QtCore import Qt

    API_URL = "http://127.0.0.1:5000/schedule"

    class ScheduleApp(QWidget):
        def __init__(self):
            super().__init__()

            self.setWindowTitle("🗓️ AI Daily Planner")
            self.setGeometry(200, 200, 500, 450)
            self.setStyleSheet(self.load_styles())  # Apply styles

            self.layout = QVBoxLayout()

            # Title
            self.title_label = QLabel("📅 Today's Schedule")
            self.title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.layout.addWidget(self.title_label)

            # Schedule List
            self.task_list = QListWidget()
            self.task_list.setStyleSheet(
                "QListWidget { background-color: #1e1e1e; color: white; border-radius: 8px; padding: 5px; }")
            self.layout.addWidget(self.task_list)

            # Add Task Inputs
            form_layout = QFormLayout()
            self.task_name_input = QLineEdit()
            self.task_time_input = QLineEdit()
            form_layout.addRow("📝 Task Name:", self.task_name_input)
            form_layout.addRow("⏰ Task Time:", self.task_time_input)
            self.layout.addLayout(form_layout)

            # Buttons
            button_layout = QHBoxLayout()
            self.add_button = QPushButton("➕ Add Task")
            self.edit_button = QPushButton("✏️ Edit Task")
            self.delete_button = QPushButton("❌ Delete Task")
            button_layout.addWidget(self.add_button)
            button_layout.addWidget(self.edit_button)
            button_layout.addWidget(self.delete_button)
            self.layout.addLayout(button_layout)

            # Connect Buttons to Actions
            self.add_button.clicked.connect(self.add_task)
            self.edit_button.clicked.connect(self.edit_task)
            self.delete_button.clicked.connect(self.delete_task)

            self.setLayout(self.layout)
            self.fetch_schedule()

        def load_styles(self):
            """Returns modern CSS styles for the app."""
            return """
                QWidget {
                    background-color: #121212;
                    color: white;
                    font-size: 14px;
                }
                QLabel {
                    color: #ffcc00;
                    font-size: 16px;
                }
                QPushButton {
                    background-color: #ffcc00;
                    color: black;
                    border-radius: 10px;
                    padding: 8px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #ffaa00;
                }
                QPushButton:pressed {
                    background-color: #cc8800;
                }
                QLineEdit {
                    background-color: #1e1e1e;
                    color: white;
                    border: 2px solid #ffcc00;
                    border-radius: 5px;
                    padding: 5px;
                }
            """

        def fetch_schedule(self):
            """Fetch the schedule from the Flask API and update the UI."""
            self.task_list.clear()
            try:
                response = requests.get(API_URL)
                if response.status_code == 200:
                    self.schedule = response.json()
                    for task in self.schedule:
                        self.task_list.addItem(f"{task['id']}. {task['time']} - {task['name']}")
                else:
                    self.title_label.setText("Failed to load schedule!")
            except Exception as e:
                self.title_label.setText(f"Error: {str(e)}")

        def add_task(self):
            """Send a new task to the backend."""
            name = self.task_name_input.text().strip()
            time = self.task_time_input.text().strip()
            if not name or not time:
                QMessageBox.warning(self, "Input Error", "Task name and time cannot be empty!")
                return

            response = requests.post(API_URL, json={"name": name, "time": time})
            if response.status_code == 201:
                QMessageBox.information(self, "Success", "Task added successfully!")
                self.fetch_schedule()
            else:
                QMessageBox.warning(self, "Error", "Failed to add task.")

        def edit_task(self):
            """Edit an existing task."""
            selected_item = self.task_list.currentItem()
            if not selected_item:
                QMessageBox.warning(self, "Selection Error", "Select a task to edit!")
                return

            task_id = int(selected_item.text().split(".")[0])
            name = self.task_name_input.text().strip()
            time = self.task_time_input.text().strip()

            if not name and not time:
                QMessageBox.warning(self, "Input Error", "Enter a new name or time to edit!")
                return

            response = requests.put(f"{API_URL}/{task_id}", json={"name": name, "time": time})
            if response.status_code == 200:
                QMessageBox.information(self, "Success", "Task updated successfully!")
                self.fetch_schedule()
            else:
                QMessageBox.warning(self, "Error", "Failed to update task.")

        def delete_task(self):
            """Delete a selected task."""
            selected_item = self.task_list.currentItem()
            if not selected_item:
                QMessageBox.warning(self, "Selection Error", "Select a task to delete!")
                return

            task_id = int(selected_item.text().split(".")[0])

            response = requests.delete(f"{API_URL}/{task_id}")
            if response.status_code == 200:
                QMessageBox.information(self, "Success", "Task deleted successfully!")
                self.fetch_schedule()
            else:
                QMessageBox.warning(self, "Error", "Failed to delete task.")

    # Run the PyQt Application
    if __name__ == "__main__":
        app = QApplication(sys.argv)
        window = ScheduleApp()
        window.show()
        sys.exit(app.exec())

    def fetch_schedule(self):
        """Fetch the schedule from the Flask API and update the UI."""
        self.task_list.clear()
        try:
            response = requests.get(API_URL)
            if response.status_code == 200:
                self.schedule = response.json()
                for task in self.schedule:
                    self.task_list.addItem(f"{task['id']}. {task['time']} - {task['name']}")
            else:
                self.title_label.setText("Failed to load schedule!")
        except Exception as e:
            self.title_label.setText(f"Error: {str(e)}")

    def add_task(self):
        """Send a new task to the backend."""
        name = self.task_name_input.text().strip()
        time = self.task_time_input.text().strip()
        if not name or not time:
            QMessageBox.warning(self, "Input Error", "Task name and time cannot be empty!")
            return

        response = requests.post(API_URL, json={"name": name, "time": time})
        if response.status_code == 201:
            QMessageBox.information(self, "Success", "Task added successfully!")
            self.fetch_schedule()
        else:
            QMessageBox.warning(self, "Error", "Failed to add task.")

    def edit_task(self):
        """Edit an existing task."""
        selected_item = self.task_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Selection Error", "Select a task to edit!")
            return

        task_id = int(selected_item.text().split(".")[0])
        name = self.task_name_input.text().strip()
        time = self.task_time_input.text().strip()

        if not name and not time:
            QMessageBox.warning(self, "Input Error", "Enter a new name or time to edit!")
            return

        response = requests.put(f"{API_URL}/{task_id}", json={"name": name, "time": time})
        if response.status_code == 200:
            QMessageBox.information(self, "Success", "Task updated successfully!")
            self.fetch_schedule()
        else:
            QMessageBox.warning(self, "Error", "Failed to update task.")

    def delete_task(self):
        """Delete a selected task."""
        selected_item = self.task_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Selection Error", "Select a task to delete!")
            return

        task_id = int(selected_item.text().split(".")[0])

        response = requests.delete(f"{API_URL}/{task_id}")
        if response.status_code == 200:
            QMessageBox.information(self, "Success", "Task deleted successfully!")
            self.fetch_schedule()
        else:
            QMessageBox.warning(self, "Error", "Failed to delete task.")


# Run the PyQt Application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScheduleApp()
    window.show()
    sys.exit(app.exec())

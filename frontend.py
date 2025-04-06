import re
import sqlite3
import sys
import datetime
from ai_scheduler import generate_schedule


from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas

import requests
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QLineEdit, QFormLayout, QHBoxLayout, QListWidget, QMessageBox, QCalendarWidget, QTableWidget, QSizePolicy,
    QHeaderView, QTableWidgetItem, QFileDialog, QColorDialog
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

        self.selected_item = None  # Variable to hold the selected table item

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

        self.schedule_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)  # Proper resizing
        # Make columns resize dynamically when window size changes
        self.schedule_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.schedule_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.schedule_table.setDragEnabled(True)
        self.schedule_table.setAcceptDrops(True)
        self.schedule_table.setDropIndicatorShown(True)
        self.schedule_table.cellChanged.connect(self.cell_changed)
        # Connect item click to a method to store selected item
        self.schedule_table.cellClicked.connect(self.on_item_clicked)
        right_layout.addWidget(self.schedule_table)

        self.hBox_pdf_ai_scheduler_holder = QHBoxLayout()

        #Ai Scheduler button
        self.generate_button = QPushButton("🧠 Generate AI Schedule")
        self.generate_button.clicked.connect(self.run_ai_schedule)

        #Save to pdf button
        self.save_pdf_button = QPushButton("💾 Save to PDF")
        self.save_pdf_button.clicked.connect(self.save_to_pdf)

        self.hBox_pdf_ai_scheduler_holder.addWidget(self.generate_button)
        self.hBox_pdf_ai_scheduler_holder.addWidget(self.save_pdf_button)

        right_layout.addLayout(self.hBox_pdf_ai_scheduler_holder)

        # Create a horizontal box layout to hold the buttons
        self.hBox_edit_colour_refresh = QHBoxLayout()

        # Create the "Edit Colour" button
        self.editColour_button = QPushButton("🎨 Edit Colour")
        self.editColour_button.clicked.connect(self.open_color_picker)

        # Create the "Refresh Schedule" button
        self.refresh_button = QPushButton("🔄 Refresh Schedule")

        # Connect the refresh button to the update_table method
        self.refresh_button.clicked.connect(self.update_table)

        # Add buttons to the horizontal layout
        self.hBox_edit_colour_refresh.addWidget(self.editColour_button)
        self.hBox_edit_colour_refresh.addWidget(self.refresh_button)

        right_layout.addLayout(self.hBox_edit_colour_refresh)


        self.layout.addLayout(right_layout, 3)  # Makes the right side larger than the left

        self.add_button.clicked.connect(self.add_task)
        self.edit_button.clicked.connect(self.edit_task)
        self.delete_button.clicked.connect(self.delete_task)

        self.setLayout(self.layout)
        self.update_table()
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

        task_name = task_item.text().strip()

        if task_name:
            try:
                # Connect to the database (replace with your actual database path or connection details)
                connection = sqlite3.connect('tasks.db')  # Replace with your database path
                cursor = connection.cursor()

                # SQL query to fetch the color for the task name
                cursor.execute("SELECT color FROM tasks WHERE name = ?", (task_name,))
                result = cursor.fetchone()

                if result:
                    task_color = result[0]  # Assuming the color is stored in the first column
                    color = QColor(task_color)  # Convert the color (assuming it's stored in hex format)
                    task_item.setBackground(QBrush(color))  # Set the background to the fetched color
                else:
                    logging.warning(f"No color found for task {task_name} at {row}, {column}")

                # Set the text color to black explicitly
                task_item.setForeground(QBrush(QColor(0, 0, 0)))  # Ensure the text is black

                logging.info(f"Task {task_name} at {row}, {column} set to color")
            except sqlite3.Error as e:
                logging.error(f"Database error: {str(e)}")
            finally:
                connection.close()  # Always close the database connection

        self.schedule_table.blockSignals(False)  # 🟢 Re-enable signals

    def update_table(self):
        try:
            response = requests.get(API_URL)
            if response.status_code == 200:
                tasks = response.json()  # Get the task data from the response

                # Clear any previous tasks from the table
                for row in range(self.schedule_table.rowCount()):
                    for col in range(self.schedule_table.columnCount()):
                        self.schedule_table.setItem(row, col, None)  # Clear the cell

                # Iterate over each task and add it to the correct time slot in the table
                for task in tasks:
                    task_name = task['name']
                    task_time = task['time']

                    # Convert the time string to a row (assuming the format is 'HH:MM AM/PM')
                    row = self.get_row_from_time(task_time)
                    if row is None:
                        continue  # Skip tasks with invalid times

                    # Find the column based on the day (you can map it to a specific column index)
                    day_of_week = self.get_day_of_week()
                    column = self.get_column_from_day(day_of_week)

                    # Get the color for the task from the database
                    color = self.get_task_color(task_name)

                    # Create a new item and set its text (task name)
                    item = QTableWidgetItem(task_name)
                    item.setForeground(QBrush(QColor("black")))  # Text color black

                    # Set the background color of the task item if a valid color is found
                    if color:
                        item.setBackground(QBrush(QColor(color)))  # Set background to the task's color
                    else:
                        item.setBackground(QBrush(QColor("lightblue")))  # Fallback color

                    self.schedule_table.setItem(row, column, item)
            else:
                QMessageBox.warning(self, "Error", "Failed to load tasks from the server!")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Network Error", f"Failed to connect to server!\n{str(e)}")

    def get_task_color(self, task_name):
        """
        Retrieves the color for a task from the database using its name.
        Returns None if no color is found.
        """
        try:
            # Connect to the database
            connection = sqlite3.connect('tasks.db')  # Replace with your database path
            cursor = connection.cursor()

            # SQL query to fetch the color for the task name
            cursor.execute("SELECT color FROM tasks WHERE name = ?", (task_name,))
            result = cursor.fetchone()

            if result:
                task_color = result[0]  # Assuming the color is stored in the first column
                return task_color
            else:
                return None  # No color found for this task
        except sqlite3.Error as e:
            print(f"Database error: {str(e)}")
            return None  # Return None if there's an error
        finally:
            connection.close()  # Always close the database connection

    def get_row_from_time(self, time):
        """Convert a task time (HH:MM AM/PM) to a row index in the table."""
        time_pattern = r'^(0?[1-9]|1[0-2]):([0-5][0-9])\s*(AM|PM)$'
        match = re.match(time_pattern, time.strip())
        if match:
            hour = int(match.group(1))
            if match.group(3) == 'PM' and hour != 12:
                hour += 12
            elif match.group(3) == 'AM' and hour == 12:
                hour = 0
            return hour  # Return the row index for the 24-hour format (0-23)
        return None  # Return None if the time format is invalid

    def get_day_of_week(self):
        """Assign a day of the week (0-6) based on the current date."""
        # Get the current date
        current_date = datetime.datetime.now()

        # Get the day of the week (Monday=0, Tuesday=1, ..., Sunday=6)
        return current_date.weekday()

    def get_column_from_day(self, day_of_week):
        """Convert the day of the week (0-6) to a column index in the table."""
        return day_of_week  # 0 = Monday, 1 = Tuesday, ..., 6 = Sunday

    def save_to_pdf(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Schedule as PDF", "", "PDF Files (*.pdf)")
        if not file_path:
            return

        try:
            c = canvas.Canvas(file_path, pagesize=landscape(letter))
            width, height = landscape(letter)

            c.setFont("Helvetica-Bold", 18)
            c.drawCentredString(width / 2, height - 40, "Weekly Schedule")

            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            hours = [f"{h}:00" for h in range(24)]

            col_width = width / (len(days) + 1)
            row_height = (height - 80) / (len(hours) + 1)

            # Draw headers
            c.setFont("Helvetica-Bold", 10)
            for i, day in enumerate(days):
                c.drawString((i + 1) * col_width + 5, height - 60, day)
            for j, hour in enumerate(hours):
                c.drawString(5, height - 80 - (j + 1) * row_height + 5, hour)

            # Draw task content
            c.setFont("Helvetica", 8)
            for row in range(self.schedule_table.rowCount()):
                for col in range(self.schedule_table.columnCount()):
                    item = self.schedule_table.item(row, col)
                    if item:
                        text = item.text()
                        x = (col + 1) * col_width + 5
                        y = height - 80 - (row + 1) * row_height + 5
                        c.drawString(x, y, text)

            c.save()
            QMessageBox.information(self, "Success", f"Schedule saved to {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save PDF:\n{str(e)}")

    def on_item_clicked(self, row, column):
        """This method is triggered when a table cell is clicked."""
        item = self.schedule_table.item(row, column)

        # Check if the item is empty or has no text
        if item is None or item.text().strip() == "":
            self.selected_item = None  # Set selected_item to None if the item text is empty
            self.editColour_button.setEnabled(False)  # Disable the edit color button
        else:
            self.selected_item = item  # Store the selected item for color editing
            self.editColour_button.setEnabled(True)  # Enable the edit color button if the item has text

    def open_color_picker(self):
        """Open the QColorDialog to pick a color."""
        if not self.selected_item or not self.selected_item.text().strip():  # Check if item is valid and has text
            QMessageBox.warning(self, "No Item Selected", "Please select a task with a name from the schedule first!")
            return

        # Open the color picker dialog
        color = QColorDialog.getColor()

        if color.isValid():  # Check if the color is valid
            selected_color = color.name()  # Get the color in HEX format

            # Optionally, update the color in the database as well
            task_name = self.selected_item.text()
            self.update_task_color_in_db(task_name, selected_color)
            self.selected_item.setBackground(QBrush(color))

            logging.info(f"Color for task '{task_name}' updated to {selected_color}")

    def update_task_color_in_db(self, task_name, color):
        """Update the task color in the database."""
        try:
            connection = sqlite3.connect('tasks.db')
            cursor = connection.cursor()

            cursor.execute("UPDATE tasks SET color = ? WHERE name = ?", (color, task_name))
            connection.commit()
            connection.close()

        except sqlite3.Error as e:
            print(f"Database error: {str(e)}")

    def run_ai_schedule(self):
        # You can also pull tasks from your UI dynamically here
        task_names = ["Terra,Gaming"]

        try:
            generate_schedule(task_names)
            QMessageBox.information(self, "AI Schedule", "AI-generated schedule saved to predicted_schedule.db")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate schedule:\n{str(e)}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ScheduleApp()
    window.show()
    sys.exit(app.exec())

import sys
import os
import glob
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QLabel, QPushButton, QFileDialog, QHBoxLayout, QMessageBox,
                           QListWidget, QDialog, QLineEdit, QSpinBox, QFrame, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QFont, QScreen, QIcon

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cv_job_matcher import batch_match_cv_to_jobs, display_results
from job_cv_matcher import batch_match_job_to_cvs, get_job_files
from job_selection_dialog import JobSelectionDialog
from cv_selection_dialog import CVSelectionDialog
from results_dialog import ResultsDialog
from chat_dialog import ChatDialog
from excel_report_dialog import ExcelReportDialog
from generate_excel_report import generate_excel_report

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CV and Job Matching System")
        self.setWindowState(Qt.WindowState.WindowMaximized)  # Set window to maximized state

        # Set background color for the main window
        self.setStyleSheet("""
            QMainWindow { 
                background: #f6f8fa; 
            }
            QPushButton {
                background-color: #1976d2;
                color: white;
                border: none;
                padding: 28px 36px;
                text-align: center;
                font-size: 22px;
                margin: 4px 2px;
                border-radius: 12px;
                min-width: 280px;
                min-height: 140px;
                font-family: 'Segoe UI';
                font-weight: bold;
                transition: background 0.2s;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
        """)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(40)

        # Add title
        title = QLabel("CV and Job Matching System")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont('Segoe UI', 32, QFont.Weight.Bold))
        title.setStyleSheet("color: #1976d2;")
        main_layout.addWidget(title)

        # Add description
        description = QLabel("Select an option to begin:")
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setFont(QFont('Segoe UI', 18))
        description.setStyleSheet("color: #424242;")
        main_layout.addWidget(description)

        # Create button container
        button_container = QFrame()
        button_container.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 18px;
                border: 1px solid #e0e0e0;
                padding: 40px;
            }
            QPushButton {
                background-color: #1976d2;
                color: white;
                border: none;
                padding: 20px;
                text-align: center;
                font-size: 18px;
                margin: 4px 2px;
                border-radius: 12px;
                min-width: 200px;
                min-height: 120px;
                font-family: 'Segoe UI';
                font-weight: bold;
                transition: background 0.2s;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(32)
        shadow.setXOffset(0)
        shadow.setYOffset(8)
        shadow.setColor(Qt.GlobalColor.gray)
        button_container.setGraphicsEffect(shadow)

        # Create button layout
        button_layout = QHBoxLayout(button_container)
        button_layout.setSpacing(30)  # Spacing between buttons
        button_layout.setContentsMargins(20, 20, 20, 20)  # Margins around the buttons
        self.add_buttons(button_layout)

        # Add button container to main layout
        main_layout.addWidget(button_container, stretch=1)

    def add_buttons(self, layout):
        # First button - Match Job to CVs
        match_job_button = QPushButton("Match a Specific\nJob to CVs")
        match_job_button.setFont(QFont('Segoe UI', 18, QFont.Weight.Bold))
        match_job_button.setCursor(Qt.CursorShape.PointingHandCursor)
        match_job_button.clicked.connect(self.match_job_to_cvs)
        layout.addWidget(match_job_button)

        # Second button - Match CV to Jobs
        match_cv_button = QPushButton("Match a Specific\nCV to Jobs")
        match_cv_button.setFont(QFont('Segoe UI', 18, QFont.Weight.Bold))
        match_cv_button.setCursor(Qt.CursorShape.PointingHandCursor)
        match_cv_button.clicked.connect(self.match_cv_to_jobs)
        layout.addWidget(match_cv_button)

        # Third button - Interactive Analyser
        chat_button = QPushButton("Cv Analyser\nInterface")
        chat_button.setFont(QFont('Segoe UI', 18, QFont.Weight.Bold))
        chat_button.setCursor(Qt.CursorShape.PointingHandCursor)
        chat_button.clicked.connect(self.chat_interface)
        layout.addWidget(chat_button)

        # Fourth button - Generate Excel Report
        excel_button = QPushButton("Generate Excel\nReport")
        excel_button.setFont(QFont('Segoe UI', 18, QFont.Weight.Bold))
        excel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        excel_button.clicked.connect(self.generate_excel_report)
        layout.addWidget(excel_button)

    def match_job_to_cvs(self):
        dialog = JobSelectionDialog(self)
        if dialog.exec():
            selected_job = dialog.get_selected_job()
            if selected_job:
                # Use the file path directly instead of trying to extract ID
                job_path = selected_job['file_path']
                num_cvs = dialog.cv_count.value()
                
                # Perform matching
                results, job_name = batch_match_job_to_cvs(job_path, num_cvs)
                
                # Show results
                if results:
                    results_dialog = ResultsDialog(results, job_name, self)
                    results_dialog.exec()
                else:
                    QMessageBox.warning(self, "No Results", "No matching CVs found for the selected job.")
    
    def match_cv_to_jobs(self):
        dialog = CVSelectionDialog(self)
        if dialog.exec():
            selected_cv = dialog.get_selected_cv()
            if selected_cv:
                # Use the file path directly instead of trying to extract ID
                cv_path = selected_cv['file_path']
                num_jobs = dialog.job_count.value()
                
                # Perform matching
                results, cv_name = batch_match_cv_to_jobs(cv_path, num_jobs)
                
                # Show results
                if results:
                    results_dialog = ResultsDialog(results, cv_name, self)
                    results_dialog.exec()
                else:
                    QMessageBox.warning(self, "No Results", "No matching jobs found for the selected CV.")
    
    def chat_interface(self):
        dialog = ChatDialog(self)
        dialog.exec()

    def generate_excel_report(self):
        dialog = ExcelReportDialog(self)
        if dialog.exec():
            cv_count, job_count = dialog.get_counts()
            try:
                generate_excel_report(cv_count, job_count)
                self.show_success_dialog("Excel report generated successfully!", dialog.get_file_path())
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to generate Excel report: {str(e)}")

    def show_success_dialog(self, message, file_path=None):
        """Show a success dialog with the given message and optional file path."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Success")
        dialog.setFixedSize(500, 300)  # Increased size from 400x200 to 500x300
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(30, 30, 30, 30)  # Increased margins
        layout.setSpacing(20)  # Added spacing between elements
        
        # Message label
        message_label = QLabel(message)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setFont(QFont('Segoe UI', 14))  # Increased font size
        message_label.setStyleSheet("""
            color: #1976d2;
            padding: 10px;
            background-color: #e3f2fd;
            border-radius: 8px;
        """)  # Added background and padding
        message_label.setWordWrap(True)  # Enable word wrapping
        layout.addWidget(message_label)
        
        # Button container
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(20)
        
        # OK button
        ok_button = QPushButton("OK")
        ok_button.setFont(QFont('Segoe UI', 14))  # Increased font size
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                min-width: 120px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
        """)
        ok_button.clicked.connect(dialog.accept)
        
        # Open Excel button (only shown if file_path is provided)
        if file_path:
            open_excel_button = QPushButton("Open Excel")
            open_excel_button.setFont(QFont('Segoe UI', 14))  # Increased font size
            open_excel_button.setStyleSheet("""
                QPushButton {
                    background-color: #4caf50;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 12px 24px;
                    min-width: 120px;
                    min-height: 40px;
                }
                QPushButton:hover {
                    background-color: #43a047;
                }
            """)
            open_excel_button.clicked.connect(lambda: self.open_excel_file(file_path))
            button_layout.addWidget(open_excel_button)
        
        button_layout.addWidget(ok_button)
        layout.addWidget(button_container, alignment=Qt.AlignmentFlag.AlignCenter)
        
        dialog.exec()

    def open_excel_file(self, file_path):
        """Open the Excel file using the default system application."""
        try:
            if os.path.exists(file_path):
                os.startfile(file_path)
            else:
                self.show_error_dialog(f"File not found: {file_path}")
        except Exception as e:
            self.show_error_dialog(f"Error opening file: {str(e)}")

    def show_error_dialog(self, message):
        """Show an error dialog with the given message."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Error")
        dialog.setFixedSize(500, 300)  # Increased size from 400x200 to 500x300
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(30, 30, 30, 30)  # Increased margins
        layout.setSpacing(20)  # Added spacing between elements
        
        # Message label
        message_label = QLabel(message)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setFont(QFont('Segoe UI', 14))  # Increased font size
        message_label.setStyleSheet("""
            color: #d32f2f;
            padding: 10px;
            background-color: #ffebee;
            border-radius: 8px;
        """)  # Added background and padding
        message_label.setWordWrap(True)  # Enable word wrapping
        layout.addWidget(message_label)
        
        # OK button
        ok_button = QPushButton("OK")
        ok_button.setFont(QFont('Segoe UI', 14))  # Increased font size
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                min-width: 120px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #b71c1c;
            }
        """)
        ok_button.clicked.connect(dialog.accept)
        layout.addWidget(ok_button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        dialog.exec()

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 
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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CV and Job Matching System")
        self.setGeometry(0, 0, 900, 700)  # Slightly larger for modern look

        # Set background color for the main window
        self.setStyleSheet("QMainWindow { background: #f6f8fa; }")

        # Center the window on the screen
        self.center_window()

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Card-like frame for the main content
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 18px;
                border: 1px solid #e0e0e0;
                padding: 40px 40px 32px 40px;
            }
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(32)
        shadow.setXOffset(0)
        shadow.setYOffset(8)
        shadow.setColor(Qt.GlobalColor.gray)
        card.setGraphicsEffect(shadow)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(28)

        # Add title
        title = QLabel("CV and Job Matching System")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont('Segoe UI', 28, QFont.Weight.Bold))
        card_layout.addWidget(title)

        # Add description
        description = QLabel("Select an option to begin:")
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setFont(QFont('Segoe UI', 15))
        card_layout.addWidget(description)

        # Add spacing
        card_layout.addSpacing(10)

        # Create horizontal layout for buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(30)
        self.add_buttons(button_layout)
        card_layout.addLayout(button_layout)

        # Add the card to the main layout, centered
        main_layout.addStretch()
        main_layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addStretch()

    def center_window(self):
        # Get the screen geometry
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def add_buttons(self, layout):
        # Modern button style
        button_style = """
            QPushButton {
                background-color: #1976d2;
                color: white;
                border: none;
                padding: 28px 36px;
                text-align: center;
                font-size: 22px;
                margin: 4px 2px;
                border-radius: 12px;
                min-width: 220px;
                min-height: 110px;
                font-family: 'Segoe UI';
                font-weight: bold;
                transition: background 0.2s;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
        """

        # First button - Match Job to CVs
        match_job_button = QPushButton("Match a Specific\nJob to CVs")
        match_job_button.setFont(QFont('Segoe UI', 18, QFont.Weight.Bold))
        match_job_button.setStyleSheet(button_style)
        match_job_button.setCursor(Qt.CursorShape.PointingHandCursor)
        match_job_button.clicked.connect(self.match_job_to_cvs)
        layout.addWidget(match_job_button)

        # Second button - Match CV to Jobs
        match_cv_button = QPushButton("Match a Specific\nCV to Jobs")
        match_cv_button.setFont(QFont('Segoe UI', 18, QFont.Weight.Bold))
        match_cv_button.setStyleSheet(button_style)
        match_cv_button.setCursor(Qt.CursorShape.PointingHandCursor)
        match_cv_button.clicked.connect(self.match_cv_to_jobs)
        layout.addWidget(match_cv_button)

        # Third button - Interactive Chat
        chat_button = QPushButton("Interactive\nChat Interface")
        chat_button.setFont(QFont('Segoe UI', 18, QFont.Weight.Bold))
        chat_button.setStyleSheet(button_style)
        chat_button.setCursor(Qt.CursorShape.PointingHandCursor)
        chat_button.clicked.connect(self.chat_interface)
        layout.addWidget(chat_button)

    def match_job_to_cvs(self):
        dialog = JobSelectionDialog(self)
        if dialog.exec():
            selected_job = dialog.get_selected_job()
            if selected_job:
                # Extract job ID from the selected text
                job_id = selected_job.split('ID ')[1].split(' - ')[0]
                num_cvs = dialog.cv_count.value()
                
                # Get the parent directory path
                parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                job_dir = os.path.join(parent_dir, "DataSet/job_descriptions")
                
                # Perform matching
                results, job_name = batch_match_job_to_cvs(job_id, num_cvs)
                
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
                # Extract CV ID from the selected text
                cv_id = selected_cv.split('ID ')[1].split(' - ')[0]
                num_jobs = dialog.job_count.value()
                
                # Perform matching
                results, cv_name = batch_match_cv_to_jobs(cv_id, num_jobs)
                
                # Show results
                if results:
                    results_dialog = ResultsDialog(results, cv_name, self)
                    results_dialog.exec()
                else:
                    QMessageBox.warning(self, "No Results", "No matching jobs found for the selected CV.")
    
    def chat_interface(self):
        dialog = ChatDialog(self)
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
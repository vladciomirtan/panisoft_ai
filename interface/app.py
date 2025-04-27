import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QLabel, QPushButton, QFileDialog, QHBoxLayout, QMessageBox,
                           QListWidget, QDialog)
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QFont, QScreen

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cv_job_matcher import batch_match_cv_to_jobs, display_results
from job_cv_matcher import batch_match_job_to_cvs

class JobSelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select a Job")
        self.setGeometry(100, 100, 400, 500)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Add title
        title = QLabel("Available Jobs")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont('Arial', 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Create list widget
        self.job_list = QListWidget()
        self.job_list.setFont(QFont('Arial', 12))
        layout.addWidget(self.job_list)
        
        # Add jobs to the list
        self.load_jobs()
        
        # Connect double-click signal
        self.job_list.itemDoubleClicked.connect(self.accept)
    
    def load_jobs(self):
        # Get the parent directory path
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        job_dir = os.path.join(parent_dir, "DataSet/job_descriptions")
        
        if os.path.exists(job_dir):
            job_files = [f for f in os.listdir(job_dir) if f.endswith('.docx')]
            for job_file in job_files:
                # Extract job ID and title from filename
                parts = job_file.split('_')
                if len(parts) >= 4:
                    job_id = parts[2]
                    job_title = ' '.join(parts[3:]).replace('.docx', '')
                    self.job_list.addItem(f"Job {job_id}: {job_title}")
    
    def get_selected_job(self):
        selected_item = self.job_list.currentItem()
        if selected_item:
            return selected_item.text()
        return None

class CVSelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select a CV")
        self.setGeometry(100, 100, 400, 500)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Add title
        title = QLabel("Available CVs")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont('Arial', 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Create list widget
        self.cv_list = QListWidget()
        self.cv_list.setFont(QFont('Arial', 12))
        layout.addWidget(self.cv_list)
        
        # Add CVs to the list
        self.load_cvs()
        
        # Connect double-click signal
        self.cv_list.itemDoubleClicked.connect(self.accept)
    
    def load_cvs(self):
        # Get the parent directory path
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cv_dir = os.path.join(parent_dir, "DataSet/cv")
        
        if os.path.exists(cv_dir):
            cv_files = [f for f in os.listdir(cv_dir) if f.endswith('.docx')]
            for cv_file in cv_files:
                # Extract CV ID and name from filename
                parts = cv_file.split('_')
                if len(parts) >= 3:
                    cv_id = parts[1]
                    cv_name = ' '.join(parts[2:]).replace('.docx', '')
                    self.cv_list.addItem(f"CV {cv_id}: {cv_name}")
    
    def get_selected_cv(self):
        selected_item = self.cv_list.currentItem()
        if selected_item:
            return selected_item.text()
        return None

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CV and Job Matching System")
        self.setGeometry(0, 0, 800, 600)  # Set initial size
        
        # Center the window on the screen
        self.center_window()
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Add title
        title = QLabel("CV and Job Matching System")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont('Arial', 24, QFont.Weight.Bold))
        main_layout.addWidget(title)
        
        # Add description
        description = QLabel("Select an option to begin:")
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setFont(QFont('Arial', 14))
        main_layout.addWidget(description)
        
        # Add spacing
        main_layout.addStretch()
        
        # Create horizontal layout for buttons
        button_layout = QHBoxLayout()
        self.add_buttons(button_layout)
        main_layout.addLayout(button_layout)
        
        # Add spacing
        main_layout.addStretch()
    
    def center_window(self):
        # Get the screen geometry
        screen = QApplication.primaryScreen().geometry()
        # Calculate center position
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        # Move window to center
        self.move(x, y)
    
    def add_buttons(self, layout):
        # Create button style
        button_style = """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 30px 32px;
                text-align: center;
                font-size: 24px;
                margin: 4px 2px;
                border-radius: 8px;
                min-width: 200px;
                min-height: 120px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """
        
        # Find Best CVs Button
        find_cvs_button = QPushButton("Find Best\nCVs for a Job")
        find_cvs_button.setFont(QFont('Arial', 18, QFont.Weight.Bold))
        find_cvs_button.setStyleSheet(button_style)
        find_cvs_button.clicked.connect(self.find_best_cvs)
        layout.addWidget(find_cvs_button)
        
        # Find Best Jobs Button
        find_jobs_button = QPushButton("Find Best\nJobs for a CV")
        find_jobs_button.setFont(QFont('Arial', 18, QFont.Weight.Bold))
        find_jobs_button.setStyleSheet(button_style)
        find_jobs_button.clicked.connect(self.find_best_jobs)
        layout.addWidget(find_jobs_button)
        
        # Chat Matching Button
        chat_matching_button = QPushButton("Matching\nBased on Chat")
        chat_matching_button.setFont(QFont('Arial', 18, QFont.Weight.Bold))
        chat_matching_button.setStyleSheet(button_style)
        chat_matching_button.clicked.connect(self.chat_matching)
        layout.addWidget(chat_matching_button)
    
    def find_best_cvs(self):
        # Create and show job selection dialog
        dialog = JobSelectionDialog(self)
        if dialog.exec():
            selected_job = dialog.get_selected_job()
            if selected_job:
                # Extract job ID from the selected text
                job_id = selected_job.split(':')[0].split(' ')[1]
                print(f"Selected Job: {selected_job}")
                # TODO: Implement CV matching logic here
    
    def find_best_jobs(self):
        # Create and show CV selection dialog
        dialog = CVSelectionDialog(self)
        if dialog.exec():
            selected_cv = dialog.get_selected_cv()
            if selected_cv:
                # Extract CV ID from the selected text
                cv_id = selected_cv.split(':')[0].split(' ')[1]
                print(f"Selected CV: {selected_cv}")
                # TODO: Implement job matching logic here
    
    def chat_matching(self):
        # TODO: Implement chat-based matching logic
        print("Starting chat-based matching...")

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 
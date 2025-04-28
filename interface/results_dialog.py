from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QListWidget, QPushButton, 
                           QFrame, QScrollArea, QWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QPalette, QLinearGradient, QBrush
from PyQt6.QtCore import QPoint

class ResultItem(QFrame):
    def __init__(self, match, index, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
                padding: 16px;
                margin: 8px;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Add a subtle shadow effect
        self.setGraphicsEffect(None)  # We'll add shadow in the parent widget
        
        # Title with index
        title = QLabel(f"{index}. {match.get('job_title', match.get('cv_name', 'Unknown'))}")
        title.setFont(QFont('Segoe UI', 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #1976d2;")
        layout.addWidget(title)
        
        # Score bar
        score = match['total_score'] * 100
        score_label = QLabel(f"Match Score: {score:.1f}%")
        score_label.setFont(QFont('Segoe UI', 12))
        score_label.setStyleSheet("color: #424242;")
        layout.addWidget(score_label)
        
        # Detailed scores
        details = QLabel(
            f"Industry Knowledge: {match['industry_knowledge_score']:.2f}\n"
            f"Technical Skills: {match['technical_skills_score']:.2f}\n"
            f"Job Description Match: {match['job_description_match_score']:.2f}"
        )
        details.setFont(QFont('Segoe UI', 11))
        details.setStyleSheet("color: #616161;")
        layout.addWidget(details)

        # Add reasoning
        reasoning = QLabel("Reasoning:")
        reasoning.setFont(QFont('Segoe UI', 11, QFont.Weight.Bold))
        reasoning.setStyleSheet("color: #424242; margin-top: 8px;")
        layout.addWidget(reasoning)

        reasoning_text = QLabel(match.get('reasoning', 'No reasoning provided'))
        reasoning_text.setFont(QFont('Segoe UI', 11))
        reasoning_text.setStyleSheet("color: #616161;")
        reasoning_text.setWordWrap(True)
        reasoning_text.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        layout.addWidget(reasoning_text)

class ResultsDialog(QDialog):
    def __init__(self, results, name, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Matching Results")
        self.setGeometry(100, 100, 900, 700)
        self.setStyleSheet("""
            QDialog {
                background: #f5f5f5;
            }
            QPushButton {
                background-color: #1976d2;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
        """)
        
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Add title
        title = QLabel(f"Top 5 Matches: {name}")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont('Segoe UI', 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #1976d2;")
        main_layout.addWidget(title)
        
        # Create scroll area for results
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Create container for results
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(10)
        container_layout.setContentsMargins(10, 10, 10, 10)
        
        # Add results to the container
        for i, match in enumerate(results, 1):
            result_item = ResultItem(match, i)
            container_layout.addWidget(result_item)
        
        # Add stretch to push items to the top
        container_layout.addStretch()
        
        # Set the container as the scroll area's widget
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
        
        # Add close button
        close_button = QPushButton("Close")
        close_button.setFixedSize(80, 28)
        close_button.setMinimumSize(80, 28)
        close_button.setMaximumSize(80, 28)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 13px;
                font-weight: bold;
                min-width: 80px;
                min-height: 28px;
                max-width: 80px;
                max-height: 28px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
        """)
        close_button.clicked.connect(self.accept)
        main_layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Center the dialog on the screen
        self.center_on_screen()
    
    def center_on_screen(self):
        screen = self.screen().geometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        ) 
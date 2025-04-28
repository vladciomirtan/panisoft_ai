import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSpinBox, QFrame, QGraphicsDropShadowEffect, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class ExcelReportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Generate Excel Report")
        self.setFixedSize(500, 500)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(0)

        # Card container
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 16px;
                border: 1px solid #e0e0e0;
            }
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(Qt.GlobalColor.gray)
        card.setGraphicsEffect(shadow)
        
        # Card layout
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(32, 32, 32, 32)
        card_layout.setSpacing(32)

        # Title
        title = QLabel("Generate Excel Report")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont('Segoe UI', 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #1976d2; margin-bottom: 20px;")
        card_layout.addWidget(title)

        # Input fields container
        input_container = QWidget()
        input_layout = QVBoxLayout(input_container)
        input_layout.setSpacing(20)
        input_layout.setContentsMargins(0, 0, 0, 0)

        # CV count
        cv_widget = QWidget()
        cv_layout = QHBoxLayout(cv_widget)
        cv_layout.setContentsMargins(0, 0, 0, 0)
        cv_label = QLabel("Number of CVs:")
        cv_label.setFont(QFont('Segoe UI', 14))
        cv_label.setStyleSheet("min-width: 120px; color: #424242; min-height: 40px;")
        self.cv_count = QSpinBox()
        self.cv_count.setRange(1, 100)
        self.cv_count.setValue(20)
        self.cv_count.setStyleSheet("""
            QSpinBox {
                border: 1px solid #bdbdbd;
                border-radius: 6px;
                padding: 12px 16px;
                font-size: 14px;
                background: #f3f6fa;
                min-width: 80px;
                min-height: 40px;
            }
            QSpinBox:focus {
                border: 1.5px solid #1976d2;
                background: #fff;
            }
        """)
        cv_layout.addWidget(cv_label)
        cv_layout.addWidget(self.cv_count)
        input_layout.addWidget(cv_widget)

        # Job count
        job_widget = QWidget()
        job_layout = QHBoxLayout(job_widget)
        job_layout.setContentsMargins(0, 0, 0, 0)
        job_label = QLabel("Number of Jobs:")
        job_label.setFont(QFont('Segoe UI', 14))
        job_label.setStyleSheet("min-width: 120px; color: #424242; min-height: 40px;")
        self.job_count = QSpinBox()
        self.job_count.setRange(1, 100)
        self.job_count.setValue(20)
        self.job_count.setStyleSheet("""
            QSpinBox {
                border: 1px solid #bdbdbd;
                border-radius: 6px;
                padding: 12px 16px;
                font-size: 14px;
                background: #f3f6fa;
                min-width: 80px;
                min-height: 40px;
            }
            QSpinBox:focus {
                border: 1.5px solid #1976d2;
                background: #fff;
            }
        """)
        job_layout.addWidget(job_label)
        job_layout.addWidget(self.job_count)
        input_layout.addWidget(job_widget)

        card_layout.addWidget(input_container)

        # Generate button
        button_container = QWidget()
        button_layout = QVBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        generate_button = QPushButton("Generate Report")
        generate_button.setFont(QFont('Segoe UI', 14, QFont.Weight.Bold))
        generate_button.setCursor(Qt.CursorShape.PointingHandCursor)
        generate_button.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                min-width: 160px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
        """)
        generate_button.clicked.connect(self.accept)
        button_layout.addWidget(generate_button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        card_layout.addWidget(button_container)

        # Add card to main layout
        main_layout.addWidget(card)

    def get_counts(self):
        """Get the selected CV and job counts."""
        return self.cv_count.value(), self.job_count.value()

    def get_file_path(self):
        """Get the path where the Excel report will be saved."""
        return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                          "panisoft_ai", "output", "cv_job_matching_results.xlsx")
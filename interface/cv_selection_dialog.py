import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpinBox, QPushButton,
    QListWidget, QFrame, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from cv_job_matcher import get_cv_files

class CVSelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select a CV")
        self.setFixedSize(500, 650)
        self.setStyleSheet("""
            QDialog {
                background: #f6f8fa;
            }
        """)

        # Card-like frame
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 16px;
                border: 1px solid #e0e0e0;
                padding: 24px;
            }
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(Qt.GlobalColor.gray)
        card.setGraphicsEffect(shadow)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(18)

        # Title
        title = QLabel("Available CVs")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont('Segoe UI', 20, QFont.Weight.Bold))
        card_layout.addWidget(title)

        # Search section
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search by ID or name...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #bdbdbd;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 15px;
                background: #f3f6fa;
            }
            QLineEdit:focus {
                border: 1.5px solid #1976d2;
                background: #fff;
            }
        """)
        self.search_input.textChanged.connect(self.filter_cvs)
        search_layout.addWidget(self.search_input)
        card_layout.addLayout(search_layout)

        # List widget
        self.cv_list = QListWidget()
        self.cv_list.setFont(QFont('Segoe UI', 13))
        self.cv_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                background: #fafbfc;
                padding: 6px;
            }
            QListWidget::item {
                padding: 12px 8px;
                margin-bottom: 4px;
            }
            QListWidget::item:selected {
                background: #e3f2fd;
                color: #1976d2;
                border-radius: 6px;
            }
        """)
        card_layout.addWidget(self.cv_list, stretch=1)

        # Number of jobs to process
        job_count_layout = QHBoxLayout()
        job_count_label = QLabel("Number of jobs to process:")
        job_count_label.setFont(QFont('Segoe UI', 11))
        self.job_count = QSpinBox()
        self.job_count.setRange(1, 100)
        self.job_count.setValue(20)
        self.job_count.setStyleSheet("""
            QSpinBox {
                border: 1px solid #bdbdbd;
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 13px;
                background: #f3f6fa;
                min-width: 60px;
            }
        """)
        job_count_layout.addWidget(job_count_label)
        job_count_layout.addWidget(self.job_count)
        card_layout.addLayout(job_count_layout)

        # Select button
        select_button = QPushButton("Select CV")
        select_button.setFont(QFont('Segoe UI', 14, QFont.Weight.Bold))
        select_button.setCursor(Qt.CursorShape.PointingHandCursor)
        select_button.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 0;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
        """)
        select_button.clicked.connect(self.accept)
        card_layout.addWidget(select_button)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.addStretch()
        main_layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addStretch()

        # Add CVs to the list
        self.load_cvs()
        self.cv_list.itemDoubleClicked.connect(self.accept)

    def load_cvs(self):
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cv_files, cv_display_names = get_cv_files(base_dir=parent_dir)
        self.cv_list.clear()
        for cv_file, display_name in cv_display_names.items():
            self.cv_list.addItem(display_name)

    def filter_cvs(self):
        search_text = self.search_input.text().lower()
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cv_files, cv_display_names = get_cv_files(base_dir=parent_dir)
        self.cv_list.clear()
        for cv_file, display_name in cv_display_names.items():
            if search_text in display_name.lower():
                self.cv_list.addItem(display_name)

    def get_selected_cv(self):
        selected_item = self.cv_list.currentItem()
        if selected_item:
            return selected_item.text()
        return None
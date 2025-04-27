import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpinBox, QPushButton,
    QListWidget, QFrame, QGraphicsDropShadowEffect, QRadioButton, QButtonGroup, QListWidgetItem
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from file_uploader import FileUploader, LocalFileUploader, DatasetFileUploader

class JobSelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select a Job")
        self.setFixedSize(500, 750)  # Increased height from 650 to 750
        self.setStyleSheet("""
            QDialog {
                background: #f6f8fa;
            }
            QRadioButton {
                font-size: 13px;
                padding: 8px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
            }
            QRadioButton::indicator:unchecked {
                border: 2px solid #bdbdbd;
                border-radius: 9px;
                background: white;
            }
            QRadioButton::indicator:checked {
                border: 2px solid #1976d2;
                border-radius: 9px;
                background: #1976d2;
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
        title = QLabel("Available Jobs")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont('Segoe UI', 20, QFont.Weight.Bold))
        card_layout.addWidget(title)

        # Upload source selection
        upload_layout = QVBoxLayout()
        upload_label = QLabel("Upload from:")
        upload_label.setFont(QFont('Segoe UI', 11))
        upload_layout.addWidget(upload_label)
        
        # Create radio buttons
        self.upload_buttons = QButtonGroup()
        self.dataset_radio = QRadioButton("DataSet Folder")
        self.local_radio = QRadioButton("Local Computer")
        self.upload_buttons.addButton(self.dataset_radio)
        self.upload_buttons.addButton(self.local_radio)
        
        # Set default selection
        self.dataset_radio.setChecked(True)
        
        # Connect signals
        self.dataset_radio.toggled.connect(self.on_upload_source_changed)
        self.local_radio.toggled.connect(self.on_upload_source_changed)
        
        # Add radio buttons to layout
        radio_layout = QHBoxLayout()
        radio_layout.addWidget(self.dataset_radio)
        radio_layout.addWidget(self.local_radio)
        upload_layout.addLayout(radio_layout)
        
        card_layout.addLayout(upload_layout)

        # Search section
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search by ID or title...")
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
        self.search_input.textChanged.connect(self.filter_jobs)
        search_layout.addWidget(self.search_input)
        card_layout.addLayout(search_layout)

        # List widget
        self.job_list = QListWidget()
        self.job_list.setFont(QFont('Segoe UI', 13))
        self.job_list.setStyleSheet("""
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
        card_layout.addWidget(self.job_list, stretch=1)

        # Number of CVs to process
        cv_count_layout = QHBoxLayout()
        cv_count_label = QLabel("Number of CVs to process:")
        cv_count_label.setFont(QFont('Segoe UI', 11))
        self.cv_count = QSpinBox()
        self.cv_count.setRange(1, 100)
        self.cv_count.setValue(20)
        self.cv_count.setStyleSheet("""
            QSpinBox {
                border: 1px solid #bdbdbd;
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 13px;
                background: #f3f6fa;
                min-width: 60px;
            }
        """)
        cv_count_layout.addWidget(cv_count_label)
        cv_count_layout.addWidget(self.cv_count)
        card_layout.addLayout(cv_count_layout)

        # Select button
        select_button = QPushButton("Select Job")
        select_button.setFont(QFont('Segoe UI', 11, QFont.Weight.Bold))
        select_button.setCursor(Qt.CursorShape.PointingHandCursor)
        select_button.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                min-width: 100px;
                min-height: 32px;
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

        # Initialize uploaders
        self.dataset_uploader = DatasetFileUploader("job_descriptions")
        self.local_uploader = LocalFileUploader()
        
        # Add jobs to the list
        self.load_jobs()
        self.job_list.itemDoubleClicked.connect(self.accept)

    def on_upload_source_changed(self, checked):
        """Handle upload source change."""
        if checked:
            self.load_jobs()

    def load_jobs(self):
        """Load jobs using the selected uploader."""
        uploader = self.dataset_uploader if self.dataset_radio.isChecked() else self.local_uploader
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        job_files, job_display_names = uploader.get_files(base_dir=parent_dir)
        self.job_list.clear()
        
        # Store file paths for later use
        self.file_paths = {}
        
        for job_file, display_name in job_display_names.items():
            item = QListWidgetItem(display_name)
            # Store the full path as data
            if isinstance(uploader, LocalFileUploader):
                # For local files, use the full path directly
                item.setData(Qt.ItemDataRole.UserRole, job_file)
            else:
                # For dataset files, construct the path
                item.setData(Qt.ItemDataRole.UserRole, os.path.join(parent_dir, "DataSet", "job_descriptions", job_file))
            self.job_list.addItem(item)
            self.file_paths[display_name] = item.data(Qt.ItemDataRole.UserRole)

    def filter_jobs(self):
        """Filter jobs based on search text."""
        search_text = self.search_input.text().lower()
        uploader = self.dataset_uploader if self.dataset_radio.isChecked() else self.local_uploader
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        job_files, job_display_names = uploader.get_files(base_dir=parent_dir)
        self.job_list.clear()
        
        # Store file paths for later use
        self.file_paths = {}
        
        for job_file, display_name in job_display_names.items():
            if search_text in display_name.lower():
                item = QListWidgetItem(display_name)
                # Store the full path as data
                if isinstance(uploader, LocalFileUploader):
                    # For local files, use the full path directly
                    item.setData(Qt.ItemDataRole.UserRole, job_file)
                else:
                    # For dataset files, construct the path
                    item.setData(Qt.ItemDataRole.UserRole, os.path.join(parent_dir, "DataSet", "job_descriptions", job_file))
                self.job_list.addItem(item)
                self.file_paths[display_name] = item.data(Qt.ItemDataRole.UserRole)

    def get_selected_job(self):
        """Get the selected job."""
        selected_item = self.job_list.currentItem()
        if selected_item:
            # Return both the display name and the file path
            return {
                'display_name': selected_item.text(),
                'file_path': selected_item.data(Qt.ItemDataRole.UserRole)
            }
        return None

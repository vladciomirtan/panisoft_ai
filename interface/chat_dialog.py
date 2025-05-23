from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                           QFrame, QScrollArea, QWidget, QTextEdit, QComboBox, QLineEdit,
                           QMessageBox, QProgressBar, QButtonGroup, QRadioButton)
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QPoint, QTimer, QRect
from PyQt6.QtGui import QFont, QIcon, QTextCursor, QColor, QPalette, QLinearGradient, QBrush, QPainter, QPen
import os
import sys

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from document_processor import extract_text
from matcher import CVJobMatcher
from config import GEMINI_API_KEY
from file_uploader import FileUploader, LocalFileUploader, DatasetFileUploader

class AnimatedButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                transition: background-color 0.3s;
            }
            QPushButton:hover {
                background-color: #1565c0;
                transform: scale(1.05);
            }
            QPushButton:pressed {
                background-color: #0d47a1;
                transform: scale(0.95);
            }
        """)
        
        # Add hover animation
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)

class ChatMessage(QFrame):
    def __init__(self, message, is_user=False, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background: {'#e3f2fd' if is_user else 'white'};
                border-radius: 12px;
                border: 1px solid #e0e0e0;
                padding: 16px;
                margin: 8px;
                opacity: 0;
            }}
        """)
        
        layout = QVBoxLayout(self)
        
        # Message text
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setFont(QFont('Segoe UI', 11))
        message_label.setStyleSheet("color: #424242;")
        layout.addWidget(message_label)
        
        # Add fade-in animation
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.start()

class ScoreBar(QFrame):
    def __init__(self, score, label, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
                padding: 12px;
                margin: 4px;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Label and score
        score_layout = QHBoxLayout()
        label_widget = QLabel(label)
        label_widget.setFont(QFont('Segoe UI', 12, QFont.Weight.Bold))
        label_widget.setStyleSheet("color: #424242;")
        score_layout.addWidget(label_widget)
        
        score_text = QLabel(f"{score:.1f}%")
        score_text.setFont(QFont('Segoe UI', 12, QFont.Weight.Bold))
        score_text.setStyleSheet("color: #1976d2;")
        score_layout.addWidget(score_text)
        score_layout.addStretch()
        
        layout.addLayout(score_layout)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(int(score))
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: none;
                background: #e0e0e0;
                border-radius: 4px;
                height: 12px;
            }
            QProgressBar::chunk {
                background: #1976d2;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.progress)
        
        # Add animation
        self.animation = QPropertyAnimation(self.progress, b"value")
        self.animation.setDuration(1000)
        self.animation.setStartValue(0)
        self.animation.setEndValue(int(score))
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.start()

class LoadingSpinner(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(50, 50)
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(50)  # Update every 50ms
        self.setStyleSheet("background: transparent;")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw spinning circle
        painter.setPen(QPen(QColor("#1976d2"), 3))
        painter.drawArc(5, 5, 40, 40, self.angle * 16, 270 * 16)
        
        self.angle = (self.angle + 10) % 360

class LoadingWidget(QFrame):
    def __init__(self, message="Processing...", parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.9);
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(15)
        
        # Add spinner
        self.spinner = LoadingSpinner()
        layout.addWidget(self.spinner, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Add message
        self.message_label = QLabel(message)
        self.message_label.setFont(QFont('Segoe UI', 11))
        self.message_label.setStyleSheet("color: #424242;")
        layout.addWidget(self.message_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Set fixed size
        self.setFixedSize(200, 120)
        
        # Add fade-in animation
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.start()

class ChatDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("CV-Job Analyser")
        self.setWindowState(Qt.WindowState.WindowMaximized)  # Force maximized state
        self.setStyleSheet("""
            QDialog {
                background: #f5f5f5;
            }
            QComboBox {
                padding: 6px;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                background: white;
                min-height: 32px;
            }
            QComboBox:hover {
                border-color: #1976d2;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);
                width: 12px;
                height: 12px;
            }
        """)
        
        # Initialize matcher
        self.matcher = CVJobMatcher()
        
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)
        
        # Add title with gradient
        title_frame = QFrame()
        title_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1976d2, stop:1 #2196f3);
                border-radius: 8px;
                padding: 8px;
            }
        """)
        title_layout = QVBoxLayout(title_frame)
        
        title = QLabel("CV-Job Analyser")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont('Segoe UI', 18, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        title_layout.addWidget(title)
        
        subtitle = QLabel("Check if your CV is a good fit for your dream job")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setFont(QFont('Segoe UI', 12))
        subtitle.setStyleSheet("color: rgba(255, 255, 255, 0.9);")
        title_layout.addWidget(subtitle)
        
        main_layout.addWidget(title_frame)
        
        # Create chat area
        self.chat_area = QScrollArea()
        self.chat_area.setWidgetResizable(True)
        self.chat_area.setStyleSheet("""
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
            QScrollBar::handle:vertical:hover {
                background: #1976d2;
            }
        """)
        
        # Create container for chat messages
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setSpacing(10)
        self.chat_layout.setContentsMargins(10, 10, 10, 10)
        
        # Set the container as the scroll area's widget
        self.chat_area.setWidget(self.chat_container)
        main_layout.addWidget(self.chat_area, stretch=3)  # Increased stretch factor for chat area
        
        # Create input area
        input_frame = QFrame()
        input_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
                padding: 8px;
            }
        """)
        input_layout = QVBoxLayout(input_frame)
        input_layout.setSpacing(6)
        
        # CV selection
        cv_layout = QHBoxLayout()
        cv_layout.setSpacing(6)
        cv_label = QLabel("Select CV:")
        cv_label.setFont(QFont('Segoe UI', 11))
        cv_label.setStyleSheet("color: #424242;")
        cv_layout.addWidget(cv_label)
        
        self.cv_combo = QComboBox()
        self.cv_combo.setMinimumWidth(200)
        cv_layout.addWidget(self.cv_combo)
        
        # Create CV radio buttons
        cv_radio_layout = QVBoxLayout()
        cv_radio_layout.setSpacing(4)
        cv_radio_label = QLabel("Upload from:")
        cv_radio_label.setFont(QFont('Segoe UI', 11))
        cv_radio_label.setStyleSheet("color: #424242;")
        cv_radio_layout.addWidget(cv_radio_label)
        
        self.cv_upload_buttons = QButtonGroup()
        self.cv_dataset_radio = QRadioButton("DataSet Folder")
        self.cv_local_radio = QRadioButton("Local Computer")
        self.cv_upload_buttons.addButton(self.cv_dataset_radio)
        self.cv_upload_buttons.addButton(self.cv_local_radio)
        
        # Set default selection
        self.cv_dataset_radio.setChecked(True)
        
        # Connect signals
        self.cv_dataset_radio.toggled.connect(self.on_cv_upload_source_changed)
        self.cv_local_radio.toggled.connect(self.on_cv_upload_source_changed)
        
        # Add radio buttons to layout
        cv_radio_buttons_layout = QHBoxLayout()
        cv_radio_buttons_layout.setSpacing(6)
        cv_radio_buttons_layout.addWidget(self.cv_dataset_radio)
        cv_radio_buttons_layout.addWidget(self.cv_local_radio)
        cv_radio_layout.addLayout(cv_radio_buttons_layout)
        
        cv_layout.addLayout(cv_radio_layout)
        
        input_layout.addLayout(cv_layout)
        
        # Job selection
        job_layout = QHBoxLayout()
        job_layout.setSpacing(6)
        job_label = QLabel("Select Job:")
        job_label.setFont(QFont('Segoe UI', 11))
        job_label.setStyleSheet("color: #424242;")
        job_layout.addWidget(job_label)
        
        self.job_combo = QComboBox()
        self.job_combo.setMinimumWidth(200)
        job_layout.addWidget(self.job_combo)
        
        # Create job radio buttons
        job_radio_layout = QVBoxLayout()
        job_radio_layout.setSpacing(4)
        job_radio_label = QLabel("Upload from:")
        job_radio_label.setFont(QFont('Segoe UI', 11))
        job_radio_label.setStyleSheet("color: #424242;")
        job_radio_layout.addWidget(job_radio_label)
        
        self.job_upload_buttons = QButtonGroup()
        self.job_dataset_radio = QRadioButton("DataSet Folder")
        self.job_local_radio = QRadioButton("Local Computer")
        self.job_upload_buttons.addButton(self.job_dataset_radio)
        self.job_upload_buttons.addButton(self.job_local_radio)
        
        # Set default selection
        self.job_dataset_radio.setChecked(True)
        
        # Connect signals
        self.job_dataset_radio.toggled.connect(self.on_job_upload_source_changed)
        self.job_local_radio.toggled.connect(self.on_job_upload_source_changed)
        
        # Add radio buttons to layout
        job_radio_buttons_layout = QHBoxLayout()
        job_radio_buttons_layout.setSpacing(6)
        job_radio_buttons_layout.addWidget(self.job_dataset_radio)
        job_radio_buttons_layout.addWidget(self.job_local_radio)
        job_radio_layout.addLayout(job_radio_buttons_layout)
        
        job_layout.addLayout(job_radio_layout)
        
        input_layout.addLayout(job_layout)
        
        # Initialize uploaders
        self.cv_dataset_uploader = DatasetFileUploader("cv")
        self.cv_local_uploader = LocalFileUploader()
        self.job_dataset_uploader = DatasetFileUploader("job_descriptions")
        self.job_local_uploader = LocalFileUploader()
        
        # Add style for radio buttons
        self.setStyleSheet("""
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
        
        # Populate initial lists
        self.populate_cv_combo()
        self.populate_job_combo()
        
        # Match button
        match_button = QPushButton("Match")
        match_button.setFont(QFont('Segoe UI', 11, QFont.Weight.Bold))
        match_button.setCursor(Qt.CursorShape.PointingHandCursor)
        match_button.setStyleSheet("""
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
        match_button.clicked.connect(self.perform_match)
        input_layout.addWidget(match_button)
        
        main_layout.addWidget(input_frame)
        
        # Add close button
        close_button = QPushButton("Close")
        close_button.setFont(QFont('Segoe UI', 11, QFont.Weight.Bold))
        close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                min-width: 100px;
                min-height: 32px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        close_button.clicked.connect(self.reject)
        main_layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Center the dialog on the screen
        self.center_on_screen()
        
        # Add welcome message
        self.add_message("Welcome to the CV-Job analyser interface! Select a CV and a job description to begin analysis.", False)
        
        # Add loading widget
        self.loading_widget = None
    
    def center_on_screen(self):
        screen = self.screen().geometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )
    
    def on_cv_upload_source_changed(self, checked):
        """Handle CV upload source change."""
        if checked:
            self.populate_cv_combo()

    def on_job_upload_source_changed(self, checked):
        """Handle job upload source change."""
        if checked:
            self.populate_job_combo()

    def populate_cv_combo(self):
        """Populate the CV combo box with available CVs."""
        uploader = self.cv_dataset_uploader if self.cv_dataset_radio.isChecked() else self.cv_local_uploader
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cv_files, cv_display_names = uploader.get_files(base_dir=base_dir)
        
        self.cv_combo.clear()
        for file, display_name in cv_display_names.items():
            self.cv_combo.addItem(display_name, file)
    
    def populate_job_combo(self):
        """Populate the job combo box with available job descriptions."""
        uploader = self.job_dataset_uploader if self.job_dataset_radio.isChecked() else self.job_local_uploader
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        job_files, job_display_names = uploader.get_files(base_dir=base_dir)
        
        self.job_combo.clear()
        for file, display_name in job_display_names.items():
            self.job_combo.addItem(display_name, file)
    
    def add_message(self, message, is_user=False):
        """Add a message to the chat area."""
        message_widget = ChatMessage(message, is_user)
        self.chat_layout.addWidget(message_widget)
        
        # Scroll to bottom with animation
        QTimer.singleShot(100, lambda: self.chat_area.verticalScrollBar().setValue(
            self.chat_area.verticalScrollBar().maximum()
        ))
    
    def add_score_bars(self, result):
        """Add animated score bars for the match results."""
        scores_frame = QFrame()
        scores_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
                padding: 16px;
                margin: 8px;
            }
        """)
        
        scores_layout = QVBoxLayout(scores_frame)
        
        # Add score bars
        scores_layout.addWidget(ScoreBar(
            result.industry_knowledge_score * 100,
            "Industry Knowledge"
        ))
        scores_layout.addWidget(ScoreBar(
            result.technical_skills_score * 100,
            "Technical Skills"
        ))
        scores_layout.addWidget(ScoreBar(
            result.job_description_match_score * 100,
            "Job Description Match"
        ))
        scores_layout.addWidget(ScoreBar(
            result.total_score * 100,
            "Total Score"
        ))
        
        self.chat_layout.addWidget(scores_frame)
    
    def show_loading(self, message="Processing match..."):
        """Show the loading animation."""
        self.loading_widget = LoadingWidget(message, self)
        self.loading_widget.move(
            (self.width() - self.loading_widget.width()) // 2,
            (self.height() - self.loading_widget.height()) // 2
        )
        self.loading_widget.show()

    def hide_loading(self):
        """Hide the loading animation."""
        if self.loading_widget:
            self.loading_widget.hide()
            self.loading_widget = None

    def clear_chat_area(self):
        """Clear all messages from the chat area except the welcome message."""
        # Remove all widgets except the first one (welcome message)
        while self.chat_layout.count() > 1:
            item = self.chat_layout.takeAt(1)
            if item.widget():
                item.widget().deleteLater()

    def perform_match(self):
        """Perform the CV-job matching and display results."""
        cv_file = self.cv_combo.currentData()
        job_file = self.job_combo.currentData()
        
        if not cv_file or not job_file:
            QMessageBox.warning(self, "Error", "Please select both a CV and a job description.")
            return
        
        # Get full paths
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cv_path = os.path.join(base_dir, "DataSet", "cv", cv_file)
        job_path = os.path.join(base_dir, "DataSet", "job_descriptions", job_file)
        
        try:
            # Clear previous results
            self.clear_chat_area()
            
            # Show loading animation
            self.show_loading("Extracting text from files...")
            
            # Extract text from files
            cv_content = extract_text(cv_path)
            job_content = extract_text(job_path)
            
            # Update loading message
            if self.loading_widget:
                self.loading_widget.message_label.setText("Analyzing match...")
            
            # Perform matching
            result = self.matcher.match(cv_content, job_content)
            
            # Hide loading animation
            self.hide_loading()
            
            # Format results
            cv_name = self.cv_combo.currentText()
            job_name = self.job_combo.currentText()
            
            # Add match header
            header_frame = QFrame()
            header_frame.setStyleSheet("""
                QFrame {
                    background: #e3f2fd;
                    border-radius: 8px;
                    border: 1px solid #1976d2;
                    padding: 12px;
                    margin: 8px;
                }
            """)
            header_layout = QVBoxLayout(header_frame)
            
            header_label = QLabel(f"Match Analysis: {cv_name} → {job_name}")
            header_label.setFont(QFont('Segoe UI', 14, QFont.Weight.Bold))
            header_label.setStyleSheet("color: #1976d2;")
            header_layout.addWidget(header_label)
            
            self.chat_layout.addWidget(header_frame)
            
            # Add score bars
            self.add_score_bars(result)
            
            # Add reasoning
            reasoning_frame = QFrame()
            reasoning_frame.setStyleSheet("""
                QFrame {
                    background: white;
                    border-radius: 8px;
                    border: 1px solid #e0e0e0;
                    padding: 12px;
                    margin: 8px;
                }
            """)
            reasoning_layout = QVBoxLayout(reasoning_frame)
            
            reasoning_label = QLabel("Reasoning")
            reasoning_label.setFont(QFont('Segoe UI', 12, QFont.Weight.Bold))
            reasoning_label.setStyleSheet("color: #424242;")
            reasoning_layout.addWidget(reasoning_label)
            
            reasoning_text = QLabel(result.reasoning)
            reasoning_text.setWordWrap(True)
            reasoning_text.setFont(QFont('Segoe UI', 11))
            reasoning_text.setStyleSheet("color: #616161;")
            reasoning_layout.addWidget(reasoning_text)
            
            self.chat_layout.addWidget(reasoning_frame)
            
            # Add rating
            rating = "Excellent Match ⭐⭐⭐⭐⭐" if result.total_score >= 0.8 else \
                    "Strong Match ⭐⭐⭐⭐" if result.total_score >= 0.6 else \
                    "Good Match ⭐⭐⭐" if result.total_score >= 0.4 else \
                    "Fair Match ⭐⭐" if result.total_score >= 0.2 else \
                    "Poor Match ⭐"
            
            rating_frame = QFrame()
            rating_frame.setStyleSheet("""
                QFrame {
                    background: #e3f2fd;
                    border-radius: 8px;
                    border: 1px solid #1976d2;
                    padding: 12px;
                    margin: 8px;
                }
            """)
            rating_layout = QVBoxLayout(rating_frame)
            
            rating_label = QLabel("Match Rating")
            rating_label.setFont(QFont('Segoe UI', 12, QFont.Weight.Bold))
            rating_label.setStyleSheet("color: #1976d2;")
            rating_layout.addWidget(rating_label)
            
            rating_text = QLabel(rating)
            rating_text.setFont(QFont('Segoe UI', 14))
            rating_text.setStyleSheet("color: #1976d2;")
            rating_layout.addWidget(rating_text)
            
            self.chat_layout.addWidget(rating_frame)
            
        except Exception as e:
            self.hide_loading()
            self.add_message(f"Error: {str(e)}", False) 
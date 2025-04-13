import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QComboBox, 
                            QProgressBar, QFileDialog, QFrame, QSpacerItem,
                            QSizePolicy)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap

from constants import (APP_NAME, SUPPORTED_AUDIO_FORMATS, SUPPORTED_VIDEO_FORMATS, 
                     AUDIO_QUALITIES, VIDEO_QUALITIES)
from styles import MAIN_STYLE
from utils import get_download_directory, validate_youtube_url
from downloader import Downloader

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(700, 500)
        self.setStyleSheet(MAIN_STYLE)
        
        # Initialize components
        self.downloader = Downloader()
        self.download_directory = os.path.expanduser("~/Downloads")
        
        # Set up UI
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Header with title
        header_layout = QHBoxLayout()
        title_label = QLabel(APP_NAME)
        title_label.setObjectName("titleLabel")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)
        
        # URL input section
        url_layout = QHBoxLayout()
        url_layout.setSpacing(10)
        
        url_label = QLabel("YouTube URL:")
        self.url_input = QLineEdit()
        self.url_input.setObjectName("urlInput")
        self.url_input.setPlaceholderText("Enter YouTube video URL here...")
        
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input, 1)
        main_layout.addLayout(url_layout)
        
        # Format selection section
        format_layout = QHBoxLayout()
        format_layout.setSpacing(10)
        
        format_label = QLabel("Format:")
        self.format_combo = QComboBox()
        self.format_combo.addItems(["MP3 Audio", "MP4 Video"])
        
        quality_label = QLabel("Quality:")
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(AUDIO_QUALITIES)  # Default to audio
        
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_combo)
        format_layout.addWidget(quality_label)
        format_layout.addWidget(self.quality_combo)
        format_layout.addStretch()
        main_layout.addLayout(format_layout)
        
        # Directory selection section
        dir_layout = QHBoxLayout()
        dir_layout.setSpacing(10)
        
        dir_label = QLabel("Save to:")
        self.dir_input = QLineEdit(self.download_directory)
        self.dir_input.setReadOnly(True)
        self.browse_btn = QPushButton("Browse")
        
        dir_layout.addWidget(dir_label)
        dir_layout.addWidget(self.dir_input, 1)
        dir_layout.addWidget(self.browse_btn)
        main_layout.addLayout(dir_layout)
        
        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #3E3E3E;")
        main_layout.addWidget(separator)
        
        # Download button section
        download_layout = QHBoxLayout()
        download_layout.setSpacing(15)
        
        self.download_btn = QPushButton("Download")
        self.download_btn.setObjectName("downloadBtn")
        self.download_btn.setIcon(QIcon("resources/icons/download.png"))
        self.download_btn.setIconSize(QSize(20, 20))
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setEnabled(False)
        
        download_layout.addWidget(self.download_btn)
        download_layout.addWidget(self.cancel_btn)
        main_layout.addLayout(download_layout)
        
        # Progress section
        progress_layout = QVBoxLayout()
        progress_layout.setSpacing(5)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        
        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("statusLabel")
        
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.status_label)
        main_layout.addLayout(progress_layout)
        
        # Add spacer at the bottom
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Set central widget
        self.setCentralWidget(main_widget)
        
    def _connect_signals(self):
        # Connect UI signals
        self.format_combo.currentIndexChanged.connect(self._update_quality_options)
        self.browse_btn.clicked.connect(self._browse_directory)
        self.download_btn.clicked.connect(self._start_download)
        self.cancel_btn.clicked.connect(self._cancel_download)
        
        # Connect downloader signals
        self.downloader.progress_signal.connect(self.progress_bar.setValue)
        self.downloader.status_signal.connect(self.status_label.setText)
        self.downloader.finished_signal.connect(self._download_finished)
        
    def _update_quality_options(self, index):
        self.quality_combo.clear()
        if index == 0:  # Audio
            self.quality_combo.addItems(AUDIO_QUALITIES)
        else:  # Video
            self.quality_combo.addItems(VIDEO_QUALITIES)
            
    def _browse_directory(self):
        dir_path = get_download_directory(self)
        if dir_path:
            self.download_directory = dir_path
            self.dir_input.setText(dir_path)
            
    def _start_download(self):
        url = self.url_input.text().strip()
        if not url:
            self.status_label.setText("Please enter a YouTube URL")
            return
            
        if not validate_youtube_url(url):
            self.status_label.setText("Invalid YouTube URL")
            return
            
        format_index = self.format_combo.currentIndex()
        format_type = SUPPORTED_AUDIO_FORMATS[0] if format_index == 0 else SUPPORTED_VIDEO_FORMATS[0]
        quality = self.quality_combo.currentText()
        
        # Update UI
        self.download_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        
        # Start download
        self.downloader.download(url, format_type, quality, self.download_directory)
        
    def _cancel_download(self):
        self.downloader.cancel()
        self.cancel_btn.setEnabled(False)
        
    def _download_finished(self, success, filepath):
        self.download_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        
        if success:
            self.progress_bar.setValue(100)
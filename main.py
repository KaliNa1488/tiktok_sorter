import os
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, 
                             QFileDialog, QLabel, QVBoxLayout, QWidget, 
                             QMessageBox, QHBoxLayout, QFrame, QSizePolicy,
                             QLineEdit, QInputDialog, QScrollArea)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl, QTimer, Qt, QSize
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor, QLinearGradient, QBrush

class VideoCategorizerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Categorizer Pro")
        self.setGeometry(100, 100, 1000, 750)
        
        # Initialize variables
        self.current_video_index = 0
        self.video_files = []
        self.source_folder = ""
        self.custom_categories = []  # Store custom categories
        
        # Set application style
        self.set_style()
        
        # Create UI elements
        self.create_ui()
        
        # Initialize media player
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.stateChanged.connect(self.handle_state_changed)
        self.media_player.error.connect(self.handle_player_error)
        
        # Timer for checking playback status
        self.playback_check_timer = QTimer()
        self.playback_check_timer.timeout.connect(self.check_playback_status)
        self.playback_check_timer.start(1000)

    def set_style(self):
        # Set dark theme palette
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(35, 35, 35))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, QColor(25, 25, 25))
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Highlight, QColor(142, 45, 197).lighter())
        palette.setColor(QPalette.HighlightedText, Qt.black)
        QApplication.setPalette(palette)
        
        # Set style sheet for additional styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #353535;
            }
            QPushButton {
                background-color: #5c5c5c;
                border: 1px solid #6a6a6a;
                border-radius: 5px;
                padding: 8px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #6a6a6a;
            }
            QPushButton:pressed {
                background-color: #4a4a4a;
            }
            QLabel {
                color: white;
            }
            QFrame {
                background-color: #454545;
                border-radius: 5px;
            }
            #category_frame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #8e2dc5, stop:1 #4b1a6e);
                border-radius: 10px;
            }
            #header_label {
                font-size: 18px;
                font-weight: bold;
                color: white;
            }
            #status_label {
                font-size: 14px;
                color: #aaaaaa;
                padding: 5px;
                background-color: #454545;
                border-radius: 5px;
            }
            #custom_categories_frame {
                background-color: #454545;
                border-radius: 10px;
            }
            QScrollArea {
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                background: #454545;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #6a6a6a;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical {
                border: none;
                background: none;
                height: 0px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
            }
            QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
                subcontrol-position: top;
                subcontrol-origin: margin;
            }
        """)

    def create_ui(self):
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Header
        header = QLabel("Video Categorizer Pro")
        header.setObjectName("header_label")
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)
        
        # Open folder button
        self.open_button = QPushButton("📁 Open Video Folder")
        self.open_button.setIconSize(QSize(24, 24))
        self.open_button.setFixedHeight(45)
        self.open_button.clicked.connect(self.open_folder_dialog)
        main_layout.addWidget(self.open_button)
        
        # Status label
        self.status_label = QLabel("No folder selected")
        self.status_label.setObjectName("status_label")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setWordWrap(True)
        main_layout.addWidget(self.status_label)
        
        # Video widget with frame
        video_frame = QFrame()
        video_frame.setFrameShape(QFrame.StyledPanel)
        video_frame.setLineWidth(2)
        video_layout = QVBoxLayout()
        video_layout.setContentsMargins(5, 5, 5, 5)
        
        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumSize(640, 360)
        video_layout.addWidget(self.video_widget)
        video_frame.setLayout(video_layout)
        main_layout.addWidget(video_frame, 1)
        
        # Default category buttons frame
        default_category_frame = QFrame()
        default_category_frame.setObjectName("category_frame")
        default_category_layout = QHBoxLayout()
        default_category_layout.setContentsMargins(20, 15, 20, 15)
        default_category_layout.setSpacing(20)
        
        # Travel button
        self.travel_button = QPushButton("✈️ Travel")
        self.travel_button.setIconSize(QSize(24, 24))
        self.travel_button.setFixedHeight(50)
        self.travel_button.clicked.connect(lambda: self.categorize_video("travel"))
        self.travel_button.setEnabled(False)
        default_category_layout.addWidget(self.travel_button)
        
        # Food button
        self.food_button = QPushButton("🍔 Food")
        self.food_button.setIconSize(QSize(24, 24))
        self.food_button.setFixedHeight(50)
        self.food_button.clicked.connect(lambda: self.categorize_video("food"))
        self.food_button.setEnabled(False)
        default_category_layout.addWidget(self.food_button)
        
        # Idea button
        self.idea_button = QPushButton("💡 Idea")
        self.idea_button.setIconSize(QSize(24, 24))
        self.idea_button.setFixedHeight(50)
        self.idea_button.clicked.connect(lambda: self.categorize_video("idea"))
        self.idea_button.setEnabled(False)
        default_category_layout.addWidget(self.idea_button)
        
        default_category_frame.setLayout(default_category_layout)
        main_layout.addWidget(default_category_frame)
        
        # Custom categories section
        custom_cat_frame = QFrame()
        custom_cat_frame.setObjectName("custom_categories_frame")
        custom_cat_layout = QVBoxLayout()
        custom_cat_layout.setContentsMargins(15, 15, 15, 15)
        
        # Add custom category button
        self.add_category_btn = QPushButton("➕ Add Custom Category")
        self.add_category_btn.setFixedHeight(40)
        self.add_category_btn.clicked.connect(self.add_custom_category)
        custom_cat_layout.addWidget(self.add_category_btn)
        
        # Custom categories buttons container
        self.custom_categories_container = QWidget()
        self.custom_categories_layout = QHBoxLayout()
        self.custom_categories_layout.setContentsMargins(0, 10, 0, 0)
        self.custom_categories_layout.setSpacing(15)
        self.custom_categories_container.setLayout(self.custom_categories_layout)
        
        # Scroll area for custom categories
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.custom_categories_container)
        custom_cat_layout.addWidget(scroll_area)
        
        custom_cat_frame.setLayout(custom_cat_layout)
        main_layout.addWidget(custom_cat_frame)
        
        main_widget.setLayout(main_layout)

    def add_custom_category(self):
        text, ok = QInputDialog.getText(self, 'Add Custom Category', 
                                        'Enter category name:')
        if ok and text:
            if text.lower() in ['travel', 'food', 'idea']:
                QMessageBox.warning(self, "Error", "This is a default category!")
                return
                
            if text not in self.custom_categories:
                self.custom_categories.append(text)
                self.create_custom_category_button(text)
            else:
                QMessageBox.warning(self, "Error", "Category already exists!")

    def create_custom_category_button(self, category_name):
        btn = QPushButton(f"⭐ {category_name}")
        btn.setFixedHeight(45)
        btn.clicked.connect(lambda: self.categorize_video(category_name))
        self.custom_categories_layout.addWidget(btn)
        
        # Enable buttons if we have videos
        if self.video_files:
            btn.setEnabled(True)

    def open_folder_dialog(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder with Videos")
        if folder:
            self.source_folder = folder
            self.load_video_files()
            self.status_label.setText(f"Folder: {folder}")
    
    def load_video_files(self):
        self.video_files = []
        extensions = ('.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.mpg', '.mpeg')
        
        for file in os.listdir(self.source_folder):
            if file.lower().endswith(extensions):
                self.video_files.append(file)
        
        if self.video_files:
            self.video_files.sort()
            self.current_video_index = 0
            self.play_current_video()
            self.enable_category_buttons(True)
            self.enable_custom_category_buttons(True)
        else:
            self.status_label.setText("No video files found in selected folder")
            self.enable_category_buttons(False)
            self.enable_custom_category_buttons(False)
    
    def play_current_video(self):
        if self.current_video_index < len(self.video_files):
            video_path = os.path.join(self.source_folder, self.video_files[self.current_video_index])
            media_content = QMediaContent(QUrl.fromLocalFile(video_path))
            
            self.media_player.stop()
            self.media_player.setMedia(media_content)
            self.media_player.play()
            self.status_label.setText(f"Playing: {self.video_files[self.current_video_index]}")
    
    def handle_state_changed(self, state):
        if state == QMediaPlayer.StoppedState and self.media_player.mediaStatus() == QMediaPlayer.EndOfMedia:
            self.media_player.setPosition(0)
            self.media_player.play()
    
    def check_playback_status(self):
        if (self.media_player.state() == QMediaPlayer.PlayingState and 
            self.media_player.position() == 0 and 
            self.media_player.mediaStatus() == QMediaPlayer.LoadedMedia):
            self.media_player.play()
    
    def handle_player_error(self, error):
        error_msg = ""
        if error == QMediaPlayer.NoError:
            return
        elif error == QMediaPlayer.ResourceError:
            error_msg = "Resource error - file might be corrupted or codec missing"
        elif error == QMediaPlayer.FormatError:
            error_msg = "Format error - file format not supported"
        elif error == QMediaPlayer.NetworkError:
            error_msg = "Network error"
        elif error == QMediaPlayer.AccessDeniedError:
            error_msg = "Access denied"
        else:
            error_msg = "Unknown playback error"
        
        current_file = self.video_files[self.current_video_index] if self.video_files else "unknown"
        full_msg = f"Error playing {current_file}: {error_msg}\n\nSkipping to next video."
        
        QMessageBox.warning(self, "Playback Error", full_msg)
        self.skip_to_next_video()
    
    def skip_to_next_video(self):
        if self.video_files:
            self.current_video_index += 1
            if self.current_video_index >= len(self.video_files):
                self.current_video_index = 0
            self.play_current_video()
    
    def categorize_video(self, category):
        if not self.video_files or self.current_video_index >= len(self.video_files):
            return
        
        category_folder = os.path.join(self.source_folder, category)
        os.makedirs(category_folder, exist_ok=True)
        
        current_file = self.video_files[self.current_video_index]
        src_path = os.path.join(self.source_folder, current_file)
        dest_path = os.path.join(category_folder, current_file)
        
        try:
            self.media_player.stop()
            self.media_player.setMedia(QMediaContent())
            QTimer.singleShot(100, lambda: self.perform_file_move(src_path, dest_path, category, current_file))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to prepare for file move: {str(e)}")
    
    def perform_file_move(self, src_path, dest_path, category, current_file):
        try:
            os.rename(src_path, dest_path)
            self.status_label.setText(f"Moved '{current_file}' to '{category}'")
            
            self.video_files.pop(self.current_video_index)
            
            if self.video_files:
                if self.current_video_index >= len(self.video_files):
                    self.current_video_index = 0
                self.play_current_video()
            else:
                self.media_player.stop()
                self.status_label.setText("No more videos in folder")
                self.enable_category_buttons(False)
                self.enable_custom_category_buttons(False)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to move file: {str(e)}\n\nFile might still be in use. Trying again...")
            QTimer.singleShot(500, lambda: self.perform_file_move(src_path, dest_path, category, current_file))
    
    def enable_category_buttons(self, enabled):
        self.travel_button.setEnabled(enabled)
        self.food_button.setEnabled(enabled)
        self.idea_button.setEnabled(enabled)
    
    def enable_custom_category_buttons(self, enabled):
        for i in range(self.custom_categories_layout.count()):
            widget = self.custom_categories_layout.itemAt(i).widget()
            if isinstance(widget, QPushButton):
                widget.setEnabled(enabled)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    try:
        app.setStyle('Fusion')
    except:
        pass
    
    window = VideoCategorizerApp()
    window.show()
    sys.exit(app.exec_())
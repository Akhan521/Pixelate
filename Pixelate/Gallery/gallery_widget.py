from PyQt6.QtWidgets import ( QApplication, QMainWindow, QHBoxLayout, 
                              QVBoxLayout, QWidget, QGraphicsScene, 
                              QGraphicsProxyWidget, QMenuBar, QMenu,
                              QFileDialog, QMessageBox, QSizePolicy,
                              QWidgetAction, QLabel, QListWidget,
                              QListWidgetItem, QPushButton, QDialog)

from PyQt6.QtGui import QGuiApplication, QColor, QFont, QFontDatabase, QPixmap, QPainter
from PyQt6.QtCore import Qt, QSize
# from Pixelate.Gallery.gallery_manager import GalleryManager
from Gallery.gallery_manager import GalleryManager
from Pixelate.User_Authentication.auth_manager import AuthManager

class GalleryWidget(QWidget):

    def __init__(self, gallery_manager):
        super().__init__()
        self.gallery_manager = gallery_manager

        # Create a layout for the gallery widget.
        layout = QVBoxLayout()
        
        # Gallery header.
        header = QLabel("Pixelate Gallery")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setObjectName("GalleryHeader")
        
        # A refresh button to reload the gallery.
        refresh_button = QPushButton("Refresh Gallery")
        refresh_button.clicked.connect(self.load_gallery)

        # A button to close the gallery widget.
        close_button = QPushButton("Close Gallery")
        close_button.clicked.connect(self.close_gallery)

        # A layout for our buttons.
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(0)
        button_layout.addWidget(refresh_button)
        button_layout.addWidget(close_button)

        # A list of sprites in the gallery.
        self.sprite_list = QListWidget()
        self.sprite_list.itemDoubleClicked.connect(self.show_sprite_details)

        # Adding our widgets to the layout.
        layout.addWidget(header)
        layout.addLayout(button_layout)
        layout.addWidget(self.sprite_list)
        self.setStyleSheet(self.get_style())
        self.setLayout(layout)

        # Load the gallery when the widget is created.
        self.load_gallery()

    # A method to close the gallery widget.
    def close_gallery(self):
        self.gallery_manager.auth_manager.logout()
        print("Gallery closed and user logged out.")
        self.close()

    # A method to load the gallery of sprites.
    def load_gallery(self):

        # Clear the existing sprite list.
        self.sprite_list.clear()

        # Get the gallery of sprites from the gallery manager.
        sprites = self.gallery_manager.get_gallery()

        # Add each sprite to the sprite list.
        for sprite in sprites:
            item = QListWidgetItem(f"{sprite['title']} by {sprite['creator_username']} - {sprite.get('likes', 0)} likes")
            # Storing the sprite ID within the item for later on when we show the sprite details.
            item.setData(Qt.ItemDataRole.UserRole, sprite["id"])
            self.sprite_list.addItem(item)

    # A method to show the details of a sprite.
    def show_sprite_details(self, item):
        # Get the sprite ID from the item.
        sprite_id = item.data(Qt.ItemDataRole.UserRole)

        # Get the sprite from the gallery manager.
        sprite_data = self.gallery_manager.get_sprite(sprite_id)

        # Show the sprite details in a dialog.
        if sprite_data:
            dialog = SpriteDetailsDialog(sprite_data, self.gallery_manager)
            dialog.exec()
            # Reload the gallery after the dialog is closed.
            self.load_gallery()

    # Default styling.
    def get_style(self):
        return f'''
        QWidget {{
            background-color: #f0f0f0;
            font-family: {self.get_font().family()};
            color: #333333;
        }}
        QLabel {{
            color: #333333;
            margin-left: 10px;
            margin-right: 10px;
            font-size: 14px;
        }}
        QLabel#GalleryHeader {{
            font-size: 24px;
            font-weight: bold;
            color: white;
            margin-bottom: 10px;
            padding: 12px;
            background-color: purple;
            border-radius: 8px;
        }}
        QListWidget {{
            background-color: white;
            color: #333333;
            padding: 8px;
            margin: 10px;
            border: 2px solid #d0d0d0;
            border-radius: 10px;
        }}
        QListWidget::item {{
            padding: 12px;
            margin: 8px;
            border: 1px solid #d0d0d0;
            border-radius: 8px;
            background-color: #f8f8f8;
        }}
        QListWidget::item:hover {{
            background-color: #e6d8f0;
            border: 1px solid #9370DB;
        }}
        QListWidget::item:selected {{
            background-color: purple;
            color: white;
            border: 1px solid white;
        }}
        QScrollBar:vertical {{
            border: none;
            background: #f0f0f0;
            width: 10px;
            margin: 0px;
        }}
        QScrollBar::handle:vertical {{
            background: #9370DB;
            min-height: 20px;
            border-radius: 5px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: #7B68EE;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        QPushButton {{
            color: #333333;
            background-color: white;
            padding: 12px;
            margin: 10px;
            margin-bottom: 12px;
            border: 2px solid #A9A9A9;
            border-radius: 8px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            color: white;
            background-color: purple;
            border: 2px solid white;
        }}
        QPushButton:pressed {{
            color: white;
            background-color: #4B0082;
            border: 2px solid white;
        }}
    '''

    # A method to get our pixelated font.
    def get_font(self):

        # Setting up our pixelated font:
        font_path = "fonts/Press_Start_2P/PressStart2P-Regular.ttf"

        # Adding our pixelated font to the QFontDatabase.
        font_id = QFontDatabase.addApplicationFont(font_path)
        
        # If the font was loaded successfully, we'll use it for our button text.
        if font_id != -1:
            pixelated_font = QFont("Press Start 2P")
        else:
            # If the font wasn't loaded, we'll use the default application font.
            pixelated_font = QFont()

        return pixelated_font

# Our sprite details dialog.
class SpriteDetailsDialog(QDialog):

    def __init__(self, sprite_data, gallery_manager):
        super().__init__()
        self.sprite_data = sprite_data
        self.gallery_manager = gallery_manager
        self.setWindowTitle(f"{sprite_data['title']}")

        # Create a layout for the dialog.
        layout = QVBoxLayout()

        # Display the sprite title and creator.
        title_label = QLabel(f"Title: {sprite_data['title']} by {sprite_data['creator_username']}")
        title_label.setObjectName("SpriteTitle")

        # Display the sprite description.
        desc_label = QLabel(f"Description: {sprite_data.get('description', 'No description')}")
        desc_label.setWordWrap(True)
        desc_label.setObjectName("SpriteDescription")

        # Display a preview of the sprite.
        sprite_preview = QLabel()
        pixels_data = sprite_data.get("pixels_data", {})
        dimensions = pixels_data.get("dimensions", (512, 512))
        pixels = pixels_data.get("pixels", {})
        pixel_size = 5
        pixmap_size = QSize(dimensions[0] * pixel_size, dimensions[1] * pixel_size)
        pixmap = QPixmap(pixmap_size)
        pixmap.fill(QColor(0, 0, 0, 0))
        
        painter = QPainter(pixmap)
        for (x, y), rgba in pixels.items():
            color = QColor(*rgba)
            painter.fillRect(x * pixel_size, y * pixel_size, pixel_size, pixel_size, color)
        painter.end()

        sprite_preview.setPixmap(pixmap)
        sprite_preview.setFixedSize(pixmap_size)
        sprite_preview.setObjectName("SpritePreview")

        # Display likes and a like button.
        likes_layout = QHBoxLayout()
        self.likes_label = QLabel(f"Likes: {self.sprite_data.get('likes', 0)}")
        self.likes_label.setObjectName("LikesLabel")
        self.like_button = QPushButton("Like") if not self.sprite_data.get("liked_by_user", False) else QPushButton("Unlike")
        self.like_button.clicked.connect(self.toggle_like)
        self.like_button.setObjectName("LikeButton")
        likes_layout.addWidget(self.likes_label)
        likes_layout.addWidget(self.like_button)

        # Adding our widgets to the layout.
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        layout.addWidget(sprite_preview)
        layout.addLayout(likes_layout)
        self.setStyleSheet(self.get_style())
        self.setLayout(layout)

    # A method to toggle the like status of the sprite (using the gallery manager).
    def toggle_like(self):

        like_status, sprite_data = self.gallery_manager.toggle_like(self.sprite_data["id"])
        self.sprite_data.update(sprite_data)

        if like_status == "Liked":
            self.likes_label.setText(f"Likes: {self.sprite_data.get('likes', 0)}")
            self.like_button.setText("Unlike")
        elif like_status == "Unliked":
            self.likes_label.setText(f"Likes: {self.sprite_data.get('likes', 0)}")
            self.like_button.setText("Like")

    # Default styling.
    def get_style(self):
        return f'''
        QDialog {{
            background-color: #f0f0f0;
            font-family: {self.get_font().family()};
            color: #333333;
            padding: 15px;
        }}
        QLabel {{
            color: #333333;
            margin-left: 10px;
            margin-right: 10px;
            font-size: 14px;
            padding: 5px;
        }}
        QLabel#SpriteTitle {{
            font-size: 18px;
            font-weight: bold;
            color: #4B0082;
            margin-bottom: 10px;
            padding: 8px;
            background-color: #e6d8f0;
            border-radius: 8px;
        }}
        QLabel#SpriteDescription {{
            background-color: white;
            padding: 12px;
            margin: 8px;
            border: 1px solid #d0d0d0;
            border-radius: 8px;
        }}
        QLabel#SpritePreview {{
            border: 2px solid #9370DB;
            border-radius: 10px;
            padding: 5px;
            background-color: white;
            margin: 15px;
        }}
        QLabel#LikesLabel {{
            font-weight: bold;
            color: #4B0082;
            font-size: 16px;
        }}
        QScrollBar:vertical {{
            border: none;
            background: #f0f0f0;
            width: 10px;
            margin: 0px;
        }}
        QScrollBar::handle:vertical {{
            background: #9370DB;
            min-height: 20px;
            border-radius: 5px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: #7B68EE;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        QPushButton {{
            color: #333333;
            background-color: white;
            padding: 12px;
            margin: 10px;
            margin-bottom: 12px;
            border: 2px solid #9370DB;
            border-radius: 8px;
            font-weight: bold;
            min-width: 100px;
        }}
        QPushButton:hover {{
            color: white;
            background-color: #9370DB;
            border: 2px solid #7B68EE;
        }}
        QPushButton:pressed {{
            color: white;
            background-color: #4B0082;
            border: 2px solid #7B68EE;
        }}
        /* Special styling for the like button */
        QPushButton#LikeButton {{
            background-color: #f0f0f0;
            border: 2px solid #9370DB;
        }}
        QPushButton#LikeButton:hover {{
            background-color: #9370DB;
            color: white;
        }}
    '''

    # A method to get our pixelated font.
    def get_font(self):

        # Setting up our pixelated font:
        font_path = "fonts/Press_Start_2P/PressStart2P-Regular.ttf"

        # Adding our pixelated font to the QFontDatabase.
        font_id = QFontDatabase.addApplicationFont(font_path)
        
        # If the font was loaded successfully, we'll use it for our button text.
        if font_id != -1:
            pixelated_font = QFont("Press Start 2P")
        else:
            # If the font wasn't loaded, we'll use the default application font.
            pixelated_font = QFont()

        return pixelated_font
    


if __name__ == "__main__":
    app = QApplication([])

    # Initialize the authentication manager.
    auth_manager = AuthManager()

    # Initialize the gallery manager.
    gallery_manager = GalleryManager(auth_manager)

    # Create the gallery widget.
    gallery_widget = GalleryWidget(gallery_manager)
    gallery_widget.show()

    app.exec()
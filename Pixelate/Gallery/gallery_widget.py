from PyQt6.QtWidgets import ( QApplication, QMainWindow, QHBoxLayout, 
                              QVBoxLayout, QWidget, QGraphicsScene, 
                              QGraphicsProxyWidget, QMenuBar, QMenu,
                              QFileDialog, QMessageBox, QSizePolicy,
                              QWidgetAction, QLabel, QListWidget,
                              QListWidgetItem, QPushButton, QDialog)

from PyQt6.QtGui import QGuiApplication, QColor, QFont, QFontDatabase, QPixmap, QPainter
from PyQt6.QtCore import Qt, QSize
from gallery_manager import GalleryManager
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
        header.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        # A refresh button to reload the gallery.
        refresh_button = QPushButton("Refresh Gallery")
        refresh_button.clicked.connect(self.load_gallery)

        # A list of sprites in the gallery.
        self.sprite_list = QListWidget()
        self.sprite_list.itemDoubleClicked.connect(self.show_sprite_details)

        # Adding our widgets to the layout.
        layout.addWidget(header)
        layout.addWidget(refresh_button)
        layout.addWidget(self.sprite_list)
        self.setLayout(layout)

        # Load the gallery when the widget is created.
        self.load_gallery()

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

        # Display the sprite description.
        desc_label = QLabel(f"Description: {sprite_data.get('description', 'No description')}")
        desc_label.setWordWrap(True)

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

        # Display likes and a like button.
        likes_layout = QHBoxLayout()
        self.likes_label = QLabel(f"Likes: {self.sprite_data.get('likes', 0)}")
        self.like_button = QPushButton("Like") if self.sprite_data.get('likes', 0) == 0 else QPushButton("Unlike")
        self.like_button.clicked.connect(self.toggle_like)
        likes_layout.addWidget(self.likes_label)
        likes_layout.addWidget(self.like_button)

        # Adding our widgets to the layout.
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        layout.addWidget(sprite_preview)
        layout.addLayout(likes_layout)
        self.setLayout(layout)

    # A method to toggle the like status of the sprite (using the gallery manager).
    def toggle_like(self):

        like_status = self.gallery_manager.toggle_like(self.sprite_data["id"])

        if like_status == "Liked":
            self.likes_label.setText(f"Likes: {self.sprite_data.get('likes', 0) + 1}")
            self.like_button.setText("Unlike")
        elif like_status == "Unliked":
            self.likes_label.setText(f"Likes: {self.sprite_data.get('likes', 0) - 1}")
            self.like_button.setText("Like")


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
from PyQt6.QtWidgets import ( QApplication, QMainWindow, QHBoxLayout, 
                              QVBoxLayout, QWidget, QGraphicsScene, 
                              QGraphicsProxyWidget, QMenuBar, QMenu,
                              QFileDialog, QMessageBox, QSizePolicy,
                              QWidgetAction, QLabel, QListWidget,
                              QListWidgetItem, QPushButton, QDialog)

from PyQt6.QtGui import QGuiApplication, QColor, QFont, QFontDatabase, QAction
from PyQt6.QtCore import Qt
from Pixelate.Gallery.gallery_manager import GalleryManager
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
        # self.sprite_list.itemDoubleClicked.connect(self.show_sprite_details)

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
        sprite = self.gallery_manager.get_sprite(sprite_id)

#         # Show the sprite details in a dialog.
#         if sprite:
#             dialog = SpriteDetailsDialog(sprite, self.gallery_manager)
#             dialog.exec()
#             # Reload the gallery after the dialog is closed.
#             self.load_gallery()

# # Our sprite details dialog.
# class SpriteDetailsDialog(Q)

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
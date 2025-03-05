
from PyQt6.QtWidgets import ( QApplication, QMainWindow, QHBoxLayout, 
                              QVBoxLayout, QWidget, QGraphicsScene, 
                              QGraphicsProxyWidget, QMenuBar, QMenu,
                              QFileDialog, QMessageBox, QSizePolicy,
                              QWidgetAction, QLabel, QListWidget,
                              QListWidgetItem, QPushButton, QDialog,
                              QLineEdit)

from PyQt6.QtGui import QGuiApplication, QColor, QFont, QFontDatabase, QAction
from PyQt6.QtCore import Qt
from gallery_manager import GalleryManager
from Pixelate.User_Authentication.auth_manager import AuthManager
from Pixelate.custom_messagebox import CustomMessageBox
from Pixelate.validations import validate_dimensions, validate_imported_data
import ast

# A widget to upload sprites to the gallery.
class UploadWidget(QWidget):

    def __init__(self, gallery_manager):
        super().__init__()
        self.gallery_manager = gallery_manager
        self.pixels_data = None

        # Create a layout for the upload widget.
        layout = QVBoxLayout()

        # Upload header.
        header = QLabel("Upload a Sprite")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("font-size: 24px; font-weight: bold;")

        # A title label and text box.
        title_label = QLabel("Title:")
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter a title for your sprite")

        # A description label and text box.
        description_label = QLabel("Description:")
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Enter a description for your sprite")

        # A label to show which sprite is currently selected.
        self.sprite_label = QLabel("Selected Sprite: None")
        self.sprite_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # A button to select a sprite.
        select_button = QPushButton("Select Sprite")
        select_button.clicked.connect(self.select_sprite)

        # A button to upload the sprite.
        upload_button = QPushButton("Upload Sprite")
        upload_button.clicked.connect(self.upload_sprite)

        # Adding our widgets to the layout.
        layout.addWidget(header)
        layout.addWidget(title_label)
        layout.addWidget(self.title_input)
        layout.addWidget(description_label)
        layout.addWidget(self.description_input)
        layout.addWidget(self.sprite_label)
        layout.addWidget(select_button)
        layout.addWidget(upload_button)
        self.setLayout(layout)

    # A method to upload a sprite to the gallery.
    def upload_sprite(self):
        # Get the title and description from the input fields.
        title = self.title_input.text().strip()
        description = self.description_input.text().strip()

        # If the title or description is empty, show an error message.
        if not title or not description:
            CustomMessageBox("Error", "Please enter a title and description for your sprite.", type="error")
            return
        
        # If the pixels data is empty, show an error message.
        if not self.pixels_data:
            CustomMessageBox("Error", "No sprite data to upload.", type="error")
            return
        
        # Upload the sprite to the gallery.
        if self.gallery_manager.upload_sprite(title, description, self.pixels_data):
            CustomMessageBox("Success", "Sprite uploaded successfully!", type="info")
            # Clear the title and description input fields.
            self.title_input.clear()
            self.description_input.clear()
        else:
            CustomMessageBox("Error", "An error occurred while uploading the sprite.", type="error")
            # Clearing the pixels data.
            self.pixels_data = None
            # Updating our sprite label to show that no sprite is selected.
            self.sprite_label.setText("Selected Sprite: None")

    # A method to select a sprite to upload (file dialog).
    def select_sprite(self):
        
        # Prompting the user to select a sprite file.
        filepath, _ = QFileDialog.getOpenFileName(self, "Select Sprite", "", "Pix Files (*.pix)")

        if filepath:

            dimensions = None  # To store our canvas dimensions.
            pixels = None      # To store our pixels dictionary data.

            try:

                # Reading the contents of our .pix file.
                with open(filepath, "r") as file:
                    # Reading the first line of the file (which should contain the dimensions of our canvas).
                    dimensions = file.readline().strip()
                    # Reading the rest of the file (which should contain our pixels dictionary).
                    pixels = file.read()

                # Parsing our canvas dimensions using the ast module. (Converting our string tuple to an actual tuple).
                dimensions = ast.literal_eval(dimensions)

                # Validating our dimensions to ensure that they're in the correct format.
                if not validate_dimensions(dimensions):
                    CustomMessageBox(title   = "ERROR: invalid/missing dimensions", 
                                     message = "The selected file is missing or has invalid dimensions.", 
                                     type    = "error")
                    return

                # Parsing our text file using the ast module. (Converting our string dict. to an actual dict.)
                pixels = ast.literal_eval(pixels)

                # Validating our pixels data to ensure that it's in the correct format.
                if not validate_imported_data(pixels):
                    CustomMessageBox(title   = "ERROR: invalid data format/type", 
                                     message = "The data in the selected file is not in the correct format.", 
                                     type    = "error")
                    return
                
                # If our dimensions and pixels data are valid, we'll set up our canvas with the imported data.
                else:
                    CustomMessageBox(title   = "Success", 
                                     message = "Sprite selected successfully.", 
                                     type    = "info")

                    # Storing our pixels data.
                    pixels_data = {
                        "dimensions": dimensions,
                        "pixels": pixels
                    }
                    self.pixels_data = pixels_data

                    # Updating our sprite label to show the selected sprite.
                    self.sprite_label.setText(f"Selected Sprite: {filepath}")

            except Exception as e:
                CustomMessageBox(title   = "ERROR: failed to select sprite", 
                                 message = str(e), 
                                 type    = "warning")

# # Test the UploadWidget.
# app = QApplication([])
# gallery_manager = GalleryManager(AuthManager())
# upload_widget = UploadWidget(gallery_manager)
# upload_widget.show()
# app.exec()
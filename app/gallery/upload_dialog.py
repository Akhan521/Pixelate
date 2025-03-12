
from PyQt6.QtWidgets import ( QApplication, QMainWindow, QHBoxLayout, 
                              QVBoxLayout, QWidget, QGraphicsScene, 
                              QGraphicsProxyWidget, QMenuBar, QMenu,
                              QFileDialog, QMessageBox, QSizePolicy,
                              QWidgetAction, QLabel, QListWidget,
                              QListWidgetItem, QPushButton, QDialog,
                              QLineEdit, QTextEdit, QDialogButtonBox,)

from PyQt6.QtGui import QGuiApplication, QColor, QFont, QFontDatabase, QMovie
from PyQt6.QtCore import Qt, QThread, pyqtSignal
# from gallery_manager import GalleryManager
from app.gallery.gallery_manager import GalleryManager
from app.user_auth.auth_manager import AuthManager
from app.custom_messagebox import CustomMessageBox
from app.validations import validate_dimensions, validate_imported_data
import ast

# A file loader thread to handle loading .pix files in the background.
# This ensures that our application remains responsive while loading files.
class FileLoaderThread(QThread):
    # Our signals:
    file_loaded = pyqtSignal(dict, str) # pixels_data, project_name
    error_occurred = pyqtSignal(str)    # error_message

    def __init__(self, filepath):
        super().__init__()
        self.filepath = filepath

    def run(self):
        # Now, we'll try to load the file.
        try:
            # Reading the contents of our .pix file.
            with open(self.filepath, "r") as file:
                # Reading the first line of the file (which should contain the dimensions of our canvas).
                dimensions = file.readline().strip()
                # Reading the rest of the file (which should contain our pixels dictionary).
                pixels = file.read()

            # Parsing our canvas dimensions using the ast module. (Converting our string tuple to an actual tuple).
            dimensions = ast.literal_eval(dimensions)

            # Validating our dimensions to ensure that they're in the correct format.
            if not validate_dimensions(dimensions):
                self.error_occurred.emit("The selected file is missing or has invalid dimensions.")
                return

            # Parsing our text file using the ast module. (Converting our string dict. to an actual dict.)
            pixels = ast.literal_eval(pixels)

            # Validating our pixels data to ensure that it's in the correct format.
            if not validate_imported_data(pixels):
                self.error_occurred.emit("The data in the selected file is not in the correct format.")
                return

            # If our dimensions and pixels data are valid, we'll set up our canvas with the imported data.
            else:
                # Storing our pixels data.
                pixels_data = {
                    "dimensions": dimensions,
                    "pixels": pixels
                }

                # Our project's name (for display purposes).
                project_name = self.filepath.split("/")[-1]

                # Emitting our file_loaded signal.
                self.file_loaded.emit(pixels_data, project_name)

        except Exception as e:
            self.error_occurred.emit(str(e))

# A thread to handle uploading sprites to the gallery.
class UploadThread(QThread):
    # Our signals:
    sprite_uploaded = pyqtSignal(bool)
    error_occurred = pyqtSignal(str)

    def __init__(self, gallery_manager, title, description, file_name, pixels_data):
        super().__init__()
        self.gallery_manager = gallery_manager
        self.title = title
        self.description = description
        self.file_name = file_name
        self.pixels_data = pixels_data

    def run(self):
        # Now, we'll try to upload the sprite.
        try:
            # Uploading the sprite to the gallery.
            success = self.gallery_manager.upload_sprite(self.title, self.description, self.file_name, self.pixels_data)
            self.sprite_uploaded.emit(success)

        except Exception as e:
            self.error_occurred.emit(str(e))

# A dialog to upload sprites to the gallery.
class UploadDialog(QDialog):

    def __init__(self, gallery_manager):
        super().__init__()
        self.gallery_manager = gallery_manager
        self.file_name = None
        self.pixels_data = None
        self.setFixedSize(400, 460)

        # Hiding our system taskbar and keeping our dialog on top.
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)

        # Create a layout for the upload widget.
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        # Upload header.
        header = QLabel("Upload Sprite")
        header.setAlignment(Qt.AlignmentFlag.AlignLeft)
        header.setStyleSheet(self.get_header_style())
        header.setFixedHeight(40)

        # A title label and text box.
        title_label = QLabel("Title:")
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter a title for your sprite.")

        # A description label and text box.
        description_label = QLabel("Description:")
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Enter a description for your sprite.")

        # A label to show if a sprite is selected.
        self.sprite_label = QLabel("Selected Sprite: None")
        self.sprite_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sprite_label.setWordWrap(True)

        # A button to select a sprite.
        select_button = QPushButton("Select Sprite")
        select_button.clicked.connect(self.select_sprite)

        # Creating a button box to hold our buttons (OK and Cancel).
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        # If the user clicks OK, we'll upload the sprite.
        self.buttons.accepted.connect(self.upload_sprite)
        # If the user clicks Cancel, we'll close the widget.
        self.buttons.rejected.connect(self.close)
        self.buttons.setCenterButtons(True)

        # A loading label that will be shown while a sprite is being uploaded.
        self.loading_label = QLabel("Uploading Sprite...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setVisible(False)
        
        # A loading animation to show while an image is being generated.
        self.movie = QMovie("Pixelate/loading.gif")
        if self.movie.isValid():
            self.loading_label.setMovie(self.movie)
        else:
            CustomMessageBox("Error", "An error occurred while loading the loading animation.", type="error")

        # Adding our widgets to the layout.
        layout.addWidget(header)
        layout.addWidget(title_label)
        layout.addWidget(self.title_input)
        layout.addWidget(description_label)
        layout.addWidget(self.description_input)
        layout.addWidget(self.sprite_label)
        layout.addWidget(select_button)
        layout.addWidget(self.buttons)
        layout.addWidget(self.loading_label)
        self.setLayout(layout)
        self.setStyleSheet(self.get_style())

    # A method to upload a sprite to the gallery.
    def upload_sprite(self):
        # Get the title and description from the input fields.
        title = self.title_input.text().strip()
        description = self.description_input.toPlainText().strip()

        # If the title or description is empty, show an error message.
        if not title or not description:
            CustomMessageBox("Error", "Please enter a title and description for your sprite.", type="error")
            return
        
        # If the pixels data is empty, show an error message.
        if not self.pixels_data:
            CustomMessageBox("Error", "No sprite data to upload.", type="error")
            return
        
        # If the file name is empty, show an error message.
        if not self.file_name:
            CustomMessageBox("Error", "No sprite selected.", type="error")
            return
        
        # Disable our UI during sprite upload to prevent any issues.
        self.title_input.setReadOnly(True)
        self.description_input.setReadOnly(True)
        self.buttons.hide()

        # Start our loading animation.
        self.loading_label.setVisible(True)
        self.movie.start()

        # Create an upload thread to upload the sprite in the background.
        self.upload_thread = UploadThread(self.gallery_manager, title, description, self.file_name, self.pixels_data)
        self.upload_thread.sprite_uploaded.connect(self.on_sprite_uploaded)
        self.upload_thread.error_occurred.connect(self.on_error_occurred)
        self.upload_thread.finished.connect(self.upload_thread.deleteLater)
        self.upload_thread.start()

    # A method to select a sprite to upload (file dialog).
    def select_sprite(self):
        
        # Prompting the user to select a sprite file.
        filepath, _ = QFileDialog.getOpenFileName(self, "Select Sprite", "", "Pix Files (*.pix)")

        # If the user hasn't selected a file, we'll return.
        if not filepath:
            return

        # Disable our UI during file loading to prevent any issues.
        self.title_input.setReadOnly(True)
        self.description_input.setReadOnly(True)
        self.buttons.hide()

        # Start our loading animation.
        self.loading_label.setVisible(True)
        self.movie.start()

        # Create a file loader thread to load the sprite file in the background.
        self.file_loader_thread = FileLoaderThread(filepath)
        self.file_loader_thread.file_loaded.connect(self.on_file_loaded)
        self.file_loader_thread.error_occurred.connect(self.on_error_occurred)
        self.file_loader_thread.finished.connect(self.file_loader_thread.deleteLater)
        self.file_loader_thread.start()

    # Our file loaded signal handler.
    def on_file_loaded(self, pixels_data, project_name):
        # Stop our loading animation.
        self.movie.stop()
        self.loading_label.setVisible(False)

        # Re-enable our UI after file loading.
        self.title_input.setReadOnly(False)
        self.description_input.setReadOnly(False)
        self.buttons.show()

        # Storing our pixels data.
        self.pixels_data = pixels_data

        # Updating our sprite label.
        self.sprite_label.setText(f"Selected Sprite: {project_name}")
        self.file_name = project_name

        # Showing a success message.
        CustomMessageBox("Success", "Sprite selected successfully.", type="info")

    # Our sprite uploaded signal handler.
    def on_sprite_uploaded(self, success):
        # Stop our loading animation.
        self.movie.stop()
        self.loading_label.setVisible(False)

        # Re-enable our UI.
        self.title_input.setReadOnly(False)
        self.description_input.setReadOnly(False)
        self.buttons.show()

        # Clear the input fields and pixels data.
        self.title_input.clear()
        self.description_input.clear()
        self.sprite_label.setText("Selected Sprite: None")
        self.pixels_data = None
        self.file_name = None

        if success:
            # Showing a success message.
            CustomMessageBox("Success", "Sprite uploaded successfully.", type="info")
        else:
            # Showing an error message.
            CustomMessageBox("Error", "An error occurred while uploading the sprite.", type="error")

    # Our error signal handler.
    def on_error_occurred(self, error_message):
        # Re-enable our UI.
        self.title_input.setReadOnly(False)
        self.description_input.setReadOnly(False)
        self.buttons.show()

        # Clearing the pixels data and file name.
        self.pixels_data = None
        self.file_name = None

        # Updating our sprite label to show that no sprite is selected.
        self.sprite_label.setText("Selected Sprite: None")

        # Showing an error message.
        CustomMessageBox("Error", error_message, type="error")

    # Header styling.
    def get_header_style(self):
        return f'''
            QLabel {{
                background-color: purple;
                color: white;
                font-family: {self.get_font().family()};
                padding: 10px;
                margin: 0px;
                font-size: 20px;
            }}
            '''

    # Default styling.
    def get_style(self):
        return f'''
            QDialog {{
                background-color: lightgray;
                color: black;
            }}
            QLabel {{
                color: black;
                font-family: {self.get_font().family()};
                margin-left: 10px;
                margin-right: 10px;
                font-size: 14px;
            }}
            QLineEdit {{
                background-color: white;
                color: black;
                font-family: {self.get_font().family()};
                padding: 5px;
                margin-left: 10px;
                margin-right: 10px;
            }}
            QTextEdit {{
                background-color: white;
                color: black;
                font-family: {self.get_font().family()};
                padding: 5px;
                margin-left: 10px;
                margin-right: 10px;
            }}
            QPushButton {{
                color: black;
                background-color: white;
                font-family: {self.get_font().family()};
                padding: 10px;
                margin-left: 10px;
                margin-right: 10px;
                margin-bottom: 10px;
                border: 2px solid #A9A9A9;
                border-radius: 10px;
            }}
            QPushButton:hover {{
                color: white;
                background-color: purple;
                border: 2px solid white;
            }}
            QPushButton:pressed {{
                color: white;
                background-color: #4B0082;
                border: 2px solid white
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

# # Test the UploadWidget.
# app = QApplication([])
# gallery_manager = GalleryManager(AuthManager())
# upload_dialog = UploadDialog(gallery_manager)
# upload_dialog.show()
# app.exec()
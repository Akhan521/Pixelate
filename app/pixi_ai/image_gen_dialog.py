from PyQt6.QtWidgets import ( QApplication, QMainWindow, QHBoxLayout, 
                              QVBoxLayout, QWidget, QGraphicsScene, 
                              QGraphicsProxyWidget, QMenuBar, QMenu,
                              QFileDialog, QMessageBox, QPushButton, 
                              QLabel, QDialog, QInputDialog, QLineEdit,
                              QTextEdit, QFormLayout, QDialogButtonBox )

from PyQt6.QtGui import QGuiApplication, QColor, QIcon, QPixmap, QFont, QFontDatabase, QMovie
from PyQt6.QtCore import Qt, QSize, QThread, pyqtSignal
from custom_messagebox import CustomMessageBox
from dotenv import load_dotenv
import requests

# Loading the environment variables.
load_dotenv()

# A worker thread for generating images in the background (to prevent the UI from freezing and to show a loading animation).
class ImageGenThread(QThread):

    # Signals to indicate that an image has been generated or that an error occurred.
    image_generated = pyqtSignal(bytes)
    error_occurred = pyqtSignal(str)

    def __init__(self, description):
        super().__init__()
        self.description = description
        # To interact with our backend, we'll store the backend URL.
        self.backend_url = "https://pixelate-backend.onrender.com"

    # A method to generate an image in the background.
    def run(self):

        try:
            # We'll send a POST request to our backend to generate an image based on the user's description.
            response = requests.post(
                f"{self.backend_url}/image/generate",
                json={"description": self.description}
            )

            # If the request was successful, we'll emit the image_generated signal.
            if response.status_code == 200:
                image_data = response.content
                self.image_generated.emit(image_data)
            else:
                # If an error occurred, we'll emit the error_occurred signal.
                self.error_occurred.emit("An error occurred while generating the image.")

        except requests.exceptions.RequestException as e:
            # If an error occurred, we'll emit the error_occurred signal.
            self.error_occurred.emit("An error occurred while generating the image.")

# A dialog that allows users to specify the image they want to generate.
class ImageGenDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        # Our generated image data.
        self.image_data = None

        # Setting our dialog to be modal.
        self.setModal(True)

        # Setting our pixelated font.
        self.setFont(self.get_font())

        # Setting the window's size.
        self.setFixedSize(400, 400)

        # Hiding our system taskbar and keeping our dialog on top.
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)

        # Creating a vertical layout to hold our widgets.
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # A custom taskbar (for styling purposes).
        taskbar = QLabel("Image Generator")
        taskbar.setAlignment(Qt.AlignmentFlag.AlignLeft)
        taskbar.setStyleSheet(self.get_taskbar_style())
        taskbar.setFixedHeight(40)
        layout.addWidget(taskbar)

        # Adding a prompt to let users know what to do.
        self.prompt = QLabel("Enter a text description of the image you want to generate.")
        
        self.prompt.setStyleSheet(self.get_default_style())
        self.prompt.setWordWrap(True)
        layout.addWidget(self.prompt)

        # Creating a text edit widget for the user to enter their description in.
        self.img_description = QTextEdit(self)
        self.img_description.setStyleSheet(self.get_default_style())
        self.img_description.setPlaceholderText("Your description goes here...")
        layout.addWidget(self.img_description)

        # Creating a button box to hold our buttons (OK and Cancel).
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        # If the user clicks OK, we'll start the image generation process.
        self.buttons.accepted.connect(self.start_generation)
        # If the user clicks Cancel, we'll reject the dialog.
        self.buttons.rejected.connect(self.reject)
        self.buttons.setCenterButtons(True)
        self.buttons.setStyleSheet(self.get_default_style())

        # Adding our buttons to our layout.
        layout.addWidget(self.buttons)

        # A loading label that will be shown while an image is being generated.
        self.loading_label = QLabel("Generating image...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # self.setContentsMargins(0, 0, 0, 10)
        self.loading_label.setVisible(False)
        self.loading_label.setStyleSheet(self.get_default_style())
        layout.addWidget(self.loading_label)
        
        # A loading animation to show while an image is being generated.
        self.movie = QMovie("./app/loading.gif")
        if self.movie.isValid():
            self.loading_label.setMovie(self.movie)
        else:
            CustomMessageBox("Error", "An error occurred while loading the loading animation.", type="error")
        
        # Setting our style.
        self.setStyleSheet(self.get_dialog_style())

        # Setting our layout.
        self.setLayout(layout)

    # When OK is clicked, we'll attempt to generate an image based on the user's description.
    def start_generation(self):
        
        description = self.img_description.toPlainText().strip()

        if not description:
            CustomMessageBox("Error: Missing Description", "Please enter a description for the image.", type = "warning")
            return
        
        # Preventing the user from interacting with the dialog while an image is being generated.
        self.buttons.setEnabled(False)
        self.img_description.setReadOnly(True)
        
        # Showing the loading label and starting the loading animation.
        self.loading_label.setVisible(True)
        self.movie.start()
        
        # We'll generate the image in the background using a worker thread.
        self.thread = ImageGenThread(description)
        # We'll connect the signals to the appropriate slots.
        self.thread.image_generated.connect(self.on_image_generated)
        self.thread.error_occurred.connect(self.on_error_occurred)
        # We'll start the thread.
        self.thread.start()

    # A slot to handle when an image has been generated.
    def on_image_generated(self, image_data=None):
        # Stopping the loading animation.
        self.movie.stop()
        self.loading_label.setVisible(False)

        # Enabling user interaction with the dialog.
        self.buttons.setEnabled(True)
        self.img_description.setReadOnly(False)

        # We'll simply store the image data and accept the dialog.
        self.image_data = image_data
        self.accept()

    # A slot to handle when an error occurs.
    def on_error_occurred(self, error_message):
        # Stopping the loading animation.
        self.movie.stop()
        self.loading_label.setVisible(False)

        # Enabling user interaction with the dialog.
        self.buttons.setEnabled(True)
        self.img_description.setReadOnly(False)

        # Showing an error message.
        CustomMessageBox("Error", error_message, type="error")

    # A method to get the image data.
    def get_image_data(self):
        return self.image_data

    # A method to get our dialog style.
    def get_dialog_style(self):
        return f'''
            QDialog {{
                background-color: lightgray;
                color: black;
            }}
            '''
    
    # A method to get our default style.
    def get_default_style(self):
        return f'''
            QTextEdit {{
                background-color: white;
                color: black;
                font-family: {self.get_font().family()};
                padding: 5px;
                margin-left: 10px;
                margin-right: 10px;
            }}
            QLabel {{
                color: black;
                font-family: {self.get_font().family()};
                margin-left: 10px;
                margin-right: 10px;
                font-size: 14px;
            }}
            QDialogButtonBox QPushButton {{
                color: black;
                font-family: {self.get_font().family()};
                background-color: white;
                padding: 10px;
                margin-right: 10px;
                margin-bottom: 10px;
                border: 2px solid #A9A9A9;
                border-radius: 10px;
            }}
            QDialogButtonBox QPushButton:hover {{
                color: white;
                background-color: #8c52ff;
                border: 2px solid white;
            }}
            QDialogButtonBox QPushButton:pressed {{
                color: white;
                background-color: purple;
                border: 2px solid white
            }}
            '''

    # A method to get our custom taskbar style.
    def get_taskbar_style(self):
        return f'''
            QLabel {{
                background-color: #8c52ff;
                color: white;
                padding: 10px;
                font-family: {self.get_font().family()};
                font-size: 20px;
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


# app = QApplication([])
# dialog = ImageGenDialog()
# dialog.show()
# app.exec()
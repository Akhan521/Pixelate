from PyQt6.QtWidgets import ( QApplication, QMainWindow, QHBoxLayout, 
                              QVBoxLayout, QWidget, QGraphicsScene, 
                              QGraphicsProxyWidget, QMenuBar, QMenu,
                              QFileDialog, QMessageBox, QPushButton, 
                              QLabel, QDialog, QInputDialog, QLineEdit,
                              QTextEdit, QFormLayout, QDialogButtonBox )

from PyQt6.QtGui import QGuiApplication, QColor, QIcon, QPixmap, QFont, QFontDatabase
from PyQt6.QtCore import Qt, QSize
from custom_messagebox import CustomMessageBox
from openai import OpenAI
from dotenv import load_dotenv
import requests
import os

# Loading the environment variables.
load_dotenv()

# A dialog that allows users to specify the image they want to generate.
class ImageGenDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        # Creating a client to interact with DALL-E.
        self.dalle_client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
        )

        # Our generated image data.
        self.image_data = None

        # Setting our dialog to be modal.
        self.setModal(True)

        # Setting our pixelated font.
        self.setFont(self.get_font())

        # Setting the window's size.
        self.setFixedSize(400, 300)

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
        layout.addWidget(taskbar)

        # Adding a prompt to let users know what to do.
        prompt = QLabel("Enter a text description of the image you want to generate.")
        
        prompt.setStyleSheet(self.get_default_style())
        prompt.setWordWrap(True)
        layout.addWidget(prompt)

        # Creating a text edit widget for the user to enter their description in.
        self.img_description = QTextEdit(self)
        self.img_description.setStyleSheet(self.get_default_style())
        self.img_description.setPlaceholderText("Your description goes here...")
        layout.addWidget(self.img_description)

        # Creating a button box to hold our buttons (OK and Cancel).
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        # If the user clicks OK, we'll accept the dialog.
        self.buttons.accepted.connect(self.accept)
        # If the user clicks Cancel, we'll reject the dialog.
        self.buttons.rejected.connect(self.reject)
        self.buttons.setStyleSheet(self.get_default_style())

        # Adding our buttons to our layout.
        layout.addWidget(self.buttons)

        # Setting our style.
        self.setStyleSheet(self.get_dialog_style())

        # Setting our layout.
        self.setLayout(layout)

    # A method to send a request to DALL-E to generate an image based on the user's description.
    def generate_image(self, description):

        style_prompt = '''Style: A pixel art image with a cartoonish style, bold outlines, 
                          and a colorblind-friendly palette. Ensure high contrast and a pixelated look.'''
                          
        try:
            # Attempting to generate a response from DALL-E.
            response = self.dalle_client.images.generate(
                model="dall-e-3",
                prompt=description + "\n" + style_prompt,
                n=1,
                size="1024x1024",
                quality="standard",
            )

            # If the response is successful, we'll store the image URL.
            image_url = response.data[0].url
            
            # We'll download the image from the URL.
            image_data = requests.get(image_url).content

            self.image_data = image_data

        except Exception as e:
            # If an error occurs, we'll display a message box to the user.
            CustomMessageBox("Error", f"An error occurred: {e}", type="error")
            return

    # When OK is clicked, we'll accept the dialog if the dimensions are valid.
    def accept(self):
        
        description = self.img_description.toPlainText().strip()

        if not description:
            CustomMessageBox("Error: Missing Description", "Please enter a description for the image.", type = "warning")
            return
        
        self.generate_image(description)
        
        super().accept()

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
                background-color: purple;
                border: 2px solid white;
            }}
            QDialogButtonBox QPushButton:pressed {{
                color: white;
                background-color: #4B0082;
                border: 2px solid white
            }}
            '''

    # A method to get our custom taskbar style.
    def get_taskbar_style(self):
        return f'''
            QLabel {{
                background-color: purple;
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
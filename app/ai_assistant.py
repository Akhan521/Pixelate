# Importing the required libraries.
from PyQt6.QtWidgets import ( QApplication, QMainWindow, QHBoxLayout, 
                              QVBoxLayout, QWidget, QGraphicsScene, 
                              QGraphicsProxyWidget, QMenuBar, QMenu,
                              QFileDialog, QMessageBox, QPushButton, 
                              QLabel, QDialog, QInputDialog, QLineEdit,
                              QTextEdit, QFormLayout, QDialogButtonBox,
                              QListWidget, QListWidgetItem)

from PyQt6.QtGui import QColor, QImage, QFont, QPixmap, QPainter, QImage
from PyQt6.QtCore import Qt, QSize, QTimer
from chat_bubble_widget import ChatBubbleWidget
from image_gen_dialog import ImageGenDialog
from gallery.gallery_widget import DimmedBackdrop
from openai import OpenAI
from dotenv import load_dotenv
import requests
import os
import json

# Loading the environment variables.
load_dotenv()

# Reading the system prompt for Pixi from a text file.
with open("app/Pixi_System_Prompt.txt", "r") as file:
    system_prompt = file.read()

# Our custom text edit to handle sending messages to Pixi when the user presses Enter.
class PixiTextEdit(QTextEdit):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ai_assistant = parent

    def keyPressEvent(self, event):
        # If the user presses Enter, we'll send their message to Pixi.
        if event.key() == Qt.Key.Key_Return and not (event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
            self.ai_assistant.send_message()
        else:
            super().keyPressEvent(event)

# Our AI assistant will be implemented as a chat widget.
class AIAssistant(QWidget):

    def __init__(self, width, height, canvas=None, main_window=None):

        super().__init__()

        # Storing a reference to the canvas (to handle image generation + drawing).
        self.canvas = canvas

        # Storing a reference to the main window (to dim the background during image generation).
        self.main_window = main_window

        # To interact with our backend, we'll store the backend URL.
        self.backend_url = "https://pixelate-backend.onrender.com"
        
        # Setting the width and height of our chat widget.
        self.width = width
        self.height = height
        self.setFixedWidth(self.width)

        # To provide some context to our AI assistant, we'll store some messages.
        self.chat_context = []   # Each message will be stored as a dictionary (to work with the OpenAI API).
        self.context_limit = 10  # The maximum number of messages to store.

        # Adding our system prompt to the chat context.
        self.chat_context.append({"role": "system", "content": system_prompt})

        # Using a vertical layout for our chat widget's main layout.
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Creating a list widget to display our chat messages.
        self.chat_messages = QListWidget(self)
        self.chat_messages.setSpacing(3)

        # Hiding the vertical scroll bar of the chat messages list widget.
        self.chat_messages.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # To enable line wrapping, we'll set the word wrap property to True.
        self.chat_messages.setWordWrap(True)

        # Adding our chat messages list widget to our main layout.
        main_layout.addWidget(self.chat_messages)

        # We'll specify the height of our input field.
        input_field_height = 55

        # Creating a text edit widget for our input field. This is where the user will type their messages.
        self.input_field = PixiTextEdit(self)
        self.input_field.setFixedHeight(input_field_height)
        self.input_field.setFont(QFont("Press Start 2P", 8))
        self.input_field.setPlaceholderText("Type your message here...")
        self.input_field.setFocus()

        # Adding our input field to our main layout.
        main_layout.addWidget(self.input_field)

        # Creating a send button to send the user's message to Pixi.
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        self.send_button.setFont(QFont("Press Start 2P", 10))
        self.send_button.setStyleSheet(self.get_button_style())
        main_layout.addWidget(self.send_button)

        # Creating a generate button to generate an image based on the user's description.
        self.generate_button = QPushButton("Generate")
        self.generate_button.clicked.connect(self.generate_image)
        self.generate_button.setFont(QFont("Press Start 2P", 10))
        self.generate_button.setStyleSheet(self.get_button_style())
        main_layout.addWidget(self.generate_button)

        self.setStyleSheet(f'''
            QWidget {{
                background-color: {QColor(240, 240, 240, 255).name()};
                color: black;
            }}
            QListWidget {{
                background-color: white;
                border: 2px solid #d0d0d0;
                border-radius: 5px;
                padding: 5px;
            }}
            QTextEdit {{
                background-color: white;
                border: 2px solid #d0d0d0;
                border-radius: 5px;
                padding: 5px;
            }}
            QTextEdit QScrollBar:vertical {{
                border: none;
                background: #f0f0f0;
                width: 5px;
                margin: 0px;
            }}
            QTextEdit QScrollBar::handle:vertical {{
                background: #9370DB;
                min-height: 20px;
                border-radius: 5px;
            }}
            QTextEdit QScrollBar::handle:vertical:hover {{
                background: #7B68EE;
            }}
            QTextEdit QScrollBar::add-line:vertical, QTextEdit QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        ''')
        
        # Finally, we'll set the main layout of our chat widget.
        self.setLayout(main_layout)

        # Delaying the addition of the welcome message to ensure that the chat widget is displayed first.
        QTimer.singleShot(0, self.add_welcome_message)

    def add_welcome_message(self):
        # An introductory message to welcome the user (added to the chat messages list widget).
        welcome_message = "Welcome to Pixelate! I'm Pixi, your AI assistant. Feel free to ask me anything."
        self.chat_context.append({"role": "assistant", "content": welcome_message})
        self.create_list_item(welcome_message, is_user=False)
        
    # A function to set the canvas reference for our AI assistant.
    def set_canvas(self, canvas):
        self.canvas = canvas

    # A function to set the main window reference for our AI assistant.
    def set_main_window(self, main_window):
        self.main_window = main_window

    # A function to send a request to the OpenAI API and receive a response. 
    def get_response(self):

        # We'll provide a limited number of messages to Pixi to generate a response.
        chat_context = self.chat_context

        # If we've exceeded the context limit, we'll only provide the most recent messages.
        if len(self.chat_context) > self.context_limit + 1: # We add 1 to account for the system prompt.

            # We'll provide the system prompt and the most recent messages to Pixi.
            chat_context = system_prompt + self.chat_context[-self.context_limit:]

        # Now, we'll send a request to our backend server to interact with Pixi, our AI assistant.
        chat_context_json = json.dumps(chat_context)
        
        try:
            response = requests.post(
                f"{self.backend_url}/chat",
                json={"chat_context": chat_context_json}
            )

            # If the request was successful, we'll extract the response from the server.
            if response.status_code == 200:
                return response.json()
            
            # If an error occurred, we'll return a default response.
            return "I'm sorry, but I'm currently unavailable. Please try again later."
        
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while sending a request to the server: {str(e)}")
            return "I'm sorry, an error occurred while processing your request. Please try again later."

    # A function to send a message to our AI assistant, Pixi.
    def send_message(self):
        # Getting the message from our text edit widget.
        message = self.input_field.toPlainText().strip()

        # If our message isn't empty, we'll send it to our AI assistant.
        if message:

            # Adding the user's message to our chat context.
            self.chat_context.append({"role": "user", "content": message})

            # Creating a list item to display the user's message and adding it to our chat messages list widget.
            self.create_list_item(f"You: {message}", is_user=True)

            # Clearing the input field.
            self.input_field.clear()

            # Getting a response from our AI assistant, Pixi.
            response = self.get_response()

            # Adding Pixi's response to our chat context.
            self.chat_context.append({"role": "assistant", "content": response})

            # Creating a list item to display Pixi's response and adding it to our chat messages list widget.
            self.create_list_item(f"Pixi: {response}", is_user=False)

            # Automatically scrolling to the bottom of our chat messages list widget.
            self.chat_messages.scrollToBottom()

    # A function to create a list item for our chat messages list widget.
    def create_list_item(self, message, is_user=False):

        # Creating a chat bubble widget to hold our message. (Will be added to the list widget.)
        chat_bubble = ChatBubbleWidget(message, is_user, list_widget=self.chat_messages)

        # Creating an empty list item.
        list_item = QListWidgetItem(self.chat_messages)
        
        # To ensure that our list item can hold our chat bubble widget, we'll set its size hint.
        list_item.setSizeHint(chat_bubble.sizeHint())

        # Adding our list item to the chat messages list widget.
        self.chat_messages.addItem(list_item)

        # Setting our chat bubble widget as the list item.
        self.chat_messages.setItemWidget(list_item, chat_bubble)

        # Automatically scrolling to the bottom of our chat messages list widget.
        self.chat_messages.scrollToBottom()

    # Our generate_image method will be implemented here.
    def generate_image(self):

        # Providing a dimmed backdrop for the image generation dialog.
        self.backdrop = DimmedBackdrop(self.main_window)
        self.backdrop.show()

        # Creating an ImageGenDialog instance to generate an image based on the user's description.
        image_gen_dialog = ImageGenDialog()

        # If the user clicks OK, we'll generate an image based on their description.
        if image_gen_dialog.exec() == QDialog.DialogCode.Accepted:

            image_data = image_gen_dialog.get_image_data()

            # If we have valid image data, we'll store it in our canvas.
            if image_data and self.canvas:

                # We'll save the current state of our canvas before updating it with the generated image.
                self.canvas.canvas_history.save_state_and_update(self.canvas.pixels, self.canvas.canvas_buffer)

                # Using our image data, we'll create a QImage object.
                image = QImage()
                image.loadFromData(image_data)

                # We'll scale down the image to match the dimensions of our canvas.
                # We'll use Nearest Neighbor interpolation for scaling, to achieve a pixelated look.
                width, height = self.canvas.get_dimensions()
                image = image.scaled(width, height,
                                     Qt.AspectRatioMode.IgnoreAspectRatio, 
                                     Qt.TransformationMode.FastTransformation)
                
                # Storing the generated image in our canvas.
                self.canvas.set_generated_image(image)

        # Closing the dimmed backdrop after the image generation dialog is closed.
        self.backdrop.close()

    # Button Style:
    def get_button_style(self):
        return f'''
            QPushButton {{
                background-color: white;
                color: black;
                border: 1px solid black;
                border-radius: 5px;
                padding: 5px;
            }}
            QPushButton:hover {{
                /* A medium shade of gray. */
                background-color: #BEBEBE;
            }}
            QPushButton:pressed {{
                background-color: darkgray;
            }}
        '''

# app = QApplication([])
# assistant = AIAssistant(200, 400)
# assistant.show()
# app.exec()

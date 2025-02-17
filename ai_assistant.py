# Importing the required libraries.
from PyQt6.QtWidgets import ( QApplication, QMainWindow, QHBoxLayout, 
                              QVBoxLayout, QWidget, QGraphicsScene, 
                              QGraphicsProxyWidget, QMenuBar, QMenu,
                              QFileDialog, QMessageBox, QPushButton, 
                              QLabel, QDialog, QInputDialog, QLineEdit,
                              QTextEdit, QFormLayout, QDialogButtonBox,
                              QListWidget, QListWidgetItem )

from PyQt6.QtGui import QColor, QImage, QFont, QPixmap, QPainter
from PyQt6.QtCore import Qt, QSize
from chat_bubble_widget import ChatBubbleWidget
from image_gen_dialog import ImageGenDialog
from openai import OpenAI
from dotenv import load_dotenv
import os

# Loading the environment variables.
load_dotenv()

# Reading the system prompt for Pixi from a text file.
with open("Pixi_System_Prompt.txt", "r") as file:
    system_prompt = file.read()

# Our AI assistant will be implemented as a chat widget.
class AIAssistant(QWidget):

    def __init__(self, width, height, canvas=None):

        super().__init__()

        # Storing a reference to the canvas (to handle image generation).
        self.canvas = canvas

        # Creating an instance of the OpenAI class.
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Setting the width and height of our chat widget.
        self.width = width
        self.height = height
        self.setFixedSize(self.width, self.height)

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
        self.chat_messages.setFixedWidth(self.width - 20) # Subtracting 20 to account for padding.
        self.chat_messages.setSpacing(3)

        # Hiding the vertical scroll bar of the chat messages list widget.
        self.chat_messages.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # To enable line wrapping, we'll set the word wrap property to True.
        self.chat_messages.setWordWrap(True)

        # An introductory message to welcome the user (added to the chat messages list widget).
        welcome_message = "Welcome to Pixelate! I'm Pixi, your AI assistant. Feel free to ask me anything."
        self.chat_context.append({"role": "assistant", "content": welcome_message})
        self.create_list_item(welcome_message, is_user=False)     

        # Adding our chat messages list widget to our main layout.
        main_layout.addWidget(self.chat_messages)

        # We'll specify the height of our input field.
        input_field_height = 50

        # Creating a text edit widget for our input field. This is where the user will type their messages.
        self.input_field = QTextEdit(self)
        self.input_field.setFixedSize(self.width - 20, input_field_height) # Subtracting 20 to account for padding.
        self.input_field.setPlaceholderText("Type your message here...")

        # Adding our input field to our main layout.
        main_layout.addWidget(self.input_field)

        # Creating a send button to send the user's message to Pixi.
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        self.send_button.setFont(QFont("Press Start 2P", 10))
        main_layout.addWidget(self.send_button)

        # Creating a generate button to generate an image based on the user's description.
        self.generate_button = QPushButton("Generate")
        self.generate_button.clicked.connect(self.generate_image)
        self.generate_button.setFont(QFont("Press Start 2P", 10))
        main_layout.addWidget(self.generate_button)

        self.setStyleSheet(f'''
            background-color: {QColor(240, 240, 240, 255).name()};
            color: black;
        ''')
        
        # Finally, we'll set the main layout of our chat widget.
        self.setLayout(main_layout)

        
    # A function to set the canvas reference for our AI assistant.
    def set_canvas(self, canvas):
        self.canvas = canvas

    # A function to send a request to the OpenAI API and receive a response. 
    def get_response(self):

        # We'll provide a limited number of messages to Pixi to generate a response.
        chat_context = self.chat_context

        # If we've exceeded the context limit, we'll only provide the most recent messages.
        if len(self.chat_context) > self.context_limit + 1: # We add 1 to account for the system prompt.

            # We'll provide the system prompt and the most recent messages to Pixi.
            chat_context = self.chat_context[0] + self.chat_context[-self.context_limit:]

        # Now, we'll send a request to the OpenAI API w/ our chat context to get a response.
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=chat_context
            )

            return response.choices[0].message.content
        
        except Exception as e:
            return f"An error occurred: {e}"


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

    # If the user presses Ctrl + Enter, we'll send their message to Pixi.
    def keyPressEvent(self, event):

        if event.key() == Qt.Key.Key_Return and event.modifiers() == Qt.KeyboardModifier.ControlModifier:

            # Sending the user's message to Pixi.
            self.send_message()

    # Our generate_image method will be implemented here.
    def generate_image(self):

        # Creating an ImageGenDialog instance to generate an image based on the user's description.
        image_gen_dialog = ImageGenDialog()

        # If the user clicks OK, we'll generate an image based on their description.
        if image_gen_dialog.exec() == QDialog.DialogCode.Accepted:

            image_data = image_gen_dialog.get_image_data()

            # If we have valid image data, we'll store it in our canvas.
            if image_data and self.canvas:

                # Creating a pixmap from the image data.
                img_pixmap = QPixmap()
                img_pixmap.loadFromData(image_data)

                # Resizing the pixmap to fit the canvas.
                canvas_dims = self.canvas.get_dimensions()
                pixel_size = self.canvas.get_pixel_size()
                img_dims = QSize(canvas_dims[0] * pixel_size, canvas_dims[1] * pixel_size)
                img_pixmap = img_pixmap.scaled(img_dims, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

                # Saving the image to our canvas.
                self.canvas.set_generated_image(img_pixmap)


# app = QApplication([])
# assistant = AIAssistant(125, 400)
# assistant.show()
# app.exec()

# Importing basic widgets from PyQt6.
from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QWidget, QTextEdit, QHBoxLayout, QApplication, QListWidget, QListWidgetItem, QLabel
# Importing the necessary modules to work with canvas drawings.
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt
# Importing necessary modules for our AI assistant.
from openai import OpenAI
from dotenv import load_dotenv
import os

# Loading the environment variables.
load_dotenv()

# Our AI assistant will be implemented as a chat widget.
class AIAssistant(QWidget):

    def __init__(self, width, height):

        super().__init__()

        # Creating an instance of the OpenAI class.
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Setting the width and height of our chat widget.
        self.width = width
        self.height = height
        self.setFixedSize(self.width, self.height)

        # Using a vertical layout for our chat widget's main layout.
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Creating a list widget to display our chat messages.
        self.chat_messages = QListWidget(self)
        self.chat_messages.setAlternatingRowColors(True)
        self.chat_messages.setSpacing(2)

        # An introductory message to welcome the user.
        welcome_message = "Pixi: Welcome to Pixelate! Feel free to ask me about anything related to your art."
        welcome_item = QListWidgetItem(welcome_message)

        # Adding the welcome message to our chat messages list widget.
        self.chat_messages.addItem(welcome_item)

        # To enable line wrapping, we'll set the word wrap property to True.
        self.chat_messages.setWordWrap(True)

        # Adding our chat messages list widget to our main layout.
        main_layout.addWidget(self.chat_messages)

        # We'll specify the height of our input field.
        input_field_height = 50

        # Creating a text edit widget for our input field. This is where the user will type their messages.
        self.input_field = QTextEdit(self)
        self.input_field.setFixedHeight(input_field_height)
        self.input_field.setPlaceholderText("Type your message here...")
        main_layout.addWidget(self.input_field)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        main_layout.addWidget(self.send_button)

        self.setStyleSheet(f'''
            background-color: {QColor(240, 240, 240, 255).name()};
        ''')
        
        # Finally, we'll set the main layout of our chat widget.
        self.setLayout(main_layout)

        
    # A function to send a request to the OpenAI API and receive a response.
    def get_response(self, message):
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": message
                }
            ]
        )

        return response.choices[0].message.content
    
    # If the user presses Ctrl + Enter, we'll submit the message.
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.submit_message()
        
        return super().keyPressEvent(event)

    # A function to send a message to our AI assistant, Pixi.
    def send_message(self):
        # Getting the message from our text edit widget.
        message = self.input_field.toPlainText().strip()

        # If our message isn't empty, we'll send it to our AI assistant.
        if message:
            # Creating a list item to display our message.
            message_item = QListWidgetItem(f"You: {message}")

            # Adding the message to our chat messages list widget.
            self.chat_messages.addItem(message_item)

            # Clearing the input field.
            self.input_field.clear()

            # Getting a response from our AI assistant, Pixi.
            response = self.get_response(message)

            # Creating a list item to display Pixi's response.
            response_item = QListWidgetItem(f"Pixi: {response}")

            # Adding Pixi's response to our chat messages list widget.
            self.chat_messages.addItem(response_item)

    # A function to create a list item for our chat messages list widget.
    def create_list_item(self, message):

        # Creating an empty list item.
        list_item = QListWidgetItem(self.chat_messages)

        # A widget to hold our message.
        message_widget = QWidget()

        # Using a horizontal layout for our message widget.
        message_layout = QHBoxLayout()

        # Creating a label to display our message.
        message_label = QLabel(message)
        message_label.setWordWrap(True)

        # Adding the label to our message layout.
        message_layout.addWidget(message_label)

        # Setting the layout of our message widget.
        message_widget.setLayout(message_layout)

        # Setting the widget of our list item.
        list_item.setSizeHint(message_widget.sizeHint())

        self.chat_messages.addItem(list_item)
        self.chat_messages.setItemWidget(list_item, message_widget)

    
# app = QApplication([])
# window = AIAssistant(125, 400)
# window.show()
# app.exec()

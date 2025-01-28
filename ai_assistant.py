# Importing basic widgets from PyQt6.
from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QWidget, QTextEdit, QHBoxLayout
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

        # Creating a text box for our chat widget.
        self.text_box = QTextEdit(self)

        # Enabling line wrapping.
        self.text_box.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)

        # Our initial welcome message.
        initial_message = "Welcome to Pixelate! Feel free to ask me about anything related to your art."
        self.text_box.setPlaceholderText(initial_message)

        self.text_box.setStyleSheet(f'''
            background-color: {QColor(240, 240, 240, 255).name()};
            border: 1px solid black;
        ''')

        # Adding the text box to our main layout.
        main_layout.addWidget(self.text_box)

        # Our submit button will be used to send messages to our AI assistant.
        button_layout = QHBoxLayout()
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.submit_message)

        self.submit_button.setStyleSheet(f'''
            background-color: {QColor(240, 240, 240, 255).name()};
            border: 1px solid black;
        ''')

        # Our clear button will be used to clear the chat.
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear)

        self.clear_button.setStyleSheet(f'''
            background-color: {QColor(240, 240, 240, 255).name()};
            border: 1px solid black;
        ''')

        # Adding our buttons to the button layout.
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.submit_button)

        # Adding our button layout to our main layout.
        main_layout.addLayout(button_layout)

        # Finally, we'll set the main layout of our chat widget.
        self.setLayout(main_layout)

    # A function to clear the chat.
    def clear(self):
        self.text_box.clear()
        self.text_box.setPlaceholderText("Feel free to ask me about anything related to your art!")
        
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

    # A function to submit a message.
    def submit_message(self):
        message = self.text_box.toPlainText()
        response = self.get_response(message)
        self.text_box.append(f"\nPixAI: {response}\n\n")

    

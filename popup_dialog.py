from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QDialog, QPushButton, QTextEdit, QLabel, QApplication
from PyQt6.QtGui import QColor, QGuiApplication
from PyQt6.QtCore import Qt
import re
import ast

class PopUpDialog(QDialog):

    def __init__(self, ai_assistant):

        super().__init__()

        # Storing a reference to our AI assistant.
        self.ai_assistant = ai_assistant

        self.setWindowTitle("Pixi - AI Assistant")
        self.setGeometry(0, 0, 300, 200)
        
        # Creating a vertical layout for our dialog.
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Creating a label to display the prompt.
        self.prompt = QLabel("Describe the image that you'd like to generate.", self)
        self.prompt.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Adding some styling to our prompt.
        self.prompt.setStyleSheet(self.get_label_style())
        layout.addWidget(self.prompt)

        # Creating a text edit widget for the user to input their description.
        self.description = QTextEdit(self)
        self.description.setPlaceholderText("Enter your description here...")
        # Adding some styling to our text edit widget.
        self.description.setStyleSheet(self.get_text_edit_style())
        layout.addWidget(self.description)

        # Adding a generate button to our dialog.
        self.generate_button = QPushButton("Generate", self)
        self.generate_button.setToolTip("Generate an image based on the description provided.")
        self.generate_button.clicked.connect(self.generate)

        # Adding some styling to our generate button.
        self.generate_button.setStyleSheet(self.get_button_style(type="generate"))
        layout.addWidget(self.generate_button)

        # Adding a close button to our dialog.
        self.close_button = QPushButton("Close", self)
        self.close_button.setToolTip("Close the AI assistant.")
        self.close_button.clicked.connect(self.close)

        # Adding some styling to our close button.
        self.close_button.setStyleSheet(self.get_button_style(type="close"))
        layout.addWidget(self.close_button)

        # To store the output of our image generation request.
        self.output = None

        # Setting the layout of our dialog.
        self.setLayout(layout)

    # Centering the dialog on the screen when shown.
    def showEvent(self, event):
        
        # Getting our primary screen.
        screen = QGuiApplication.primaryScreen()

        # Retrieving the dimensions of our screen.
        screen_geometry = screen.geometry()

        # Finding the center of the screen.
        center = screen_geometry.center()

        # Finding the center of our dialog popup.
        dialog_center = self.rect().center()

        # Moving the dialog to the center of the screen.
        self.move(center - dialog_center)

        super().showEvent(event)

    # A function to generate an image based on the user's description.
    def generate(self):

        # The prompt for our AI assistant.
        prompt = "Generate a dictionary of colors that best represents the following description: "
        
        # Retrieving the user's description.
        description = self.description.toPlainText().strip()

        # If the description isn't empty, we'll send a request to our AI assistant.
        if description:

            # Prefixing the user's description with the prompt.
            description = prompt + description

            # Clearing our text edit widget.
            self.description.clear()

            # Adding the user's description to our chat context.
            self.ai_assistant.chat_context.append({"role": "user", "content": description})
            
            # Getting a response from our AI assistant.
            response = self.ai_assistant.get_response()

            # Adding the AI assistant's response to our chat context.
            self.ai_assistant.chat_context.append({"role": "assistant", "content": response})

            # Our returned output should only be the portion of the response with the dictionary of colors.
            # We'll use a regular expression to extract the dictionary from the response.
            pattern = r"\{.*\}"

            # Searching for the pattern in the response. If it's found, we'll get back a match object.
            match = re.search(pattern, response)

            # If we found a match, we'll convert the matched text to a dictionary and store it.
            if match:
                try:
                    self.output = ast.literal_eval(match.group())
                except Exception as e:
                    print(f"An error occurred: {e}")
                    print("Unable to generate image.")
            
            # Closing the dialog once we've gotten a response.
            self.close()

    # A function to style our prompt label.
    def get_label_style(self):
        return '''
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2E3440;             /* Dark gray text color */
                background-color: #D8DEE9;  /* Light gray background */
                border: 2px solid #4C566A;  /* Dark gray border */
                border-radius: 10px;        /* Rounded corners */
                padding: 15px;              /* Padding inside the label */
                
            }
        '''
    
    # A function to style our text edit widget.
    def get_text_edit_style(self):
        return '''
            QTextEdit {
                font-size: 14px; 
                color: #2E3440;
                background-color: #ECEFF4; 
                border: 2px solid #4C566A;
                border-radius: 10px; 
                padding: 10px;
                selection-background-color: #5E81AC;  /* Background color of selected text */
                selection-color: #FFFFFF;             /* Text color of selected text */
            }
            QTextEdit:hover {
                border: 2px solid #5E81AC;            /* Border color on hover */
            }
        '''
    
    # A function to style our generate button.
    def get_button_style(self, type="generate"):
        if type == "generate":
            return '''
                QPushButton {
                    font-size: 14px;
                    color: #FFFFFF;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4C566A, stop:1 #2E3440);
                    border: 2px solid #2E3440;
                    border-radius: 10px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #5E81AC, stop:1 #4C566A);
                    border: 2px solid #4C566A;
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2E3440, stop:1 #5E81AC);
                    border: 2px solid #5E81AC;
                }
            ''' 
        # Styling for the close button.
        else:
            return '''
                QPushButton {
                    font-size: 14px;
                    color: #FFFFFF;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #BF616A, stop:1 #BF616A);
                    border: 2px solid #BF616A;
                    border-radius: 10px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #D08770, stop:1 #BF616A);
                    border: 2px solid #BF616A;
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #BF616A, stop:1 #D08770);
                    border: 2px solid #D08770;
                }
            '''


# app = QApplication([])
# dialog = PopUpDialog()
# dialog.show()
# app.exec()

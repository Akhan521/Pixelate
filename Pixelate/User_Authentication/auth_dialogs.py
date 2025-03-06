
# Our login dialog for user authentication.
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QListWidget, QListWidgetItem, QDialog,
                             QLineEdit, QMessageBox, QGridLayout, QScrollArea,
                             QApplication)
from PyQt6.QtGui import QPixmap, QColor, QFontDatabase, QFont
from PyQt6.QtCore import Qt

class LoginDialog(QDialog):

    def __init__(self):
        super().__init__()

        # Hiding our system taskbar and keeping our dialog on top.
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        
        # Setting up our layout.
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # Create a header label.
        self.header_label = QLabel("Gallery - Login")
        self.header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header_label.setStyleSheet(self.get_header_style())
        layout.addWidget(self.header_label)

        # Create a label for the user to enter their email.
        self.email_label = QLabel("Email:")
        self.email_input = QLineEdit()

        # Create a label for the user to enter their password.
        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()

        # Create a button to log the user in.
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.accept)

        # Create a button to register a new user.
        self.register_button = QPushButton("Register")
        self.register_button.clicked.connect(self.register)

        # Create a button to close the dialog.
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.reject)

        # A layout to hold our buttons.
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(2)
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.register_button)

        # Add all of our widgets to the layout.
        layout.addWidget(self.email_label)
        layout.addWidget(self.email_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addLayout(button_layout)
        layout.addWidget(self.close_button)
        self.setStyleSheet(self.get_style())
        self.setLayout(layout)

    # A method to switch to a registration dialog.
    def register(self):
        # Closing our login dialog and opening the registration dialog.
        self.close()
        register_dialog = RegisterDialog()
        register_dialog.exec()

    # Header styling.
    def get_header_style(self):
        return f'''
            QLabel {{
                background-color: purple;
                color: white;
                padding: 10px;
                margin: 0px;
                font-size: 20px;
            }}
            '''

    # Default styling.
    def get_style(self):
        return f'''
            QWidget {{
                background-color: lightgray;
                font-family: {self.get_font().family()};
                color: black;
            }}
            QLabel {{
                color: black;
                margin-left: 10px;
                margin-right: 10px;
                font-size: 14px;
            }}
            QLineEdit {{
                background-color: white;
                color: black;
                padding: 5px;
                margin-left: 10px;
                margin-right: 10px;
            }}
            QTextEdit {{
                background-color: white;
                color: black;
                padding: 5px;
                margin-left: 10px;
                margin-right: 10px;
            }}
            QPushButton {{
                color: black;
                background-color: white;
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

class RegisterDialog(QDialog):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Pixelate - Register")

        # Setting up our layout.
        layout = QVBoxLayout()

        # Create a label for the user to enter their username.
        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()

        # Create a label for the user to enter their email.
        self.email_label = QLabel("Email:")
        self.email_input = QLineEdit()

        # Create a label for the user to enter their password.
        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password) # Hide the password.

        # Create a button to register the user.
        self.register_button = QPushButton("Register")
        self.register_button.clicked.connect(self.accept)

        # Create a button to switch to the login dialog.
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login)

        # Add all of our widgets to the layout.
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.email_label)
        layout.addWidget(self.email_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.register_button)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    # A method to switch to a login dialog.
    def login(self):
        # Closing our registration dialog and opening the login dialog.
        self.close()
        login_dialog = LoginDialog()
        login_dialog.exec()


#Testing our login dialog.
app = QApplication([])
login_dialog = LoginDialog()
login_dialog.exec()

# Testing our registration dialog.
# app = QApplication([])
# register_dialog = RegisterDialog()
# register_dialog.exec()

# Our login dialog for user authentication.
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QListWidget, QListWidgetItem, QDialog,
                             QLineEdit, QMessageBox, QGridLayout, QScrollArea,
                             QApplication)
from PyQt6.QtGui import QPixmap, QColor
from PyQt6.QtCore import Qt

class LoginDialog(QDialog):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Pixelate - Login")
        
        # Setting up our layout.
        layout = QVBoxLayout()

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

        # Add all of our widgets to the layout.
        layout.addWidget(self.email_label)
        layout.addWidget(self.email_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        layout.addWidget(self.register_button)

        self.setLayout(layout)

    # A method to switch to a registration dialog.
    def register(self):
        # Closing our login dialog and opening the registration dialog.
        self.close()
        register_dialog = RegisterDialog()
        register_dialog.exec()

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

        self.setLayout(layout)

    # A method to switch to a login dialog.
    def login(self):
        # Closing our registration dialog and opening the login dialog.
        self.close()
        login_dialog = LoginDialog()
        login_dialog.exec()


# Testing our login dialog.
# app = QApplication([])
# login_dialog = LoginDialog()
# login_dialog.exec()

# Testing our registration dialog.
# app = QApplication([])
# register_dialog = RegisterDialog()
# register_dialog.exec()
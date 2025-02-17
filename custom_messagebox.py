# A styled, reusable message box for our application.

from PyQt6.QtWidgets import ( QApplication, QMainWindow, QHBoxLayout, 
                              QVBoxLayout, QWidget, QGraphicsScene, 
                              QGraphicsProxyWidget, QMenuBar, QMenu,
                              QFileDialog, QMessageBox, QPushButton, 
                              QLabel, QDialog, QInputDialog, QLineEdit,
                              QFormLayout, QDialogButtonBox, QStyle )

from PyQt6.QtGui import QGuiApplication, QColor, QIcon, QPixmap, QFont, QFontDatabase
from PyQt6.QtCore import Qt, QSize


class CustomMessageBox(QDialog):
        
    def __init__(self, title="Message", message="This is a message box.", type="info"):
        super().__init__()

        # Setting our dialog to be modal.
        self.setModal(True)

        # Setting our pixelated font.
        self.setFont(self.get_font())

        # Hiding our system taskbar and keeping our dialog on top.
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)

        # Creating a form layout to hold our widgets.
        layout = QFormLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setVerticalSpacing(20)

        # A custom taskbar (for styling purposes).
        taskbar = QLabel(title)
        taskbar.setAlignment(Qt.AlignmentFlag.AlignLeft)
        taskbar.setStyleSheet(self.get_taskbar_style(type = type))
        layout.addRow(taskbar)

        # An icon to display the type of message.
        icon = self.set_icon(type)

        # Creating a label to display our message.
        message_label = QLabel(message)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setWordWrap(True)
        message_label.setStyleSheet(self.get_style())
        layout.addRow(icon, message_label)

        # Creating an OK button to close the message box.
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        self.buttons.accepted.connect(self.accept)
        self.buttons.setStyleSheet(self.get_style())

        # Adding our buttons to our layout.
        layout.addRow(self.buttons)

        # Setting the default style for our message box.
        self.setStyleSheet(self.get_style(type = type))

        # Setting our layout.
        self.setLayout(layout)
        self.setFixedSize(600, 200)
        self.exec()

    # A method to set our message box's icon.
    def set_icon(self, type="info"):
        icons = {
            "info": QStyle.StandardPixmap.SP_MessageBoxInformation,
            "error": QStyle.StandardPixmap.SP_MessageBoxCritical,
            "warning": QStyle.StandardPixmap.SP_MessageBoxWarning,
            "question": QStyle.StandardPixmap.SP_MessageBoxQuestion
        }

        icon = QLabel()
        # Get the standard icon for the message box and set it as the pixmap for our label.
        icon_pixmap = self.style().standardIcon(icons[type])
        icon_pixmap = icon_pixmap.pixmap(QSize(50, 50))
        icon.setPixmap(icon_pixmap)
        return icon

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
    
    # A method to get our custom style.
    def get_style(self, type="info"):

        border_color = "purple" if type == "info" else "darkred" if type == "error" or type == "warning" else "darkgreen"
        return f'''
            QDialog {{
                background-color: lightgray;
                border: 2px solid {border_color};
            }}
            QLabel {{
                color: black;
                font-family: {self.get_font().family()};
                padding: 10px;
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
    def get_taskbar_style(self, type):

        bg_color = "purple" if type == "info" else "darkred" if type == "error" or type == "warning" else "darkgreen"
        return f'''
            QLabel {{
                background-color: {bg_color};
                color: white;
                padding: 10px;
                font-family: {self.get_font().family()};
                font-size: 16px;
            }}
            '''
    
# # Creating our application.
# app = QApplication([])
# # Creating our message box.
# message_box = CustomMessageBox(title="Error", message="This is an error message.", type="error")
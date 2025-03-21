from PyQt6.QtWidgets import ( QApplication, QMainWindow, QHBoxLayout, 
                              QVBoxLayout, QWidget, QGraphicsScene, 
                              QGraphicsProxyWidget, QMenuBar, QMenu,
                              QFileDialog, QMessageBox, QPushButton, 
                              QLabel, QDialog, QInputDialog, QLineEdit,
                              QFormLayout, QDialogButtonBox )

from PyQt6.QtGui import QGuiApplication, QColor, QIcon, QPixmap, QFont, QFontDatabase
from PyQt6.QtCore import Qt, QSize
from custom_messagebox import CustomMessageBox

# A dialog that allows users to create a new project by specifying its dimensions.
class NewSpriteDialog(QDialog):

    def __init__(self):
        super().__init__()

        # Setting our dialog to be modal.
        self.setModal(True)

        # Setting our pixelated font.
        self.setFont(self.get_font())

        # Setting the window's size.
        self.setFixedSize(300, 150)

        # Hiding our system taskbar and keeping our dialog on top.
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)

        # Creating a form layout to hold our widgets.
        layout = QFormLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setVerticalSpacing(20)
        
        # A custom taskbar (for styling purposes).
        taskbar = QLabel("New Sprite")
        taskbar.setAlignment(Qt.AlignmentFlag.AlignLeft)
        taskbar.setStyleSheet(self.get_taskbar_style())
        layout.addRow(taskbar)

        # Adding a note that each pixel box will be 15x15 pixels.
        note = QLabel("Note: Boxes are 15x15 pixels wide.")
        note.setStyleSheet(self.get_default_style())
        note.setWordWrap(True)
        layout.addRow(note)

        # Creating a label and input for the width.
        width_label = QLabel("Width:")
        width_label.setStyleSheet(self.get_default_style())
        self.width_input = QLineEdit(self)
        self.width_input.setStyleSheet(self.get_default_style())
        self.width_input.setPlaceholderText("In pixel boxes")
        layout.addRow(width_label, self.width_input)
        
        # Creating a label and input for the height.
        height_label = QLabel("Height:")
        height_label.setStyleSheet(self.get_default_style())
        self.height_input = QLineEdit(self)
        self.height_input.setStyleSheet(self.get_default_style())
        self.height_input.setPlaceholderText("In pixel boxes")
        layout.addRow(height_label, self.height_input)

        # Creating a button box to hold our buttons (OK and Cancel).
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        # If the user clicks OK, we'll accept the dialog.
        self.buttons.accepted.connect(self.accept)
        # If the user clicks Cancel, we'll reject the dialog.
        self.buttons.rejected.connect(self.reject)
        self.buttons.setStyleSheet(self.get_default_style())

        # Adding our buttons to our layout.
        layout.addRow(self.buttons)

        # Setting our style.
        self.setStyleSheet(self.get_dialog_style())

        # Setting our layout.
        self.setLayout(layout)

    # When OK is clicked, we'll accept the dialog if the dimensions are valid.
    def accept(self):
        
        # Getting the dimensions from our inputs.
        dimensions = self.get_dimensions()

        # If the dimensions are valid, we'll accept the dialog.
        if dimensions:
            self.dimensions = dimensions
            super().accept()

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
            QLineEdit {{
                background-color: white;
                color: black;
                font-family: {self.get_font().family()};
                padding: 5px;
                margin-left: -5px;
                margin-right: 10px;
            }}
            QLabel {{
                color: black;
                font-family: {self.get_font().family()};
                margin-left: 5px;
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

    # A method to get our dimensions as a tuple.
    def get_dimensions(self):

        # Defining the minimum and maximum sizes for our sprite.
        min_size = 2
        max_size = 512

        # Getting the width and height from our inputs.
        width = self.width_input.text()
        height = self.height_input.text()

        if not width or not height:
            CustomMessageBox("Warning", "Please enter both dimensions.", type="warning")
            return None
        
        try:
            width = int(width)
            height = int(height)

            if width < min_size or height < min_size:
                message = f"The minimum size for a sprite is {min_size}x{min_size}."
                CustomMessageBox("Warning", message, type="warning")
                return None
            elif width > max_size or height > max_size:
                message = f"The maximum size for a sprite is {max_size}x{max_size}."
                CustomMessageBox("Warning", message, type="warning")
                return None
            
            return (width, height)

        except Exception as e:
            CustomMessageBox("Error", f"An error occurred: {str(e)}", type="error")
            return None

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
# dialog = NewSpriteDialog()
# dialog.show()
# app.exec()
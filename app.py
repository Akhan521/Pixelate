from PyQt6.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt6.QtGui import QGuiApplication, QColor, QIcon, QPixmap, QFont, QFontDatabase
from PyQt6.QtCore import Qt, QSize
from main_window import MainWindow

# Our starting screen.
class StartScreen(QMainWindow):

    def __init__(self):

        super().__init__()

        # Setting the window title.
        self.setWindowTitle("Pixelate")

        # Our application's window will be maximized when shown. The sizes of our widgets will depend on the window's size when maximized.
        # For starters, we'll be storing the primary screen (to get its dimensions).
        self.screen = QGuiApplication.primaryScreen()
        
        # Retrieving the dimensions of our window.
        self.screen_geometry = self.screen.geometry()

        # Defining an offset for our logo, so that it doesn't take up the entire screen.
        logo_offset = 300
        logo_width = self.screen_geometry.width() - logo_offset
        logo_height = self.screen_geometry.height() - logo_offset
        logo_size = QSize(logo_width, logo_height)

        # We'll fix the width and height of our window to its maximized size (to prevent resizing).
        self.setFixedSize(self.screen_geometry.width(), self.screen_geometry.height())

        # Using a vertical layout for our screen.
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Creating a label to hold our logo.
        logo_label = QLabel(self)

        # To display our logo, we'll use a pixmap that will be placed inside our label.
        logo_pixmap = QPixmap("icons/Pixelate_Logo.png")

        # Scaling our logo pixmap, while maintaining the aspect ratio of our logo.
        logo_pixmap = logo_pixmap.scaled(logo_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        logo_label.setPixmap(logo_pixmap)

        # Adding the logo button to our layout.
        layout.addWidget(logo_label)

        # Creating a new button to start our application.
        new_button = QPushButton("NEW", self)
        new_button.setStyleSheet(self.get_button_style())
        new_button.clicked.connect(self.start)
        layout.addWidget(new_button)

        # Creating an exit button to close our application.
        exit_button = QPushButton("EXIT", self)
        exit_button.setStyleSheet(self.get_button_style())
        exit_button.clicked.connect(self.close)
        layout.addWidget(exit_button)

        # Giving our window a gray background.
        self.setStyleSheet('''
            background-color: #BBBBBB;
        ''')

        # Storing a reference to a MainWindow instance.
        self.main_window = MainWindow()

        # Creating a widget to hold our layout.
        widget = QWidget()
        widget.setLayout(layout)

        # Setting it as the central widget of our window.
        self.setCentralWidget(widget)

    # A method to start our application using the main window.
    def start(self):
        self.main_window.showMaximized()
        self.hide()

    def get_button_style(self):

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

        return f'''
            QPushButton {{
                background-color: purple;
                color: white;
                font-size: 20px;
                font-family: {pixelated_font.family()};
                padding: 10px;
                border: 2px solid white;
                border-radius: 10px;
            }}
            QPushButton:hover {{
                /* A very dark shade of purple. */
                background-color: #4B0082;
            }}
            QPushButton:pressed {{
                background-color: purple;
            }}
            '''


app = QApplication([])
window = StartScreen()
window.showMaximized()
app.exec()
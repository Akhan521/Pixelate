from PyQt6.QtWidgets import ( QApplication, QMainWindow, QHBoxLayout, 
                              QVBoxLayout, QWidget, QGraphicsScene, 
                              QGraphicsProxyWidget, QMenuBar, QMenu,
                              QFileDialog, QMessageBox, QPushButton, 
                              QLabel, QDialog, QInputDialog, QLineEdit,
                              QFormLayout )

from PyQt6.QtGui import QGuiApplication, QColor, QIcon, QPixmap, QFont, QFontDatabase
from PyQt6.QtCore import Qt, QSize, QTimer
from main_window import MainWindow
from app.canvas.new_sprite_dialog import NewSpriteDialog
from custom_messagebox import CustomMessageBox
from app.tools.validations import validate_dimensions, validate_imported_data
from gallery.gallery_manager import GalleryManager
from gallery.gallery_widget import GalleryWidget, DimmedBackdrop
from app.user_auth.auth_manager import AuthManager
from app.user_auth.auth_dialogs import LoginDialog
import ast

# Our starting screen.
class StartScreen(QMainWindow):

    def __init__(self):

        super().__init__()

        # Setting the window title.
        self.setWindowTitle("Pixelate")

        # Our application's window will be fullscreen when shown. The sizes of our widgets will depend on the window's size.
        # For starters, we'll be storing the primary screen (to get its dimensions).
        self.screen = QGuiApplication.primaryScreen()
        
        # Retrieving the dimensions of our window.
        self.screen_geometry = self.screen.geometry()

        # A dimmed backdrop to be displayed behind our login/register dialogs.
        self.dimmed_backdrop = DimmedBackdrop(self)
        self.dimmed_backdrop.hide()

        # Defining an offset for our logo, so that it doesn't take up the entire screen.
        logo_offset = 300
        logo_width = self.screen_geometry.width() - logo_offset
        logo_height = self.screen_geometry.height() - logo_offset
        logo_size = QSize(logo_width, logo_height)

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

        # Creating a gallery button to allow users to access the Pixelate gallery.
        gallery_button = QPushButton("GALLERY", self)
        gallery_button.setStyleSheet(self.get_button_style())
        gallery_button.clicked.connect(self.open_gallery)
        layout.addWidget(gallery_button)

        # Creating an open button to allow users to continue from previous projects.
        open_button = QPushButton("OPEN", self)
        open_button.setStyleSheet(self.get_button_style())
        open_button.clicked.connect(self.open)
        layout.addWidget(open_button)

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

        # Creating a widget to hold our layout.
        widget = QWidget()
        widget.setLayout(layout)

        # Setting it as the central widget of our window.
        self.setCentralWidget(widget)

    # A method to open the Pixelate gallery.
    def open_gallery(self):

        # Create an authentication manager instance.
        self.auth_manager = AuthManager()

        # Create a gallery manager instance.
        self.gallery_manager = GalleryManager(self.auth_manager)

        # Create a login dialog.
        login_dialog = LoginDialog(self.auth_manager)

        # If the user is not logged in, we'll prompt them to log in.
        if not self.auth_manager.is_logged_in():
            # Displaying the dimmed backdrop.
            self.dimmed_backdrop.show()

            # Executing the login dialog.
            logged_in = login_dialog.exec()
            if logged_in == QDialog.DialogCode.Accepted:
                # Hiding the dimmed backdrop.
                self.dimmed_backdrop.hide()

                # If the user successfully logs in, we'll open the gallery.
                self.gallery_widget = GalleryWidget(self.gallery_manager)
                self.gallery_widget.showFullScreen()
            else:
                # Hiding the dimmed backdrop.
                self.dimmed_backdrop.hide()

                # If the user canceled/closed the login dialog, we'll check to see whether they've registered + logged in.
                # The register dialog will automatically log the user in if they successfully register.
                # (i.e. if the user is logged in by this point, they've registered successfully).
                if self.auth_manager.is_logged_in():
                    self.gallery_widget = GalleryWidget(self.gallery_manager)
                    self.gallery_widget.showFullScreen()

    # A method to start our application using the main window.
    def start(self):

        # Displaying the dimmed backdrop.
        self.dimmed_backdrop.show()

        # Creating a dialog to get the dimensions of our new sprite.
        dialog = NewSpriteDialog()

        if dialog.exec() == QDialog.DialogCode.Accepted:

            # Hiding the dimmed backdrop.
            self.dimmed_backdrop.hide()

            # Getting the dimensions of our new sprite.
            dimensions = dialog.get_dimensions()

            # If the dimensions are valid, we'll start our application.
            if dimensions:

                # Creating our main window.
                self.main_window = MainWindow(dimensions)

                # Showing our main window in fullscreen.
                self.main_window.showFullScreen()

                # Closing our start screen.
                self.close()

        # Hiding the dimmed backdrop.
        self.dimmed_backdrop.hide()

    # A method to open a previous project (by loading a text file w/ our pixels data).
    def open(self):

        # Displaying the dimmed backdrop.
        self.dimmed_backdrop.show()

        # Prompting the user to select a file to open.
        filepath, _ = QFileDialog.getOpenFileName(self, "Pixelate: Open Project", "", "Pix Files (*.pix)")

        if filepath:

            dimensions = None  # To store our canvas dimensions.
            pixels = None      # To store our pixels dictionary data.

            try:

                # Reading the contents of our text file.
                with open(filepath, "r") as file:
                    # Reading the first line of the file (which should contain the dimensions of our canvas).
                    dimensions = file.readline().strip()
                    # Reading the rest of the file (which should contain our pixels dictionary).
                    pixels = file.read()

                # Parsing our canvas dimensions using the ast module. (Converting our string tuple to an actual tuple).
                dimensions = ast.literal_eval(dimensions)

                # Validating our dimensions to ensure that they're in the correct format.
                if not validate_dimensions(dimensions):
                    CustomMessageBox(title   = "ERROR: invalid/missing dimensions", 
                                     message = "The selected file is missing or has invalid dimensions.", 
                                     type    = "error")
                    self.dimmed_backdrop.hide()
                    return

                # Parsing our text file using the ast module. (Converting our string dict. to an actual dict.)
                pixels = ast.literal_eval(pixels)

                # Validating our pixels data to ensure that it's in the correct format.
                if not validate_imported_data(pixels):
                    CustomMessageBox(title   = "ERROR: invalid data format/type", 
                                     message = "The data in the selected file is not in the correct format.", 
                                     type    = "error")
                    self.dimmed_backdrop.hide()
                    return
                
                # If our dimensions and pixels data are valid, we'll set up our canvas with the imported data.
                else:
                    CustomMessageBox(title   = "Success", 
                                     message = "Project opened successfully.", 
                                     type    = "info")
                    self.dimmed_backdrop.hide()

                    # Creating our main window with the imported dimensions.
                    self.main_window = MainWindow(dimensions)

                    # Converting our pixels data to a dictionary of the form {(x,y): QColor}.
                    pixels = self.main_window.canvas.convert_to_qcolor_format(pixels)

                    # Setting the pixels data of our canvas.
                    self.main_window.canvas.update_pixels(pixels)

                    # Jumping straight to the main window.
                    self.main_window.showFullScreen()
                    
                    # Closing our start screen.
                    self.close()

            except Exception as e:
                CustomMessageBox(title   = "ERROR: failed to open project", 
                                 message = str(e), 
                                 type    = "warning")
                self.dimmed_backdrop.hide()

        # Hiding the dimmed backdrop.
        self.dimmed_backdrop.hide()

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
                background-color: #8c52ff;
                color: white;
                font-size: 20px;
                font-family: {pixelated_font.family()};
                padding: 10px;
                border: 2px solid white;
                border-radius: 10px;
            }}
            QPushButton:hover {{
                background-color: purple;
            }}
            QPushButton:pressed {{
                /* A very dark shade of purple. */
                background-color: #4B0082;
            }}
            '''
        
# Creating our application.
app = QApplication([])
window = StartScreen()
window.showFullScreen()
app.exec()
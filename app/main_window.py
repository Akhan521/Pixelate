from PyQt6.QtWidgets import ( QApplication, QMainWindow, QHBoxLayout, 
                              QVBoxLayout, QWidget, QGraphicsScene, 
                              QGraphicsProxyWidget, QMenuBar, QMenu,
                              QFileDialog, QMessageBox, QSizePolicy,
                              QWidgetAction, QLabel, QDialog )

from PyQt6.QtGui import QGuiApplication, QColor, QFont, QFontDatabase, QAction, QImage, QPainter
from PyQt6.QtCore import Qt
from tools.tools import Tools
import ast

from canvas.pixelate_canvas import PixelateCanvas
from canvas.color_selection_window import ColorSelectionWindow
from canvas.zoomable_canvas_view import ZoomableCanvasView
from gallery.gallery_manager import GalleryManager
from gallery.gallery_widget import GalleryWidget, DimmedBackdrop
from gallery.upload_dialog import UploadDialog
from user_auth.auth_manager import AuthManager
from user_auth.auth_dialogs import LoginDialog
from pixi_ai.ai_assistant import AIAssistant
from custom_messagebox import CustomMessageBox
from app.tools.validations import validate_dimensions, validate_imported_data

class MainWindow(QMainWindow):
    # Our constructor will invoke QMainWindow's constructor.
    def __init__(self, dimensions):

        super().__init__()
        self.auth_manager = None    # To handle user auth for our gallery.
        self.gallery_manager = None # To handle gallery operations.
        self.gallery_widget = None  # To display our gallery.
        
        # Setting the window title.
        self.setWindowTitle("Pixelate")

        # A dimmed backdrop.
        self.dimmed_backdrop = DimmedBackdrop(self)
        self.dimmed_backdrop.hide()

        # Setting up our menu bar.
        self.init_menubar()
        
        # Our application's window will be fullscreen. The sizes of our widgets will depend on the window's size.
        # For starters, we'll be storing the primary screen (to get its dimensions).
        self.screen = QGuiApplication.primaryScreen()
        
        # Retrieving the dimensions of our window.
        self.screen_geometry = self.screen.geometry()

        # An offset for our chatbox height (to prevent the window from cutting off the chatbox).
        chatbox_height_offset = 200

        # Finally, we'll set the values of our pixel size, grid width, and grid height.
        self.pixel_size = 15
        width, height = dimensions
        self.grid_width = width
        self.grid_height = height
        
        # Using a horizontal layout for our program's main layout.
        layout = QHBoxLayout()

        # Creating a left window widget to hold our color selection window and chat widget.
        left_window = QWidget()
        # Defining an offset for our left window border (to prevent it from cutting off the color selection window).
        left_window_offset = 15

        # Using a vertical layout for our left window.
        left_layout = QVBoxLayout()
        left_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        left_layout.setSpacing(0)

        # Creating our color selection window + adding it to our layout.
        self.color_selection_window = ColorSelectionWindow(self.pixel_size, self.grid_width, self.grid_height)
        left_layout.addWidget(self.color_selection_window)
        
        # Creating our AI assistant widget + adding it to our layout. It should be as wide as our color selection window.
        chat_box_width = self.color_selection_window.width
        chat_box_height = self.screen_geometry.height() - self.color_selection_window.height - chatbox_height_offset
        self.ai_assistant = AIAssistant(chat_box_width, chat_box_height)
        left_layout.addWidget(self.ai_assistant)

        # Our left window should be as wide as our color selection window + the offset.
        left_window_width = self.color_selection_window.width + left_window_offset
        left_window_height = self.color_selection_window.height + chat_box_height + left_window_offset
        # left_window.setFixedSize(left_window_width, left_window_height)
        left_window.setFixedWidth(left_window_width)
        left_window.setStyleSheet("background-color: lightgray;")

        # Adding our left layout to our left window.
        left_window.setLayout(left_layout)

        # Adding our left window to our main layout.
        layout.addWidget(left_window)

        # Creating our canvas widget.
        self.canvas = PixelateCanvas(self.color_selection_window, self.pixel_size, self.grid_width, self.grid_height)

        # To achieve zoom functionality, we'll need the following:
        self.scene        = QGraphicsScene()       # Creating a scene to hold our canvas.
        self.proxy_widget = QGraphicsProxyWidget() # Creating a proxy widget that will be embedded in our view.
        self.proxy_widget.setWidget(self.canvas)   # Setting our canvas as the proxy widget.
        self.scene.addItem(self.proxy_widget)      # Adding the proxy widget to our scene (this embeds our canvas in the scene).

        # To finalize our zoom functionality, we'll create a view to display our scene.
        self.canvas_view = ZoomableCanvasView(self.scene, self.proxy_widget)
        layout.addWidget(self.canvas_view)

        # Storing a reference of our canvas + main window in our AI assistant.
        self.ai_assistant.set_canvas(self.canvas)
        self.ai_assistant.set_main_window(self)

        # Creating and sizing our tools window:
        tool_window_width = 300
        # The height of our tools window will be the same as our left window.
        tool_window_height = left_window_height
        self.tools = Tools(self.proxy_widget, tool_window_width, tool_window_height)
        self.canvas_view.set_tools(self.tools)
        layout.addWidget(self.tools)

        # Giving our main window a gray background.
        self.setStyleSheet(f'''
            background-color: #BBBBBB;   
        ''')

        # Creating an intermediary widget to hold our layout + setting the layout.
        window = QWidget()
        window.setLayout(layout)

        # Setting the central widget of our application.
        self.setCentralWidget(window)

    # A method to save our canvas to a text file (saving the pixels dictionary).
    def save_canvas(self):

        # Displaying our dimmed backdrop.
        self.dimmed_backdrop.show()

        # Retrieving our pixels dictionary (which contains the color of each pixel).
        # We'd like to have our dictionary in the form {(x,y): rgba_tuple}.
        pixels = self.canvas.convert_to_rgba_format()
        pixels = pixels.__str__()

        # Opening a file dialog to prompt to the user to specify where they'd like to save their work.
        filepath, _ = QFileDialog.getSaveFileName(self, "Pixelate: Save File", "", "Pix Files (*.pix)")

        if filepath:

            try:
                with open(filepath, "w") as file:
                    # Writing the dimensions of our canvas to the file.
                    file.write(f"({self.grid_width},{self.grid_height})\n")
                    # Writing the pixels dictionary to the file.
                    file.write(pixels)
                CustomMessageBox(title   = "Success", 
                                 message = "Project saved successfully.", 
                                 type    = "info")
                self.dimmed_backdrop.hide()

            except Exception as e:
                CustomMessageBox(title   = "ERROR: failed to save project", 
                                 message = str(e), 
                                 type    = "warning")
                self.dimmed_backdrop.hide()
                
        else:
            CustomMessageBox(title="Warning",
                            message="You have not saved your project.",
                            type="warning")
            self.dimmed_backdrop.hide()     

    # A method to import a canvas from a text file (loading the pixels dictionary).
    def import_canvas(self):

        # Displaying our dimmed backdrop.
        self.dimmed_backdrop.show()

        # Prompting the user to select a file to open.
        filepath, _ = QFileDialog.getOpenFileName(self, "Pixelate: Import Canvas", "", "Pix Files (*.pix)")

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
                
                # If our dimensions are valid, they must match the dimensions of our canvas.
                if dimensions != (self.grid_width, self.grid_height):
                    CustomMessageBox(title   = "ERROR: invalid dimensions", 
                                     message = "The dimensions of the selected file do not match the dimensions of the current canvas.", 
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
                                     message = "Project imported successfully.", 
                                     type    = "info")
                    self.dimmed_backdrop.hide()

                    # Converting our pixels data to a dictionary of the form {(x,y): QColor}.
                    pixels = self.canvas.convert_to_qcolor_format(pixels)

                    # Updating the pixels data of our canvas.
                    self.canvas.update_pixels(pixels)

            except Exception as e:
                CustomMessageBox(title   = "ERROR: failed to import project", 
                                 message = str(e), 
                                 type    = "warning")
                self.dimmed_backdrop.hide()

        # Hiding our dimmed backdrop.
        self.dimmed_backdrop.hide()

    # A method to export our canvas as a PNG image.
    def export_canvas(self):

        # Displaying our dimmed backdrop.
        self.dimmed_backdrop.show()

        file_path, _ = QFileDialog.getSaveFileName(self, "Export as PNG", "", "PNG Files (*.png)")

        # If no file path was chosen return error message.
        if not file_path:
            CustomMessageBox(title="Export Canceled", message="No save location was provided.", type="warning")
            self.dimmed_backdrop.hide()
            return

        try:
            # Create an image with the canvas size
            image = QImage(self.canvas.canvas_buffer.size(), QImage.Format.Format_ARGB32)

            # Use QPainter to render the canvas onto the image
            painter = QPainter(image)
            painter.drawPixmap(0, 0, self.canvas.canvas_buffer)
            painter.end()

            # Save the image as PNG
            if image.save(file_path, "PNG"):
                CustomMessageBox(title="Success!", message="Image exported successfully!", type="info")
            else:
                CustomMessageBox(title="Error!", message="Failed to save image.", type="error")

            # Hiding our dimmed backdrop.
            self.dimmed_backdrop.hide()

        except Exception as e:
            CustomMessageBox(title="Error!", message=f"An unexpected error occurred: {str(e)}", type="error")
            self.dimmed_backdrop.hide()

    # A method to open our gallery.
    def open_gallery(self):
        
        # If we don't have a gallery manager, we'll create one.
        if not self.gallery_manager:

            # Create an authentication manager instance.
            self.auth_manager = AuthManager()

            # Create a gallery manager instance.
            self.gallery_manager = GalleryManager(self.auth_manager)

        # If the user is not logged in, we'll prompt them to log in.
        if not self.auth_manager.is_logged_in():
            # Displaying our dimmed backdrop.
            self.dimmed_backdrop.show()

            # Prompting the user to log in.
            login_dialog = LoginDialog(self.auth_manager)
            logged_in = login_dialog.exec()
            if logged_in == QDialog.DialogCode.Accepted:
                # Hiding our dimmed backdrop.
                self.dimmed_backdrop.hide()

                # If the user successfully logs in, we'll open the gallery.
                self.gallery_widget = GalleryWidget(self.gallery_manager)
                self.gallery_widget.showFullScreen()
            else:
                # Hiding our dimmed backdrop.
                self.dimmed_backdrop.hide()

                # If the user canceled/closed the login dialog, we'll check to see whether they've registered + logged in.
                # The register dialog will automatically log the user in if they successfully register.
                # (i.e. if the user is logged in by this point, they've registered successfully).
                if self.auth_manager.is_logged_in():
                    self.gallery_widget = GalleryWidget(self.gallery_manager)
                    self.gallery_widget.showFullScreen()

        # If the user is already logged in, we'll open the gallery.
        else:
            self.gallery_widget = GalleryWidget(self.gallery_manager)
            self.gallery_widget.showFullScreen()

    # A method to upload a sprite to the gallery.
    def upload_to_gallery(self):

        # If we don't have a gallery manager, we'll create one.
        if not self.gallery_manager:

            # Create an authentication manager instance.
            self.auth_manager = AuthManager()

            # Create a gallery manager instance.
            self.gallery_manager = GalleryManager(self.auth_manager)

        # If the user is not logged in, we'll prompt them to log in.
        if not self.auth_manager.is_logged_in():
            # Displaying our dimmed backdrop.
            self.dimmed_backdrop.show()

            # Prompting the user to log in.
            login_dialog = LoginDialog(self.auth_manager)
            logged_in = login_dialog.exec()

            if logged_in == QDialog.DialogCode.Accepted:
                # If the user successfully logs in, we'll open the upload dialog.
                upload_dialog = UploadDialog(self.gallery_manager)
                upload_dialog.finished.connect(self.dimmed_backdrop.hide)
                upload_dialog.exec()

            else:
                # If the user canceled/closed the login dialog, we'll check to see whether they've registered + logged in.
                # The register dialog will automatically log the user in if they successfully register.
                # (i.e. if the user is logged in by this point, they've registered successfully).
                if self.auth_manager.is_logged_in():
                    upload_dialog = UploadDialog(self.gallery_manager)
                    upload_dialog.finished.connect(self.dimmed_backdrop.hide)
                    upload_dialog.exec()

            # Hiding our dimmed backdrop.
            self.dimmed_backdrop.hide()

        # If the user is already logged in, we'll open the upload dialog.
        else:
            # Displaying our dimmed backdrop.
            self.dimmed_backdrop.show()

            # If the user is already logged in, we'll open the upload dialog.
            upload_dialog = UploadDialog(self.gallery_manager)
            upload_dialog.finished.connect(self.dimmed_backdrop.hide)
            upload_dialog.exec()

    # A method to log out from the gallery.
    def logout_from_gallery(self):

        # Displaying our dimmed backdrop.
        self.dimmed_backdrop.show()

        # If we have an auth manager and the user is logged in, we'll log them out.
        if self.auth_manager and self.auth_manager.is_logged_in():
            self.auth_manager.logout()
            CustomMessageBox(title   = "Success", 
                             message = "You have successfully logged out from the gallery.", 
                             type    = "info")
        else:
            CustomMessageBox(title="Warning",
                            message="You are already logged out.",
                            type="warning")

        # Hiding our dimmed backdrop.
        self.dimmed_backdrop.hide()

    # A method to setup our menubar:
    def init_menubar(self):

        # Creating a menu bar for our application.
        menubar = self.menuBar()
        menubar.setStyleSheet(self.get_menubar_style())

        # Creating a file menu for our menu bar.
        file_menu = menubar.addMenu("File")

        # Creating a save action for our file menu.
        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_canvas)
        file_menu.addAction(save_action)

        # Creating an import action for our file menu.
        import_action = QAction("Import", self)
        import_action.setShortcut("Ctrl+I")
        import_action.triggered.connect(self.import_canvas)
        file_menu.addAction(import_action)

        # Creating an export action to save as PNG
        export_action = QAction("Export as PNG", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_canvas)
        file_menu.addAction(export_action) 

        # Creating a menu for our gallery.
        gallery_menu = menubar.addMenu("Gallery")

        # Creating an open gallery action for our gallery menu.
        open_gallery_action = QAction("Open Gallery", self)
        open_gallery_action.setShortcut("Ctrl+G")
        open_gallery_action.triggered.connect(self.open_gallery)
        gallery_menu.addAction(open_gallery_action)

        # Creating an upload action for our gallery menu.
        upload_action = QAction("Upload to Gallery", self)
        upload_action.setShortcut("Ctrl+U")
        upload_action.triggered.connect(self.upload_to_gallery)
        gallery_menu.addAction(upload_action)

        # Creating a logout action for our gallery menu.
        logout_action = QAction("Logout", self)
        logout_action.setShortcut("Ctrl+L")
        logout_action.triggered.connect(self.logout_from_gallery)
        gallery_menu.addAction(logout_action)

        # Adding a close button to our menu bar.
        close_action = QAction("Close", self)
        close_action.setShortcut("Ctrl+Q")
        close_action.triggered.connect(self.close)
        menubar.addAction(close_action)

    # A method to retrieve the style of our menu bar.
    def get_menubar_style(self):

        pixelated_font = QFont("Press Start 2P")
        pixelated_font.setPointSize(16)

        return f'''
            QMenuBar {{
                /* A light shade of purple. */
                background-color: #9370DB;
                color: white;
                font-family: {pixelated_font.family()};
            }}
            QMenuBar::item:selected {{
                /* A darker shade of purple. */
                background-color: #6A5ACD;
                color: white;
            }}
            QMenuBar::item:pressed {{
                /* An even darker shade of purple. */
                background-color: #483D8B;
            }}

            QMenu {{
                background-color: lightgray;
                color: black;
                font-family: {pixelated_font.family()};
                border: 1px solid black;
            }}
            QMenu::item {{
                padding: 10px 20px;
                border-bottom: 1px solid darkgray;
            }}
            QMenu::item:selected {{
                /* A medium shade of gray. */
                background-color: #BEBEBE;
                color: black;
            }}
            QMenu::item:pressed {{
                background-color: darkgray;
            }}
        '''
        
# app = QApplication([])
# # dim = 32
# dim = 64
# window = MainWindow((dim, dim))
# window.showMaximized()
# app.exec()
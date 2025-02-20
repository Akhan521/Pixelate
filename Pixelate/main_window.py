from PyQt6.QtWidgets import ( QApplication, QMainWindow, QHBoxLayout, 
                              QVBoxLayout, QWidget, QGraphicsScene, 
                              QGraphicsProxyWidget, QMenuBar, QMenu,
                              QFileDialog, QMessageBox, QSizePolicy,
                              QWidgetAction )

from PyQt6.QtGui import QGuiApplication, QColor, QFont, QFontDatabase, QAction
from PyQt6.QtCore import Qt
from tools import Tools
import ast

from pixelate_canvas import PixelateCanvas
from color_selection_window import ColorSelectionWindow
from zoomable_canvas_view import ZoomableCanvasView
from ai_assistant import AIAssistant
from validations import validate_dimensions, validate_imported_data

class MainWindow(QMainWindow):
    # Our constructor will invoke QMainWindow's constructor.
    def __init__(self, dimensions):

        super().__init__()
        
        # Setting the window title.
        self.setWindowTitle("Pixelate")

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
        left_window.setFixedSize(left_window_width, left_window_height)
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

        # Storing a reference of our canvas in our AI assistant.
        self.ai_assistant.set_canvas(self.canvas)

        # Creating and sizing our tools window:
        tool_window_width = 300
        # The height of our tools window will be the same as our left window.
        tool_window_height = left_window_height
        self.tools = Tools(self.proxy_widget, tool_window_width, tool_window_height)
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

        # Retrieving our pixels dictionary (which contains the color of each pixel).
        # We'd like to have our dictionary in the form {(x,y): rgba_tuple}.
        pixels = self.canvas.convert_to_rgba_format()
        pixels = pixels.__str__()

        # Opening a file dialog to prompt to the user to specify where they'd like to save their work.
        filepath, _ = QFileDialog.getSaveFileName(self, "Pixelate: Save File", "", "Text Files (*.txt)")

        if filepath:

            try:
                with open(filepath, "w") as file:
                    # Writing the dimensions of our canvas to the file.
                    file.write(f"({self.grid_width},{self.grid_height})\n")
                    # Writing the pixels dictionary to the file.
                    file.write(pixels)

            except Exception as e:
                QMessageBox.warning(self, f"ERROR: failed to save file - {str(e)}")

    # A method to import a canvas from a text file (loading the pixels dictionary).
    def import_canvas(self):

        # Prompting the user to select a file to open.
        filepath, _ = QFileDialog.getOpenFileName(self, "Pixelate: Import Canvas", "", "Text Files (*.txt)")

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
                    QMessageBox.warning(self, "ERROR: invalid/missing dimensions", "The selected file is missing or has invalid dimensions.")
                    return
                
                # If our dimensions are valid, they must match the dimensions of our canvas.
                if dimensions != (self.grid_width, self.grid_height):
                    QMessageBox.warning(self, "ERROR: invalid dimensions", "The dimensions of the selected file do not match the dimensions of the current canvas.")
                    return

                # Parsing our text file using the ast module. (Converting our string dict. to an actual dict.)
                pixels = ast.literal_eval(pixels)

                # Validating our pixels data to ensure that it's in the correct format.
                if not validate_imported_data(pixels):
                    QMessageBox.warning(self, "ERROR: invalid data format/type", "The data in the selected file is not in the correct format.")
                    return
                
                # If our dimensions and pixels data are valid, we'll set up our canvas with the imported data.
                else:
                    QMessageBox.information(self, "Success", "Project imported successfully.")

                    # Converting our pixels data to a dictionary of the form {(x,y): QColor}.
                    pixels = self.canvas.convert_to_qcolor_format(pixels)

                    # Updating the pixels data of our canvas.
                    self.canvas.update_pixels(pixels)

            except Exception as e:
                QMessageBox.warning(self, f"ERROR: failed to import project", str(e))

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
                background-color: lightgray;
                color: black;
                font-family: {pixelated_font.family()};
            }}
            QMenuBar::item:selected {{
                background-color: gray;
                color: black;
            }}
            QMenuBar::item:pressed {{
                background-color: darkgray;
            }}

            QMenu {{
                background-color: lightgray;
                color: black;
                font-family: {pixelated_font.family()};
            }}
            QMenu::item:selected {{
                background-color: gray;
                color: black;
            }}
            QMenu::item:pressed {{
                background-color: darkgray;
            }}
        '''
    
app = QApplication([])
window = MainWindow((64, 64))
window.showMaximized()
app.exec()
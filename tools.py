# Importing basic widgets from PyQt6.
from PyQt6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget
# Importing the necessary modules to work with canvas drawings.
from PyQt6.QtGui import QPainter, QColor, QIcon
from PyQt6.QtCore import Qt, QSize
# Importing our canvas class.
from pixelate_canvas import PixelateCanvas
from canvas_history import CanvasHistory

class Tools(QMainWindow):
    
    # Our constructor will initialize our tools window.
    # We provide our canvas to handle canvas operations with our tools.
    def __init__(self, canvas, pixel_size=15, grid_width=32, grid_height=32):

        super().__init__()
        self.canvas = canvas

        # Fixing the size of our tools window to 100 pixels wide and the height of our canvas.
        self.setFixedSize(100, pixel_size * grid_height)

        # Setting the background color of our window to light gray.
        self.setStyleSheet("background-color: lightgray;")

        # Specifying our icons path and the size of our icons.
        self.icons_path = "icons/"
        self.icon_size = QSize(30, 30)

        # Using a vertical layout for our tools window.
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Creating our very first tool/button: the clear button.
        button = QPushButton()
        button.setStyleSheet("background-color: white;")
        button.setIcon(QIcon(self.icons_path + "clear_icon_1.png"))
        button.setIconSize(self.icon_size)

        # Connecting the button's clicked signal to a lambda function that clears the canvas.
        button.clicked.connect(self.clear_canvas)
        layout.addWidget(button)

        # Our next tool/button will be the undo button.
        button = QPushButton()
        button.setStyleSheet("background-color: white;")
        button.setIcon(QIcon(self.icons_path + "undo_icon_1.png"))
        button.setIconSize(self.icon_size)

        # Connecting the button's clicked signal to our undo method.
        button.clicked.connect(self.undo)
        layout.addWidget(button)

        # Then, we'll add a redo button to go with our undo button.
        button = QPushButton()
        button.setStyleSheet("background-color: white;")
        button.setIcon(QIcon(self.icons_path + "redo_icon_1.png"))
        button.setIconSize(self.icon_size)

        # Connecting the button's clicked signal to our redo method.
        button.clicked.connect(self.redo)
        layout.addWidget(button)

        # Our fill tool will be next.
        button = QPushButton()
        button.setStyleSheet("background-color: white;")
        button.setIcon(QIcon(self.icons_path + "fill_icon_1.png"))
        button.setIconSize(self.icon_size)

        # Connecting its signal to a function that will set the canvas's fill mode to True.
        button.clicked.connect(lambda: self.set_fill_mode(True))
        layout.addWidget(button)

        # Our pencil tool:
        button = QPushButton()
        button.setStyleSheet("background-color: white;")
        button.setIcon(QIcon(self.icons_path + "pencil.png"))

        # Connecting its signal to a function that will set the canvas's fill mode to False.
        button.clicked.connect(self.use_pencil_tool)
        button.setIconSize(self.icon_size)
        layout.addWidget(button)

        # Our cursor tool:
        button = QPushButton()
        button.setStyleSheet("background-color: white;")
        button.setIcon(QIcon(self.icons_path + "drag_icon_1.png"))
        button.setIconSize(self.icon_size)

        # Connecting its signal to a function that will set our drag state to True.
        button.clicked.connect(self.use_cursor_tool)
        layout.addWidget(button)

        # Creating an intermediary widget to hold our layout.
        window = QWidget()
        window.setLayout(layout)

        # Setting the central widget of our tools window.
        self.setCentralWidget(window)

    def clear_canvas(self):
        
        # Clearing our dictionary of pixels.
        self.canvas.pixels = {}

        # Clearing our set of preview pixels.
        self.canvas.preview_pixels.clear()

        # Redrawing a brand new canvas.
        self.canvas.update()

    def undo(self):

        # Calling the undo method of our canvas history object.
        # It will return the last state of our canvas which we'll reassign to our canvas.
        self.canvas.pixels = self.canvas.canvas_history.undo(self.canvas.pixels)
        
        # Redrawing our canvas.
        self.canvas.update()
        
    def redo(self):
        
        # Calling the redo method of our canvas history object.
        # It will return the last state of our canvas which we'll reassign to our canvas.
        self.canvas.pixels = self.canvas.canvas_history.redo(self.canvas.pixels)

        # Redrawing our canvas.
        self.canvas.update()

    def set_fill_mode(self, fill_mode):

        # Setting the fill mode of our canvas.
        self.canvas.set_fill_mode(fill_mode)

    def use_pencil_tool(self):

        # Setting the fill mode of our canvas to False.
        self.canvas.set_fill_mode(False)

        # Setting the drag state of our canvas to False.
        self.canvas.set_draggable(False)

    def use_cursor_tool(self):

        # Setting the drag state of our canvas to True.
        self.canvas.set_draggable(True)
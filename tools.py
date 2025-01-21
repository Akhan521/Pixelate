# Importing basic widgets from PyQt6.
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
# Importing the necessary modules to work with canvas drawings.
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt
# Importing our canvas class.
from pixelate_canvas import PixelateCanvas
from canvas_history import CanvasHistory

class Tools(QMainWindow):
    
    # Our constructor will initialize our tools window.
    # We provide the canvas to handle canvas operations with our tools.
    def __init__(self, canvas, pixel_size=15, grid_width=32, grid_height=32):

        super().__init__()
        self.canvas = canvas

        # Fixing the size of our tools window to 100 pixels wide and the height of our canvas.
        self.setFixedSize(100, pixel_size * grid_height)

        # Setting the background color of our window to light gray.
        self.setStyleSheet("background-color: lightgray;")

        # Using a vertical layout for our tools window.
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Creating our very first tool/button: the clear button.
        button = QPushButton("Clear")
        button.setStyleSheet("background-color: white;")

        # Connecting the button's clicked signal to a lambda function that clears the canvas.
        button.clicked.connect(lambda: self.clear_canvas(self.canvas))
        layout.addWidget(button)

        # Our next tool/button will be the undo button.
        button = QPushButton("Undo")
        button.setStyleSheet("background-color: white;")

        # Connecting the button's clicked signal to our undo method.
        button.clicked.connect(lambda: self.undo(self.canvas))
        layout.addWidget(button)

        # Then, we'll add a redo button to go with our undo button.
        button = QPushButton("Redo")
        button.setStyleSheet("background-color: white;")

        # Connecting the button's clicked signal to our redo method.
        button.clicked.connect(lambda: self.redo(self.canvas))
        layout.addWidget(button)

        # Our fill tool will be next.
        button = QPushButton("Fill")
        button.setStyleSheet("background-color: white;")

        # Connecting its signal to a function that will set the canvas's fill mode to True.
        button.clicked.connect(lambda: self.set_fill_mode(True))
        layout.addWidget(button)

        # Our pencil tool:
        button = QPushButton("Pencil")
        button.setStyleSheet("background-color: white;")

        # Connecting its signal to a function that will set the canvas's fill mode to False.
        button.clicked.connect(self.use_pencil_tool)
        layout.addWidget(button)

        # Creating an intermediary widget to hold our layout.
        window = QWidget()
        window.setLayout(layout)

        # Setting the central widget of our tools window.
        self.setCentralWidget(window)

    def clear_canvas(self, canvas):
        
        # Clearing our dictionary of pixels.
        self.canvas.pixels = {}

        # Redrawing a brand new canvas.
        self.canvas.update()

    def undo(self, canvas):

        # Calling the undo method of our canvas history object.
        # It will return the last state of our canvas which we'll reassign to our canvas.
        self.canvas.pixels = self.canvas.canvas_history.undo(self.canvas.pixels)
        
        # Redrawing our canvas.
        self.canvas.update()
        
    def redo(self, canvas):
        
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
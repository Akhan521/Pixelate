# Importing basic widgets from PyQt6.
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
# Importing the necessary modules to work with canvas drawings.
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt
# Importing our canvas class.
from pixelate_canvas import PixelateCanvas

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

        # Adding the button to our layout.
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
        
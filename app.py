import PyQt6
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QHBoxLayout, QWidget
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt
from tools import Tools
from pixelate_canvas import PixelateCanvas
from color_selection_window import ColorSelectionWindow


class MainWindow(QMainWindow):
    # Our constructor will invoke QMainWindow's constructor.
    def __init__(self):

        super().__init__()
        
        # Setting the window title and size.
        self.setWindowTitle("Pixelate")
        self.setGeometry(100, 100, 800, 600)

        # Using a horizontal layout for our program.
        layout = QHBoxLayout()

        # Creating our color selection window + adding it to our layout.
        self.color_selection_window = ColorSelectionWindow()
        layout.addWidget(self.color_selection_window)

        # Creating our canvas widget + adding it to our layout.
        self.canvas = PixelateCanvas(self.color_selection_window)
        layout.addWidget(self.canvas)

        # Creating our tools widget + adding it to our layout.
        self.tools = Tools(self.canvas)
        layout.addWidget(self.tools)

        # Creating an intermediary widget to hold our layout.
        window = QWidget()
        window.setLayout(layout)

        # Setting the central widget of our application.
        self.setCentralWidget(window)
        

# Creating the application instance.
app = QApplication([])
window = MainWindow()
window.show()
app.exec()
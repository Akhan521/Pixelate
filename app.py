from PyQt6.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QWidget, QGraphicsScene, QGraphicsProxyWidget
from tools import Tools
from pixelate_canvas import PixelateCanvas
from color_selection_window import ColorSelectionWindow
from zoomable_canvas_view import ZoomableCanvasView


class MainWindow(QMainWindow):
    # Our constructor will invoke QMainWindow's constructor.
    def __init__(self):

        super().__init__()
        
        # Setting the window title and size.
        self.setWindowTitle("Pixelate")
        self.setMinimumSize(800, 600)

        self.pixel_size = 15
        self.grid_width = 32
        self.grid_height = 32

        # Using a horizontal layout for our program.
        layout = QHBoxLayout()

        # Creating our color selection window + adding it to our layout.
        self.color_selection_window = ColorSelectionWindow(self.pixel_size, self.grid_width, self.grid_height)
        layout.addWidget(self.color_selection_window)

        # Creating our canvas widget.
        self.canvas = PixelateCanvas(self.color_selection_window, self.pixel_size, self.grid_width, self.grid_height)

        # To achieve zoom functionality, we'll need the following:
        self.scene        = QGraphicsScene()       # Creating a scene to hold our canvas.
        self.proxy_widget = QGraphicsProxyWidget() # Creating a proxy widget that will be embedded in our view.
        self.proxy_widget.setWidget(self.canvas)   # Setting our canvas as the proxy widget.
        self.scene.addItem(self.proxy_widget)      # Adding the proxy widget to our scene (this embeds our canvas in the scene).\

        # To finalize our zoom functionality, we'll create a view to display our scene.
        self.canvas_view = ZoomableCanvasView(self.scene, self.canvas)
        layout.addWidget(self.canvas_view)

        # Creating our tools widget + adding it to our layout.
        self.tools = Tools(self.canvas, self.pixel_size, self.grid_width, self.grid_height)
        layout.addWidget(self.tools)
        
        # Creating an intermediary widget to hold our layout + setting the layout.
        window = QWidget()   
        window.setLayout(layout)

        # Setting the central widget of our application.
        self.setCentralWidget(window)
        

# Creating the application instance.
app = QApplication([])
window = MainWindow()
window.show()
app.exec()
from PyQt6.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QWidget, QGraphicsScene, QGraphicsProxyWidget
from PyQt6.QtGui import QGuiApplication, QColor
from PyQt6.QtCore import Qt
from tools import Tools
from pixelate_canvas import PixelateCanvas
from color_selection_window import ColorSelectionWindow
from zoomable_canvas_view import ZoomableCanvasView
from ai_assistant import AIAssistant

class MainWindow(QMainWindow):
    # Our constructor will invoke QMainWindow's constructor.
    def __init__(self):

        super().__init__()
        
        # Setting the window title.
        self.setWindowTitle("Pixelate")
        
        # Our application's window will be maximized when shown. The sizes of our widgets will depend on the window's size when maximized.
        # For starters, we'll be storing the primary screen (to get its dimensions).
        self.screen = QGuiApplication.primaryScreen()
        
        # Retrieving the dimensions of our window.
        self.screen_geometry = self.screen.geometry()

        # We don't want our canvas to fill the entire screen, so we'll offset the width and height using the following values.
        canvas_width_offset = 300
        canvas_height_offset = 200

        # Finally, we'll set the values of our pixel size, grid width, and grid height.
        self.pixel_size = 15
        self.grid_width = (self.screen_geometry.width() - canvas_width_offset) // self.pixel_size
        self.grid_height = (self.screen_geometry.height() - canvas_height_offset) // self.pixel_size
        # self.grid_width = 32
        # self.grid_height = 32

        # We'll fix the width and height of our window to its maximized size (to prevent resizing).
        self.setFixedSize(self.screen_geometry.width(), self.screen_geometry.height())
        
        # Using a horizontal layout for our program's main layout.
        layout = QHBoxLayout()

        # Creating a left window to hold our color selection window and chat widget.
        left_window = QWidget()
        # Defining an offset for our left window border (to prevent it from cutting off the color selection window).
        left_window_offset = 15

        # Using a vertical layout for our left window.
        left_layout = QVBoxLayout()
        left_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        left_layout.setSpacing(0)

        # Creating our color selection window + adding it to our layout.
        self.color_selection_window = ColorSelectionWindow(self.pixel_size, self.grid_width, self.grid_height)
        left_layout.addWidget(self.color_selection_window)
        
        # Creating our AI assistant widget + adding it to our layout. It should be as wide as our color selection window.
        chat_box_width = self.color_selection_window.width
        chat_box_height = (self.pixel_size * self.grid_height) - self.color_selection_window.height
        self.ai_assistant = AIAssistant(chat_box_width, chat_box_height)
        left_layout.addWidget(self.ai_assistant)

        # Our left window should be as wide as our color selection window + the offset.
        left_window_width = self.color_selection_window.width + left_window_offset
        left_window_height = self.pixel_size * self.grid_height + left_window_offset
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
        self.canvas_view = ZoomableCanvasView(self.scene, self.canvas)
        layout.addWidget(self.canvas_view)

        # Creating and sizing our tools window:
        tool_window_width = 100
        # The height of our tools window will be the same as our left window.
        tool_window_height = left_window_height
        self.tools = Tools(self.canvas, tool_window_width, tool_window_height)
        layout.addWidget(self.tools)

        # Giving our main window a gray background.
        self.setStyleSheet("background-color: #BBBBBB;")

        # Creating an intermediary widget to hold our layout + setting the layout.
        window = QWidget()
        window.setLayout(layout)

        # Setting the central widget of our application.
        self.setCentralWidget(window)
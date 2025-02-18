# Importing basic widgets from PyQt6.
from PyQt6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QApplication, QHBoxLayout
# Importing the necessary modules to work with canvas drawings.
from PyQt6.QtGui import QPainter, QColor, QIcon, QPixmap, QCursor
from PyQt6.QtCore import Qt, QSize
# Importing our canvas class.
from pixelate_canvas import PixelateCanvas
from canvas_history import CanvasHistory

class Tools(QMainWindow):
    
    # Our constructor will initialize our tools window.
    # We provide our canvas (through our proxy widget) to handle canvas operations with our tools.
    def __init__(self, proxy_widget, width, height):

        super().__init__()
        self.proxy_widget = proxy_widget
        self.canvas = self.proxy_widget.widget()
        self.width = width
        self.height = height

        # Fixing the size of our tools window.
        self.setFixedSize(self.width, self.height)

        # Setting the background color of our window to light gray.
        self.setStyleSheet("background-color: lightgray;")

        # Specifying our icons path and the size of our icons.
        self.icons_path = "icons/"
        self.icon_size = QSize(30, 30)

        # Using a vertical layout as our main layout.
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # A horizontal layout to hold the following tools: clear, undo, and redo.
        top_row_layout = QHBoxLayout()

        # Creating our very first tool/button: the clear button.
        button = QPushButton()
        button.setStyleSheet("background-color: white;")
        button.setIcon(QIcon(self.icons_path + "clear_icon.png"))
        button.setIconSize(self.icon_size)

        # Connecting the button's clicked signal to a method that clears the canvas.
        button.clicked.connect(self.clear_canvas)
        top_row_layout.addWidget(button)

        # Our next tool/button will be the undo button.
        button = QPushButton()
        button.setStyleSheet("background-color: white;")
        button.setIcon(QIcon(self.icons_path + "undo_icon.png"))
        button.setIconSize(self.icon_size)

        # Connecting the button's clicked signal to our undo method.
        button.clicked.connect(self.undo)
        top_row_layout.addWidget(button)

        # Then, we'll add a redo button to go with our undo button.
        button = QPushButton()
        button.setStyleSheet("background-color: white;")
        button.setIcon(QIcon(self.icons_path + "redo_icon.png"))
        button.setIconSize(self.icon_size)

        # Connecting the button's clicked signal to our redo method.
        button.clicked.connect(self.redo)
        top_row_layout.addWidget(button)

        # Adding our top row layout to our main layout.
        layout.addLayout(top_row_layout)

        # Our fill tool will be next.
        button = QPushButton()
        button.setStyleSheet("background-color: white;")
        button.setIcon(QIcon(self.icons_path + "fill_icon.png"))
        button.setIconSize(self.icon_size)

        # Connecting its signal to a function that will set the canvas's fill mode to True.
        button.clicked.connect(lambda: self.set_fill_mode(True))
        layout.addWidget(button)

        # Our eyedropper tool:
        button = QPushButton()
        button.setStyleSheet("background-color: white;")
        button.setIcon(QIcon(self.icons_path + "eyedropper_icon.png"))

        # Connecting its signal to a function that will set the eyedropper tool.
        button.clicked.connect(self.use_eyedropper_tool)
        button.setIconSize(self.icon_size)
        layout.addWidget(button)

        # Our cursor tool:
        button = QPushButton()
        button.setStyleSheet("background-color: white;")
        button.setIcon(QIcon(self.icons_path + "drag_icon.png"))
        button.setIconSize(self.icon_size)

        # Connecting its signal to a function that will set our drag state to True.
        button.clicked.connect(self.use_cursor_tool)
        layout.addWidget(button)

        # Our pencil tool:
        button = QPushButton()
        button.setStyleSheet("background-color: white;")
        button.setIcon(QIcon(self.icons_path + "pencil.png"))

        # Connecting its signal to a function that will allow us to draw.
        button.clicked.connect(self.use_pencil_tool)
        button.setIconSize(self.icon_size)
        layout.addWidget(button)

        # Our eraser tool:
        button = QPushButton()
        button.setStyleSheet("background-color: white;")
        button.setIcon(QIcon(self.icons_path + "eraser_icon.png"))

        # Connecting its signal to a function that will allow us to erase (drawing w/ our background color).
        button.clicked.connect(self.use_erase_tool)
        button.setIconSize(self.icon_size)
        layout.addWidget(button)

        # Our line tool:
        button = QPushButton()
        button.setStyleSheet("background-color: white;")
        button.setIcon(QIcon(self.icons_path + "line_icon.png"))
        button.setIconSize(self.icon_size)

        # Connecting its signal to a function that will set our drag state to True.
        button.clicked.connect(self.use_line_tool)
        button.setIconSize(self.icon_size)
        layout.addWidget(button)

        self.setStyleSheet("color: black;")

        # Creating an intermediary widget to hold our layout.
        window = QWidget()
        window.setLayout(layout)

        # Setting the background color of our window to light gray.
        self.setStyleSheet("background-color: lightgray;")

        # Setting the central widget of our tools window.
        self.setCentralWidget(window)

    def clear_canvas(self):

        # Saving our current canvas state to allow for undo functionality.
        self.canvas.canvas_history.save_state_and_update(self.canvas.pixels, self.canvas.generated_image)
        
        # Clearing our dictionary of pixels.
        self.canvas.pixels = {}

        # Clearing our preview pixel.
        self.canvas.preview_pixel = None

        # Clearing our generated image.
        self.canvas.generated_image = None

        # Redrawing a brand new canvas.
        self.canvas.update()

    def undo(self):

        # Calling the undo method of our canvas history object.
        # It will return the last state of our canvas which we'll update our canvas with.
        last_state = self.canvas.canvas_history.undo(self.canvas.pixels, self.canvas.generated_image)
        self.canvas.pixels, self.canvas.generated_image = last_state
        
        # Redrawing our canvas.
        self.canvas.update()
        
    def redo(self):
        
        # Calling the redo method of our canvas history object.
        # It will return the last state of our canvas which we'll update our canvas with.
        last_state = self.canvas.canvas_history.redo(self.canvas.pixels, self.canvas.generated_image)
        self.canvas.pixels, self.canvas.generated_image = last_state

        # Redrawing our canvas.
        self.canvas.update()

    def set_fill_mode(self, fill_mode):

        # Setting our cursor to be an arrow cursor.
        self.canvas.setCursor(Qt.CursorShape.ArrowCursor)

        # Setting the fill mode of our canvas.
        self.canvas.set_fill_mode(fill_mode)

        # Setting the drag state of our canvas to False.
        self.canvas.set_draggable(False)

        # Setting the eyedropper mode of our canvas to False.
        self.canvas.set_eyedropper_mode(False)

        # Setting the erase mode of our canvas to False.
        self.canvas.set_erase_mode(False)

        # Setting the line tool mode of our canvas to False.
        self.canvas.set_line_mode(False)

    def use_pencil_tool(self):

        # Setting our cursor to be an arrow cursor.
        self.canvas.setCursor(Qt.CursorShape.ArrowCursor)

        # Setting the fill mode of our canvas to False.
        self.canvas.set_fill_mode(False)

        # Setting the drag state of our canvas to False.
        self.canvas.set_draggable(False)

        #Setting eyedropper mode to False.
        self.canvas.set_eyedropper_mode(False)

        # Setting the erase mode of our canvas to False.
        self.canvas.set_erase_mode(False)

        # Setting the line tool mode of our canvas to False.
        self.canvas.set_line_mode(False)

    def use_erase_tool(self):
        
        # Setting our cursor to be an arrow cursor.
        self.canvas.setCursor(Qt.CursorShape.ArrowCursor)

        # Setting the fill mode of our canvas to False.
        self.canvas.set_fill_mode(False)

        # Setting the drag state of our canvas to False.
        self.canvas.set_draggable(False)

        # Setting eyedropper mode to False.
        self.canvas.set_eyedropper_mode(False)

        # Setting the erase mode of our canvas to True.
        self.canvas.set_erase_mode(True)

        # Setting the line tool mode of our canvas to False.
        self.canvas.set_line_mode(False)

    def use_cursor_tool(self):

        # Setting our cursor to be an open hand cursor to indicate that it's draggable.
        self.canvas.setCursor(Qt.CursorShape.OpenHandCursor)

        # Setting the fill mode of our canvas to False.
        self.canvas.set_fill_mode(False)

        # Setting the drag state of our canvas to True.
        self.canvas.set_draggable(True)

        #Setting eyedropper mode to False.
        self.canvas.set_eyedropper_mode(False)

        # Setting the erase mode of our canvas to False.
        self.canvas.set_erase_mode(False)

        # Setting the line tool mode of our canvas to False.
        self.canvas.set_line_mode(False)

    def use_eyedropper_tool(self):
        # To set our cursor as an eyedropper icon, we'll use a pixmap.
        eyedropper_pixmap = QPixmap(self.icons_path + "eyedropper_icon.png")
        # Resizing our pixmap.
        eyedropper_pixmap = eyedropper_pixmap.scaled(30, 30, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        # Finally, we'll set our cursor to the pixmap we created and adjust its hotspot (where the click is registered).
        eyedropper_cursor = QCursor(eyedropper_pixmap, 0, 30) # The hotspot is at the bottom of the cursor.
        self.canvas.setCursor(eyedropper_cursor)

        # Setting the fill mode of our canvas to False.
        self.canvas.set_fill_mode(False)

        # Setting the drag state of our canvas to False.
        self.canvas.set_draggable(False)

        # Setting the eyedropper mode of our canvas to True.
        self.canvas.set_eyedropper_mode(True)

        # Setting the erase mode of our canvas to False.
        self.canvas.set_erase_mode(False)

        # Setting the line tool mode of our canvas to False.
        self.canvas.set_line_mode(False)
        
    def use_line_tool(self):
        # Setting our cursor to be an arrow cursor.
        self.canvas.setCursor(Qt.CursorShape.ArrowCursor)

        # Setting the fill mode of our canvas to False.
        self.canvas.set_fill_mode(False)

        # Setting the drag state of our canvas to False.
        self.canvas.set_draggable(False)

        # Setting eyedropper mode to False.
        self.canvas.set_eyedropper_mode(False)

        # Setting the erase mode of our canvas to False.
        self.canvas.set_erase_mode(False)

        # Setting the line tool mode of our canvas to True.
        self.canvas.set_line_mode(True)

# app = QApplication([])
# tools = Tools(None, 300, 500)
# tools.show()
# app.exec()

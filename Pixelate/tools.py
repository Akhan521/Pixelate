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
        self.canvas       = self.proxy_widget.widget()
        self.width        = width
        self.height       = height

        # Fixing the size of our tools window.
        self.setFixedWidth(self.width)

        # Specifying our icons path and the size of our icons.
        self.icons_path = "icons/"
        self.icon_size  = QSize(30, 30)

        # To store our tool buttons (for styling purposes).
        self.tools = []
        self.active_tool = None

        # Using a vertical layout as our main layout.
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # A horizontal layout to hold the following tools: clear, undo, and redo.
        top_row_layout = QHBoxLayout()

        # Creating our very first tool/button: the clear button.
        button = QPushButton()
        button.setStyleSheet(self.get_default_button_style())
        button.setIcon(QIcon(self.icons_path + "clear_icon.png"))
        button.setIconSize(self.icon_size)

        # Connecting the button's clicked signal to a method that clears the canvas.
        button.clicked.connect(self.clear_canvas)
        top_row_layout.addWidget(button)

        # Our next tool/button will be the undo button.
        button = QPushButton()
        button.setStyleSheet(self.get_default_button_style())
        button.setIcon(QIcon(self.icons_path + "undo_icon.png"))
        button.setIconSize(self.icon_size)

        # Connecting the button's clicked signal to our undo method.
        button.clicked.connect(self.undo)
        top_row_layout.addWidget(button)

        # Then, we'll add a redo button to go with our undo button.
        button = QPushButton()
        button.setStyleSheet(self.get_default_button_style())
        button.setIcon(QIcon(self.icons_path + "redo_icon.png"))
        button.setIconSize(self.icon_size)

        # Connecting the button's clicked signal to our redo method.
        button.clicked.connect(self.redo)
        top_row_layout.addWidget(button)

        # Adding our top row layout to our main layout.
        layout.addLayout(top_row_layout)

        # Our fill tool will be next.
        button = QPushButton()
        button.setStyleSheet(self.get_default_button_style())
        button.setIcon(QIcon(self.icons_path + "fill_icon.png"))
        button.setIconSize(self.icon_size)

        # Connecting its signal to a function that will set the canvas's fill mode to True.
        button.clicked.connect(lambda: self.set_fill_mode(True))
        self.tools.append(button)
        layout.addWidget(button)

        # Our eyedropper tool:
        button = QPushButton()
        button.setStyleSheet(self.get_default_button_style())
        button.setIcon(QIcon(self.icons_path + "eyedropper_icon.png"))

        # Connecting its signal to a function that will set the eyedropper tool.
        button.clicked.connect(self.use_eyedropper_tool)
        button.setIconSize(self.icon_size)
        self.tools.append(button)
        layout.addWidget(button)

        # Our cursor tool:
        button = QPushButton()
        button.setStyleSheet(self.get_default_button_style())
        button.setIcon(QIcon(self.icons_path + "drag_icon.png"))
        button.setIconSize(self.icon_size)

        # Connecting its signal to a function that will set our drag state to True.
        button.clicked.connect(self.use_cursor_tool)
        self.tools.append(button)
        layout.addWidget(button)

        # Our pencil tool:
        button = QPushButton()
        button.setStyleSheet(self.get_active_button_style())
        button.setIcon(QIcon(self.icons_path + "pencil.png"))

        # Connecting its signal to a function that will allow us to draw.
        button.clicked.connect(self.use_pencil_tool)
        button.setIconSize(self.icon_size)
        self.tools.append(button)
        layout.addWidget(button)

        # Our eraser tool:
        button = QPushButton()
        button.setStyleSheet(self.get_default_button_style())
        button.setIcon(QIcon(self.icons_path + "eraser_icon.png"))

        # Connecting its signal to a function that will allow us to erase (drawing w/ our background color).
        button.clicked.connect(self.use_erase_tool)
        button.setIconSize(self.icon_size)
        self.tools.append(button)
        layout.addWidget(button)

        # Our line tool:
        button = QPushButton()
        button.setStyleSheet(self.get_default_button_style())
        button.setIcon(QIcon(self.icons_path + "line_icon.png"))
        button.setIconSize(self.icon_size)

        # Connecting its signal to a function that will set our line tool state to True.
        button.clicked.connect(self.use_line_tool)
        button.setIconSize(self.icon_size)
        self.tools.append(button)
        layout.addWidget(button)

        # Our square tool:
        button = QPushButton()
        button.setStyleSheet(self.get_default_button_style())
        button.setIcon(QIcon(self.icons_path + "square_icon.png"))
        button.setIconSize(self.icon_size)

        # Connecting its signal to a function that will set our drag state to True.
        button.clicked.connect(self.use_square_tool)
        button.setIconSize(self.icon_size)
        self.tools.append(button)
        layout.addWidget(button)

        # Creating an intermediary widget to hold our layout.
        window = QWidget()
        window.setLayout(layout)

        # Setting the background color of our window to light gray.
        self.setStyleSheet("background-color: lightgray; color: black;")

        # Setting the central widget of our tools window.
        self.setCentralWidget(window)

    def clear_canvas(self):

        # Saving our current canvas state to allow for undo functionality.
        self.canvas.canvas_history.save_state_and_update(self.canvas.pixels, self.canvas.canvas_buffer)
        
        # Clearing our dictionary of pixels.
        self.canvas.pixels = {}

        # Resetting our canvas buffer to an empty grid.
        self.canvas.canvas_buffer = self.canvas.grid.copy()

        # Clearing our preview pixel.
        self.canvas.preview_pixel = None

        # Clearing our generated image.
        self.canvas.generated_image = None

        # Redrawing a brand new canvas.
        self.canvas.update()

    def undo(self):

        # Calling the undo method of our canvas history object.
        # It will return the last state of our canvas which we'll update our canvas with.
        pixels, last_buffer = self.canvas.canvas_history.undo(self.canvas.pixels, self.canvas.canvas_buffer)
        self.canvas.pixels = pixels
        self.canvas.canvas_buffer = last_buffer
        
        # Redrawing our canvas.
        self.canvas.update()
        
    def redo(self):
        
        # Calling the redo method of our canvas history object.
        # It will return the last state of our canvas which we'll update our canvas with.
        pixels, last_buffer = self.canvas.canvas_history.redo(self.canvas.pixels, self.canvas.canvas_buffer)
        self.canvas.pixels = pixels
        self.canvas.canvas_buffer = last_buffer

        # Redrawing our canvas.
        self.canvas.update()

    def set_fill_mode(self, fill_mode):

        # Setting it as the active tool and updating the styles of our buttons.
        self.active_tool = self.tools[0]
        self.update_button_styles()

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

        # Setting the square tool mode of our canvas False.
        self.canvas.set_square_mode(False)

    def use_pencil_tool(self):

        # Setting it as the active tool and updating the styles of our buttons.
        self.active_tool = self.tools[3]
        self.update_button_styles()

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

        # Setting the square tool mode of our canvas False.
        self.canvas.set_square_mode(False)

    def use_erase_tool(self):

        # Setting it as the active tool and updating the styles of our buttons.
        self.active_tool = self.tools[4]
        self.update_button_styles()
        
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

        # Setting the square tool mode of our canvas False.
        self.canvas.set_square_mode(False)

    def use_cursor_tool(self):

        # Setting it as the active tool and updating the styles of our buttons.
        self.active_tool = self.tools[2]
        self.update_button_styles()

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

        # Setting the square tool mode of our canvas False.
        self.canvas.set_square_mode(False)

    def use_eyedropper_tool(self):

        # Setting it as the active tool and updating the styles of our buttons.
        self.active_tool = self.tools[1]
        self.update_button_styles()

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

        # Setting the square tool mode of our canvas False.
        self.canvas.set_square_mode(False)
        
    def use_line_tool(self):

        # Setting it as the active tool and updating the styles of our buttons.
        self.active_tool = self.tools[5]
        self.update_button_styles()

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

        # Setting the square tool mode of our canvas False.
        self.canvas.set_square_mode(False)

    def use_square_tool(self):

        # Setting it as the active tool and updating the styles of our buttons.
        self.active_tool = self.tools[6]
        self.update_button_styles()
        
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

        # Setting the line tool mode of our canvas False.
        self.canvas.set_line_mode(False)

        #Setting the square tool mode of our canvas True.
        self.canvas.set_square_mode(True)

    # Default button style.
    def get_default_button_style(self):
        return f'''
            QPushButton {{
                background-color: white;
                color: black;
                border-radius: 5px;
                padding: 5px;
            }}
            QPushButton:hover {{
                /* A medium shade of gray. */
                background-color: #BEBEBE;
            }}
            QPushButton:pressed {{
                background-color: darkgray;
            }}
        '''
    
    # Active button style.
    def get_active_button_style(self):
        return f'''
            QPushButton {{
                /* A lighter shade of purple. */
                background-color: #9370DB;
                color: white;
                padding: 5px;
                border: 2px solid white;
                border-radius: 10px;
            }}
            QPushButton:hover {{
                /* A darker shade of purple. */
                background-color: #6A5ACD;
            }}
            QPushButton:pressed {{
                /* An even darker shade of purple. */
                background-color: #483D8B;
            }}
        '''
    
    # A method to update the styles of our buttons.
    def update_button_styles(self):
        for button in self.tools:
            if button == self.active_tool:
                button.setStyleSheet(self.get_active_button_style())
            else:
                button.setStyleSheet(self.get_default_button_style())
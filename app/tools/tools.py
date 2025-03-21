# Importing basic widgets from PyQt6.
from PyQt6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QApplication, QHBoxLayout, QMenu
# Importing the necessary modules to work with canvas drawings.
from PyQt6.QtGui import QPainter, QColor, QIcon, QPixmap, QCursor, QFont
from PyQt6.QtCore import Qt, QSize, QPoint
# Importing our canvas class.
from canvas.pixelate_canvas import PixelateCanvas
from canvas.canvas_history import CanvasHistory

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
        self.active_tools = [None, None]

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

        # Our circle tool:
        button = QPushButton()
        button.setStyleSheet(self.get_default_button_style())
        button.setIcon(QIcon(self.icons_path + "circle_icon.png"))
        button.setIconSize(self.icon_size)

        # Connecting its signal to a function that will set our drag state to True.
        button.clicked.connect(self.use_circle_tool)
        button.setIconSize(self.icon_size)
        self.tools.append(button)
        layout.addWidget(button)

        # Our LMS tool:
        self.lms_button = FilterButton()
        self.lms_button.setStyleSheet(self.get_default_button_style())
        self.lms_button.setIcon(QIcon(self.icons_path + "smart_filter.png"))

        # Create a dropdown menu for the different filters
        self.lms_menu = QMenu(self)
        self.protanopia_action = self.lms_menu.addAction("Protanopia", lambda: self.use_smart_filter("Protanopia"))
        self.deuteranopia_action = self.lms_menu.addAction("Deuteranopia", lambda: self.use_smart_filter("Deuteranopia"))
        self.tritanopia_action = self.lms_menu.addAction("Tritanopia", lambda: self.use_smart_filter("Tritanopia"))

        self.protanopia_action.setCheckable(True)
        self.deuteranopia_action.setCheckable(True)
        self.tritanopia_action.setCheckable(True)

        self.lms_menu.setStyleSheet(self.get_menu_style())

        # Connect smart filter menu to the button.
        self.lms_button.clicked.connect(self.show_lms_menu)
        self.lms_button.setMenu(self.lms_menu)
        self.lms_button.setIconSize(self.icon_size)
        self.tools.append(self.lms_button)
        layout.addWidget(self.lms_button)

        # Creating an intermediary widget to hold our layout.
        window = QWidget()
        window.setLayout(layout)

        # Setting the background color of our window to light gray.
        self.setStyleSheet("background-color: lightgray; color: black;")

        # Setting the central widget of our tools window.
        self.setCentralWidget(window)

    # A method to show the LMS menu.
    def show_lms_menu(self):
        menu = self.lms_button.getMenu()
        
        # Get the lms_button's rect.
        rect = self.lms_button.rect()

        # Get the bottom right corner of the rect and map it to global coordinates.
        bottom_right = self.lms_button.mapToGlobal(rect.bottomRight())

        # Show the menu at the bottom right corner of the lms_button.
        menu_width = menu.sizeHint().width()

        # Calculate the x and y positions for the menu.
        offset = 5
        x = bottom_right.x() - menu_width - offset
        y = bottom_right.y() + offset

        # Show the menu at the calculated position.
        menu.popup(QPoint(x, y))

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
        self.active_tools[0] = self.tools[0]
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

        # Setting the circle tool mode of our canvas False.
        self.canvas.set_circle_mode(False)

    def use_pencil_tool(self):

        # Setting it as the active tool and updating the styles of our buttons.
        self.active_tools[0] = self.tools[3]
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

        # Setting the circle tool mode of our canvas False.
        self.canvas.set_circle_mode(False)

    def use_erase_tool(self):

        # Setting it as the active tool and updating the styles of our buttons.
        self.active_tools[0] = self.tools[4]
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

        # Setting the circle tool mode of our canvas False.
        self.canvas.set_circle_mode(False)

    def use_cursor_tool(self):

        # Setting it as the active tool and updating the styles of our buttons.
        self.active_tools[0] = self.tools[2]
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

        # Setting the circle tool mode of our canvas False.
        self.canvas.set_circle_mode(False)

    def use_eyedropper_tool(self):

        # Setting it as the active tool and updating the styles of our buttons.
        self.active_tools[0] = self.tools[1]
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

        # Setting the circle tool mode of our canvas False.
        self.canvas.set_circle_mode(False)
        
    def use_line_tool(self):

        # Setting it as the active tool and updating the styles of our buttons.
        self.active_tools[0] = self.tools[5]
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

        # Setting the circle tool mode of our canvas False.
        self.canvas.set_circle_mode(False)

    def use_square_tool(self):

        # Setting it as the active tool and updating the styles of our buttons.
        self.active_tools[0] = self.tools[6]
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

        # Setting the circle tool mode of our canvas False.
        self.canvas.set_circle_mode(False)

    def use_circle_tool(self):

        # Setting it as the active tool and updating the styles of our buttons.
        self.active_tools[0] = self.tools[7]
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
        self.canvas.set_square_mode(False)

        # Setting the circle tool mode of our canvas True.
        self.canvas.set_circle_mode(True)

    def use_smart_filter(self, cvd_type):
        # Setting our active filter and updating the styles of our buttons.
        self.active_tools[1] = self.tools[8]

        # Check if the filter is already active...
        if self.canvas.is_filter_on and self.canvas.filter_type == cvd_type:
            # Turn off the filter.
            self.canvas.is_filter_on = False
            self.canvas.filter_type = None
            self.canvas.restore_buffer()
            self.canvas.color_selection_window.restore_color_palette()
            self.active_tools[1] = None

            # Uncheck the action.
            if cvd_type == "Protanopia":
                self.protanopia_action.setChecked(False)
            elif cvd_type == "Deuteranopia":
                self.deuteranopia_action.setChecked(False)
            elif cvd_type == "Tritanopia":
                self.tritanopia_action.setChecked(False)

        else:
            # Apply the filter to our canvas and color palette.
            self.canvas.daltonize_canvas(cvd_type)
            self.canvas.color_selection_window.daltonize_color_palette(cvd_type)

            # Check the action and uncheck others
            if cvd_type == "Protanopia":
                self.protanopia_action.setChecked(True)
                self.deuteranopia_action.setChecked(False)
                self.tritanopia_action.setChecked(False)

            elif cvd_type == "Deuteranopia":
                self.protanopia_action.setChecked(False)
                self.deuteranopia_action.setChecked(True)
                self.tritanopia_action.setChecked(False)

            elif cvd_type == "Tritanopia":
                self.protanopia_action.setChecked(False)
                self.deuteranopia_action.setChecked(False)
                self.tritanopia_action.setChecked(True)

        # Update the canvas
        self.canvas.update()
        self.update_button_styles()

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
            QPushButton::menu-indicator {{
                subcontrol-origin: padding;
                subcontrol-position: right bottom;
                right: 5px; /* To move the arrow left/right */
                bottom: 5px; /* To move the arrow up/down */
                padding-right: 10px; /* Adds padding to the right of the arrow */
                padding-left: 5px; /* Adds padding to the left of the arrow */
                padding-bottom: 5px; /* Adds padding to the bottom of the arrow */
            }}
        '''
    
    # Active button style.
    def get_active_button_style(self):
        return f'''
            QPushButton {{
                /* A lighter shade of purple. */
                background-color: #8c52ff;
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
            QPushButton::menu-indicator {{
                subcontrol-origin: padding;
                subcontrol-position: right bottom;
                right: 5px; /* To move the arrow left/right */
                bottom: 5px; /* To move the arrow up/down */
                padding-right: 10px; /* Adds padding to the right of the arrow */
                padding-left: 5px; /* Adds padding to the left of the arrow */
                padding-bottom: 5px; /* Adds padding to the bottom of the arrow */
            }}
        '''
    
    # A method to update the styles of our buttons.
    def update_button_styles(self):
        for button in self.tools:
            if button in self.active_tools:
                button.setStyleSheet(self.get_active_button_style())
            else:
                button.setStyleSheet(self.get_default_button_style())

    # A method to retrieve the style of our menu bar.
    def get_menu_style(self):

        pixelated_font = QFont("Press Start 2P")
        pixelated_font.setPointSize(16)

        return f'''
            QMenu {{
                background-color: lightgray;
                color: black;
                font-family: {pixelated_font.family()};
                border: 1px solid black;
                min-width: 150px;
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
            QMenu::item:checked {{
                background-color: #8c52ff;
                color: white;
                font-weight: bold;
            }}
        '''

# A custom filter button for our LMS filter.
class FilterButton(QPushButton):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.menu = None

    def setMenu(self, menu):
        self.menu = menu
        super().setMenu(menu)

    def mousePressEvent(self, event):
        # Emit the clicked signal when the button is clicked; don't show the menu yet.
        self.clicked.emit()
        self.setDown(False) # Don't keep the button pressed.
        event.accept()

    def getMenu(self):
        return self.menu

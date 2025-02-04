# Importing basic widgets from PyQt6.
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QHBoxLayout, QVBoxLayout, QWidget
# Importing the necessary modules to work with canvas drawings.
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt
from color_button import ColorButton

class ColorSelectionWindow(QMainWindow):
    def __init__(self, pixel_size=15, grid_width=32, grid_height=32):

        super().__init__()

        # Size of each color button: 20x20 pixels.
        self.button_size = 20

        # Grid dimensions: 6 rows and 5 columns.
        self.rows    = 6
        self.columns = 5
        
        # Defining an offset for our main window border.
        self.window_border_offset = 25

        # Defining variables to store our primary and secondary colors.
        self.set_primary_color(QColor("black"))
        self.set_secondary_color(QColor("blue"))

        # Setting the window title and size (using the button size and grid dimensions).
        self.setWindowTitle("Color Selection")

        # Defining a list of 30 default colors to choose from.
        self.colors = [
            QColor("red"), QColor("green"), QColor("blue"),
            QColor("cyan"), QColor("magenta"), QColor("yellow"),
            QColor("black"), QColor("white"), QColor("gray"),
            QColor("darkRed"), QColor("darkGreen"), QColor("darkBlue"),
            QColor("darkCyan"), QColor("darkMagenta"), QColor("darkYellow"),
            QColor("darkGray"), QColor("lightGray"), QColor("transparent"),
            QColor("aqua"), QColor("chartreuse"), QColor("coral"),
            QColor("darkOrange"), QColor("darkViolet"), QColor("gold"),
            QColor("indigo"), QColor("khaki"), QColor("lime"),
            QColor("navy"), QColor("olive"), QColor("orange")
        ]

        # Setting the background color of our window to light gray.
        self.setStyleSheet("background-color: lightgray;")

        # Using a vertical layout for all of our widgets (our primary layout).
        main_layout = QVBoxLayout()
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(0, 0, 0, 0)
        # Using a grid layout for the color selection window: a 6x5 grid.
        grid_layout = QGridLayout()
        grid_layout.setSpacing(0)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        # Using a horizontal layout for our primary and secondary colors row.
        selected_colors_layout = QHBoxLayout()
        selected_colors_layout.setContentsMargins(0, 0, 0, 0)

        # Creating a button for each color.
        for i, color in enumerate(self.colors):
            # Creating a button w/ the given background color + a border.
            button = ColorButton(color_selection_window=self)
            button.setStyleSheet(f"background-color: {color.name()}; border: 1px solid black;")
            # Adding the button to our grid layout. We'll need to specify the row and column for each button.
            grid_layout.addWidget(button, i // self.columns, i % self.columns)
            # Fixing the size of each button.
            button.setFixedSize(self.button_size, self.button_size)
        
        # We'll then add our primary and secondary color boxes below.
        button = ColorButton(color_selection_window=self)
        button.setStyleSheet(f"background-color: {self.get_primary_color().name()}; border: 1px solid black;")
        selected_colors_layout.addWidget(button)
        button = ColorButton(color_selection_window=self)
        button.setStyleSheet(f"background-color: {self.get_secondary_color().name()}; border: 1px solid black;")
        selected_colors_layout.addWidget(button)

        # Creating an intermediary widget to hold all of our other widgets.
        window = QWidget()
        # Creating our next widget to hold our grid layout (for color selection).
        color_grid = QWidget()
        # Creating our final widget to hold our primary/secondary color boxes.
        self.selected_colors = QWidget()

        # Adding our layouts to their respective widgets.
        color_grid.setLayout(grid_layout)
        self.selected_colors.setLayout(selected_colors_layout)
        main_layout.addWidget(color_grid)
        main_layout.addWidget(self.selected_colors)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        window.setLayout(main_layout)

        # Fixing the size of our color selection grid widget and our primary/secondary color boxes.
        color_grid.setFixedSize(self.button_size * self.columns, self.button_size * self.rows)
        self.selected_colors.setFixedWidth(self.button_size * self.columns)

        # Our width will be the size of each button multiplied by the number of columns + an offset.
        # Additionally, I'll add some padding to make the window look better.
        self.width = self.button_size * self.columns + self.window_border_offset + 50
        self.height = self.button_size * (self.rows + 2) + self.window_border_offset
        self.setFixedSize(self.width, self.height)
        
        # Setting the central widget of our application.
        self.setCentralWidget(window)

    # This method will update our primary/secondary color boxes to reflect the colors we've chosen.
    # We'll be redrawing the widget to reflect these changes.
    def update_selected_colors(self):

        # Once we've chosen a color, we'll need to update the color of our primary/secondary color boxes:
        # To do this, we'll first need access to the layout of our selected colors widget.
        # Note: our selected colors widget has only 2 sub-widgets (our 2 color boxes/buttons).
        layout = self.selected_colors.layout()

        # We'll then access the primary color button.
        # The very first widget is our primary color button (at index 0).
        primary_color_button = layout.itemAt(0).widget()
        # We'll update the background color of our primary color button.
        primary_color_button.setStyleSheet(f"background-color: {self.get_primary_color().name()}; border: 1px solid black;")

        # Next, we'll do the same for our secondary color button (at index 1).
        secondary_color_button = layout.itemAt(1).widget() 
        secondary_color_button.setStyleSheet(f"background-color: {self.get_secondary_color().name()}; border: 1px solid black;")

    # The following method will return the primary color.
    def get_primary_color(self):
        return self.primary_color
    
    # The following method will return the secondary color.
    def get_secondary_color(self):
        return self.secondary_color
    
    # A setter for our primary color.
    def set_primary_color(self, color):
        self.primary_color = color

    # A setter for our secondary color.
    def set_secondary_color(self, color):
        self.secondary_color = color

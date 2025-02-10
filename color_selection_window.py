# Importing basic widgets from PyQt6.
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QHBoxLayout, QVBoxLayout, QWidget
# Importing the necessary modules to work with canvas drawings.
from PyQt6.QtGui import QPainter, QColor, QFontDatabase, QFont
from PyQt6.QtCore import Qt
from color_button import ColorButton

class ColorSelectionWindow(QMainWindow):
    def __init__(self, pixel_size=15, grid_width=32, grid_height=32):

        super().__init__()

        # Size of each color button: 20x20 pixels.
        self.button_size = 20
        self.button_border = 1 # Border size for each button (in pixels).

        # Grid dimensions: 6 rows and 5 columns.
        self.rows    = 6
        self.columns = 5
        
        # Defining offsets for our main window border.
        self.width_offset  = 50
        self.height_offset = 85

        # Defining variables to store our primary and secondary colors.
        self.set_primary_color(QColor("black"))
        self.set_secondary_color(QColor("blue"))

        # Setting the window title and size (using the button size and grid dimensions).
        self.setWindowTitle("Color Selection")

        # Our predefined color palettes (Normal, Protanopia, Deuteranopia, and Tritanopia).
        # We'll store these palettes in a dictionary; each palette will consist of 30 colors.
        self.color_palettes = {
            "Normal": [
                QColor(0, 0, 0), QColor(255, 255, 255), QColor(255, 0, 0), QColor(0, 255, 0), QColor(0, 0, 255),
                QColor(255, 255, 0), QColor(255, 0, 255), QColor(0, 255, 255), QColor(128, 0, 0), QColor(0, 128, 0),
                QColor(0, 0, 128), QColor(128, 128, 0), QColor(128, 0, 128), QColor(0, 128, 128), QColor(192, 192, 192),
                QColor(128, 128, 128), QColor(255, 128, 128), QColor(128, 255, 128), QColor(128, 128, 255), QColor(255, 255, 128),
                QColor(255, 128, 255), QColor(128, 255, 255), QColor(0, 0, 64), QColor(0, 64, 0), QColor(64, 0, 0),
                QColor(0, 64, 64), QColor(64, 0, 64), QColor(64, 64, 0), QColor(64, 64, 64), QColor(255, 255, 255)
            ],
            "Protanopia": [
                QColor(0, 0, 0), QColor(255, 255, 255), QColor(255, 0, 0), QColor(0, 255, 0), QColor(0, 0, 255),
                QColor(255, 255, 0), QColor(255, 0, 255), QColor(0, 255, 255), QColor(128, 0, 0), QColor(0, 128, 0),
                QColor(0, 0, 128), QColor(128, 128, 0), QColor(128, 0, 128), QColor(0, 128, 128), QColor(192, 192, 192),
                QColor(128, 128, 128), QColor(255, 128, 128), QColor(128, 255, 128), QColor(128, 128, 255), QColor(255, 255, 128),
                QColor(255, 128, 255), QColor(128, 255, 255), QColor(0, 0, 64), QColor(0, 64, 0), QColor(64, 0, 0),
                QColor(0, 64, 64), QColor(64, 0, 64), QColor(64, 64, 0), QColor(64, 64, 64), QColor(255, 255, 255)
            ],
            "Deuteranopia": [
                QColor(0, 0, 0), QColor(255, 255, 255), QColor(255, 0, 0), QColor(0, 255, 0), QColor(0, 0, 255),
                QColor(255, 255, 0), QColor(255, 0, 255), QColor(0, 255, 255), QColor(128, 0, 0), QColor(0, 128, 0),
                QColor(0, 0, 128), QColor(128, 128, 0), QColor(128, 0, 128), QColor(0, 128, 128), QColor(192, 192, 192),
                QColor(128, 128, 128), QColor(255, 128, 128), QColor(128, 255, 128), QColor(128, 128, 255), QColor(255, 255, 128),
                QColor(255, 128, 255), QColor(128, 255, 255), QColor(0, 0, 64), QColor(0, 64, 0), QColor(64, 0, 0),
                QColor(0, 64, 64), QColor(64, 0, 64), QColor(64, 64, 0), QColor(64, 64, 64), QColor(255, 255, 255)
            ],
            "Tritanopia": [
                QColor(0, 0, 0), QColor(255, 255, 255), QColor(255, 0, 0), QColor(0, 255, 0), QColor(0, 0, 255),
                QColor(255, 255, 0), QColor(255, 0, 255), QColor(0, 255, 255), QColor(128, 0, 0), QColor(0, 128, 0),
                QColor(0, 0, 128), QColor(128, 128, 0), QColor(128, 0, 128), QColor(0, 128, 128), QColor(192, 192, 192),
                QColor(128, 128, 128), QColor(255, 128, 128), QColor(128, 255, 128), QColor(128, 128, 255), QColor(255, 255, 128),
                QColor(255, 128, 255), QColor(128, 255, 255), QColor(0, 0, 64), QColor(0, 64, 0), QColor(64, 0, 0),
                QColor(0, 64, 64), QColor(64, 0, 64), QColor(64, 64, 0), QColor(64, 64, 64), QColor(255, 255, 255)
            ]
        }

        # Setting the background color of our window to light gray.
        self.setStyleSheet("background-color: lightgray;")

        # Using a vertical layout for all of our widgets (our primary layout).
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Using a horizontal layout for our palette selection buttons.
        palettes_layout = self.setup_palettes()
        main_layout.addLayout(palettes_layout)

        # Using a grid layout for the color selection window: a 6x5 grid.
        grid_layout = QGridLayout()

        # Using a horizontal layout for our primary and secondary colors row.
        selected_colors_layout = QHBoxLayout()

        # Creating a button for each color.
        for i, color in enumerate(self.color_palettes["Normal"]):
            # Creating a button w/ the given background color + a border.
            button = ColorButton(color_selection_window=self)
            button.setStyleSheet(f"background-color: {color.name()}; border: {self.button_border}px solid black;")
            # Adding the button to our grid layout. We'll need to specify the row and column for each button.
            grid_layout.addWidget(button, i // self.columns, i % self.columns)
            # Fixing the size of each button.
            button.setFixedSize(self.button_size - self.button_border, self.button_size - self.button_border)
        
        # We'll then add our primary and secondary color boxes below.
        button = ColorButton(color_selection_window=self)
        button.setStyleSheet(f"background-color: {self.get_primary_color().name()}; border: {self.button_border}px solid black;")
        selected_colors_layout.addWidget(button)
        button = ColorButton(color_selection_window=self)
        button.setStyleSheet(f"background-color: {self.get_secondary_color().name()}; border: {self.button_border}px solid black;")
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
        window.setLayout(main_layout)

        # Fixing the size of our color selection grid widget and our primary/secondary color boxes.
        # color_grid.setFixedSize(self.button_size * self.columns, self.button_size * self.rows)

        # Fixing the size of our window.
        self.width = self.button_size * self.columns + self.width_offset
        self.height = self.button_size * self.rows + self.height_offset
        self.setFixedSize(self.width, self.height)
        
        # Setting the central widget of our application.
        self.setCentralWidget(window)

    # A method to load our color palette. This will be used to set the colors of our color selection buttons.
    def load_palette(self, palette):

        # We'll need access to our central widget's layout (which holds our color selection widget).
        layout = self.centralWidget().layout()

        # We'll then access the grid layout of our color selection widget.
        grid_layout = layout.itemAt(1).widget().layout()

        # We'll then access each button in our grid layout and set its color to the corresponding color in our palette.
        for i, color in enumerate(self.color_palettes[palette]):
            button = grid_layout.itemAt(i).widget()
            button.setStyleSheet(f"background-color: {color.name()}; border: {self.button_border}px solid black;")

        # We'll update the selected colors to reflect the changes we've made.
        self.update_selected_colors()

    # A method to set up our palette selection buttons.
    def setup_palettes(self):
        
        # Our palette selection buttons will be stored in a horizontal layout.
        layout = QHBoxLayout()

        # We'll create a button for each palette.
        for palette in self.color_palettes.keys():
            # We'll set the text of our button to be the first letter of the palette name.
            button = QPushButton(palette[:1])
            button.clicked.connect(lambda _, palette=palette: self.load_palette(palette))
            button.setStyleSheet(self.palette_button_style())
            layout.addWidget(button)

        return layout
    
    # A method to style our palette selection buttons.
    def palette_button_style(self):

        # Setting up our pixelated font:
        font_path = "fonts/Press_Start_2P/PressStart2P-Regular.ttf"

        # Adding our pixelated font to the QFontDatabase.
        font_id = QFontDatabase.addApplicationFont(font_path)
        
        # If the font was loaded successfully, we'll use it for our button text.
        if font_id != -1:
            pixelated_font = QFont("Press Start 2P")
        else:
            # If the font wasn't loaded, we'll use the default application font.
            pixelated_font = QFont()

        return f'''
            QPushButton {{
                background-color: white;
                border: 1px solid black;
                color: black;
                font-family: {QFont("Press Start 2P").family()};
                border-radius: 5px;
                padding: 5px;
            }}
            QPushButton:hover {{
                background-color: lightgray;
            }}
            QPushButton:pressed {{
                background-color: gray;
            }}
    '''

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
        primary_color_button.setStyleSheet(f'''background-color: {self.get_primary_color().name()}; 
                                               border: {self.button_border}px solid black;''')

        # Next, we'll do the same for our secondary color button (at index 1).
        secondary_color_button = layout.itemAt(1).widget() 
        secondary_color_button.setStyleSheet(f'''background-color: {self.get_secondary_color().name()};
                                                 border: {self.button_border}px solid black;''')

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

app = QApplication([])
window = ColorSelectionWindow()
window.show()
app.exec()

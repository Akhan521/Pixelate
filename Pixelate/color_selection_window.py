# Importing basic widgets from PyQt6.
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QHBoxLayout, QVBoxLayout, QWidget, QColorDialog
# Importing the necessary modules to work with canvas drawings.
from PyQt6.QtGui import QPainter, QColor, QFontDatabase, QFont
from PyQt6.QtCore import Qt
from color_button import ColorButton

class ColorSelectionWindow(QMainWindow):
    def __init__(self, pixel_size=15, grid_width=32, grid_height=32):

        super().__init__()

        self.button_size   = 20  # Size of each color button (in pixels).
        self.button_border = 1   # Border size for each button (in pixels).

        # Grid dimensions: 6 rows and 5 columns.
        self.rows    = 6
        self.columns = 5
        
        # Defining offsets for our main window border.
        self.width_offset  = 50
        self.height_offset = 120

        # Defining variables to store our primary and secondary colors.
        self.set_primary_color(QColor("black"))
        self.set_secondary_color(QColor("white"))

        # Setting the window title and size (using the button size and grid dimensions).
        self.setWindowTitle("Color Selection")

        # Our predefined color palettes (Normal, Protanopia, Deuteranopia, and Tritanopia).
        # We'll store these palettes in a dictionary; each palette will consist of 30 colors.
        self.color_palettes = {
            "Normal": [
                QColor(0, 0, 0), QColor(255, 255, 255), QColor(255, 0, 0), QColor(0, 255, 0), QColor(0, 0, 255),
                QColor(255, 255, 0), QColor(255, 0, 255), QColor(0, 255, 255), QColor(128, 0, 0), QColor(0, 128, 0),
                QColor(0, 0, 128), QColor(128, 128, 0), QColor(128, 0, 128), QColor(0, 128, 128), QColor(192, 192, 192),
                QColor(128, 128, 128), QColor(200, 100, 100), QColor(100, 200, 100), QColor(100, 100, 200), QColor(220, 220, 100),
                QColor(220, 100, 220), QColor(100, 220, 220), QColor(50, 50, 100), QColor(50, 100, 50), QColor(100, 50, 50),
                QColor(50, 100, 100), QColor(100, 50, 100), QColor(100, 100, 50), QColor(75, 75, 75), QColor(180, 90, 90)
            ],
            "Protanopia": [
                QColor(0, 0, 0), QColor(255, 255, 255), QColor(0, 0, 255), QColor(255, 255, 0), QColor(0, 128, 255),
                QColor(0, 128, 128), QColor(255, 180, 0), QColor(0, 128, 0), QColor(180, 180, 0), QColor(90, 90, 90),
                QColor(0, 0, 128), QColor(200, 0, 200), QColor(0, 255, 255), QColor(180, 180, 180), QColor(120, 120, 120),
                QColor(255, 150, 150), QColor(120, 255, 120), QColor(120, 120, 255), QColor(255, 255, 150), QColor(255, 150, 255),
                QColor(120, 255, 255), QColor(30, 30, 100), QColor(30, 100, 30), QColor(100, 30, 30), QColor(30, 100, 100),
                QColor(100, 30, 100), QColor(100, 100, 30), QColor(75, 75, 75), QColor(160, 160, 80), QColor(80, 160, 160)
            ],
            "Deuteranopia": [
                QColor(0, 0, 0), QColor(255, 255, 255), QColor(0, 0, 255), QColor(255, 0, 0), QColor(0, 128, 255),
                QColor(0, 128, 128), QColor(255, 180, 0), QColor(90, 90, 90), QColor(180, 180, 0), QColor(100, 100, 100),
                QColor(0, 0, 128), QColor(200, 0, 200), QColor(0, 255, 255), QColor(180, 180, 180), QColor(120, 120, 120),
                QColor(255, 150, 150), QColor(120, 255, 120), QColor(120, 120, 255), QColor(255, 255, 150), QColor(255, 150, 255),
                QColor(120, 255, 255), QColor(30, 30, 100), QColor(30, 100, 30), QColor(100, 30, 30), QColor(30, 100, 100),
                QColor(100, 30, 100), QColor(100, 100, 30), QColor(75, 75, 75), QColor(160, 160, 80), QColor(80, 160, 160)
            ],
            "Tritanopia": [
                QColor(0, 0, 0), QColor(255, 255, 255), QColor(255, 0, 0), QColor(0, 255, 0), QColor(128, 0, 128),
                QColor(0, 180, 255), QColor(255, 128, 0), QColor(0, 128, 0), QColor(180, 180, 0), QColor(90, 90, 90),
                QColor(0, 0, 128), QColor(200, 0, 200), QColor(0, 255, 255), QColor(180, 180, 180), QColor(120, 120, 120),
                QColor(255, 150, 150), QColor(120, 255, 120), QColor(120, 120, 255), QColor(255, 255, 150), QColor(255, 150, 255),
                QColor(120, 255, 255), QColor(30, 30, 100), QColor(30, 100, 30), QColor(100, 30, 30), QColor(30, 100, 100),
                QColor(100, 30, 100), QColor(100, 100, 30), QColor(75, 75, 75), QColor(160, 160, 80), QColor(80, 160, 160)
            ]
        }

        # To store our palette buttons (for styling purposes).
        self.palette_buttons = []
        # To store our active palette button (to style it differently from the rest).
        self.active_palette_button = None

        # Setting the background color of our window to light gray.
        self.setStyleSheet("background-color: lightgray;")

        # Using a vertical layout for all of our widgets (our primary layout).
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Using a horizontal layout for our palette selection buttons.
        palettes_layout = self.setup_palettes()
        main_layout.addLayout(palettes_layout)

        # Adding a button to open the color dialog window (for custom colors).
        button = QPushButton("Custom")
        button.clicked.connect(self.open_color_dialog)
        button.setStyleSheet(self.palette_button_style())
        main_layout.addWidget(button)

        # Using a grid layout for the color selection window: a 6x5 grid.
        grid_layout = self.create_grid_layout()

        # Using a horizontal layout for our primary and secondary colors row.
        selected_colors_layout = QHBoxLayout()
        
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

    # A method to open the color dialog window (for custom colors).
    def open_color_dialog(self):

        # We'll create a QColorDialog widget to allow the user to select a custom color.
        color_dialog = QColorDialog()
        # We'll set the initial color of the dialog to be the primary color.
        color_dialog.setCurrentColor(self.get_primary_color())

        # If the user selects a color, we'll update our primary color to reflect this change.
        if color_dialog.exec() == QColorDialog.DialogCode.Accepted:
            self.set_primary_color(color_dialog.selectedColor())
            self.update_selected_colors()

    # A method to load our color palette. This will be used to set the colors of our color selection buttons.
    def load_palette(self, palette):

        # Setting the active palette button to the button that triggered the signal.
        self.active_palette_button = self.sender()

        # We'll style our active palette button differently from the rest.
        for button in self.palette_buttons:
            if button == self.active_palette_button:
                button.setStyleSheet(self.active_palette_button_style())
            else:
                button.setStyleSheet(self.palette_button_style())

        # We'll need access to our central widget's layout (which holds our color selection widget).
        layout = self.centralWidget().layout()

        # We'll then access the grid layout of our color selection widget.
        grid_layout = layout.itemAt(2).widget().layout()

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

            # We'll set our active palette button to be the first button in our list (Normal).
            if not self.active_palette_button:
                self.active_palette_button = button
                button.setStyleSheet(self.active_palette_button_style())
            else:
                button.setStyleSheet(self.palette_button_style())
                
            self.palette_buttons.append(button)
            layout.addWidget(button)

        return layout
    
    # A method to create and return our grid layout (using the default color palette).
    def create_grid_layout(self):

        # We'll create a grid layout to hold our color selection buttons.
        grid_layout = QGridLayout()

        # We'll create a button for each color in our default color palette.
        for i, color in enumerate(self.color_palettes["Normal"]):
            # Creating a button w/ the given background color + a border.
            button = ColorButton(color_selection_window=self)
            button.setStyleSheet(f"background-color: {color.name()}; border: {self.button_border}px solid black;")
            # Adding the button to our grid layout. We'll need to specify the row and column for each button.
            grid_layout.addWidget(button, i // self.columns, i % self.columns)
            # Fixing the size of each button.
            button.setFixedSize(self.button_size - self.button_border, self.button_size - self.button_border)
        
        return grid_layout
    
    # A method to style our active palette button.
    def active_palette_button_style(self):

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

        # Styling the button of our active palette.
        if self.active_palette_button:
            return f'''
                QPushButton {{
                    background-color: purple;
                    color: white;
                    font-family: {pixelated_font.family()};
                    padding: 10px;
                    border: 2px solid white;
                    border-radius: 10px;
                }}
                QPushButton:hover {{
                    /* A very dark shade of purple. */
                    background-color: #4B0082;
                }}
                QPushButton:pressed {{
                    background-color: purple;
                }}
            '''
    
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

        # Otherwise, we'll style the rest of our palette selection buttons differently.
        return f'''
            QPushButton {{
                background-color: white;
                border: 1px solid black;
                color: black;
                font-family: {pixelated_font.family()};
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

# app = QApplication([])
# window = ColorSelectionWindow()
# window.show()
# app.exec()

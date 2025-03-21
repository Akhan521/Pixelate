# Importing basic widgets from PyQt6.
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QHBoxLayout, QVBoxLayout, QWidget, QColorDialog, QLabel
# Importing the necessary modules to work with canvas drawings.
from PyQt6.QtGui import QPainter, QColor, QFontDatabase, QFont, QGuiApplication
from PyQt6.QtCore import Qt
from canvas.color_button import ColorButton
from canvas.color_approx_mapping import ColorApproximator
from tools.smart_filter import daltonize

class ColorSelectionWindow(QMainWindow):
    def __init__(self, pixel_size=15, grid_width=32, grid_height=32):

        super().__init__()

        self.button_size   = 20  # Size of each color button (in pixels).
        self.button_border = 1   # Border size for each button (in pixels).

        # Grid dimensions: 6 rows and 5 columns.
        self.rows    = 6
        self.columns = 5
        
        # Defining offsets for our main window border.
        self.width_offset  = 75
        self.height_offset = 150

        # Defining variables to store our primary and secondary colors.
        self.set_primary_color(QColor("black"))
        self.set_secondary_color(QColor("white"))

        # Fixing the size of our window.
        self.width = self.button_size * self.columns + self.width_offset
        self.height = self.button_size * self.rows + self.height_offset
        self.setFixedSize(self.width, self.height)

        # Our filter status.
        self.is_filter_on = False
        self.filter_type = None # The type of color vision deficiency filter to apply.

        # Our predefined color palettes (Normal, Protanopia, Deuteranopia, and Tritanopia).
        # We'll store these palettes in a dictionary; each palette will consist of 30 colors.
        self.color_palettes = {
            "Normal": [
                QColor(0, 0, 0), QColor(255, 255, 255), QColor(255, 0, 0), QColor(0, 255, 0), QColor(0, 0, 255),
                QColor(255, 255, 0), QColor(255, 0, 255), QColor(0, 255, 255), QColor(128, 0, 0), QColor(0, 128, 0),
                QColor(0, 0, 128), QColor(128, 128, 0), QColor(128, 0, 128), QColor(0, 128, 128), QColor(192, 192, 192),
                QColor(128, 128, 128), QColor(200, 100, 100), QColor(100, 200, 100), QColor(100, 100, 200), QColor(220, 220, 100),
                QColor(220, 100, 220), QColor(100, 220, 220), QColor(50, 50, 100), QColor(50, 100, 50), QColor(100, 50, 50),
                QColor(50, 100, 100), QColor(100, 50, 100), QColor(100, 100, 50), QColor(54, 69, 79), QColor(180, 90, 90)
            ],
            "Protanopia": [
                QColor(0, 0, 0), QColor(255, 255, 255), QColor(0, 0, 255), QColor(255, 255, 0), QColor(0, 128, 255),
                QColor(0, 128, 128), QColor(255, 180, 0), QColor(0, 128, 0), QColor(180, 180, 0), QColor(90, 90, 90),
                QColor(0, 0, 128), QColor(200, 0, 200), QColor(0, 255, 255), QColor(180, 180, 180), QColor(120, 120, 120),
                QColor(255, 150, 150), QColor(120, 255, 120), QColor(120, 120, 255), QColor(255, 255, 150), QColor(255, 150, 255),
                QColor(120, 255, 255), QColor(30, 30, 100), QColor(30, 100, 30), QColor(100, 30, 30), QColor(30, 100, 100),
                QColor(100, 30, 100), QColor(100, 100, 30), QColor(54, 69, 79), QColor(160, 160, 80), QColor(80, 160, 160)
            ],
            "Deuteranopia": [
                QColor(0, 0, 0), QColor(255, 255, 255), QColor(0, 0, 255), QColor(255, 0, 0), QColor(0, 128, 255),
                QColor(0, 128, 128), QColor(255, 180, 0), QColor(90, 90, 90), QColor(180, 180, 0), QColor(100, 100, 100),
                QColor(0, 0, 128), QColor(200, 0, 200), QColor(0, 255, 255), QColor(180, 180, 180), QColor(120, 120, 120),
                QColor(255, 150, 150), QColor(120, 255, 120), QColor(120, 120, 255), QColor(255, 255, 150), QColor(255, 150, 255),
                QColor(120, 255, 255), QColor(30, 30, 100), QColor(30, 100, 30), QColor(100, 30, 30), QColor(30, 100, 100),
                QColor(100, 30, 100), QColor(100, 100, 30), QColor(54, 69, 79), QColor(160, 160, 80), QColor(80, 160, 160)
            ],
            "Tritanopia": [
                QColor(0, 0, 0), QColor(255, 255, 255), QColor(255, 0, 0), QColor(0, 255, 0), QColor(128, 0, 128),
                QColor(0, 180, 255), QColor(255, 128, 0), QColor(0, 128, 0), QColor(180, 180, 0), QColor(90, 90, 90),
                QColor(0, 0, 128), QColor(200, 0, 200), QColor(0, 255, 255), QColor(180, 180, 180), QColor(120, 120, 120),
                QColor(255, 150, 150), QColor(120, 255, 120), QColor(120, 120, 255), QColor(255, 255, 150), QColor(255, 150, 255),
                QColor(120, 255, 255), QColor(30, 30, 100), QColor(30, 100, 30), QColor(100, 30, 30), QColor(30, 100, 100),
                QColor(100, 30, 100), QColor(100, 100, 30), QColor(54, 69, 79), QColor(160, 160, 80), QColor(80, 160, 160)
            ]
        }

        # Creating an instance of our color approximator class (to handle our approximation labels).
        self.color_approximator = ColorApproximator()

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
        button.setColor(self.get_primary_color().name())
        selected_colors_layout.addWidget(button)
        button = ColorButton(color_selection_window=self)
        button.setStyleSheet(f"background-color: {self.get_secondary_color().name()}; border: {self.button_border}px solid black;")
        button.setColor(self.get_secondary_color().name())
        selected_colors_layout.addWidget(button)

        # Our color approximation label which will store the name of the color closest to the selected color.
        self.color_approx_label = QLabel("Color:\nNone")
        self.color_approx_label.setFixedWidth(self.width - 20) # Account for padding.
        self.color_approx_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.color_approx_label.setStyleSheet(f'''
            font-family: "Press Start 2P";
            font-size: 12px;
            color: black;
        ''')

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
        main_layout.addWidget(self.color_approx_label)
        window.setLayout(main_layout)
        
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
            # We'll update the hexadecimal color value of our custom color button.
            button.setColor(color.name())
            # We'll update the background color of our custom color button.
            color = color if not self.is_filter_on else daltonize(color, self.filter_type)
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
            # We'll store the hexadecimal color value of our button.
            button.setColor(color.name())
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
                    /* A light shade of purple. */
                    background-color: #9370DB;
                    color: white;
                    font-family: {pixelated_font.family()};
                    padding: 10px;
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
                background-color: darkgray;
            }}
    '''

    # This method will update our primary/secondary color boxes to reflect the colors we've chosen.
    # We'll be redrawing the widget to reflect these changes.
    def update_selected_colors(self):

        # Once we've chosen a color, we'll need to update the color of our primary/secondary color boxes:
        # To do this, we'll first need access to the layout of our selected colors widget.
        # Note: our selected colors widget has only 2 sub-widgets (our 2 color boxes/buttons).
        layout = self.selected_colors.layout()

        # The very first widget is our primary color button (at index 0).
        primary_color_button = layout.itemAt(0).widget()
        primary_color = self.get_primary_color() if not self.is_filter_on else daltonize(self.get_primary_color(), self.filter_type)
        # We'll update the background color of our primary color button.
        primary_color_button.setStyleSheet(f'''background-color: {primary_color.name()}; 
                                               border: {self.button_border}px solid black;''')
        primary_color_button.setColor(self.get_primary_color().name())

        # Next, we'll do the same for our secondary color button (at index 1).
        secondary_color_button = layout.itemAt(1).widget() 
        secondary_color = self.get_secondary_color() if not self.is_filter_on else daltonize(self.get_secondary_color(), self.filter_type)
        # We'll update the background color of our secondary color button.
        secondary_color_button.setStyleSheet(f'''background-color: {secondary_color.name()};
                                                 border: {self.button_border}px solid black;''')
        secondary_color_button.setColor(self.get_secondary_color().name())

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

    # A method to set the color approximation label. Here, we provide the input color (QColor object).
    # Our color approximator will find the closest color to the input color and set the label accordingly.
    def set_color_approx_label(self, color):
        if isinstance(color, QColor):
            # Our approximator returns the name of the closest color as a string.
            closest_color = self.color_approximator.closest_color_cie76(color)
            self.color_approx_label.setText(f"Color:\n{closest_color}")
        else:
            self.color_approx_label.setText("Color:\nNone")

    # A method to daltonize our color palette.
    def daltonize_color_palette(self, cvd_type):
        self.is_filter_on = True
        self.filter_type = cvd_type
        
        # We'll need access to our central widget's layout (which holds our color selection widget).
        layout = self.centralWidget().layout()

        # We'll then access the grid layout of our color selection widget.
        grid_layout = layout.itemAt(2).widget().layout()

        # We'll then access each button in our grid layout and daltonize its color.
        for i in range(self.rows * self.columns):
            button = grid_layout.itemAt(i).widget()
            # Getting our button's color (unfiltered).
            color = QColor(button.color)
            daltonized_color = daltonize(color, cvd_type)
            button.setStyleSheet(f"background-color: {daltonized_color.name()}; border: {self.button_border}px solid black;")

        # We'll daltonize our primary and secondary colors as well.
        self.daltonize_selected_colors(cvd_type)

    def daltonize_selected_colors(self, cvd_type):
        
        # We'll access our primary and secondary color buttons and update their colors.
        selected_colors_layout = self.selected_colors.layout()
        primary_color_button = selected_colors_layout.itemAt(0).widget()
        secondary_color_button = selected_colors_layout.itemAt(1).widget()
        daltonized_primary_color = daltonize(self.get_primary_color(), cvd_type)
        daltonized_secondary_color = daltonize(self.get_secondary_color(), cvd_type)
        primary_color_button.setStyleSheet(f"background-color: {daltonized_primary_color.name()}; border: {self.button_border}px solid black;")
        secondary_color_button.setStyleSheet(f"background-color: {daltonized_secondary_color.name()}; border: {self.button_border}px solid black;")

    # A method to restore the original color palette (after daltonizing).
    def restore_color_palette(self):
        self.is_filter_on = False
        self.filter_type = None

        # We'll need access to our central widget's layout (which holds our color selection widget).
        layout = self.centralWidget().layout()

        # We'll then access the grid layout of our color selection widget.
        grid_layout = layout.itemAt(2).widget().layout()

        # Determining the active palette.
        active_palette = self.active_palette_button.text()
        active_palette = "Normal" if active_palette == "N" else "Protanopia" if active_palette == "P" else "Deuteranopia" if active_palette == "D" else "Tritanopia"

        # We'll then access each button in our grid layout and set its color to the corresponding color in our palette.
        for i, color in enumerate(self.color_palettes[active_palette]):
            button = grid_layout.itemAt(i).widget()
            button.setStyleSheet(f"background-color: {color.name()}; border: {self.button_border}px solid black;")

        # We'll update the selected colors to reflect the changes we've made.
        self.update_selected_colors()
    
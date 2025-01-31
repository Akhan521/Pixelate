# Importing basic widgets from PyQt6.
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QHBoxLayout, QVBoxLayout, QWidget
# Importing the necessary modules to work with canvas drawings.
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt

# A custom color button class that inherits from QPushButton.
class ColorButton(QPushButton):

    def __init__(self, text="", color_selection_window=None):

        super().__init__(text)

        # Storing a reference to the color selection window (to work w/ its primary and secondary colors).
        self.color_selection_window = color_selection_window

    # Overriding the mousePressEvent method to handle setting primary and secondary colors of our color selection window.
    def mousePressEvent(self, event):
        
        # Getting our mouse button's stylesheet.
        button_stylesheet = self.styleSheet()

        # Extracting the background color from the stylesheet.
        button_color = button_stylesheet.split("background-color: ")[1].split(";")[0]

        # Checking if the left mouse button was clicked.
        if event.button() == Qt.MouseButton.LeftButton:

            # Setting the primary color of our color selection window.
            self.color_selection_window.set_primary_color(QColor(button_color))

        # Checking if the right mouse button was clicked.
        elif event.button() == Qt.MouseButton.RightButton:
            
            # Setting the secondary color of our color selection window.
            self.color_selection_window.set_secondary_color(QColor(button_color))

        # Updating the color selection window's primary and secondary colors.
        self.color_selection_window.update_selected_colors()

        super().mousePressEvent(event)


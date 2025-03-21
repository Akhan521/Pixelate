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

        # Storing our color as a hexadecimal string.
        self.color = "#000000" # Default color is black.

    # Overriding the mousePressEvent method to handle setting primary and secondary colors of our color selection window.
    def mousePressEvent(self, event):
        
        # Getting our button's color (unfiltered).
        button_color = self.color

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

    # Overriding the enterEvent method to set our color selection window's approximation label.
    def enterEvent(self, event):

        # Getting our button's color (unfiltered).
        button_color = self.color

        # Setting the approximation label of our color selection window.
        self.color_selection_window.set_color_approx_label(QColor(button_color))

        super().enterEvent(event)

    # Overriding the leaveEvent method to clear our color selection window's approximation label.
    def leaveEvent(self, event):

        # Clearing the approximation label of our color selection window.
        self.color_selection_window.set_color_approx_label("None")

        super().leaveEvent(event)

    def setColor(self, color):

        # Setting our button's color as a hexadecimal string.
        self.color = color

# Importing basic widgets from PyQt6.
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
# Importing the necessary modules to work with canvas drawings.
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt
from color_selection_window import ColorSelectionWindow
from canvas_history import CanvasHistory

# Defining a custom canvas widget for Pixelate.
class PixelateCanvas(QWidget):

    # Our constructor will handle the initialization of the canvas.
    # We provide the color selection window to handle color changes.
    def __init__(self, color_selection_window, pixel_size=15, grid_width=32, grid_height=32):

        # Invoking the parent class constructor.
        super().__init__()

        # Storing the color selection window to access the chosen colors.
        self.color_selection_window = color_selection_window

        # Setting up our canvas:
        self.pixel_size = pixel_size   # This will be the size of each pixel.
        self.grid_width = grid_width   # The number of pixels wide the canvas will be.
        self.grid_height = grid_height # The number of pixels tall the canvas will be.

        # We'll also need to store the color of each pixel.
        # Our dictionary will map the (x, y) coordinates of each pixel to a color. Initially, all pixels will be white.
        self.pixels = {(x, y): QColor("white") for x in range(self.grid_width) for y in range(self.grid_height)}

        # Finally, we'll need to store copies of our canvas to implement undo/redo functionality.
        self.canvas_history = CanvasHistory()

        # Finally, we'll set the size of the canvas.
        self.setFixedSize(self.pixel_size * self.grid_width, self.pixel_size * self.grid_height)

    # Overriding the paintEvent method, which handles drawing on the canvas.
    def paintEvent(self, event):
        # Drawing our canvas.
        self.draw_canvas()
        
    # This method will draw a canvas w/ grid lines.
    # We provide a QPainter object as a parameter; it will handle all drawing operations.
    def draw_canvas(self):

        # Creating a QPainter object to draw on the canvas.
        painter = QPainter(self)

        # If our painter object is not active, we'll simply return.
        if not painter.isActive():
            return
        
        # Drawing each pixel on our canvas.
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                # We'll use the color of the pixel at (x, y). If no color is found, we'll use white as our default.
                color = self.pixels.get((x, y), QColor("white"))
                # Coloring in our pixel: We provide the x, y coordinates, the width and height of the pixel, and the color.
                painter.fillRect(x * self.pixel_size, y * self.pixel_size, self.pixel_size, self.pixel_size, color)

        # To visualize our pixels, we'll draw grid lines:
        painter.setPen(Qt.PenStyle.SolidLine)
        painter.setPen(QColor("lightgray"))

        # Drawing vertical lines.
        for x in range(self.grid_width + 1):
            # Draws a line from (x1, y1) to (x2, y2).
            painter.drawLine(x * self.pixel_size, 0, x * self.pixel_size, self.pixel_size * self.grid_height)

        # Drawing horizontal lines.
        for y in range(self.grid_height + 1):
            # Draws a line from (x1, y1) to (x2, y2).
            painter.drawLine(0, y * self.pixel_size, self.pixel_size * self.grid_width, y * self.pixel_size)

    # The following method will draw a pixel @ the given (x, y) coordinates with the given color (QColor object).
    def draw_pixel(self, x, y, color):

        # Checking whether the pixel is within the canvas bounds.
        if 0 <= x < self.grid_width and 0 <= y < self.grid_height:

            # Updating the color of the pixel at (x, y).
            self.pixels[(x, y)] = color
            # Repainting our canvas to reflect the changes.
            self.update()

    # Overriding the mousePressEvent method to draw pixels on our canvas.
    def mousePressEvent(self, event):
        # Before drawing, we'll save the current state of our canvas in the canvas history object.
        # This ensures that we can undo our strokes if needed.
        self.canvas_history.save_state(self.pixels)

        # Getting the x and y coordinates of our mouse click and converting them to pixel coordinates.
        x, y = event.pos().x(), event.pos().y()
        x = x // self.pixel_size
        y = y // self.pixel_size

        # For now, we'll draw a pixel at the given coordinates.
        self.draw_pixel(x, y, self.color_selection_window.get_primary_color())

    # Similarly, we'll override the mouseMoveEvent method to draw pixels as we drag our mouse.
    def mouseMoveEvent(self, event):

        # Getting the x and y coordinates of our mouse click and converting them to pixel coordinates.
        x, y = event.pos().x(), event.pos().y()
        x = x // self.pixel_size
        y = y // self.pixel_size
        
        # For now, we'll draw a pixel at the given coordinates.
        self.draw_pixel(x, y, self.color_selection_window.get_primary_color())

    # When we release the mouse button, we'll save the current state of our canvas.
    # This state will be stored within our canvas history object.
    def mouseReleaseEvent(self, event):
        pass

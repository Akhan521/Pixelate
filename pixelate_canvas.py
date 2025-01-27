# Importing basic widgets from PyQt6.
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
# Importing the necessary modules to work with canvas drawings.
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt, QEvent
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

        # We'll have a set of preview pixels to show the pixels we're about to draw.
        self.preview_pixels = set()

        # Finally, we'll need to store copies of our canvas to implement undo/redo functionality.
        self.canvas_history = CanvasHistory()

        # To store whether we're in fill mode (for the use of our fill tool).
        self.fill_mode = False

        # To store whether we're in eyedropper mode
        self.eyedropper_mode = False

        # Finally, we'll set the size of the canvas.
        self.setFixedSize(self.pixel_size * self.grid_width, self.pixel_size * self.grid_height)

        # To work with mouse hover events, we'll set the following attribute.
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

        # To store whether our canvas is draggable.
        self.is_draggable = False


    # Overriding the event method to handle hover events as well.
    def event(self, event):
        
        # If we're hovering over our canvas, we'll preview the pixel we're about to draw.
        if event.type() == QEvent.Type.HoverMove:

            # Getting the x and y coordinates of our mouse hover and converting them to pixel coordinates.
            x, y = event.position().x(), event.position().y()
            x = x // self.pixel_size
            y = y // self.pixel_size

            # Ensuring that our coordinates are integers.
            x, y = int(x), int(y)

            # We'll clear our preview pixels set. We're only interested in previewing the pixels we're selecting.
            self.preview_pixels.clear()

            # If we're in fill mode, we'll get the starting coordinates of our fill operation.
            if self.fill_mode:
                target_color = self.pixels.get((x, y), QColor("white"))
                self.get_fill_mode_preview_pixels(x, y, target_color)

            # If we're simply in pencil mode, we'll preview the pixel we're about to draw.
            else:
                # We'll now add the coordinates of the pixel we're hovering over to our set.
                self.preview_pixels.add((x, y))

            # Repainting our canvas to reflect the changes.
            self.update()

        # If we leave the canvas, we'll clear the preview pixels set and repaint the canvas.
        elif event.type() == QEvent.Type.HoverLeave:
            self.preview_pixels.clear()
            self.update()

        # Then, we'll handle the event as usual.
        return super().event(event)

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

        # If we have any preview pixels, we'll draw them on our canvas.
        if self.preview_pixels:
            self.preview(painter)

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

        # If our canvas is draggable, we'll return since we're not drawing.
        if self.is_draggable:
            return

        # If our eyedropper mode is enabled, return since we're not drawing.
        if self.eyedropper_mode:
            return

        # Otherwise, we'll ensure that the pixel is within bounds.
        if 0 <= x < self.grid_width and 0 <= y < self.grid_height:

            # Updating the color of the pixel at (x, y).
            self.pixels[(x, y)] = color
            # Repainting our canvas to reflect the changes.
            self.update()
    
    # This method handles drawing the preview pixels on our canvas.
    def draw_preview_pixels(self, painter, preview_color):

        # If our canvas is draggable, we'll return since we're not drawing.
        if self.is_draggable:
            return

        # If our eyedropper mode is enabled, return since we're not drawing.
        if self.eyedropper_mode:
            return

        # If our painter object is not active, we'll simply return.
        if not painter.isActive():
            return

        # For each pixel we'd like to preview, we'll draw it on our canvas.
        # Recall that preview_pixels is a set of (x, y) coordinates.
        for x, y in self.preview_pixels:
            # Drawing the preview pixels on our canvas.
            painter.fillRect(x * self.pixel_size, y * self.pixel_size, self.pixel_size, self.pixel_size, preview_color)


    # Overriding the mousePressEvent method to draw pixels on our canvas.
    def mousePressEvent(self, event):

        # Before drawing, we'll save the current state of our canvas in the canvas history object.
        # This ensures that we can undo our strokes if needed.
        self.canvas_history.save_state(self.pixels)

        # Getting the x and y coordinates of our mouse click and converting them to pixel coordinates.
        x, y = event.pos().x(), event.pos().y()
        x = x // self.pixel_size
        y = y // self.pixel_size

        # If we're in fill mode, we'll use the fill method to fill in areas.
        if self.fill_mode:
            target_color = self.pixels.get((x, y), QColor("white"))
            replacement_color = self.color_selection_window.get_primary_color()
            self.fill(x, y, target_color, replacement_color)
            return

        #If we are in eyedropper mode, we will copy the selected color onto the primary color.
        if self.eyedropper_mode:
            target_color = self.pixels.get((x, y), QColor("white"))
            self.color_selection_window.set_primary_color(target_color)
            self.color_selection_window.update_selected_colors()
            return

        # Otherwise, we'll draw a pixel at the given coordinates.
        self.draw_pixel(x, y, self.color_selection_window.get_primary_color())

    # Similarly, we'll override the mouseMoveEvent method to draw pixels as we drag our mouse.
    def mouseMoveEvent(self, event):
        
        # Getting the x and y coordinates of our mouse click and converting them to pixel coordinates.
        x, y = event.pos().x(), event.pos().y()
        x = x // self.pixel_size
        y = y // self.pixel_size
        
        # For now, we'll draw a pixel at the given coordinates.
        self.draw_pixel(x, y, self.color_selection_window.get_primary_color())

    # To set our canvas to fill mode, we'll use the following method.
    def set_fill_mode(self, fill_mode):
        self.fill_mode = fill_mode

    # To set our canvas to fill mode, we'll use the following method.
    def set_eyedropper_mode(self, eyedropper_mode):
        self.eyedropper_mode = eyedropper_mode

    # If the fill mode of our canvas is active, we'll use the following method to fill in areas.
    def fill(self, x, y, target_color, replacement_color):

        # If the pixel is out of bounds or the target and replacement colors are the same, we'll return.
        if not (0 <= x < self.grid_width and 0 <= y < self.grid_height) or target_color == replacement_color:
            return
        
        # If the color of the pixel at (x, y) is not the color we'd like to replace, we'll return.
        if self.pixels.get((x, y), QColor("white")) != target_color:
            return
        
        # Otherwise, we'll fill the pixel with the replacement color.
        self.draw_pixel(x, y, replacement_color)

        # We'll recursively fill the neighboring pixels (our 4 cardinal directions).
        self.fill(x + 1, y, target_color, replacement_color)
        self.fill(x - 1, y, target_color, replacement_color)
        self.fill(x, y + 1, target_color, replacement_color)
        self.fill(x, y - 1, target_color, replacement_color)

    # The following method will allow us to preview pixels on our canvas before drawing them.
    # As we hover over the canvas, we'll see a preview of the pixels we're about to draw.
    # We provide a QPainter object to handle all drawing operations.
    def preview(self, painter):

        # Getting our primary color (with some transparency).
        preview_color = self.color_selection_window.get_primary_color()

        # Drawing the preview pixels on our canvas.
        self.draw_preview_pixels(painter, preview_color)


    # This method will store all of the pixels that we'd be previewing in fill mode.
    # We use an iterative approach to avoid hitting the recursion limit.
    # It behaves similarly to the fill method, but this method is called as we hover over the canvas.
    # We only need to provide the starting coordinates of our fill operation and the target color.
    def get_fill_mode_preview_pixels(self, x, y, target_color):

        # Using a stack to simulate recursion.
        stack = [(x, y)]

        # As long as we have pixels to process, we'll continue.
        while stack:
            # Getting the coordinates of the pixel we'll be processing as well as its color.
            x, y = stack.pop()
            color = self.pixels.get((x, y), QColor("white"))

            ''' We'll handle our base cases first.
                    1. If the pixel is out of bounds, we'll skip it.
                    2. If the pixel is not the target color, we'll skip it.
                    (We're only interested in the pixels we're targeting.)
                    3. If the pixel is already in our preview pixels list, we'll skip it.
            '''
            if not (0 <= x < self.grid_width and 0 <= y < self.grid_height) or color != target_color:
                continue

            if (x, y) in self.preview_pixels:
                continue

            # Otherwise, we'll add this pixel to our preview pixels set.
            self.preview_pixels.add((x, y))

            # We'll now process the neighboring pixels.
            stack.append((x + 1, y))
            stack.append((x - 1, y))
            stack.append((x, y + 1))
            stack.append((x, y - 1))

    # To set the draggable state of our canvas, we'll use the following method.
    def set_draggable(self, draggable):
        self.is_draggable = draggable
        
        

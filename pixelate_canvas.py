# Importing basic widgets from PyQt6.
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
# Importing the necessary modules to work with canvas drawings.
from PyQt6.QtGui import QPainter, QColor, QPixmap
from PyQt6.QtCore import Qt, QEvent, QRect
from color_selection_window import ColorSelectionWindow
from canvas_history import CanvasHistory
from collections import deque

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
        # Our dictionary will map the (x, y) coordinates of each pixel to a color. By default, all pixels are white.
        self.pixels = {}

        # We'll have a preview pixel to show the pixel we're about to draw. (The (x, y) coordinates of the pixel.)
        self.preview_pixel = None

        # We'll need to store copies of our pixel colors to implement undo/redo functionality.
        self.canvas_history = CanvasHistory()

        # To store whether we're in fill mode (for the use of our fill tool).
        self.fill_mode = False

        # To store whether we're in eyedropper mode
        self.eyedropper_mode = False

        # To store whether our canvas is draggable.
        self.is_draggable = False

        # Finally, we'll set the size of the canvas.
        self.setFixedSize(self.pixel_size * self.grid_width, self.pixel_size * self.grid_height)

        # To work with mouse hover events, we'll set the following attribute.
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

        # Finally, we'll have an underlying grid that will serve as our base layer.
        # This grid will be drawn only once. All subsequent drawings will be on top of this grid.
        self.init_grid()

        # When in fill mode, we'll need to keep track of visited pixels to avoid redundant operations.
        self.visited = set()

    # This method will create a grid for our canvas. It will be implemented as a QPixmap object.
    # We'll initialize the grid with a white background and draw grid lines on top of it.
    def init_grid(self):

        # Creating a QPixmap object to store our grid. (This will serve as our canvas's base layer.)
        self.grid = QPixmap(self.pixel_size * self.grid_width, self.pixel_size * self.grid_height)

        # Drawing grid lines on our QPixmap object.
        painter = QPainter(self.grid)
        painter.setPen(Qt.PenStyle.SolidLine)
        # Setting our pen color to a more transparent black.
        painter.setPen(QColor(0, 0, 0, 50))

        # First, we'll fill our grid with a light, transparent gray background.
        self.grid.fill(QColor(240, 240, 240, 255))

        # Drawing vertical lines.
        for x in range(self.grid_width + 1):
            # Draws a line from (x1, y1) to (x2, y2).
            painter.drawLine(x * self.pixel_size, 0, x * self.pixel_size, self.pixel_size * self.grid_height)

        # Drawing horizontal lines.
        for y in range(self.grid_height + 1):
            # Draws a line from (x1, y1) to (x2, y2).
            painter.drawLine(0, y * self.pixel_size, self.pixel_size * self.grid_width, y * self.pixel_size)

        painter.end()

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

            # We'll clear our preview pixel. We're only interested in previewing the pixel we're hovering over.
            self.preview_pixel = None

            # If we're simply in pencil mode, we'll preview the pixel we're about to draw.
            # We'll set the coordinates of the pixel we're hovering over to our preview pixel.
            self.preview_pixel = (x, y)

            # Repainting our canvas to reflect the changes.
            self.update()

        # If we leave the canvas, we'll clear the preview pixels set and repaint the canvas.
        elif event.type() == QEvent.Type.HoverLeave:
            self.preview_pixel = None
            self.update()

        # Then, we'll handle the event as usual.
        return super().event(event)

    # Overriding the paintEvent method, which handles drawing on the canvas.
    def paintEvent(self, event):

        painter = QPainter(self)

        # We'll draw our pre-rendered grid. We're simply reusing the grid we created earlier.
        painter.drawPixmap(0, 0, self.grid)

        # Now, we'll only redraw the pixel that needs updating. This is given by the event.
        pixel_to_update = event.rect()

        # Going through each pixel:
        for (x, y), color in self.pixels.items():
            # If the current pixel is within the area that needs updating, we'll redraw it.
            current_pixel = QRect(x * self.pixel_size, y * self.pixel_size, self.pixel_size, self.pixel_size)
            if pixel_to_update.intersects(current_pixel):
                painter.fillRect(current_pixel, color)
        
        # If we have any preview pixel, we'll draw it on our canvas.
        if self.preview_pixel:
            self.preview(painter)

        painter.end()

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
            
            # Repainting only the area where the pixel color was updated.
            # We provide the coordinates of the pixel and its dimensions to trigger a repaint of that area.
            self.update(QRect(x * self.pixel_size, y * self.pixel_size, self.pixel_size, self.pixel_size))
    
    # This method handles drawing the preview pixel on our canvas.
    def draw_preview_pixel(self, painter, preview_color):

        # If our canvas is draggable, we'll return since we're not drawing.
        if self.is_draggable:
            return

        # If our eyedropper mode is enabled, return since we're not drawing.
        if self.eyedropper_mode:
            return

        # If our painter object is not active, we'll simply return.
        if not painter.isActive():
            return

        # Drawing the preview pixel on our canvas via its coordinates.
        x, y = self.preview_pixel
        painter.fillRect(x * self.pixel_size, y * self.pixel_size, self.pixel_size, self.pixel_size, preview_color)

    # A function to convert our pixels dictionary to a dictionary of the form {(x, y): rgba_tuple}.
    def convert_to_rgba_format(self):
        
        # Creating an empty dictionary that we'll populate with RGBA tuples.
        rgba_pixels = {}

        # Iterating over the pixels dictionary.
        for (x, y), color in self.pixels.items():

            # Converting the QColor object to an RGBA tuple.
            rgba_tuple = (color.red(), color.green(), color.blue(), color.alpha())

            # Adding the RGBA tuple to our dictionary.
            rgba_pixels[(x, y)] = rgba_tuple

        return rgba_pixels

    # Overriding the mousePressEvent method to draw pixels on our canvas.
    def mousePressEvent(self, event):

        # Before drawing, we'll save the current state of our canvas in the canvas history object.
        # Since we've begun drawing, we shouldn't be able to redo any actions. Thus, we'll clear the redo stack.
        # This ensures that we can undo our strokes if needed, but we can't redo any actions.
        self.canvas_history.save_state_and_update(self.pixels)

        # Getting the x and y coordinates of our mouse click and converting them to pixel coordinates.
        x, y = event.pos().x(), event.pos().y()
        x = x // self.pixel_size
        y = y // self.pixel_size

        # If we're in fill mode, we'll use the fill method to fill in areas.
        if self.fill_mode:
            target_color = self.pixels.get((x, y), QColor("white"))
            replacement_color = self.color_selection_window.get_primary_color()
            self.fill(x, y, target_color, replacement_color)
            # Once we've filled in the area, we'll clear the visited set.
            self.visited.clear()
            return

        #If we are in eyedropper mode, we will copy the selected color onto the primary color.
        if self.eyedropper_mode:
            target_color = self.pixels.get((x, y), QColor("white"))
            self.color_selection_window.set_primary_color(target_color)
            self.color_selection_window.update_selected_colors()
            return

        # If the left mouse button was clicked, we'll draw with the primary color.
        if event.button() == Qt.MouseButton.LeftButton:
            color = self.color_selection_window.get_primary_color()
            self.draw_pixel(x, y, color)
        
        # If the right mouse button was clicked, we'll draw with the secondary color.
        elif event.button() == Qt.MouseButton.RightButton:
            color = self.color_selection_window.get_secondary_color()
            self.draw_pixel(x, y, color)


    # Similarly, we'll override the mouseMoveEvent method to draw pixels as we drag our mouse.
    def mouseMoveEvent(self, event):
        
        # Getting the x and y coordinates of our mouse click and converting them to pixel coordinates.
        x, y = event.pos().x(), event.pos().y()
        x = x // self.pixel_size
        y = y // self.pixel_size
        
        # If the left mouse button is being dragged, we'll draw with the primary color.
        if event.buttons() == Qt.MouseButton.LeftButton:
            color = self.color_selection_window.get_primary_color()
            self.draw_pixel(x, y, color)

        # If the right mouse button is being dragged, we'll draw with the secondary color.
        elif event.buttons() == Qt.MouseButton.RightButton:
            color = self.color_selection_window.get_secondary_color()
            self.draw_pixel(x, y, color)
        

    # To set our canvas to fill mode, we'll use the following method.
    def set_fill_mode(self, fill_mode):
        self.fill_mode = fill_mode

    # To set our canvas to fill mode, we'll use the following method.
    def set_eyedropper_mode(self, eyedropper_mode):
        self.eyedropper_mode = eyedropper_mode

    # If the fill mode of our canvas is active, we'll use the following method to fill in areas.
    def fill(self, x, y, target_color, replacement_color):

        # Using a stack to simulate recursion.
        stack = deque([(x, y)])

        # As long as we have pixels to process, we'll continue.
        while stack:
            # Getting the coordinates of the pixel we'll be processing.
            x, y = stack.pop()

            # If we've already visited/processed the pixel, we'll skip it.
            if (x, y) in self.visited:
                continue

            # Otherwise, we'll get the color of the pixel and continue w/ processing it.
            color = self.pixels.get((x, y), QColor("white"))

            ''' We'll handle our base cases first.
                    1. If the pixel is out of bounds, we'll skip it.
                    2. If the pixel is not the target color, we'll skip it.
                    (We're only interested in the pixels we're targeting.)
            '''
            if not (0 <= x < self.grid_width and 0 <= y < self.grid_height) or color != target_color:
                continue

            # Otherwise, we'll draw the pixel with the replacement color.
            self.draw_pixel(x, y, replacement_color)

            # We'll mark the pixel as visited/processed.
            self.visited.add((x, y))

            # We'll now process the neighboring pixels.
            stack.extend([(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)])
            
    # The following method will allow us to preview pixels on our canvas before drawing them.
    # As we hover over the canvas, we'll see a preview of the pixels we're about to draw.
    # We provide a QPainter object to handle all drawing operations.
    def preview(self, painter):

        # Getting our primary color (with some transparency).
        preview_color = self.color_selection_window.get_primary_color()

        # Drawing the preview pixels on our canvas.
        self.draw_preview_pixel(painter, preview_color)


    # To set the draggable state of our canvas, we'll use the following method.
    def set_draggable(self, draggable):
        self.is_draggable = draggable
        
        

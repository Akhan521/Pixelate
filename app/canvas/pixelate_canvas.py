# Importing basic widgets from PyQt6.
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
# Importing the necessary modules to work with canvas drawings.
from PyQt6.QtGui import QPainter, QColor, QPixmap, QRegion
from PyQt6.QtCore import Qt, QEvent, QRect, QTimer
from canvas.color_selection_window import ColorSelectionWindow
from canvas.canvas_history import CanvasHistory
from collections import deque

# Defining a custom canvas widget for Pixelate.
class PixelateCanvas(QWidget):

    # Our constructor will handle the initialization of the canvas.
    # We provide the color selection window to handle color changes.
    def __init__(self, color_selection_window, pixel_size=15, grid_width=32, grid_height=32):

        # Invoking the parent class constructor.
        super().__init__()
        
        # The start and end points for the line tool.
        self.line_start = (0,0)
        self.line_end   = (0,0)

        # The start and end points for the square tool.
        self.square_start = (0, 0)
        self.square_end   = (0, 0)

        # To store the state of the mouse button.
        self.mouse_button_pressed = False  

        # Our default color will be a light, transparent gray.
        self.default_color = QColor(240, 240, 240, 255)

        # Storing the color selection window to access the chosen colors.
        self.color_selection_window = color_selection_window

        # Setting up our canvas:
        self.pixel_size  = pixel_size   # This will be the size of each pixel.
        self.grid_width  = grid_width   # The number of pixels wide the canvas will be.
        self.grid_height = grid_height  # The number of pixels tall the canvas will be.

        # We'll also need to store the color of each pixel.
        # Our dictionary will map the (x, y) coordinates of each pixel to a color.
        self.pixels = {}

        # We'll have a preview pixel to show the pixel we're about to draw. (The (x, y) coordinates of the pixel.)
        self.preview_pixel = None

        # We'll need to store copies of our pixel colors to implement undo/redo functionality.
        self.canvas_history = CanvasHistory()

        # Our various drawing modes will be stored as boolean flags.
        self.fill_mode       = False
        self.eyedropper_mode = False
        self.is_draggable    = False
        self.erase_mode      = False
        self.line_mode       = False
        self.square_mode     = False

        # Finally, we'll set the size of the canvas.
        self.setFixedSize(self.pixel_size * self.grid_width, self.pixel_size * self.grid_height)

        # To work with mouse hover events, we'll set the following attribute.
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

        # Our grid will be initialized as a QPixmap object (our base layer).
        self.grid = self.init_grid()

        # Our canvas buffer will store the current state of our canvas (initially set to the grid).
        self.canvas_buffer = self.grid.copy()

        # When in fill mode, we'll need to keep track of visited pixels to avoid redundant operations.
        self.visited = set()

        # To store our generated image (from the AI assistant).
        self.generated_image = None

        # To handle our color approximation delay, we'll use a QTimer object.
        # The idea is that we'll only update the color approximation label after a certain delay.
        self.color_approx_timer = QTimer(self)
        self.color_approx_timer.setInterval(250)    # 250 milliseconds
        self.color_approx_timer.setSingleShot(True) # To trigger the timer only once.
        self.color_approx_timer.timeout.connect(self.update_color_approx_label)

        # To store the color we're approximating.
        self.color_to_approx = None

    # A method to set our generated image.
    def set_generated_image(self, image):

        # Updating our pixels dictionary with the generated image's colors.
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                color = image.pixelColor(x, y)
                self.pixels[(x, y)] = color

        # Scaling our image up to fit the canvas (each pixel of our generated image will be a pixel square on our canvas).
        image = image.scaled(self.pixel_size * self.grid_width, self.pixel_size * self.grid_height, Qt.AspectRatioMode.IgnoreAspectRatio)

        # Storing the scaled image as a QPixmap object.
        image = QPixmap.fromImage(image)
        self.generated_image = image

        # Repainting our canvas to display the generated image.
        self.update()

    # This method will create a grid for our canvas. It will be implemented as a QPixmap object.
    # We'll initialize the grid with a light gray background and draw grid lines on top of it.
    def init_grid(self):

        # Creating a QPixmap object to store our grid. (This will serve as our canvas's base layer.)
        grid = QPixmap(self.pixel_size * self.grid_width, self.pixel_size * self.grid_height)

        # Drawing grid lines on our QPixmap object.
        painter = QPainter(grid)
        painter.setPen(Qt.PenStyle.SolidLine)
        # Setting our pen color to a more transparent black.
        painter.setPen(QColor(0, 0, 0, 50))

        # First, we'll fill our grid with a light, transparent gray background.
        grid.fill(self.default_color)

        # Drawing vertical lines.
        for x in range(self.grid_width + 1):
            # Draws a line from (x1, y1) to (x2, y2).
            painter.drawLine(x * self.pixel_size, 0, x * self.pixel_size, self.pixel_size * self.grid_height)

        # Drawing horizontal lines.
        for y in range(self.grid_height + 1):
            # Draws a line from (x1, y1) to (x2, y2).
            painter.drawLine(0, y * self.pixel_size, self.pixel_size * self.grid_width, y * self.pixel_size)

        painter.end()
        return grid

    # Overriding the event method to handle hover events as well.
    def event(self, event):

        # If we're hovering over our canvas, we'll preview the pixel we're about to draw.
        if event.type() == QEvent.Type.HoverMove:

            # Getting the x and y coordinates of our mouse and converting them to pixel coordinates.
            x, y = event.position().x(), event.position().y()
            x = int(x / self.pixel_size)
            y = int(y / self.pixel_size)

            # To avoid unnecessary updates, we'll only update the preview pixel if it has changed.
            if self.preview_pixel == (x, y):
                return super().event(event)

            # To boost performance, we'll only update the pixels that need updating: the previous preview pixel and the current one.
            previous_preview = self.preview_pixel
            self.preview_pixel = (x, y)

            # If the previous preview pixel exists, we'll update it on our canvas.
            if previous_preview:
                self.update(QRect(previous_preview[0] * self.pixel_size, previous_preview[1] * self.pixel_size, 
                                  self.pixel_size, self.pixel_size))
                
            # Now, we'll update the current preview pixel on our canvas.
            self.update(QRect(x * self.pixel_size, y * self.pixel_size, self.pixel_size, self.pixel_size))

            # Storing the color of the pixel we're approximating.
            self.color_to_approx = self.pixels.get((x, y), self.default_color)

            # Starting the color approximation timer.
            self.color_approx_timer.start()

        # Upon leaving the canvas, we'll clear the preview pixel and update our canvas.
        elif event.type() == QEvent.Type.HoverLeave:
            
            # Before clearing the preview pixel, we'll update it on our canvas.
            if self.preview_pixel:
                self.update(QRect(self.preview_pixel[0] * self.pixel_size, self.preview_pixel[1] * self.pixel_size, 
                                  self.pixel_size, self.pixel_size))
            
            # Now, we'll clear the preview pixel.
            self.preview_pixel = None

            # We'll also clear the color to approximate.
            self.color_to_approx = None

            # Updating the color approximation label immediately.
            self.color_selection_window.set_color_approx_label("None")

        # Then, we'll handle the event as usual.
        return super().event(event)
    
    # A method to update the color approximation label.
    def update_color_approx_label(self):

        if self.color_to_approx:
            self.color_selection_window.set_color_approx_label(self.color_to_approx)
        else:
            self.color_selection_window.set_color_approx_label("None")

    # Overriding the paintEvent method, which handles drawing on the canvas.
    def paintEvent(self, event):

        painter = QPainter(self)

        # We'll draw our pre-rendered canvas buffer.
        painter.drawPixmap(0, 0, self.canvas_buffer)

        # If we have a generated image (QPixmap object), we'll set it to our canvas buffer.
        if self.generated_image:

            # Setting the canvas buffer to the generated image.
            self.canvas_buffer = self.generated_image

            # Clearing the generated image afterwards.
            self.generated_image = None

        # Displaying our previews.
        self.preview(painter)

        painter.end()

    # The following method will draw a pixel @ the given (x, y) coordinates with the given color (QColor object).
    def draw_pixel(self, pixel, color):
        x, y = pixel

        # If our canvas is in any of the following modes, we'll return since we're not drawing.
        if self.is_draggable or self.eyedropper_mode:
            return

        # Otherwise, we'll ensure that the pixel is within bounds.
        if self.is_within_canvas(pixel):

            # Updating the color of the pixel at (x, y).
            self.pixels[pixel] = color

            # Updating the canvas buffer to display the pixel.
            current_pixel = QRect(x * self.pixel_size, y * self.pixel_size, self.pixel_size, self.pixel_size)
            buffer_painter = QPainter(self.canvas_buffer)
            buffer_painter.fillRect(current_pixel, color)
            buffer_painter.end()
            
            # Repainting the pixel we've drawn on our canvas.
            self.update(current_pixel)
    
    # This method handles drawing the preview pixel on our canvas.
    def draw_preview_pixel(self, painter, preview_color):

        # If our canvas is in any of the following modes, we'll return since we're not drawing.
        if self.is_draggable or self.eyedropper_mode:
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
    
    # A function to convert our pixels dictionary to a dictionary of the form {(x, y): QColor}.
    def convert_to_qcolor_format(self, rgba_pixels):

        # Creating an empty dictionary that we'll populate with QColor objects.
        qcolor_pixels = {}

        # Iterating over the pixels dictionary.
        for (x, y), rgba_tuple in rgba_pixels.items():

            # Creating a QColor object from the RGBA tuple.
            color = QColor(*rgba_tuple)

            # Adding the QColor object to our dictionary.
            qcolor_pixels[(x, y)] = color

        return qcolor_pixels

    # A method to "erase" a pixel at the given (x, y) coordinates (for our eraser tool).
    # We update the canvas buffer by repainting the pixel with the default color.
    def erase_pixel(self, pixel):

        # Removing the pixel from our pixels dictionary.
        del self.pixels[pixel]

        # Storing the current pixel.
        x, y = pixel
        current_pixel = QRect(x * self.pixel_size, y * self.pixel_size, self.pixel_size, self.pixel_size)

        # Repainting the pixel with the default color.
        buffer_painter = QPainter(self.canvas_buffer)
        buffer_painter.fillRect(current_pixel, self.default_color)
        buffer_painter.end()

    # Overriding the mousePressEvent method to draw pixels on our canvas.
    def mousePressEvent(self, event):

        # If the middle mouse button is pressed, we'll return to avoid drawing.
        if event.button() == Qt.MouseButton.MiddleButton:
            return

        # Before drawing, we'll save the current state of our canvas in the canvas history object.
        self.canvas_history.save_state_and_update(self.pixels, self.canvas_buffer)

        #If Mouse Button is clicked, set true
        self.mouse_button_pressed = True

        # Getting the x and y coordinates of our mouse click and converting them to pixel coordinates.
        x, y = event.pos().x(), event.pos().y()
        x = x // self.pixel_size
        y = y // self.pixel_size
        pixel = (x, y)

        if self.line_mode:
            # Store the starting point & end point.
            self.line_start = pixel
            self.line_end = pixel
            return

        if self.square_mode:
            # Store the starting point & end point.
            self.square_start = pixel
            self.square_end = pixel
            return

        # If we press the left mouse button, we'll draw with the primary color.
        if event.button() == Qt.MouseButton.LeftButton:
            
            # If we're in eyedropper mode, we'll get the color of the pixel we're clicking on.
            if self.eyedropper_mode:
                color = self.pixels.get(pixel, self.default_color)
                # Then, we'll update our primary color w/ the color of the pixel we're clicking on.
                self.color_selection_window.set_primary_color(color)
                self.color_selection_window.update_selected_colors()
                return
            
            # Otherwise, we'll get the primary color from the color selection window.
            color = self.color_selection_window.get_primary_color()

        elif event.button() == Qt.MouseButton.RightButton:
            
            # If we're in eyedropper mode, we'll get the color of the pixel we're clicking on.
            if self.eyedropper_mode:
                color = self.pixels.get(pixel, self.default_color)
                # Then, we'll update our secondary color w/ the color of the pixel we're clicking on.
                self.color_selection_window.set_secondary_color(color)
                self.color_selection_window.update_selected_colors()
                return
            
            # Otherwise, we'll get the secondary color from the color selection window.
            color = self.color_selection_window.get_secondary_color()

        # If we're in erase mode, we'll "delete" the pixel at the given coordinates.
        if self.erase_mode:
            if pixel in self.pixels:
                self.erase_pixel(pixel)
            return

        # If we're in fill mode, we'll use the fill method to fill in areas.
        if self.fill_mode:
            target_color = self.pixels.get(pixel, self.default_color)
            replacement_color = color
            self.fill(pixel, target_color, replacement_color)
            # Once we've filled in the area, we'll clear the visited set.
            self.visited.clear()
            return

        # Drawing the pixel at the given coordinates with the selected color.
        self.draw_pixel(pixel, color)

    def mouseReleaseEvent(self, event):

        self.mouse_button_pressed = False

        if self.line_mode:

            x, y = event.pos().x(), event.pos().y()
            x = x // self.pixel_size
            y = y // self.pixel_size

            self.line_end = (x, y)

            # Retrieving the primary color.
            color = self.color_selection_window.get_primary_color()

            # Drawing the line on our canvas buffer.
            self.draw_line(self.line_start, self.line_end, color, is_preview=False)
            return

        if self.square_mode:

            x, y = event.pos().x(), event.pos().y()
            x = x // self.pixel_size
            y = y // self.pixel_size

            self.square_end = (x, y)

            # Retrieving the primary color.
            color = self.color_selection_window.get_primary_color()

            # If the start and end points are within the canvas bounds, we'll draw the square on our canvas buffer.
            if self.is_within_canvas(self.square_start) and self.is_within_canvas(self.square_end):
                self.draw_square(self.square_start, self.square_end, color, is_preview=False)
            return

    # Similarly, we'll override the mouseMoveEvent method to draw pixels as we drag our mouse.
    def mouseMoveEvent(self, event):

        # If the middle mouse button is pressed, we'll return to avoid drawing.
        if event.buttons() == Qt.MouseButton.MiddleButton:
            return
        
        # Getting the x and y coordinates of our mouse click and converting them to pixel coordinates.
        x, y = event.pos().x(), event.pos().y()
        x = x // self.pixel_size
        y = y // self.pixel_size
        pixel = (x, y)

        # Line Preview (if we're in line mode and dragging the mouse).
        if self.line_mode and event.buttons() == Qt.MouseButton.LeftButton:

            # Update the end point of the line.
            self.line_end = pixel

            # Repaint the canvas to show the new preview line.
            self.update()
            return

        #If in square mode, we will draw a preview if mouse is clicked and moving.
        if self.square_mode and event.buttons() == Qt.MouseButton.LeftButton:

            # Update the end point of the square.
            self.square_end = pixel

            # Repaint the canvas to show the new preview square.
            self.update()
            return

        # If we're in erase mode, we'll "delete" the pixel at the given coordinates.
        if self.erase_mode:
            if pixel in self.pixels:
                self.erase_pixel(pixel)
            return
        
        # If the left mouse button is being pressed, we'll draw with the primary color.
        if event.buttons() == Qt.MouseButton.LeftButton:
            color = self.color_selection_window.get_primary_color()

        # If the right mouse button is being pressed, we'll draw with the secondary color.
        elif event.buttons() == Qt.MouseButton.RightButton:
            color = self.color_selection_window.get_secondary_color()

        self.draw_pixel(pixel, color)

    # To set our canvas to fill mode, we'll use the following method.
    def set_fill_mode(self, fill_mode):
        self.fill_mode = fill_mode

    # To set our canvas to fill mode, we'll use the following method.
    def set_eyedropper_mode(self, eyedropper_mode):
        self.eyedropper_mode = eyedropper_mode

    # To set our canvas to erase mode, we'll use the following method.
    def set_erase_mode(self, erase_mode):
        self.erase_mode = erase_mode

    # To set our canvas to line mode, we'll use the following method.
    def set_line_mode(self, line_mode):
        self.line_mode = line_mode

    # To set our canvas to square mode, we'll use the following method.
    def set_square_mode(self, square_mode):
        self.square_mode = square_mode

    # A method to get our canvas dimensions.
    def get_dimensions(self):
        return (self.grid_width, self.grid_height)
    
    # A method to get our pixel size.
    def get_pixel_size(self):
        return self.pixel_size

    # If the fill mode of our canvas is active, we'll use the following method to fill in areas.
    def fill(self, pixel, target_color, replacement_color):

        # Using a stack to simulate recursion.
        stack = deque([pixel])

        # As long as we have pixels to process, we'll continue.
        while stack:
            # Getting the coordinates of the pixel we'll be processing.
            next_pixel = stack.pop()

            # If we've already visited/processed the pixel, we'll skip it.
            if next_pixel in self.visited:
                continue

            # Otherwise, we'll get the color of the pixel and continue w/ processing it.
            color = self.pixels.get(next_pixel, self.default_color)

            ''' We'll handle our base cases first.
                    1. If the pixel is out of bounds, we'll skip it.
                    2. If the pixel is not the target color, we'll skip it.
                    (We're only interested in the pixels we're targeting.)
            '''
            if not self.is_within_canvas(next_pixel) or color != target_color:
                continue

            # Otherwise, we'll draw the pixel with the replacement color.
            self.draw_pixel(next_pixel, replacement_color)

            # We'll mark the pixel as visited/processed.
            self.visited.add(next_pixel)

            # We'll now process the neighboring pixels.
            x, y = next_pixel
            stack.extend([(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)])
            
    # The following method will allow us to preview pixels on our canvas before drawing them.
    # We provide a QPainter object to handle all drawing operations.
    def preview(self, painter):

        # If we're in erase mode, the preview pixel will be the same color as the background.
        if self.erase_mode:
            preview_color = self.default_color

        # Getting our primary color.
        else:
            preview_color = self.color_selection_window.get_primary_color()

        # If we're in line mode and the mouse button was pressed, we'll draw a preview line.
        if self.line_mode and self.mouse_button_pressed:

            # We'll draw the preview line directly onto the canvas, not the canvas buffer.
            self.draw_line(self.line_start, self.line_end, preview_color, is_preview=True, painter=painter)

        # If we're in square mode and the mouse button was pressed, we'll draw a preview square.
        if self.square_mode and self.mouse_button_pressed:

            # We'll draw the preview square directly onto the canvas, not the canvas buffer.
            self.draw_square(self.square_start, self.square_end, preview_color, is_preview=True, painter=painter)

        # If we have a preview pixel, we'll draw it on our canvas.
        if self.preview_pixel:
            self.draw_preview_pixel(painter, preview_color)

    # To set the draggable state of our canvas, we'll use the following method.
    def set_draggable(self, draggable):
        self.is_draggable = draggable

    # A getter method to retrieve the current state of our canvas.
    def get_pixels(self):
        return self.pixels
    
    # A method to set the pixels of our canvas.
    def set_pixels(self, pixels):
        self.pixels = pixels
    
    # A method to update the pixels of our canvas (adding new pixels; not replacing the existing ones).
    # (Will be used to implement import functionality from within the main app window.)
    def update_pixels(self, pixels):
        self.pixels.update(pixels)

        # Updating the canvas buffer to display the new pixels.
        for (x, y), color in pixels.items():
            current_pixel = QRect(x * self.pixel_size, y * self.pixel_size, self.pixel_size, self.pixel_size)
            buffer_painter = QPainter(self.canvas_buffer)
            buffer_painter.fillRect(current_pixel, color)
            buffer_painter.end()

        # Repainting the canvas to display the new pixels.
        self.update()

    # Method to draw a line on screen given a color, start, and end point.
    def draw_line(self, start, end, color, is_preview=False, painter=None):
        x1, y1 = start
        x2, y2 = end

        # Store distance, step direction, and error.
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy

        while True:

            # Within canvas bounds...
            if self.is_within_canvas((x1, y1)):

                if is_preview:
                    # For our preview line, we'll draw it directly onto our canvas, not the canvas buffer.
                    painter.fillRect(x1 * self.pixel_size, y1 * self.pixel_size, self.pixel_size, self.pixel_size, color)

                else:
                    # Otherwise, we'll draw the line on our canvas buffer.
                    self.draw_pixel((x1, y1), color)

            # Bresenham’s Algorithm:
            if x1 == x2 and y1 == y2:
                break

            # To determine the next pixel to draw, we'll calculate the error.
            e2 = 2 * err

            # Horizontal step decision.
            if e2 > -dy:
                err -= dy
                x1 += sx

            # Vertical step decision.
            if e2 < dx:
                err += dx
                y1 += sy

    # Method to check if a coordinate is within the canvas.
    def is_within_canvas(self, pixel):
        x, y = pixel
        return 0 <= x < self.grid_width and 0 <= y < self.grid_height

    # Method to draw a square on screen given a color, start, and end point.
    def draw_square(self, start, end, color, is_preview=False, painter=None):

        # Store coordinates of start and end points.
        x1, y1 = start
        x2, y2 = end

        # Drawing all 4 sides of the square.
        self.draw_line(start, (x2, y1), color, is_preview, painter)
        self.draw_line((x2, y1), end, color, is_preview, painter)
        self.draw_line(end, (x1, y2), color, is_preview, painter)
        self.draw_line((x1, y2), start, color, is_preview, painter)
 
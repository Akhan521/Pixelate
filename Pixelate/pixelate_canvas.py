# Importing basic widgets from PyQt6.
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
# Importing the necessary modules to work with canvas drawings.
from PyQt6.QtGui import QPainter, QColor, QPixmap, QRegion
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

        # The start and end points for the line tools.
        self.line_tool_start_point = (0,0)
        self.line_tool_end_point = (0,0)

        # The start and end points for the square tools.
        self.square_tool_start_point = (0, 0)
        self.square_tool_end_point = (0, 0)

        #Variable to check if mouse button is clicked
        self.mouse_button_pressed = False  # Track if the mouse button is pressed

        # Our default color will be a light, transparent gray.
        self.default_color = QColor(240, 240, 240, 255)

        # Storing the color selection window to access the chosen colors.
        self.color_selection_window = color_selection_window

        # Setting up our canvas:
        self.pixel_size = pixel_size   # This will be the size of each pixel.
        self.grid_width = grid_width   # The number of pixels wide the canvas will be.
        self.grid_height = grid_height # The number of pixels tall the canvas will be.

        # We'll also need to store the color of each pixel.
        # Our dictionary will map the (x, y) coordinates of each pixel to a color.
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

        # To store whether our canvas is in erase mode.
        self.erase_mode = False

        # To store whether our canvas is in Line Tool.
        self.line_mode = False

        # To store whether our canvas is in Square Tool.
        self.square_mode = False

        # Finally, we'll set the size of the canvas.
        self.setFixedSize(self.pixel_size * self.grid_width, self.pixel_size * self.grid_height)

        # To work with mouse hover events, we'll set the following attribute.
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

        # Our grid will be initialized as a QPixmap object (our base layer).
        self.grid = self.init_grid()

        # When in fill mode, we'll need to keep track of visited pixels to avoid redundant operations.
        self.visited = set()

        # To store our generated image (from the AI assistant).
        self.generated_image = None

        # To store our modified pixels (these are the only pixels we'll update).
        self.modified_pixels = set()

    # A method to set our generated image.
    def set_generated_image(self, image):

        # # Scaling our image to fit the canvas (each pixel of our generated image will be a pixel square on our canvas).
        # image = image.scaled(self.pixel_size * self.grid_width, self.pixel_size * self.grid_height, Qt.AspectRatioMode.IgnoreAspectRatio)

        # Storing the scaled image.
        self.generated_image = image

        # # Updating our canvas buffer to display the generated image.
        # painter = QPainter(self.canvas_buffer)
        # painter.drawImage(0, 0, self.generated_image)
        # painter.end()

        # # Repainting our canvas to display the generated image.
        # self.update()

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

            # To update our color approximation label, we'll get the color of the pixel we're hovering over.
            color = self.pixels.get((x, y), self.default_color)
            self.color_selection_window.set_color_approx_label(color)

        # Upon leaving the canvas, we'll clear the preview pixel and update our canvas.
        elif event.type() == QEvent.Type.HoverLeave:
            
            # Before clearing the preview pixel, we'll update it on our canvas.
            if self.preview_pixel:
                self.update(QRect(self.preview_pixel[0] * self.pixel_size, self.preview_pixel[1] * self.pixel_size, 
                                  self.pixel_size, self.pixel_size))
            
            # Now, we'll clear the preview pixel.
            self.preview_pixel = None

            # We'll also clear the color approximation label.
            self.color_selection_window.set_color_approx_label("None")

        # Then, we'll handle the event as usual.
        return super().event(event)

    # Overriding the paintEvent method, which handles drawing on the canvas.
    def paintEvent(self, event):

        painter = QPainter(self)

        # We'll draw our pre-rendered grid on the canvas.
        painter.drawPixmap(0, 0, self.grid)

        # If we have a generated image, we'll draw it directly on our canvas.
        if self.generated_image:
            
            # For every pixel, we'll...
            for x in range(self.grid_width):
                for y in range(self.grid_height):

                    # Get the color of the pixel from the generated image.
                    color = self.generated_image.pixelColor(x, y)

                    # Directly update the pixel on our canvas.
                    self.pixels[(x, y)] = color

                    # Repaint the pixel on our canvas.
                    self.update(QRect(x * self.pixel_size, y * self.pixel_size, self.pixel_size, self.pixel_size))

            # Once we've drawn the generated image, we'll clear it to avoid redrawing it.
            self.generated_image = None

        # If we have any preview pixel, we'll draw it on our canvas.
        if self.preview_pixel:
            self.preview(painter)

        # # If we have no modified pixels to draw, we'll simply return.
        # if not self.modified_pixels:
        #     painter.end()
        #     return

        # Otherwise, we'll only redraw the pixel that needs updating. This is provided by the event.
        pixel_to_update = event.rect()

        # Going through each pixel:
        for (x, y), color in self.pixels.items():
            # If the current pixel is within the area that needs updating, we'll redraw it.
            current_pixel = QRect(x * self.pixel_size, y * self.pixel_size, self.pixel_size, self.pixel_size)
            if pixel_to_update.intersects(current_pixel):
                painter.fillRect(current_pixel, color)

        # # Only updating the modified pixels.
        # region = QRegion()
        # for (x, y) in self.modified_pixels:
        #     color = self.pixels.get((x, y), self.default_color)
        #     current_pixel = QRect(x * self.pixel_size, y * self.pixel_size, self.pixel_size, self.pixel_size)
        #     region += current_pixel

        #     # Updating our canvas buffer instead of the canvas directly.
        #     buffer_painter = QPainter(self.canvas_buffer)
        #     buffer_painter.fillRect(current_pixel, color)
        #     buffer_painter.end()

        # Clearing our modified pixels and updating the modified region.
        # self.modified_pixels.clear()
        # self.update(region)
        painter.end()

    # The following method will draw a pixel @ the given (x, y) coordinates with the given color (QColor object).
    def draw_pixel(self, x, y, color):

        # If our canvas is draggable, we'll return since we're not drawing.
        if self.is_draggable:
            return

        # If our eyedropper mode is enabled, return since we're not drawing.
        if self.eyedropper_mode:
            return

        # If line mode is enabled, return since we handle it separately.
        if self.line_mode:
            return

        # If line mode is enabled, return since we handle it separately.
        if self.square_mode:
            return

        # Otherwise, we'll ensure that the pixel is within bounds.
        if 0 <= x < self.grid_width and 0 <= y < self.grid_height:

            # Updating the color of the pixel at (x, y).
            self.pixels[(x, y)] = color

            # Adding the current pixel to the modified pixels set.
            # self.modified_pixels.add((x, y))
            
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

        #if we are in square mode and mouse button is pressed, then show preview.
        if self.square_mode and self.mouse_button_pressed:

            #Get start and end points and store color.
            start = self.square_tool_start_point
            end = self.square_tool_end_point
            x1, y1 = start
            x2, y2 = end
            color = preview_color

            # Draw the top of the square
            while True:
                #make sure x1 and y1 is in range.
                if self.is_within_canvas(x1, y1):

                    # show the preview for a single pixel
                    painter.fillRect(x1 * self.pixel_size, y1 * self.pixel_size, self.pixel_size, self.pixel_size,
                                     preview_color)

                    # We provide the coordinates of the pixel and its dimensions to trigger a repaint of that area.
                    self.update(QRect(x1 * self.pixel_size, y1 * self.pixel_size, self.pixel_size, self.pixel_size))

                    # stop drawing when x1 reaches x2, if has not, increment in the direction of x2.
                    if x1 == x2:
                        break
                    if x1 < x2:
                        x1 = x1 + 1
                    else:
                        x1 = x1 - 1
                else:
                    break

            #Reset the coordinates.
            x1, y1 = start
            x2, y2 = end

            # Draw the left side of the square.
            while True:
                #check if in bounds.
                if self.is_within_canvas(x1, y1):

                    # show the preview for a single pixel
                    painter.fillRect(x1 * self.pixel_size, y1 * self.pixel_size, self.pixel_size, self.pixel_size,
                                     preview_color)

                    # We provide the coordinates of the pixel and its dimensions to trigger a repaint of that area.
                    self.update(QRect(x1 * self.pixel_size, y1 * self.pixel_size, self.pixel_size, self.pixel_size))

                    # stop drawing when y1 reaches y2, if has not, increment in the direction of y2.
                    if y1 == y2:
                        break
                    if y1 < y2:
                        y1 = y1 + 1
                    else:
                        y1 = y1 - 1
                else:
                    break

            #Reset coordinates.
            x1, y1 = start
            x2, y2 = end

            # Offset y coordinates.
            y1 = y2

            # Draw the bottom side of the square.
            while True:
                #Check if in bounds.
                if self.is_within_canvas(x1, y1):

                    # show the preview for a single pixel
                    painter.fillRect(x1 * self.pixel_size, y1 * self.pixel_size, self.pixel_size, self.pixel_size,
                                     preview_color)

                    # We provide the coordinates of the pixel and its dimensions to trigger a repaint of that area.
                    self.update(QRect(x1 * self.pixel_size, y1 * self.pixel_size, self.pixel_size, self.pixel_size))

                    # stop drawing when x1 reaches x2, if has not, increment in the direction of x2.
                    if x1 == x2:
                        break
                    if x1 < x2:
                        x1 = x1 + 1
                    else:
                        x1 = x1 - 1
                else:
                    break

            #reset coordinates.
            x1, y1 = start
            x2, y2 = end

            # Offset x coordinates.
            x1 = x2

            # Draw the right side of the square.
            while True:
                #check bounds.
                if self.is_within_canvas(x1, y1):

                    # show the preview for a single pixel
                    painter.fillRect(x1 * self.pixel_size, y1 * self.pixel_size, self.pixel_size, self.pixel_size,
                                     preview_color)

                    # We provide the coordinates of the pixel and its dimensions to trigger a repaint of that area.
                    self.update(QRect(x1 * self.pixel_size, y1 * self.pixel_size, self.pixel_size, self.pixel_size))

                    # stop drawing when y1 reaches y2, if has not, increment in the direction of y2.
                    if y1 == y2:
                        break
                    if y1 < y2:
                        y1 = y1 + 1
                    else:
                        y1 = y1 - 1
                else:
                    break
            return

        #If we are in line mode, then draw the preview for the line.
        if self.line_mode:

            #store the start and end points of mouse press and release.
            x1, y1 = self.line_tool_start_point
            x2, y2 = self.line_tool_end_point

            #store distance of start and end points.
            dx = abs(x2 - x1)
            dy = abs(y2 - y1)

            #stores the step direction (sx positive means move right, sy positive means move up, negatives is opposite direction).
            sx = 1 if x1 < x2 else -1
            sy = 1 if y1 < y2 else -1

            #stores error.
            err = dx - dy

            #loop for the entire line.
            while True:
                # Draw preview of line only when in bounds and when mouse button is pressed.
                if 0 <= x1 < self.grid_width and 0 <= y1 < self.grid_height and self.mouse_button_pressed:

                    # show the preview for a single pixel
                    painter.fillRect(x1 * self.pixel_size, y1 * self.pixel_size, self.pixel_size, self.pixel_size,
                                     preview_color)

                    # We provide the coordinates of the pixel and its dimensions to trigger a repaint of that area.
                    self.update(QRect(x1 * self.pixel_size, y1 * self.pixel_size, self.pixel_size, self.pixel_size))

                #Bresenham’s Algorithm:
                #stop if current pixel reaches end point.
                if x1 == x2 and y1 == y2:
                    break
                e2 = 2 * err

                #Horizontal step calculation.
                if e2 > -dy:
                    err -= dy
                    x1 += sx

                #Vertical step calculation.
                if e2 < dx:
                    err += dx
                    y1 += sy
            return

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

    # Overriding the mousePressEvent method to draw pixels on our canvas.
    def mousePressEvent(self, event):

        # If the middle mouse button is pressed, we'll return to avoid drawing.
        if event.button() == Qt.MouseButton.MiddleButton:
            return

        # Before drawing, we'll save the current state of our canvas in the canvas history object.
        # Since we've begun drawing, we shouldn't be able to redo any actions. Thus, we'll clear the redo stack.
        # This ensures that we can undo our strokes if needed, but we can't redo any actions.
        self.canvas_history.save_state_and_update(self.pixels)

        #If Mouse Button is clicked, set true
        self.mouse_button_pressed = True

        # Getting the x and y coordinates of our mouse click and converting them to pixel coordinates.
        x, y = event.pos().x(), event.pos().y()
        x = x // self.pixel_size
        y = y // self.pixel_size

        if self.line_mode:
            # Store the starting point & end point.
            self.line_tool_start_point = (x, y)
            self.line_tool_end_point = (x, y)
            return

        if self.square_mode:
            # Store the starting point & end point.
            self.square_tool_start_point = (x, y)
            self.square_tool_end_point = (x, y)
            return

        # If we press the left mouse button, we'll draw with the primary color.
        if event.button() == Qt.MouseButton.LeftButton:
            
            # If we're in eyedropper mode, we'll get the color of the pixel we're clicking on.
            if self.eyedropper_mode:
                color = self.pixels.get((x, y), self.default_color)
                # Then, we'll update our primary color w/ the color of the pixel we're clicking on.
                self.color_selection_window.set_primary_color(color)
                self.color_selection_window.update_selected_colors()
                return
            # Otherwise, we'll get the primary color from the color selection window.
            color = self.color_selection_window.get_primary_color()

        elif event.button() == Qt.MouseButton.RightButton:
            
            # If we're in eyedropper mode, we'll get the color of the pixel we're clicking on.
            if self.eyedropper_mode:
                color = self.pixels.get((x, y), self.default_color)
                # Then, we'll update our secondary color w/ the color of the pixel we're clicking on.
                self.color_selection_window.set_secondary_color(color)
                self.color_selection_window.update_selected_colors()
                return
            
            # Otherwise, we'll get the secondary color from the color selection window.
            color = self.color_selection_window.get_secondary_color()

        # If we're in erase mode, we'll delete the pixel at the given coordinates.
        if self.erase_mode:
            if (x, y) in self.pixels:
                del self.pixels[(x, y)]
                self.update(QRect(x * self.pixel_size, y * self.pixel_size, self.pixel_size, self.pixel_size))
            return

        # If we're in fill mode, we'll use the fill method to fill in areas.
        if self.fill_mode:
            target_color = self.pixels.get((x, y), self.default_color)
            replacement_color = color
            self.fill(x, y, target_color, replacement_color)
            # Once we've filled in the area, we'll clear the visited set.
            self.visited.clear()
            return

        # Drawing the pixel at the given coordinates with the selected color.
        self.draw_pixel(x, y, color)

    #Happens when the mouse button is released.
    def mouseReleaseEvent(self, event):

        # If Mouse Button is released, set false.
        self.mouse_button_pressed = False

        # If in line mode, get the end point when mouse is released.
        if self.line_mode:

            #Get x and y position of mouse
            x, y = event.pos().x(), event.pos().y()
            x = x // self.pixel_size
            y = y // self.pixel_size

            self.line_tool_end_point = (x, y)

            # Retrieve the selected color
            color = self.color_selection_window.get_primary_color()

            # Draw Line
            self.draw_line(self.line_tool_start_point, self.line_tool_end_point, color)
            return

        if self.square_mode:
            #Get x and y position of mouse
            x, y = event.pos().x(), event.pos().y()
            x = x // self.pixel_size
            y = y // self.pixel_size

            self.square_tool_end_point = (x, y)

            # Retrieve the selected color
            color = self.color_selection_window.get_primary_color()

            x1, y1 = self.square_tool_start_point
            x2, y2 = self.square_tool_end_point

            if self.is_within_canvas(x1,x2) and self.is_within_canvas(x2,y2):
                # Draw Square
                self.draw_square(self.square_tool_start_point, self.square_tool_end_point, color)
                return

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

        # If in line mode, we will draw a preview if mouse is clicked and moving.
        if self.line_mode and event.buttons() == Qt.MouseButton.LeftButton:
            # Update the temporary end point
            self.line_tool_end_point = (x, y)
            self.update()

        #If in square mode, we will draw a preview if mouse is clicked and moving.
        if self.square_mode and event.buttons() == Qt.MouseButton.LeftButton:
            self.square_tool_end_point = (x,y)
            self.update()

        # If we're in erase mode, we'll delete the pixel at the given coordinates.
        if self.erase_mode:
            if (x, y) in self.pixels:
                del self.pixels[(x, y)]
                self.update(QRect(x * self.pixel_size, y * self.pixel_size, self.pixel_size, self.pixel_size))
            return
        
        # If the left mouse button is being pressed, we'll draw with the primary color.
        if event.buttons() == Qt.MouseButton.LeftButton:
            color = self.color_selection_window.get_primary_color()

        # If the right mouse button is being pressed, we'll draw with the secondary color.
        elif event.buttons() == Qt.MouseButton.RightButton:
            color = self.color_selection_window.get_secondary_color()

        self.draw_pixel(x, y, color)

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
            color = self.pixels.get((x, y), self.default_color)

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

        # If we're in erase mode, the preview pixel will be the same color as the background.
        if self.erase_mode:
            preview_color = self.default_color

        # Getting our primary color.
        else:
            preview_color = self.color_selection_window.get_primary_color()

        # Drawing the preview pixels on our canvas.
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

    #Method to draw lines from start point to end point on the canvas.
    def draw_line(self, start, end, color):
        x1, y1 = start
        x2, y2 = end

        #Store distance, step direction, and error.
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy

        while True:
            # While in bounds, draw line.
            if 0 <= x1 < self.grid_width and 0 <= y1 < self.grid_height:

                #Updating the color of the pixel at (x, y).
                self.pixels[(x1, y1)] = color
                self.update(QRect(x1 * self.pixel_size, y1 * self.pixel_size, self.pixel_size, self.pixel_size))

            # Bresenham’s Algorithm:
            #break if current point reaches end point.
            if x1 == x2 and y1 == y2:
                break

            #mul error to determine direction of next pixel in line.
            e2 = 2 * err

            #Horizontal step decision.
            if e2 > -dy:
                err -= dy
                x1 += sx

            #Vertical step decision.
            if e2 < dx:
                err += dx
                y1 += sy

    #Method to check if a coordinate is within the canvas.
    def is_within_canvas(self, x, y):
        return 0 <= x < self.grid_width and 0 <= y < self.grid_height

    #Method to draw a square on screen given a color, start, and end point.
    def draw_square(self, start, end, color):

        #Store coordinates of start and end points.
        x1, y1 = start
        x2, y2 = end

        #Draw the top side of the square.
        while True:
            # check if coordinates is in bounds.
            if self.is_within_canvas(x1,y1):
                # Updating the color of the pixel at (x, y).
                self.pixels[(x1, y1)] = color
                self.update(QRect(x1 * self.pixel_size, y1 * self.pixel_size, self.pixel_size, self.pixel_size))

                # stop drawing when x1 reaches x2, if has not, increment in the direction of x2.
                if x1 == x2:
                    break
                if x1 < x2:
                    x1 = x1 + 1
                else:
                    x1 = x1 - 1
            else:
                break

        #reset coordinates.
        x1, y1 = start
        x2, y2 = end

        #Draw the left side of the square.
        while True:
            # check if coordinates is in bounds.
            if self.is_within_canvas(x1,y1):
                # Updating the color of the pixel at (x, y).
                self.pixels[(x1, y1)] = color
                self.update(QRect(x1 * self.pixel_size, y1 * self.pixel_size, self.pixel_size, self.pixel_size))

                # stop drawing when y1 reaches y2, if has not, increment in the direction of y2.
                if y1 == y2:
                    break
                if y1 < y2:
                    y1 = y1 + 1
                else:
                    y1 = y1 - 1
            else:
                break

        #reset coordinates.
        x1, y1 = start
        x2, y2 = end

        # Offset y coordinates
        y1 = y2

        #Draw the bottom side of the square
        while True:
            # check if coordinates is in bounds.
            if self.is_within_canvas(x1,y1):
                # Updating the color of the pixel at (x, y).
                self.pixels[(x1, y1)] = color
                self.update(QRect(x1 * self.pixel_size, y1 * self.pixel_size, self.pixel_size, self.pixel_size))

                # stop drawing when x1 reaches x2, if has not, increment in the direction of x2.
                if x1 == x2:
                    break
                if x1 < x2:
                    x1 = x1 + 1
                else:
                    x1 = x1 - 1
            else:
                break

        #reset coordinates.
        x1, y1 = start
        x2, y2 = end

        #Offset x coordinates
        x1 = x2

        #Draw the right side of the square
        while True:
            # check if coordinates is in bounds.
            if self.is_within_canvas(x1,y1):
                # Updating the color of the pixel at (x, y).
                self.pixels[(x1, y1)] = color
                self.update(QRect(x1 * self.pixel_size, y1 * self.pixel_size, self.pixel_size, self.pixel_size))

                # stop drawing when y1 reaches y2, if has not, increment in the direction of y2.
                if y1 == y2:
                    break
                if y1 < y2:
                    y1 = y1 + 1
                else:
                    y1 = y1 - 1
            else:
                break
# Importing QColor to work with color objects.
from PyQt6.QtGui import QColor, QPixmap

'''
    A class to store the history of our canvas:
    Each state of our canvas will be represented by a dictionary of pixel colors and a canvas buffer.
    
    The structure of our pixels dictionary will be as follows:
        (x, y) -> QColor object, where (x, y) are the coordinates of the pixel on the canvas.
    
    Our canvas buffer will be a QPixmap object that will store the current state of our canvas.
'''
class CanvasHistory:
    # Our constructor will initialize our undo/redo stacks.
    def __init__(self):
        self.undo_stack = [] # To store our undo states.
        self.redo_stack = [] # To store our redo states.

    # This method will save the current state of our canvas to the undo stack.
    def save_state(self, pixels, canvas_buffer):
        data = (pixels.copy(), canvas_buffer.copy())
        self.undo_stack.append(data)

    # When we draw on our canvas, we'll need to save the current state of our canvas and reset our redo stack.
    # The following method will handle this task.
    def save_state_and_update(self, pixels, canvas_buffer):
        
        # Adding our current state to the undo stack so that we have the ability to undo our actions.
        self.save_state(pixels, canvas_buffer)

        # Once we've drawn on our canvas, we can no longer redo any actions. Thus, we'll clear the redo stack.
        self.redo_stack.clear()

    # This method is responsible for undoing the last action performed on our canvas.
    def undo(self, pixels, canvas_buffer):
        # If we can undo an action, we'll retrieve the last state of our canvas.
        if self.undo_stack:
            # First, we must save our current state to the redo stack. This will allow us to redo our actions.
            data = (pixels.copy(), canvas_buffer.copy())
            self.redo_stack.append(data)

            # Next, we'll retrieve the last state of our canvas from the undo stack.
            pixels.clear()
            pixels, last_buffer = self.undo_stack.pop()
            
            # Finally, we'll return the last state of our canvas.
            return (pixels, last_buffer)

        # Otherwise, we'll simply return the current state of our canvas.
        return (pixels, canvas_buffer)

    # This method is responsible for redoing the last action performed on our canvas.
    def redo(self, pixels, canvas_buffer):
        # If we can redo an action, we'll retrieve the last state of our canvas.
        if self.redo_stack:
            # First, we must save our current state to the undo stack. This will allow us to undo our actions.
            self.save_state(pixels, canvas_buffer)

            # Next, we'll retrieve the last state of our canvas from the redo stack.
            pixels.clear()
            pixels, last_buffer = self.redo_stack.pop()

            # Finally, we'll return the last state of our canvas.
            return (pixels, last_buffer)

        # Otherwise, we'll simply return the current state of our canvas.
        return (pixels, canvas_buffer)
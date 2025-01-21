# Importing QColor to work with color objects.
from PyQt6.QtGui import QColor

'''
    A class to store the history of our canvas:
    Each state of our canvas will be represented by a dictionary of pixels w/ their respective colors.
    
    The structure of our dictionary will be as follows:
        (x, y) -> QColor object, where (x, y) are the coordinates of the pixel on the canvas.
'''
class CanvasHistory:
    # Our constructor will initialize our undo/redo stacks.
    def __init__(self):
        self.undo_stack = [] # To store our undo states.
        self.redo_stack = [] # To store our redo states.

    # When we draw on our canvas, we'll need to save the current state of our canvas.
    # The following method will handle this task.
    def save_state(self, pixels):
        # Adding our current state to the undo stack, so that we have the ability to undo our actions.
        # The pixels dictionary specifies the current state of our canvas.
        self.undo_stack.append(pixels.copy())

        # Once we've drawn on our canvas, we can no longer redo any actions. Thus, we'll clear the redo stack.
        self.redo_stack.clear()

    # This method is responsible for undoing the last action performed on our canvas.
    def undo(self, pixels):
        # If we can undo an action, we'll retrieve the last state of our canvas.
        if self.undo_stack:
            # First, we must save our current state to the redo stack. This will allow us to redo our actions.
            self.redo_stack.append(pixels.copy())

            # Next, we'll retrieve the last state of our canvas from the undo stack.
            pixels.clear()
            last_state = self.undo_stack.pop()
            
            # Finally, we'll update our canvas with the last state and return it.
            pixels = last_state
            return pixels

        # Otherwise, we'll simply return the current state of our canvas.
        return pixels

    # This method is responsible for redoing the last action performed on our canvas.
    def redo(self, pixels):
        # If we can redo an action, we'll retrieve the last state of our canvas.
        if self.redo_stack:
            # First, we must save our current state to the undo stack. This will allow us to undo our actions.
            self.undo_stack.append(pixels.copy())

            # Next, we'll retrieve the last state of our canvas from the redo stack.
            pixels.clear()
            last_state = self.redo_stack.pop()

            # Finally, we'll update our canvas with the last state and return it.
            pixels = last_state
            return pixels

        # Otherwise, we'll simply return the current state of our canvas.
        return pixels
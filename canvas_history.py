# Importing QColor to work with color objects.
from PyQt6.QtGui import QColor

'''
    A class to store the history of our canvas:
    Each state of our canvas will be represented by a dictionary of pixels w/ their respective colors.
    We'll also store a generated image pixmap for each state of our canvas.
    
    The structure of our dictionary will be as follows:
        (x, y) -> QColor object, where (x, y) are the coordinates of the pixel on the canvas.
'''
class CanvasHistory:
    # Our constructor will initialize our undo/redo stacks.
    def __init__(self):
        self.undo_stack = [] # To store our undo states.
        self.redo_stack = [] # To store our redo states.

    # This method will save the current state of our canvas to the undo stack.
    def save_state(self, pixels, generated_image=None):
        data = (pixels.copy(), generated_image)
        self.undo_stack.append(data)

    # When we draw on our canvas, we'll need to save the current state of our canvas and reset our redo stack.
    # The following method will handle this task.
    def save_state_and_update(self, pixels, generated_image=None):
        
        # Adding our current state to the undo stack so that we have the ability to undo our actions.
        # The pixels dictionary specifies the current state of our canvas.
        # The generated_image pixmap specifies the AI-generated image for the current state of our canvas.
        self.save_state(pixels, generated_image)

        # Once we've drawn on our canvas, we can no longer redo any actions. Thus, we'll clear the redo stack.
        self.redo_stack.clear()

    # This method is responsible for undoing the last action performed on our canvas.
    def undo(self, pixels, generated_image=None):
        # If we can undo an action, we'll retrieve the last state of our canvas.
        if self.undo_stack:
            # First, we must save our current state to the redo stack. This will allow us to redo our actions.
            data = (pixels.copy(), generated_image)
            self.redo_stack.append(data)

            # Next, we'll retrieve the last state of our canvas from the undo stack.
            pixels.clear()
            last_state, generated_image = self.undo_stack.pop()
            
            # Finally, we'll update our canvas with the last state and return it.
            pixels = last_state
            return (pixels, generated_image)

        # Otherwise, we'll simply return the current state of our canvas.
        return (pixels, generated_image)

    # This method is responsible for redoing the last action performed on our canvas.
    def redo(self, pixels, generated_image=None):
        # If we can redo an action, we'll retrieve the last state of our canvas.
        if self.redo_stack:
            # First, we must save our current state to the undo stack. This will allow us to undo our actions.
            self.save_state(pixels, generated_image)

            # Next, we'll retrieve the last state of our canvas from the redo stack.
            pixels.clear()
            last_state, generated_image = self.redo_stack.pop()

            # Finally, we'll update our canvas with the last state and return it.
            pixels = last_state
            return (pixels, generated_image)

        # Otherwise, we'll simply return the current state of our canvas.
        return (pixels, generated_image)
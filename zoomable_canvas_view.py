# Importing basic widgets from PyQt6.
from PyQt6.QtWidgets import QGraphicsView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QMouseEvent

class ZoomableCanvasView(QGraphicsView):

    def __init__(self, scene, canvas):
        # Storing our canvas to access its mouse events (for dragging purposes).
        self.canvas = canvas

        # Setting the scene for our view.
        super().__init__(scene)
        # Setting the transformation anchor to the mouse position. This allows us to zoom in/out based on the mouse position.
        # (A transformation anchor is the point in the view that remains fixed when the view is transformed.)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        # Setting the zoom factor and the min/max zoom factors.
        self.zoom_factor = 1.0
        self.min_zoom_factor = 1.0
        self.max_zoom_factor = 4.0

        # For dragging functionality, we'll need to store the last mouse position (to calculate how much we've dragged our mouse).
        self.last_mouse_pos = None 

    def wheelEvent(self, event):
        zoom_adjustment = 0.0
        # When the user scrolls up, we'll zoom in.
        if event.angleDelta().y() > 0:
            zoom_adjustment = 0.1
        # When the user scrolls down, we'll zoom out.
        else:
            zoom_adjustment = -0.1

        # If our modified zoom factor is within the acceptable range, we'll update our zoom factor.
        if self.min_zoom_factor <= self.zoom_factor + zoom_adjustment <= self.max_zoom_factor:
            self.zoom_factor += zoom_adjustment
            # To avoid issues w/ zooming, we'll set our transformation directly.
            self.setTransform(self.transform().fromScale(self.zoom_factor, self.zoom_factor))
            '''
            Here, self.transform() returns the current transformation matrix of our view.
            fromScale() creates a new transformation matrix using the current transformation matrix.
            We pass this new transformation matrix to setTransform() to update our view's transformation.
            '''

    # We'll override the mousePressEvent method to handle dragging functionality.
    def mousePressEvent(self, event):

        # If our canvas is draggable, we'll need to update our cursor and store our mouse position.
        if self.canvas.is_draggable:

            # We'll set our canvas cursor to a closed hand cursor to indicate that it's being dragged.
            self.canvas.setCursor(Qt.CursorShape.ClosedHandCursor)

            # We'll store the current mouse position to calculate how much we've dragged our mouse.
            self.last_mouse_pos = event.pos()

        # Otherwise, we'll fall back to the default behavior.
        else:
            super().mousePressEvent(event)
            

    # We'll override the mouseMoveEvent method to handle dragging functionality.
    def mouseMoveEvent(self, event):

        # If our canvas is draggable and we have a last mouse position, we'll update the position of our canvas.
        if self.canvas.is_draggable and self.last_mouse_pos:

            # We'll calculate the difference between the current mouse position and the last mouse position.
            delta = event.pos() - self.last_mouse_pos

            # Moving our scroll bars based on the difference between the current and last mouse positions.
            current_h_scroll_value = self.horizontalScrollBar().value()
            current_v_scroll_value = self.verticalScrollBar().value()
            self.horizontalScrollBar().setValue(current_h_scroll_value - delta.x())
            self.verticalScrollBar().setValue(current_v_scroll_value - delta.y())

            # Updating the last mouse position.
            self.last_mouse_pos = event.pos()

        # Otherwise, we'll fall back to the default behavior.
        else:
            super().mouseMoveEvent(event)

    # We'll override the mouseReleaseEvent method to handle dragging functionality.
    def mouseReleaseEvent(self, event):
        
        # To stop dragging, we'll need to reset our cursor and clear the last mouse position.
        if self.canvas.is_draggable:

            # We'll set our canvas cursor back to an open hand cursor.
            self.canvas.setCursor(Qt.CursorShape.OpenHandCursor)

            # Clearing the last mouse position.
            self.last_mouse_pos = None

        # Otherwise, we'll fall back to the default behavior.
        else:
            super().mouseReleaseEvent(event)


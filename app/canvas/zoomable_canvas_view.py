# Importing basic widgets from PyQt6.
from PyQt6.QtWidgets import QGraphicsView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QMouseEvent, QTransform

class ZoomableCanvasView(QGraphicsView):

    def __init__(self, scene, proxy_widget):

        # Setting the scene for our view.
        super().__init__(scene)

        # Setting the transformation anchor to our mouse cursor's position.
        # (A transformation anchor is the point in the view that remains fixed when the view is transformed.)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        # Storing our proxy widget (to move around the canvas).
        self.proxy_widget = proxy_widget

        # Storing a direct reference to our canvas.
        self.canvas = self.proxy_widget.widget()

        # Storing our tool manager (to access the current tool).
        self.tools = None

        # Disabling scroll bars for our view.
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Setting the zoom factor and the min/max zoom factors.
        self.zoom_factor = 1.0
        self.min_zoom_factor = 0.01
        self.max_zoom_factor = 4.0

        # For dragging functionality, we'll need to store the last mouse position (to calculate how much we've dragged our mouse).
        self.last_mouse_pos = None 

    # A method to set our tool manager.
    def set_tools(self, tools):
        self.tools = tools

    def wheelEvent(self, event):
        zoom_adjustment = 1.1 if event.angleDelta().y() > 0 else 0.9
        new_zoom_factor = self.zoom_factor * zoom_adjustment

        # If our modified zoom factor is within the acceptable range, we'll update our zoom factor.
        if self.min_zoom_factor <= new_zoom_factor <= self.max_zoom_factor:
            self.zoom_factor = new_zoom_factor
            # To avoid issues w/ zooming, we'll set our transformation directly.
            self.setTransform(self.transform().fromScale(self.zoom_factor, self.zoom_factor))
            '''
            Here, self.transform() returns the current transformation matrix of our view.
            fromScale() creates a new transformation matrix using the current transformation matrix.
            We pass this new transformation matrix to setTransform() to update our view's transformation.
            '''

    # We'll override the mousePressEvent method to handle dragging functionality.
    def mousePressEvent(self, event):
        
        # If the middle mouse button is pressed, we'll make our canvas draggable.
        if event.button() == Qt.MouseButton.MiddleButton:
            
            # We'll set our canvas to be draggable.
            self.canvas.set_draggable(True)

        # If our canvas is draggable, we'll need to update our cursor and store our mouse position.
        if self.canvas.is_draggable:

            # We'll set our cursor to a closed hand cursor to indicate that it's being dragged.
            self.proxy_widget.setCursor(Qt.CursorShape.ClosedHandCursor)

            # We'll store the current mouse position to calculate how much we've dragged our mouse.
            # Note: We'll store the mouse position in scene coordinates.
            self.last_mouse_pos = self.mapToScene(event.pos())

        # Otherwise, we'll fall back to the default behavior.
        else:
            super().mousePressEvent(event)
            

    # We'll override the mouseMoveEvent method to handle dragging functionality.
    def mouseMoveEvent(self, event):

        # If our canvas is draggable and we have a last mouse position, we'll update the position of our canvas.
        if self.canvas.is_draggable and self.last_mouse_pos:

            # We'll calculate the difference between the current mouse position and the last mouse position.
            current_mouse_pos = self.mapToScene(event.pos())
            delta = current_mouse_pos - self.last_mouse_pos

            # Updating the position of our proxy widget (which moves our canvas).
            proxy_pos = self.proxy_widget.pos()
            self.proxy_widget.setPos(proxy_pos + delta)

            # Updating the last mouse position.
            self.last_mouse_pos = current_mouse_pos

        # Otherwise, we'll fall back to the default behavior.
        else:
            super().mouseMoveEvent(event)

    # We'll override the mouseReleaseEvent method to handle dragging functionality.
    def mouseReleaseEvent(self, event):
        
        # To stop dragging, we'll need to reset our cursor and clear the last mouse position.
        if self.canvas.is_draggable:

            # If our middle mouse button is released, we'll make our canvas non-draggable and allow for drawing.
            if event.button() == Qt.MouseButton.MiddleButton:
                
                # Setting our cursor to be an arrow cursor.
                self.proxy_widget.setCursor(Qt.CursorShape.ArrowCursor)
                
                # Using our tool manager to set the current tool to the pencil tool.
                self.tools.use_pencil_tool()

            # Otherwise, we'll set our cursor back to an open hand cursor as it's still draggable.
            else:
                self.proxy_widget.setCursor(Qt.CursorShape.OpenHandCursor)

            # Clearing the last mouse position.
            self.last_mouse_pos = None

        # Otherwise, we'll fall back to the default behavior.
        else:
            super().mouseReleaseEvent(event)


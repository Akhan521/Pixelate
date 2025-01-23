# Importing basic widgets from PyQt6.
from PyQt6.QtWidgets import QGraphicsView

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
        self.min_zoom_factor = 0.5
        self.max_zoom_factor = 4.0

    def wheelEvent(self, event):
        zoom_adjustment = 0.0
        # When the user scrolls up, we'll zoom in.
        dir = "zooming in" if event.angleDelta().y() > 0 else "zooming out"
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
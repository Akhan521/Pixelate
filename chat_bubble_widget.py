
# Importing the necessary libraries.
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QSize

# Our chat bubble widget that will hold the user's and Pixi's messages. These will be displayed in our list widget.
class ChatBubbleWidget(QWidget):

    def __init__(self, message, is_user, list_widget):

        super().__init__()

        # To handle sizing of our chat bubble widget, we'll store the list widget that will hold it.
        self.list_widget = list_widget

        # Storing whether the message is from the user or Pixi.
        self.is_user = is_user

        # A label to store our message.
        self.message_label = QLabel(message, self)

        # Setting the word wrap property to True to allow for line wrapping.
        self.message_label.setWordWrap(True)

        # Setting the margin and alignment of our label.
        self.message_label.setMargin(10)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        # Using a vertical layout for our chat bubble widget.
        layout = QVBoxLayout()

        # Setting the spacing and margins of our layout.
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Adding our message label to the layout.
        layout.addWidget(self.message_label)

        # Setting the layout of our chat bubble widget.
        self.setLayout(layout)

        # Setting our style sheet.
        self.setStyleSheet(self.get_style())

    # A function to return the size hint of our chat bubble widget (to dynamically adjust its size based on the message).
    def sizeHint(self):

        # The width of our chat bubble widget will be the width of the list widget that holds it.
        width = self.list_widget.width() - 15  # Subtracting 15 to account for padding.

        # The height of our chat bubble widget will be the height required to display the message.
        height = self.message_label.heightForWidth(width)

        return QSize(width, height)

    # A function to return the style of our chat bubble widget (based on whether the message is from the user or Pixi).
    def get_style(self):

        # If the message is from the user, we'll use a darker shade of gray.
        if self.is_user:
            background_color = "#444"

        # If the message is from Pixi, we'll use a lighter shade of gray.
        else:
            background_color = "#888"

        # Returning the style of our chat bubble widget.
        return f'''
            QWidget {{
                background-color: {background_color};
                border-radius: 10px;
            }}
            QLabel {{
                color: white;
            }}
        '''
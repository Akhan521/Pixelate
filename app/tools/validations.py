# All validation methods are defined here.

# A method to validate the dimensions of our canvas (provided from a text file).
def validate_dimensions(dimensions):

    # If the dimensions are not a tuple of size 2, we'll return False.
    if not isinstance(dimensions, tuple) or len(dimensions) != 2:
        return False

    # If any of the dimensions are not integers, we'll return False.
    for dimension in dimensions:
        if not isinstance(dimension, int):
            return False

    return True

# A method to validate our imported data (used to check whether our data is in the correct format).
# Ideally, our data (pixels dict.) should be in the form: {(x,y): rgba_tuple}.
def validate_imported_data(pixels):
    
    # If our data is not a dictionary, we'll return False.
    if not isinstance(pixels, dict):
        return False

    # Our pixels dict. must be in the form: {(x,y): rgba_tuple}.
    for pixel_coords, rgba_tuple in pixels.items():

        # If the pixel coordinates are not a tuple of size 2, we'll return False.
        if not isinstance(pixel_coords, tuple) or len(pixel_coords) != 2:
            return False

        # If any of the pixel coordinates are not integers, we'll return False.
        for pixel_coord in pixel_coords:
            if not isinstance(pixel_coord, int):
                return False

        # If the rgba tuple is not a tuple of size 4, we'll return False.
        if not isinstance(rgba_tuple, tuple) or len(rgba_tuple) != 4:
            return False

        # If any of the rgba values are not integers, we'll return False.
        for rgba_value in rgba_tuple:
            if not isinstance(rgba_value, int):
                return False

    return True
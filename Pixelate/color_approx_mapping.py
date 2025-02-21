'''
To handle color approximation, we'll map a color to its closest color from a predefined mapping of colors.
We'll use the CIE76 color difference formula to calculate the distance between two colors.
To perform the mapping, we'll use a dictionary to store predefined color names and their corresponding QColor objects.
We'll then iterate over the dictionary to find the closest color to the input color.

Note: We implement the CIE76 color difference formula using the colormath library.
'''

import numpy
from PyQt6.QtGui import QColor
from colormath.color_objects import LabColor, sRGBColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie1976

# DISCLAIMER: delta_e_cie1976() uses numpy.asscalar() which is deprecated, so we'll patch it to use numpy.item() instead.
def patch_asscalar(x):
    return x.item()
setattr(numpy, 'asscalar', patch_asscalar)

class ColorApproximator:

    def __init__(self):

        # A dictionary to store predefined color names and their corresponding QColor objects.
        self.color_mapping = {
            # Basic Colors
            "White": QColor(255, 255, 255), "Black": QColor(0, 0, 0),
            "Red": QColor(255, 0, 0), "Green": QColor(0, 255, 0),
            "Blue": QColor(0, 0, 255), "Yellow": QColor(255, 255, 0),
            "Cyan": QColor(0, 255, 255), "Magenta": QColor(255, 0, 255),
            "Orange": QColor(255, 165, 0), "Purple": QColor(128, 0, 128),
            "Pink": QColor(255, 192, 203), "Brown": QColor(165, 42, 42),
            "Gray": QColor(128, 128, 128), "Maroon": QColor(128, 0, 0),
            "Olive": QColor(128, 128, 0), "Navy": QColor(0, 0, 128),
            "Teal": QColor(0, 128, 128), "Lime": QColor(0, 255, 0),
            "Aqua": QColor(0, 255, 255), "Fuchsia": QColor(255, 0, 255),
            "Silver": QColor(192, 192, 192), "Indigo": QColor(75, 0, 130),
            "Violet": QColor(238, 130, 238), "Beige": QColor(245, 245, 220),
            "Coral": QColor(255, 127, 80), "Gold": QColor(255, 215, 0),
            "Bronze": QColor(205, 127, 50), "Copper": QColor(184, 115, 51),
            "Platinum": QColor(229, 228, 226), "Steel": QColor(176, 196, 222),
            "Ruby": QColor(224, 17, 95), "Emerald": QColor(0, 201, 87),
            "Sapphire": QColor(15, 82, 186), "Amethyst": QColor(153, 102, 204),
            "Topaz": QColor(255, 200, 124), "Jade": QColor(0, 168, 107),
            "Obsidian": QColor(0, 0, 0), "Pearl": QColor(234, 224, 200),
            "Crimson": QColor(220, 20, 60), "Scarlet": QColor(255, 36, 0),
            "Cerulean": QColor(0, 123, 167), "Periwinkle": QColor(204, 204, 255),
            "Lilac": QColor(200, 162, 200), "Turquoise": QColor(64, 224, 208),
            "Amber": QColor(255, 191, 0), "Rose": QColor(255, 102, 178),
            "Mint": QColor(189, 252, 201), "Peach": QColor(255, 218, 185),
            "Salmon": QColor(250, 128, 114), "Lavender": QColor(230, 230, 250),
            "Khaki": QColor(240, 230, 140), "Cobalt": QColor(0, 71, 171),
            "Tangerine": QColor(255, 127, 0), "Auburn": QColor(165, 42, 42),
            "Grape": QColor(115, 44, 122), "Plum": QColor(142, 69, 133),
            "Clementine": QColor(255, 117, 24), "Velvet": QColor(99, 3, 51),
            "Iris": QColor(90, 79, 173), "Saffron": QColor(255, 153, 51),
            "Bubblegum": QColor(255, 153, 204), "Mango": QColor(255, 130, 67),
            "Chili": QColor(227, 38, 54), "Daffodil": QColor(255, 255, 49),
            "Ginger": QColor(194, 95, 28), "Honey": QColor(235, 150, 5),
            "Lemon": QColor(255, 247, 0), "Orchid": QColor(218, 112, 214),
            "Pumpkin": QColor(255, 117, 24), "Rust": QColor(183, 65, 14),
            "Sand": QColor(194, 178, 128), "Sky": QColor(135, 206, 235),
            "Taupe": QColor(72, 60, 50), "Wine": QColor(114, 47, 55),
            "Zinnia": QColor(255, 194, 132), "Ash": QColor(178, 190, 181),
            "Berry": QColor(153, 50, 204), "Cream": QColor(255, 253, 208),
            "Frost": QColor(228, 247, 255), "Glow": QColor(255, 252, 153),
            "Haze": QColor(183, 210, 227), "Ice": QColor(173, 216, 230),
            "Jet": QColor(52, 52, 52), "Kelp": QColor(69, 93, 71),
            "Lava": QColor(207, 16, 32), "Mist": QColor(196, 212, 216),
            "Nectar": QColor(255, 188, 117), "Opal": QColor(168, 195, 188),
            "Quartz": QColor(217, 208, 193), "Slate": QColor(112, 128, 144),
            "Tide": QColor(0, 128, 128), "Umber": QColor(99, 81, 71),
            "Vapor": QColor(240, 248, 255), "Willow": QColor(113, 166, 133),
            "Xanadu": QColor(115, 134, 120), "Yarrow": QColor(255, 204, 0),
            "Zest": QColor(229, 155, 15),

            # Nature-Inspired Colors
            "Forest": QColor(34, 139, 34), "Sea": QColor(46, 139, 87),
            "Olive": QColor(107, 142, 35), "Sandy": QColor(244, 164, 96),
            "Midnight": QColor(25, 25, 112), "Deep Sky": QColor(0, 191, 255),
            "Slate": QColor(112, 128, 144), "Pale Turquoise": QColor(175, 238, 238),

            # Earthy & Neutral Tones
            "Charcoal": QColor(54, 69, 79), "Eggshell": QColor(240, 234, 214),
            "Stone": QColor(144, 138, 133), "Sienna": QColor(160, 82, 45),
            "Umber": QColor(99, 81, 71),

            # Vibrant & Pastel Shades
            "Crimson": QColor(220, 20, 60), "Cerulean": QColor(0, 123, 167),
            "Coral": QColor(248, 131, 121), "Spring": QColor(0, 255, 127),

            # Metallics & Gemstones
            "Rose Gold": QColor(183, 110, 121), "Gunmetal": QColor(42, 52, 57),
            "Champagne": QColor(247, 231, 206), "Amber": QColor(255, 191, 0),

            # Fantasy & Exotic Colors
            "Dragon": QColor(220, 42, 119), "Galaxy": QColor(70, 0, 122),
            "Mystic": QColor(0, 128, 128), "Sunset": QColor(255, 94, 77),
            "Electric": QColor(125, 249, 255), "Neon": QColor(57, 255, 20),
            "Flamingo": QColor(252, 142, 172), "Lemon": QColor(255, 250, 205),
            "Cotton": QColor(255, 188, 217), "Ice": QColor(173, 216, 230),

            # More Vibrant Colors
            "Sunflower": QColor(255, 218, 51), "Rose": QColor(255, 102, 178),
            "Lime": QColor(204, 255, 0), "Electric": QColor(191, 0, 255),
            "Neon": QColor(255, 20, 147), "Neon Blue": QColor(50, 137, 255),
            "Berry": QColor(204, 0, 204), "Neon Green": QColor(57, 255, 20),
            "Neon Yellow": QColor(255, 255, 0), "Neon Orange": QColor(255, 117, 24),
            "Neon Pink": QColor(255, 105, 180), "Neon Purple": QColor(153, 0, 153),
            "Neon Red": QColor(255, 0, 0), "Neon Cyan": QColor(0, 255, 255),

            # Pastel Tones
            "Cotton": QColor(191, 255, 255), "Lavender": QColor(255, 182, 193),
            "Baby": QColor(137, 207, 240), "Powder": QColor(255, 209, 220),
            "Peachy": QColor(254, 185, 160), "Mint": QColor(152, 255, 152),
            "Powder": QColor(255, 236, 187), "Lilac": QColor(216, 191, 216),

            # Nature-Inspired Hues
            "Autumn": QColor(255, 140, 0), "Rainforest": QColor(26, 77, 55),
            "Spring": QColor(64, 225, 132), "Ocean": QColor(0, 150, 136),
            "Grass": QColor(87, 166, 57), "Pine": QColor(22, 94, 48),
            "Dew": QColor(204, 255, 204),

            # Warm & Earthy Tones
            "Desert": QColor(237, 201, 175), "Clay": QColor(200, 75, 0),
            "Rust": QColor(183, 65, 14), "Golden": QColor(204, 153, 0),
            "Pumpkin": QColor(255, 117, 24), "Cinnamon": QColor(210, 105, 30),
            "Copper": QColor(139, 69, 19), "Walnut": QColor(132, 60, 44),

            # Cool & Calm Colors
            "Iceberg": QColor(152, 245, 255), "Arctic": QColor(240, 248, 255),
            "Storm": QColor(169, 169, 169), "Cloud": QColor(248, 248, 255),
            "Soft": QColor(176, 224, 230), "Mint": QColor(245, 255, 250),
            "Silver": QColor(192, 192, 192), "Steel": QColor(70, 130, 180),

            # Deep & Dark Shades
            "Midnight": QColor(25, 25, 112), "Violet": QColor(148, 0, 211),
            "Charcoal": QColor(54, 69, 79), "Slate": QColor(106, 90, 205),
            "Indigo": QColor(75, 0, 130), "Burgundy": QColor(128, 0, 32),
            "Night": QColor(0, 0, 128),

            # Light & Fresh Shades
            "Pale": QColor(255, 255, 204), "Lavender": QColor(230, 230, 250),
            "Buttercup": QColor(255, 241, 118), "Mint": QColor(189, 252, 201),
            "Coral": QColor(240, 128, 128), "Floral": QColor(255, 182, 193),
            "Lemon": QColor(255, 247, 0), "Cream": QColor(255, 249, 220),

            # Additional Colors
            "Cobalt": QColor(0, 71, 171), "Emerald": QColor(0, 128, 0),
            "Rosewood": QColor(101, 0, 11), "Tangerine": QColor(255, 127, 0),
            "Amethyst": QColor(153, 102, 204), "Moss": QColor(138, 154, 91),
            "Peony": QColor(249, 163, 169), "Auburn": QColor(165, 42, 42),
            "Frostbite": QColor(255, 103, 163), "Limeade": QColor(188, 255, 0),
            "Butterscotch": QColor(255, 133, 0), "Turquoise": QColor(0, 199, 140),
            "Lush": QColor(0, 204, 85), "Seafoam": QColor(158, 255, 217),
            "Champagne": QColor(255, 218, 185), "Grape": QColor(115, 44, 122),
            "Storm": QColor(169, 169, 169), "Zinnia": QColor(255, 194, 132),
            "Cherry": QColor(255, 186, 201), "Sunset": QColor(255, 160, 122),
            "Taffy": QColor(255, 184, 199), "Lime": QColor(227, 255, 0),
            "Taffy": QColor(251, 153, 198), "Indigo": QColor(66, 75, 99),
            "Coral": QColor(255, 114, 87), "Tawny": QColor(205, 127, 50),
            "Caramel": QColor(255, 184, 77), "Peach": QColor(255, 218, 185),
            "Goldenrod": QColor(218, 165, 32), "Emerald": QColor(0, 128, 0),
            "Spice": QColor(176, 58, 43), "Gingerbread": QColor(169, 101, 59),
            "Bluebell": QColor(147, 112, 219), "Vermilion": QColor(227, 66, 52),
            "Cinnamon": QColor(153, 101, 21), "Plum": QColor(142, 69, 133),
            "Crimson": QColor(220, 20, 60), "Clementine": QColor(255, 117, 24),
            "Peach": QColor(255, 218, 185), "Tangerine": QColor(255, 140, 0),
            "Velvet": QColor(99, 3, 51), "Grape": QColor(83, 59, 118),
            "Fuchsia": QColor(255, 0, 255), "Pineapple": QColor(255, 225, 53),
            "Saffron": QColor(255, 153, 51), "Ruby": QColor(224, 17, 95),
            "Mint": QColor(174, 255, 156), "Bubblegum": QColor(255, 153, 204),
            "Iris": QColor(90, 79, 173), "Golden": QColor(255, 223, 0),
            "Lemonade": QColor(255, 253, 115), "Platinum": QColor(229, 228, 226),
            "Lavender": QColor(230, 230, 250), "Chocolate": QColor(61, 43, 31),
            "Orange": QColor(255, 115, 0), "Frosted": QColor(230, 230, 250),
            "Daffodil": QColor(255, 255, 49), "Ginger": QColor(194, 95, 28),
            "Lime": QColor(206, 255, 0), "Mango": QColor(255, 130, 67),
            "Chili": QColor(227, 38, 54), "Milk": QColor(255, 255, 255),
            "Tangerine": QColor(254, 133, 89), "Sun": QColor(255, 215, 0),
            "Peach": QColor(255, 181, 149),
        }

    # A method to convert a QColor object to a LabColor object (CIELAB color space).
    def qcolor_to_lab(self, color):

        rgb_color = sRGBColor(color.red(), color.green(), color.blue(), is_upscaled=True)
        lab_color = convert_color(rgb_color, LabColor)

        return lab_color
    
    # Given an input color (QColor object), find the closest color from the predefined color mapping.
    def closest_color_cie76(self, input_color):

        # First, we'll convert the input color to the Lab color space.
        input_color = self.qcolor_to_lab(input_color)

        # Initializing the minimum distance and closest color.
        min_distance = float("inf")
        closest_color = None

        # Iterating over the predefined color mapping. The keys are color names, and the values are QColor objects.
        for name, color in self.color_mapping.items():

            # Converting the predefined color to the Lab color space.
            predefined_color = self.qcolor_to_lab(color)

            # Calculating the color difference between the input color and the predefined color using the CIE76 formula.
            distance = delta_e_cie1976(input_color, predefined_color)

            # If the current predefined color is a better approximation, update our parameters.
            if distance < min_distance:
                min_distance = distance
                closest_color = name

        return closest_color

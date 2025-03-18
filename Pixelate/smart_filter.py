from PyQt6.QtGui import QColor
import numpy as np

def rgb_to_lms(r, g, b):
    L = (17.8824 * r) + (43.5161 * g) + (4.11935 * b)
    M = (3.45565 * r) + (27.1554 * g) + (3.86714 * b)
    S = (0.0299566 * r) + (0.184309 * g) + (1.46709 * b)
    return np.array([L, M, S])

def simulate_cvd(lms, cvd_matrix):
    return np.dot(cvd_matrix, lms)

def lms_to_rgb(l, m, s):
    r = (0.0809444479 * l) + (-0.130504409 * m) + (0.116721066 * s)
    g = (-0.0102485335 * l) + (0.0540193266 * m) + (-0.113614708 * s)
    b = (-0.000365296938 * l) + (-0.00412161469 * m) + (0.693511405 * s)
    return np.array([r, g, b])

def apply_error_modifications(r, g, b):
    R = 0.0 * r + 0.0 * g + 0.0 * b
    G = 0.7 * r + 1.0 * g + 0.0 * b
    B = 0.7 * r + 0.0 * g + 1.0 * b
    return np.array([R, G, B])

def daltonize(qcolor, cvd_type):
    if cvd_type != "Protanopia" and cvd_type != "Deuteranopia" and cvd_type != "Tritanopia":
        return qcolor
    
    r, g, b = qcolor.redF(), qcolor.greenF(), qcolor.blueF()
    
    # Convert RGB to LMS
    lms = rgb_to_lms(r, g, b)
    
    # Color Vision Deficiency matrices
    CVDMatrix = {
        "Protanopia": np.array([[0.0, 2.02344, -2.52581],
                                  [0.0, 1.0, 0.0],
                                  [0.0, 0.0, 1.0]]),
        "Deuteranopia": np.array([[1.0, 0.0, 0.0],
                                   [0.494207, 0.0, 1.24827],
                                   [0.0, 0.0, 1.0]]),
        "Tritanopia": np.array([[1.0, 0.0, 0.0],
                                 [0.0, 1.0, 0.0],
                                 [-0.395913, 0.801109, 0.0]])
    }
    
    cvd_matrix = CVDMatrix[cvd_type]
    simulated_lms = simulate_cvd(lms, cvd_matrix)
    simulated_rgb = lms_to_rgb(*simulated_lms)
    
    # Calculate error matrix
    error = np.array([r, g, b]) - simulated_rgb
    
    # Apply error modifications
    compensation = apply_error_modifications(*error)
    final_rgb = np.clip(compensation + np.array([r, g, b]), 0, 1)
    
    # Convert back to QColor
    return QColor.fromRgbF(*final_rgb)

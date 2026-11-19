# File to detect balloons using openCV

import cv2
import numpy as np
def make_color_mask(image,hsv_low,hsv_high):
    """ Function to create a color mask for using an image 
    Args:
        image: The image to perform color mask
        hsv_low: The lower bound of the HSV range (H,S,V)
        hsv_high: The upper bound of the HSV range (H,S,V)
    Returns:
        mask: The color mask as a matrix
    """
    # First, convert image to HSV 
    hsv = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
    # Then, create the color mask using hsv_low and hsv_high (convert to numpy array)
        # cv2.inRange returns values within the HSV range as 255 (white) and values outside as 0 (black)
    mask = cv2.inRange (hsv, np.array(hsv_low), np.array(hsv_high))
    return mask


def get_hsv_bounds(color):
    """ Function to fetch hsv bounds.
    Args:
        color: The color of the bounds being fetched
    Returns:
        low,high tuples of the hsv range
    """
    match color:
        case "blue":
            return (110, 65, 65), (123, 170, 180)
        case "green":
            return (40, 80, 80), (80, 255, 255)
        case _:
            raise ValueError("Unknown color")

def detect_balloon_color(image,color):
    """ Detect the largest blob of a specific color 
    Args:
        image: Image to detect color
        color: The desired color to detect
    Returns:
        The circle center coordinates and radius of the largest color blob
    """
    # Check color input using the HSV ranges for those colors
    hsv_low, hsv_high = get_hsv_bounds(color)
    # Create the color mask
    mask = make_color_mask(image,hsv_low,hsv_high)

    # Find outer boundaries of white blobs in binary mask 
    contours,hierarchy = cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

    # If no contours, return none
    if not contours:
        return None

    # Find the contour with the largest enclosed area
    largest = max(contours,key=cv2.contourArea)
    # Get the center coordinate and radius of the circle
    (u,v), radius = cv2.minEnclosingCircle(largest)
    return u,v,radius

def detect_balloons(image):
    """ Detect all the balloons in an image
    Args:
        image: The image to detect all balloons in
    Returns:
        detect_list: The list of detections as (u,v,radius)
    """
    # List of detections to use
    detection_list = []
    for color in ("blue","green"):
        # Add detection to list
        detection = detect_balloon_color(image,color)
        if detection is not None:
            detection_list.append(detection)
    return detection_list
            


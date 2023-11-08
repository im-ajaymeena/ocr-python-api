import io
import base64
import re
import pytesseract
from PIL import Image


def tesseract_ocr(PILimage):
    """
    ocr inference using pytesseract
    """
    text = pytesseract.image_to_string(PILimage)
    return text

def base64_to_PILimage(base64image):
    """
    Given a base64 encoded image it will decode and check validity of image and convert to a PILimage
    """
    try:
        base64image = re.sub('^data:image/.+;base64,', '', base64image)
        decoded_image_bytes = base64.b64decode(base64image)

        image_bytesio = io.BytesIO(decoded_image_bytes)

        image = Image.open(image_bytesio)
        image.copy().verify()
    except:
        raise ValueError("incompatible base64 encoding")

    return image

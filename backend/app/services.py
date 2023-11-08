from PIL import Image

import io
import base64
import re
import pytesseract
import concurrent.futures


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


def imagedata_to_PILimages(imagedata):
    """
    convert single/list of imagedata (base64 encoded images) into a PILimage/PILimages
    """


    if isinstance(imagedata, str):
        return base64_to_PILimage(imagedata)

    images = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
        image_futures = [executor.submit(base64_to_PILimage, base64image) for base64image in imagedata]
        images = [future.result() for future in concurrent.futures.as_completed(image_futures)]

    return images

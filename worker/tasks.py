import os
from celery import Celery, subtask, group, states
from celery.result import allow_join_result
from services import tesseract_ocr, base64_to_PILimage

app = Celery(
    "tasks",
    broker=os.environ.get('CELERY_BROKER_URL'),
    backend=os.environ.get('CELERY_RESULT_BACKEND'),
    worker_prefetch_multiplier=1
)


@app.task(name='ocr', bind=True)
def task_ocr(self, image_data):
    """
    Perform Optical Character Recognition (OCR) on images.

    This task performs OCR on provided image data. If a single image is provided,
    it returns the extracted text from that image. If multiple images are provided,
    it parallelly processes each image using subtasks and run them parallely with celery groups and 
    returns a list of result of each subtask texts.

    Args:
        image_data (Union[str, List[str]]): Base64-encoded image data or list of image data.

    Returns:
        Union[str, List[str]]: Extracted text from the image(s) or a list of extracted texts.
    """
    if isinstance(image_data, str):
        try:
            pil_image = base64_to_PILimage(image_data)
        except:
            self.update_state(state=states.FAILURE, meta='Invalid input image data')
            raise
        text = tesseract_ocr(pil_image)
        return text

    subtasks = []
    for base64image in image_data:
        subtasks.append(subtask('subtask_tesseract_ocr', args=(base64image,)))

    # Execute the subtasks in parallel
    result_group = group(subtasks).apply_async()
    with allow_join_result():
        return result_group.get()


@app.task(name='subtask_tesseract_ocr')
def subtask_tesseract_ocr(base64image):
    """
    Subtask for performing OCR on a single image.

    This subtask takes a base64-encoded image data and performs OCR on it using the Tesseract OCR engine.

    Args:
        base64image (str): Base64-encoded image data.

    Returns:
        str: Extracted text from the image, or None if OCR processing fails.
    """
    try:
        pil_image = base64_to_PILimage(base64image)
        text = tesseract_ocr(pil_image)
        return text
    except:
        return None

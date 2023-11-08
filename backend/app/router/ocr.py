import asyncio
import json
import websockets
from fastapi import HTTPException, APIRouter, WebSocket
from celery_client import celery_client
from celery.result import AsyncResult
from celery import states
from schemas import OCRInput
from services import tesseract_ocr, imagedata_to_PILimages

router = APIRouter()

@router.post("/image-sync", tags=["OCR-SYNC"])
def ocr_synchronous(request_input: OCRInput):
    """
    Perform synchronous OCR (Optical Character Recognition) on provided image data.

    This endpoint accepts image data and performs OCR on it. If a single image is provided,
    the OCR result is returned as text. If multiple images are provided, a list of OCR
    results corresponding to each image is returned.

    Args:
        input (OCRInput): The input containing the image_data: Union[str, list[str]].

    Returns:
        dict: If a single image is provided, returns {'text': OCR result}.
              If multiple images are provided, returns {'text': [OCR results]}.
    """
    image_data = request_input.image_data

    try:
        PILimages = imagedata_to_PILimages(image_data)

        if not(isinstance(PILimages, list)):
            output = tesseract_ocr(PILimages)
            return {'text': output}
        
        outputs = []
        for image_bytesio in PILimages:
            outputs.append(tesseract_ocr(image_bytesio))
        
        return {'text': outputs}
    
    except ValueError:
        return HTTPException(status_code=400, detail="Invalid input image data")


@router.post("/image", tags=["OCR-ASYNC"])
def ocr_create_task(request_input: OCRInput):
    """
    Initiate an asynchronous OCR task.

    This endpoint accepts image data and initiates an asynchronous OCR task using Celery.
    It returns a task ID that can be used to query the status and result of the task.

    Args:
        input (OCRInput): The input containing the image_data: Union[str, list[str]].

    Returns:
        dict: {'task_id': Task ID of the initiated OCR task}.
    """
    image_data = request_input.image_data

    task = celery_client.send_task('ocr', args=[image_data])

    return {'task_id': task.id}


@router.get("/image", tags=["OCR-ASYNC"])
def ocr_task_result(task_id: str):
    """
    Retrieve the result of an asynchronous OCR task.

    This endpoint takes a task ID and retrieves the result of an asynchronous OCR task.
    If the task is successful, it returns the OCR text result. If the task is pending or failed,
    it returns None.

    Args:
        task_id (str): Task ID of the OCR task.

    Returns:
        dict: If the task is pending or failed, returns {'text': null}.
              If the task is successful, returns {'text': OCR result}.
              If multiple images are provided, returns {'text': [OCR results]}.
    """

    task_result = AsyncResult(task_id, app=celery_client)
    
    if task_result.state == 'SUCCESS':
        return {'text': task_result.get()}
        
    return {'text': None}


@router.websocket("/watch-task")
async def watch_task_result(ws: WebSocket, task_id: str):
    """
    Watch the progress and result of an asynchronous OCR task.

    This WebSocket endpoint allows real-time monitoring of an asynchronous OCR task's progress.
    It sends status updates and, once the task is successful, sends the OCR result.

    Args:
        task_id (str): Task ID of the OCR task.
    
    This can be ran from bash with the following command:
    wscat -c ws://localhost:5000/watch-task?task_id={task_id}
    """
    try:
        await ws.accept()

        task_result = AsyncResult(task_id, app=celery_client)
        while task_result.state != 'SUCCESS':
            await asyncio.sleep(1)
            task_result = AsyncResult(task_id, app=celery_client)
            await ws.send_text(f'task id: {task_id} Pending')
            if task_result.state == states.FAILURE:
                await ws.send_text(f'task id: {task_id} FAILED')
                await ws.close()
        
        serializable_result = json.dumps({'text': task_result.get()})
        await ws.send_text(f'Result for task id: {task_id}')
        await ws.send_text(serializable_result)
        await ws.close(reason="successfully returned task result")

    except websockets.exceptions.ConnectionClosedOK:
        await ws.close()

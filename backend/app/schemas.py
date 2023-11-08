from typing import Union
from pydantic import BaseModel

class OCRInput(BaseModel):
    image_data: Union[str, list[str]]

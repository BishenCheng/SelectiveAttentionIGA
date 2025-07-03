from typing import List
from models import VaseCode
from pydantic import BaseModel

class VaseSVGResponse(BaseModel):
    svg_path: str
from pydantic import BaseModel
from typing import List, Dict, Optional


class LandmarkPoint(BaseModel):
    x: float
    y: float


class CropJobRequest(BaseModel):
    image: str
    landmarks: List[LandmarkPoint]
    segmentation_map: str


class CropJobResponse(BaseModel):
    id: str
    status: str


class CropJobStatusResponse(CropJobResponse):
    svg: Optional[str] = None
    mask_contours: Optional[Dict] = None

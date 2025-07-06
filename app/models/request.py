from pydantic import BaseModel

class LandmarkPoint(BaseModel):
    x: float
    y: float

class SubmitRequest(BaseModel):
    image: str
    segmentation_map: str
    landmarks: list[LandmarkPoint]
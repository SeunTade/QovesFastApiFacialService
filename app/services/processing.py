import base64
import io
import cv2
import numpy as np
from typing import List, Tuple, Dict, Any
from PIL import Image
import json

def create_svg(image_b64: str, segmentation_b64: str, landmarks: List[Dict[str, float]]) -> Tuple[str, Dict[int, List[Tuple[int, int]]]]:
    image_data = base64.b64decode(image_b64)
    seg_data = base64.b64decode(segmentation_b64)

    image = np.array(Image.open(io.BytesIO(image_data)).convert("RGB"))
    seg = np.array(Image.open(io.BytesIO(seg_data)).convert("L"))

    if len(landmarks) >= 2:
        dx = landmarks[1]['x'] - landmarks[0]['x']
        dy = landmarks[1]['y'] - landmarks[0]['y']
        angle = np.degrees(np.arctan2(dy, dx))
        center = (image.shape[1] // 2, image.shape[0] // 2)
        rot_mat = cv2.getRotationMatrix2D(center, angle, 1.0)
        image = cv2.warpAffine(image, rot_mat, (image.shape[1], image.shape[0]))
        seg = cv2.warpAffine(seg, rot_mat, (seg.shape[1], seg.shape[0]))

    mask_contours: Dict[int, List[Tuple[int, int]]] = {}
    unique_regions = np.unique(seg)

    for region in unique_regions:
        if region == 0:
            continue

        mask = np.uint8(seg == region) * 255
        mask = np.array(mask, dtype=np.uint8)
        contours, _ = cv2.findContours(mask.copy(), mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            simplified = cv2.approxPolyDP(largest_contour, 1.0, True)
            mask_contours[int(region)] = [(int(pt[0][0]), int(pt[0][1])) for pt in simplified]

    svg = "<svg xmlns='http://www.w3.org/2000/svg' width='{0}' height='{1}'>\n".format(image.shape[1], image.shape[0])
    for region_id, points in mask_contours.items():
        path = "M " + " L ".join("{},{}".format(x, y) for x, y in points)
        svg += "<path d='{0} Z' fill='none' stroke='red' stroke-width='2'/>\n".format(path)
    svg += "</svg>"

    return svg, mask_contours

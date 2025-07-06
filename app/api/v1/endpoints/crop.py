from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import SVGRecord
from app.worker import app as celery_app
from app.api.v1.schemas.schema import CropJobRequest, CropJobResponse, CropJobStatusResponse
from uuid import uuid4
import json

router = APIRouter()


@router.post("/submit", response_model=CropJobResponse)
def submit_crop_job(payload: CropJobRequest, db: Session = Depends(get_db)):
    job_id = str(uuid4())

    # Fix: Use empty string for svg, mask_contours instead of None
    job = SVGRecord(
        id=job_id,
        hash="",
        svg="",
        mask_contours="",
        status="pending"
    )

    db.add(job)
    db.commit()

    # Use Celery registered task name
    celery_app.send_task("app.services.job_queue.process_svg_job", args=[job_id, payload.dict()])

    return CropJobResponse(id=job_id, status="pending")


@router.get("/status/{job_id}", response_model=CropJobStatusResponse)
def check_crop_status(job_id: str, db: Session = Depends(get_db)):
    job = db.query(SVGRecord).filter(SVGRecord.id == job_id).first()

    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    response_data = CropJobStatusResponse(
        id=str(job.id),
        status=str(job.status),
        svg=job.svg if job.svg else None,
        mask_contours=json.loads(job.mask_contours) if job.mask_contours else None
    )

    return response_data

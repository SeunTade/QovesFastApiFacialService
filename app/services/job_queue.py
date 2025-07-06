from app.worker import app
from app.db.session import SessionLocal
from app.db.models import SVGRecord
from app.utils.hash import get_image_hash
from app.services.processing import create_svg
from celery import shared_task
import json
import time
from typing import Any, Optional
from sqlalchemy.exc import NoResultFound

@app.task(name="app.services.job_queue.process_svg_job")
def process_svg_job(job_id: str, data: dict):
    db = SessionLocal()

    try:
        image_b64_raw: Any = data.get('image')
        segmentation_b64_raw: Any = data.get('segmentation_map')
        landmarks_raw: Any = data.get('landmarks')

        if not isinstance(image_b64_raw, str):
            print(f"[{job_id}] Invalid or missing 'image'")
            return
        if not isinstance(segmentation_b64_raw, str):
            print(f"[{job_id}] Invalid or missing 'segmentation_map'")
            return
        if not isinstance(landmarks_raw, list):
            print(f"[{job_id}] Invalid or missing 'landmarks'")
            return

        image_b64: str = image_b64_raw
        segmentation_b64: str = segmentation_b64_raw
        landmarks: list = landmarks_raw

        job_hash = get_image_hash(image_b64 + segmentation_b64)

        existing: Optional[SVGRecord] = db.query(SVGRecord).filter(SVGRecord.hash == job_hash).first()
        if existing is not None and isinstance(existing.svg, str) and isinstance(existing.mask_contours, str):
            print(f"[{job_id}] Cache hit. Reusing previous result.")

            job_record: Optional[SVGRecord] = db.query(SVGRecord).filter(SVGRecord.id == job_id).first()
            if job_record is not None:
                job_record.hash = job_hash
                job_record.svg = existing.svg
                job_record.mask_contours = existing.mask_contours
                job_record.status = "done"
                db.commit()
            return

        svg_str, mask_contours = create_svg(image_b64, segmentation_b64, landmarks)

        job_record: Optional[SVGRecord] = db.query(SVGRecord).filter(SVGRecord.id == job_id).first()
        if job_record is not None:
            job_record.hash = job_hash
            job_record.svg = svg_str
            job_record.mask_contours = json.dumps(mask_contours)
            job_record.status = "done"
            db.commit()
        else:
            print(f"[{job_id}] ERROR: Job record not found.")

    except Exception as e:
        print(f"[{job_id}] ERROR: {str(e)}")
    finally:
        db.close()

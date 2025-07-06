# QOVES Backend Test Task — FastAPI Facial Contour Service

This FastAPI backend accepts a portrait image, facial landmarks, and a segmentation map, then asynchronously returns an SVG with overlaid facial contours. It is built to meet the QOVES Backend Test Task specification.

---

## Project Structure

```
.
├── app/
│   ├── api/v1/endpoints/crop.py       # FastAPI endpoints
│   ├── services/processing.py         # Image processing and SVG generation
│   ├── services/job_queue.py          # Celery task worker
│   ├── db/models.py                   # Postgres model definition (SVGRecord)
│   ├── worker.py                      # Celery app worker entry
│   ├── main.py                        # FastAPI entrypoint
├── docker-compose.yml                 # Docker Compose environment
├── prometheus.yml                     # Prometheus metrics configuration
├── submit_test_job.py                 # CLI testing script
├── Backend_Engineer/                  # Provided test assets
│   ├── original_image.png
│   ├── segmentation_map.png
│   ├── landmarks.txt
```

---

## Implemented Features

- Asynchronous background job processing with Celery
- Image rotation based on first two facial landmarks
- SVG contour generation using OpenCV masks and approximation
- Postgres caching for previously processed results
- Proper HTTP error responses (422, 404)
- Prometheus metrics integration
- Rich logging for CLI visibility
- Dockerized environment including Redis, Celery, Postgres

---

## API Endpoints

### POST `/api/v1/frontal/crop/submit`
Submit an image segmentation task.

Request:
```
{
  "image": "<base64 image>",
  "segmentation_map": "<base64 segmentation>",
  "landmarks": [
    {"x": 100, "y": 120},
    {"x": 140, "y": 125}
  ]
}
```
Response:
```
{
  "id": "abc123",
  "status": "pending"
}
```

### GET `/api/v1/frontal/crop/status/{id}`
Poll for the status of the submitted job.

Success Response:
```
{
  "id": "abc123",
  "status": "done",
  "svg": "<base64-encoded SVG>",
  "mask_contours": {
    "1": [[x, y], ...]
  }
}
```

---

## API Usage

Run the app:
```
docker-compose up --build
```
Submit a test request using:
```
python submit_test_job.py
```
This uses test files from `Backend_Engineer/` for the base64 image, landmarks, and segmentation map.

---

## Error Handling

- Returns `422 Unprocessable Entity` for invalid or missing facial landmarks
- Returns `404 Not Found` for invalid job IDs

Example error response:
```
{
  "detail": "Invalid or missing facial landmarks."
}
```

---

## Logging and Metrics

- Logging: Rich logging format is used for cleaner debugging output
- Prometheus: Server exposes metrics for monitoring

---

## Postgres Usage

- Each job response (SVG + contours) is cached in Postgres under `SVGRecord`
- Fields stored: `id`, `svg`, `mask_contours`, `status`

---

## Testing

Run the script to simulate a job submission:
```
python submit_test_job.py
```
This submits:
- original_image.png
- segmentation_map.png
- landmarks.txt

---

## Improvements for Future Versions

- Better face alignment using more than 2 landmarks
- Configurable delay for load-testing or live environments
- SVG enhancements: fill transparency, dashed outlines
- Smarter segmentation region smoothing and overlap correction
- Accept direct image uploads (not only base64)

---


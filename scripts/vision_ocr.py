"""Submit Arabic PDF OCR jobs to Google Cloud Vision.

Usage:
  python scripts/vision_ocr.py fahim-curriculum-ocr-2026-4851
"""
import sys
from datetime import datetime, timezone
from google.cloud import vision_v1

def main(bucket: str):
    client = vision_v1.ImageAnnotatorClient()
    run_prefix = datetime.now(timezone.utc).strftime("vision-output/%Y%m%d-%H%M%S")
    requests = []
    for filename in ("خامس 2.pdf", "خامس 3.pdf"):
        term_prefix = "term-2" if "2" in filename else "term-3"
        requests.append(vision_v1.AsyncAnnotateFileRequest(
            features=[vision_v1.Feature(type_=vision_v1.Feature.Type.DOCUMENT_TEXT_DETECTION)],
            input_config=vision_v1.InputConfig(
                gcs_source=vision_v1.GcsSource(uri=f"gs://{bucket}/input/{filename}"),
                mime_type="application/pdf",
            ),
            output_config=vision_v1.OutputConfig(
                gcs_destination=vision_v1.GcsDestination(uri=f"gs://{bucket}/{run_prefix}/{term_prefix}/")
            ),
            image_context=vision_v1.ImageContext(language_hints=["ar", "en"]),
        ))
    operation = client.async_batch_annotate_files(requests=requests)
    print("OCR submitted. Waiting for completion...")
    operation.result()
    print(f"OCR complete. JSON output: gs://{bucket}/{run_prefix}/")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/vision_ocr.py BUCKET_NAME")
    main(sys.argv[1])

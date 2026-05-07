from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import Dict
import os
from google.cloud import storage
import uuid
from src.setup.dependencies import CurrentUser

router = APIRouter(tags=["Upload"])

# Configuration
GCP_BUCKET_NAME = os.getenv("GCP_STORAGE_BUCKET")
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")

@router.post("/upload")
async def upload_file(current_user: CurrentUser, file: UploadFile = File(...)):
    """
    Uploads a file to Google Cloud Storage and returns the file metadata.
    """
    if not GCP_BUCKET_NAME:
        # Fallback to mock for development if no bucket configured
        return {
            "url": f"https://storage.example.com/faculty/uploads/{file.filename}",
            "publicId": f"faculty/uploads/{str(uuid.uuid4())}_{file.filename}",
            "name": file.filename,
            "type": file.content_type
        }

    try:
        # Initialize GCS client
        # In GCP environment, it will automatically use service account credentials
        storage_client = storage.Client(project=GCP_PROJECT_ID)
        bucket = storage_client.bucket(GCP_BUCKET_NAME)
        
        # Generate a unique path: faculty/email/filename
        file_uuid = str(uuid.uuid4())
        safe_filename = file.filename.replace(" ", "_")
        public_id = f"faculty/{current_user.email}/{file_uuid}_{safe_filename}"
        
        blob = bucket.blob(public_id)
        
        # Upload the file
        # blob.upload_from_file expects a file-like object
        blob.upload_from_file(file.file, content_type=file.content_type)
        
        # Construct public URL (Assumes bucket is publicly readable or using signed URLs)
        # For this project, we assume the bucket is configured for public access or matches GCP Run region
        url = blob.public_url
        
        return {
            "url": url,
            "publicId": public_id,
            "name": file.filename,
            "type": file.content_type
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

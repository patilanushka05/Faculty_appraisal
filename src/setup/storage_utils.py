from fastapi import UploadFile, HTTPException
from .supabase_client import get_async_supabase
import uuid

BUCKET_NAME = "faculty-docs"

async def upload_file_to_supabase(file: UploadFile, faculty_id: str) -> str:
    """
    Uploads a file to Supabase Storage and returns the file path.
    Path format: {faculty_id}/{uuid}_{original_filename}
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    file_content = await file.read()
    
    # Create a unique filename to avoid collisions
    unique_id = uuid.uuid4().hex
    file_path = f"{faculty_id}/{unique_id}_{file.filename}"
    
    try:
        # Use service role to bypass RLS for backend-initiated uploads
        async with get_async_supabase(use_service_role=True) as supabase:
            # Upload to Supabase Storage
            await supabase.storage.from_(BUCKET_NAME).upload(
                path=file_path,
                file=file_content,
                file_options={"content-type": "application/pdf", "upsert": "true"}
            )
        return file_path
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file to Supabase: {str(e)}")

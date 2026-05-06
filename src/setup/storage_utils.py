from fastapi import UploadFile, HTTPException
from .supabase_client import get_async_supabase
import uuid
import os
import aiofiles
from dotenv import load_dotenv

load_dotenv()

BUCKET_NAME = "faculty-docs"
LOCAL_STORAGE_DIR = os.getenv("LOCAL_STORAGE_DIR", "./uploads")

async def upload_file_to_supabase(file: UploadFile, faculty_id: str) -> str:
    """
    Uploads a file to Supabase Storage or Local File System.
    Path format: {faculty_id}/{uuid}_{original_filename}
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    file_content = await file.read()
    
    # Create a unique filename to avoid collisions
    unique_id = uuid.uuid4().hex
    file_path = f"{faculty_id}/{unique_id}_{file.filename}"
    
    # Check if local storage is enabled
    if os.getenv("USE_LOCAL_STORAGE", "false").lower() == "true":
        try:
            full_dir_path = os.path.join(LOCAL_STORAGE_DIR, faculty_id)
            os.makedirs(full_dir_path, exist_ok=True)
            
            full_file_path = os.path.join(LOCAL_STORAGE_DIR, file_path)
            
            async with aiofiles.open(full_file_path, 'wb') as out_file:
                await out_file.write(file_content)
                
            # Return relative path to be served via StaticFiles
            return f"/uploads/{file_path}"
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to upload file locally: {str(e)}")
    else:
        # Fallback to Supabase Storage
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

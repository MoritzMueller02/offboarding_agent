from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from supabase import Client
from uuid import UUID, uuid4
from typing import List

from app.config import Settings
from app.dependencies import get_db
from app.db.repositories.documents_repository import DocumentRepository
from app.models.schema import DocumentUploadResponse

router = APIRouter()
settings = Settings()

ALLOWD_TEXT_TYPES = {"application/pdf"}
MAX_FILE_SIZE = settings.max_file_size


@router.post("/upload", response_model = DocumentUploadResponse, status_code = 201)
async def upload_document(file: UploadFile = File(...), 
                          session_id: UUID = Form(...),
                          db: Client = Depends(get_db)):
    
    file_bytes = await file.read()
    
    if len(file_bytes) >= MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail = "File is to large")
    
    if file.content_type not in ALLOWD_TEXT_TYPES:
        raise HTTPException(status_code= 415, detail = "Unsupported File Type")
    
    
    storage_path = f"{session_id}/{uuid4()}_{file.filename}"
    
    db.storage.from_("documents").upload(
        path = storage_path,
        file = file_bytes,
        file_options= {"content-type": file.content_type},
    )
    
    repo = DocumentRepository(db)
    
    document = repo.create(
        session_id=session_id,
        storage_path=storage_path,
        file_name=file.filename,
        file_size = len(file_bytes),
        document_type = file.content_type
    )
    
    return DocumentUploadResponse(
        document_id = document["id"],
        session_id=document["session_id"],
        storage_path = document["storage_path"],
        file_name = document["file_name"],
        file_size = document["file_size"],
        processing_status=document["processing_status"]
    )
    
    
@router.get("/{document_id}", response_model = DocumentUploadResponse)
def get_document(document_id: UUID, db: Client = Depends(get_db)):
    repo = DocumentRepository(db)
    document = repo.get_by_id(document_id)
    
    if not document:
        raise HTTPException(status_code = 404, detail = "Document ntot found")
    
    return DocumentUploadResponse(
        document_id = document["id"],
        session_id=document["session_id"],
        storage_path = document["storage_path"],
        file_name = document["file_name"],
        file_size = document["file_size"],
        processing_status=document["processing_status"]
    )
    

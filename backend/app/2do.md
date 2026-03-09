backend/app/
├── main.py                      # FastAPI app, registers routers
├── config.py                    # Settings
├── dependencies.py              # Supabase client
├── schemas.py                   # Pydantic models for API
│
├── routers/                     # HTTP ENDPOINTS
│   ├── employees.py
│   ├── sessions.py
│   ├── audio.py
│   ├── transcriptions.py
│   ├── documents.py
│   └── search.py
│
├── services/                    # BUSINESS LOGIC
│   ├── transcription_service.py
│   ├── chunking_service.py
│   ├── embedding_service.py
│   ├── storage_service.py
│   └── search_service.py
│
└── db/                          # DATABASE
    ├── repositories/
    │   ├── employee_repository.py
    │   ├── session_repository.py
    │   ├── audio_repository.py
    │   ├── transcription_repository.py
    │   ├── document_repository.py
    │   └── knowledge_chunk_repository.py
    └── exceptions.py            # Custom errors
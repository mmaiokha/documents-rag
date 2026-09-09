from fastapi import FastAPI
from uploads.routers import router as uploads_router
from documents.routers import router as documents_router

app = FastAPI()


app.include_router(uploads_router)
app.include_router(documents_router)
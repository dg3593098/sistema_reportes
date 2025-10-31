from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .routes import router
from .db import Base, engine
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sistema de Reportes Escolares")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
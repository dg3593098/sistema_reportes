from pydantic import BaseModel
from datetime import datetime

class ReporteCreate(BaseModel):
    codigo: str
    descripcion: str

class UsuarioLogin(BaseModel):
    documento: str
    password: str

class ComentarioCreate(BaseModel):
    reporte_id: int
    autor_id: int
    contenido: str
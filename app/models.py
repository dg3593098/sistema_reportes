from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .db import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    documento = Column(String(50), unique=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    password = Column(String(200), nullable=False)  

    comentarios = relationship(
        "Comentario",
        back_populates="autor",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    def __repr__(self):
        return f"<Usuario id={self.id} documento={self.documento}>"


class Codigo(Base):
    __tablename__ = "codigos"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, nullable=False)
    activo = Column(Boolean, default=True)

    reportes = relationship(
        "Reporte",
        back_populates="codigo_rel",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    def __repr__(self):
        return f"<Codigo id={self.id} codigo={self.codigo} activo={self.activo}>"


class Reporte(Base):
    __tablename__ = "reportes"

    id = Column(Integer, primary_key=True, index=True)
    codigo_id = Column(Integer, ForeignKey("codigos.id", ondelete="CASCADE"), nullable=False)
    descripcion = Column(Text, nullable=False)
    fecha_envio = Column(DateTime, default=datetime.utcnow)

    codigo_rel = relationship("Codigo", back_populates="reportes")
    comentarios = relationship(
        "Comentario",
        back_populates="reporte",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    def __repr__(self):
        return f"<Reporte id={self.id} codigo_id={self.codigo_id}>"


class Comentario(Base):
    __tablename__ = "comentarios"

    id = Column(Integer, primary_key=True, index=True)
    reporte_id = Column(Integer, ForeignKey("reportes.id", ondelete="CASCADE"), nullable=False)
    autor_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    contenido = Column(Text, nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)

    reporte = relationship("Reporte", back_populates="comentarios")
    autor = relationship("Usuario", back_populates="comentarios")

    def __repr__(self):
        return f"<Comentario id={self.id} reporte_id={self.reporte_id} autor_id={self.autor_id}>"
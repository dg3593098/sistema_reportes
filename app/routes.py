from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime
import os
from .db import get_db
from .models import Usuario, Codigo, Reporte, Comentario

def contexto_base(request):
    return {"request": request, "usuario_id": request.cookies.get("usuario_id")}

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("formulario.html", {"request": request})


@router.post("/enviar_reporte")
async def enviar_reporte(
    request: Request,
    codigo: str = Form(...),
    descripcion: str = Form(...),
    db: Session = Depends(get_db),
):
    codigo_db = db.query(Codigo).filter_by(codigo=codigo, activo=True).first()
    if not codigo_db:
        return templates.TemplateResponse(
            "formulario.html",
            {"request": request, "error": "Código inválido o inactivo."},
        )

    nuevo_reporte = Reporte(codigo_id=codigo_db.id, descripcion=descripcion, fecha_envio=datetime.utcnow())
    db.add(nuevo_reporte)
    db.commit()
    db.refresh(nuevo_reporte)
    return RedirectResponse(url=f"/ver_reportes?codigo={codigo}", status_code=303)


@router.get("/ver_reportes", response_class=HTMLResponse)
async def ver_reportes(request: Request):
    return templates.TemplateResponse("reportes_por_codigo.html", {"request": request})


@router.post("/ver_reportes")
async def ver_reportes_post(
    request: Request, codigo: str = Form(...), db: Session = Depends(get_db)
):
    codigo_db = db.query(Codigo).filter_by(codigo=codigo).first()
    if not codigo_db:
        return templates.TemplateResponse(
            "reportes_por_codigo.html",
            {"request": request, "error": "Código no válido."},
        )
    reportes = db.query(Reporte).filter_by(codigo_id=codigo_db.id).all()
    return templates.TemplateResponse(
        "reportes_por_codigo.html",
        {"request": request, "reportes": reportes, "codigo": codigo},
    )


@router.post("/modificar_reporte/{reporte_id}")
async def modificar_reporte(
    request: Request,
    reporte_id: int,
    descripcion: str = Form(...),
    db: Session = Depends(get_db),
):
    reporte = db.query(Reporte).filter_by(id=reporte_id).first()
    if not reporte:
        raise HTTPException(status_code=404, detail="Reporte no encontrado.")

    reporte.descripcion = descripcion
    db.commit()
    return RedirectResponse(url="/ver_reportes", status_code=303)



@router.get("/eliminar_reporte/{reporte_id}")
async def eliminar_reporte_get(reporte_id: int, db: Session = Depends(get_db)):
    reporte = db.query(Reporte).filter_by(id=reporte_id).first()
    if not reporte:
        raise HTTPException(status_code=404, detail="Reporte no encontrado.")
    db.query(Comentario).filter_by(reporte_id=reporte_id).delete()
    db.delete(reporte)
    db.commit()
    return RedirectResponse(url="/ver_reportes", status_code=303)


@router.post("/eliminar_reporte/{reporte_id}")
async def eliminar_reporte_post(reporte_id: int, db: Session = Depends(get_db)):
    reporte = db.query(Reporte).filter_by(id=reporte_id).first()
    if not reporte:
        raise HTTPException(status_code=404, detail="Reporte no encontrado.")
    db.query(Comentario).filter_by(reporte_id=reporte_id).delete()
    db.delete(reporte)
    db.commit()
    return RedirectResponse(url="/ver_reportes", status_code=303)


@router.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login_post(
    request: Request,
    documento: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(Usuario).filter_by(documento=documento).first()
    if not user or (hasattr(user, "password") and user.password != password):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Credenciales incorrectas."},
        )
    response = RedirectResponse(url="/admin", status_code=302)
    response.set_cookie(
        key="usuario_id",
        value=str(user.id),
        httponly=True,
        samesite="lax",     
        secure=False,       
        max_age=60 * 60 * 3 
    )
    return response


@router.get("/logout")
async def logout(request: Request):
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("usuario_id")
    return response


@router.get("/admin", response_class=HTMLResponse)
async def admin(request: Request, db: Session = Depends(get_db)):
    usuario_id = request.cookies.get("usuario_id")
    if not usuario_id:
        return RedirectResponse(url="/login", status_code=303)
    reportes = db.query(Reporte).all()
    contexto = contexto_base(request)
    contexto["reportes"] = reportes
    return templates.TemplateResponse("admin.html", contexto)


@router.post("/comentario/{reporte_id}")
async def agregar_comentario(
    request: Request,
    reporte_id: int,
    contenido: str = Form(...),
    db: Session = Depends(get_db)
):
    usuario_id = request.cookies.get("usuario_id")
    if not usuario_id:
        return RedirectResponse(url="/login", status_code=303)
    nuevo_comentario = Comentario(
        reporte_id=reporte_id,
        autor_id=int(usuario_id),
        contenido=contenido
    )
    db.add(nuevo_comentario)
    db.commit()
    return RedirectResponse(url="/admin", status_code=303)


@router.post("/editar_comentario/{comentario_id}")
async def editar_comentario(comentario_id: int, contenido: str = Form(...), db: Session = Depends(get_db)):
    comentario = db.query(Comentario).filter_by(id=comentario_id).first()
    if not comentario:
        raise HTTPException(status_code=404, detail="Comentario no encontrado.")
    comentario.contenido = contenido
    db.commit()
    return RedirectResponse(url="/admin", status_code=303)


@router.get("/eliminar_comentario/{comentario_id}")
async def eliminar_comentario_get(comentario_id: int, request: Request, db: Session = Depends(get_db)):
    usuario_id = request.cookies.get("usuario_id")
    if not usuario_id:
        return RedirectResponse(url="/login", status_code=303)
    c = db.query(Comentario).filter_by(id=comentario_id).first()
    if c:
        db.delete(c)
        db.commit()
    return RedirectResponse(url="/admin", status_code=303)


@router.post("/eliminar_comentario/{comentario_id}")
async def eliminar_comentario_post(comentario_id: int, db: Session = Depends(get_db)):
    c = db.query(Comentario).filter_by(id=comentario_id).first()
    if c:
        db.delete(c)
        db.commit()
    return RedirectResponse(url="/admin", status_code=303)

@router.get("/test")
async def test():
    return {"status": "ok", "message": "Sistema de reportes operativo."}

@router.get("/estadisticas", response_class=HTMLResponse)
async def estadisticas(request: Request, db: Session = Depends(get_db)):
    usuario_id = request.cookies.get("usuario_id")
    if not usuario_id:
        return RedirectResponse(url="/login", status_code=303)
    total_reportes = db.query(Reporte).count()
    total_comentarios = db.query(Comentario).count()
    codigos_usados = db.query(Codigo).count()
    from sqlalchemy import func
    datos = (
        db.query(func.date(Reporte.fecha_envio), func.count(Reporte.id))
        .group_by(func.date(Reporte.fecha_envio))
        .order_by(func.date(Reporte.fecha_envio))
        .all()
    )
    labels = [str(r[0]) for r in datos]
    valores = [r[1] for r in datos]
    ultimos = (
        db.query(Reporte)
        .join(Codigo, Reporte.codigo_id == Codigo.id)
        .order_by(Reporte.fecha_envio.desc())
        .limit(5)
        .all()
    )
    return templates.TemplateResponse(
        "estadisticas.html",
        {
            "request": request,
            "total_reportes": total_reportes,
            "total_comentarios": total_comentarios,
            "codigos_usados": codigos_usados,
            "labels": labels,
            "valores": valores,
            "ultimos": ultimos,
        },
    )
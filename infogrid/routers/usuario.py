from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload
from http import HTTPStatus
from typing import List
from infogrid.database import get_session
from infogrid.models import Usuario as UsuarioModel
from infogrid.schemas import Usuario, UsuarioPublic

router = APIRouter(prefix='/api/v1/usuario', tags=['usuario'])


@router.get("/", status_code=HTTPStatus.OK, response_model=List[UsuarioPublic])
def list_usuarios(session: Session = Depends(get_session)):
    usuarios = session.scalars(select(UsuarioModel)).all()
    return usuarios


@router.get("/pagined/", status_code=HTTPStatus.OK, response_model=List[UsuarioPublic])
def list_usuarios_paged(limit: int = 5, skip: int = 0, session: Session = Depends(get_session)):
    usuarios = session.scalars(select(UsuarioModel).limit(limit).offset(skip)).all()
    return usuarios



@router.post("/", status_code=HTTPStatus.CREATED, response_model=UsuarioPublic)
def create_usuario(usuario: Usuario, session: Session = Depends(get_session)):
    """
    Cria um novo usuário
    """
    with session as session:
        # Verifique se o usuário já existe
        db_usuario = session.scalar(select(UsuarioModel).where(UsuarioModel.email == usuario.email))
        if db_usuario:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Usuário já existe")

        # Aqui, criamos uma instância de UsuarioModel sem passar 'registros_acesso'
        db_instance = UsuarioModel(
            nome=usuario.nome,
            email=usuario.email,
            cargo=usuario.cargo,
            telefone=usuario.telefone
        )
        
        session.add(db_instance)

        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Falha na inserção do usuário")

        session.refresh(db_instance)

    # Retorne os dados do novo usuário, excluindo 'registros_acesso' que não pertence a esse modelo
    return {
        "id": db_instance.id,
        "nome": db_instance.nome,
        "email": db_instance.email,
        "cargo": db_instance.cargo,
        "telefone": db_instance.telefone,
        "registros_acesso": []  # Esse campo é provavelmente um relacionamento e deve ser tratado separadamente
    }


@router.delete("/{usuario_id}", status_code=HTTPStatus.NO_CONTENT)
def delete_usuario(usuario_id: int, session: Session = Depends(get_session)):
    with session as session:
        db_usuario = session.scalar(select(UsuarioModel).where(UsuarioModel.id == usuario_id))
        if not db_usuario:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Usuário not found")
        session.delete(db_usuario)
        session.commit()
    return {"message": "Usuário deleted successfully"}


@router.put("/{usuario_id}", status_code=HTTPStatus.OK, response_model=UsuarioPublic)
def update_usuario(usuario_id: int, usuario: Usuario, session: Session = Depends(get_session)):
    with session as session:
        db_usuario = session.scalar(
            select(UsuarioModel)
            .where(UsuarioModel.id == usuario_id)
            # .options(joinedload(UsuarioModel.registros_acesso))  # Carrega registros de acesso
        )
        if not db_usuario:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Usuário not found")

        # Atualiza os dados do usuário
        update_data = usuario.dict()
        for key, value in update_data.items():
            setattr(db_usuario, key, value)

        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Usuário update failed")

        session.refresh(db_usuario)

    return db_usuario



@router.get("/usuarios", status_code=HTTPStatus.OK)
def count_usuarios(session: Session = Depends(get_session)):
    """
    Endpoint para contar o número de registros na tabela 'usuarios'.
    """
    quantidade = session.scalar(select(func.count()).select_from(UsuarioModel))
    return {"quantidade": quantidade}
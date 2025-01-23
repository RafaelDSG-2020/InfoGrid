from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload
from http import HTTPStatus
from typing import List
from infogrid.database import get_session
from infogrid.models import Usuario as UsuarioModel
from infogrid.schemas import Usuario, UsuarioPublic
import logging

logger = logging.getLogger("app_logger")

router = APIRouter(prefix='/api/v1/usuario', tags=['usuario'])


@router.get("/", status_code=HTTPStatus.OK, response_model=List[UsuarioPublic])
def list_usuarios(session: Session = Depends(get_session)):
    logger.info("Endpoint /usuario acessado")
    usuarios = session.scalars(select(UsuarioModel)).all()
    logger.info(f"{len(usuarios)} usuários encontrados")
    return usuarios


@router.get("/pagined/", status_code=HTTPStatus.OK, response_model=List[UsuarioPublic])
def list_usuarios_paged(limit: int = 5, skip: int = 0, session: Session = Depends(get_session)):
    logger.info(f"Endpoint /usuario/pagined acessado com limite {limit} e offset {skip}")
    usuarios = session.scalars(select(UsuarioModel).limit(limit).offset(skip)).all()
    logger.info(f"{len(usuarios)} usuários encontrados")
    return usuarios



@router.post("/", status_code=HTTPStatus.CREATED, response_model=UsuarioPublic)
def create_usuario(usuario: Usuario, session: Session = Depends(get_session)):
    """
    Cria um novo usuário
    """
    logger.info("Tentativa de criação de um novo usuário")
    with session as session:
        # Verifique se o usuário já existe
        db_usuario = session.scalar(select(UsuarioModel).where(UsuarioModel.email == usuario.email))
        if db_usuario:
            logger.warning("Tentativa de criação de usuário falhou: usuário já existe")
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
            logger.info(f"Usuário '{db_instance.nome}' criado com sucesso")
        except IntegrityError:
            session.rollback()
            logger.error("Erro ao inserir usuário", exc_info=True)
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
    logger.info(f"Tentativa de exclusão do usuário com ID {usuario_id}")
    with session as session:
        db_usuario = session.scalar(select(UsuarioModel).where(UsuarioModel.id == usuario_id))
        if not db_usuario:
            logger.warning(f"Tentativa de exclusão falhou: usuário com ID {usuario_id} não encontrado")
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Usuário not found")
        session.delete(db_usuario)
        try:
            session.commit()
            logger.info(f"Usuário com ID {usuario_id} excluído com sucesso")
        except IntegrityError as e:
            session.rollback()
            logger.error(f"Erro ao excluir usuário com ID {usuario_id}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=f"Usuário deletion failed: {str(e)}")
    return {"message": "Usuário deleted successfully"}

    #     session.commit()
    # return {"message": "Usuário deleted successfully"}


@router.put("/{usuario_id}", status_code=HTTPStatus.OK, response_model=UsuarioPublic)
def update_usuario(usuario_id: int, usuario: Usuario, session: Session = Depends(get_session)):
    logger.info(f"Tentativa de atualização do usuário com ID {usuario_id}")
    with session as session:
        db_usuario = session.scalar(
            select(UsuarioModel)
            .where(UsuarioModel.id == usuario_id)
            # .options(joinedload(UsuarioModel.registros_acesso))  # Carrega registros de acesso
        )
        if not db_usuario:
            logger.warning(f"Tentativa de atualização falhou: usuário com ID {usuario_id} não encontrado")
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Usuário not found")

        # Atualiza os dados do usuário
        update_data = usuario.dict()
        for key, value in update_data.items():
            setattr(db_usuario, key, value)

        try:
            session.commit()
            logger.info(f"Usuário com ID {usuario_id} atualizado com sucesso")
        except IntegrityError:
            session.rollback()
            logger.error(f"Erro ao atualizar usuário com ID {usuario_id}", exc_info=True)
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Usuário update failed")

        session.refresh(db_usuario)

    return db_usuario



@router.get("/usuarios", status_code=HTTPStatus.OK)
def count_usuarios(session: Session = Depends(get_session)):
    """
    Endpoint para contar o número de registros na tabela 'usuarios'.
    """
    logger.info("Endpoint /usuario/usuarios acessado para contar registros")
    quantidade = session.scalar(select(func.count()).select_from(UsuarioModel))
    logger.info(f"Quantidade de usuários: {quantidade}")
    return {"quantidade": quantidade}
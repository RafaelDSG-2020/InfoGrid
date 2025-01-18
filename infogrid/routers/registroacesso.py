import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from http import HTTPStatus
from typing import List
from infogrid.database import get_session
from infogrid.models import RegistroAcesso as RegistroAcessoModel
from infogrid.schemas import RegistroAcesso, RegistroAcessoPublic

router = APIRouter(prefix='/api/v1/registroacesso', tags=['registroacesso'])


@router.get("/", status_code=HTTPStatus.OK, response_model=List[RegistroAcessoPublic])
def list_registros_acesso(session: Session = Depends(get_session)):
    registros = session.scalars(select(RegistroAcessoModel)).all()
    return registros


@router.get("/pagined/", status_code=HTTPStatus.OK, response_model=List[RegistroAcessoPublic])
def list_registros_acesso_paged(limit: int = 5, skip: int = 0, session: Session = Depends(get_session)):
    registros = session.scalars(select(RegistroAcessoModel).limit(limit).offset(skip)).all()
    return registros

@router.post("/", status_code=HTTPStatus.CREATED, response_model=RegistroAcessoPublic)
def create_registro_acesso(registro: RegistroAcesso, session: Session = Depends(get_session)):
    """
    Creates a new access record (Registro de Acesso).
    """
    with session as session:
        # Check if the record already exists
        db_registro = session.scalar(
            select(RegistroAcessoModel)
            .where(
                (RegistroAcessoModel.usuario_id == registro.usuario_id) &
                (RegistroAcessoModel.conjunto_dados == registro.conjunto_dados) &
                (RegistroAcessoModel.data_solicitacao == registro.data_solicitacao)
            )
        )
        if db_registro:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Registro de Acesso already exists for the given criteria",
            )

        # Create a new record
        db_instance = RegistroAcessoModel(**registro.dict())
        session.add(db_instance)

        try:
            session.commit()
            session.refresh(db_instance)  # Refresh to get updated instance with ID
        except IntegrityError as e:
            session.rollback()
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=f"Failed to insert Registro de Acesso: {e.orig.args if e.orig else str(e)}"
            )

    # Deserialize permissoes_concedidas if it's stored as a string
    permissoes_concedidas = (
        json.loads(db_instance.permissoes_concedidas)
        if isinstance(db_instance.permissoes_concedidas, str)
        else db_instance.permissoes_concedidas or []
    )

    # Return the created record using the response model
    return RegistroAcessoPublic(
        id=db_instance.id,
        usuario_id=db_instance.usuario_id,
        conjunto_dados=db_instance.conjunto_dados,
        data_solicitacao=db_instance.data_solicitacao,
        finalidade_uso=db_instance.finalidade_uso,
        permissoes_concedidas=permissoes_concedidas,
        status=db_instance.status,
    )


@router.delete("/{registro_id}", status_code=HTTPStatus.NO_CONTENT)
def delete_registro_acesso(registro_id: int, session: Session = Depends(get_session)):
    with session as session:
        db_registro = session.scalar(select(RegistroAcessoModel).where(RegistroAcessoModel.id == registro_id))
        if not db_registro:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Registro de Acesso not found")
        session.delete(db_registro)
        session.commit()
    return {"message": "Registro de Acesso deleted successfully"}


@router.put("/{registro_id}", status_code=HTTPStatus.OK, response_model=RegistroAcessoPublic)
def update_registro_acesso(registro_id: int, registro: RegistroAcesso, session: Session = Depends(get_session)):
    with session as session:
        db_registro = session.scalar(select(RegistroAcessoModel).where(RegistroAcessoModel.id == registro_id))
        if not db_registro:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Registro de Acesso not found")

        # Atualiza os dados do registro de acesso
        update_data = registro.dict()
        for key, value in update_data.items():
            setattr(db_registro, key, value)

        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Registro de Acesso update failed")

        session.refresh(db_registro)

    return db_registro




@router.get("/registrosacesso", status_code=HTTPStatus.OK)
def count_databases(session: Session = Depends(get_session)):
    """
    Endpoint para contar o número de registros na tabela 'registrosacesso'.
    """
    quantidade = session.scalar(select(func.count()).select_from(RegistroAcessoModel))
    return {"quantidade": quantidade}
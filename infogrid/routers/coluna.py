from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from http import HTTPStatus
from typing import List
from infogrid.database import get_session
from infogrid.models import Coluna as ColunaModel
from infogrid.schemas import Coluna, ColunaPublic

router = APIRouter(prefix='/api/v1/coluna', tags=['coluna'])


@router.get("/", status_code=HTTPStatus.OK, response_model=List[ColunaPublic])
def list_colunas(session: Session = Depends(get_session)):
    colunas = session.scalars(select(ColunaModel)).all()
    return colunas


@router.get("/pagined/", status_code=HTTPStatus.OK, response_model=List[ColunaPublic])
def list_colunas_paged(limit: int = 5, skip: int = 0, session: Session = Depends(get_session)):
    colunas = session.scalars(select(ColunaModel).limit(limit).offset(skip)).all()
    return colunas


@router.post("/", status_code=HTTPStatus.CREATED, response_model=ColunaPublic)
def create_coluna(coluna: Coluna, session: Session = Depends(get_session)):
    """
    Cria uma nova coluna
    """
    with session as session:
        db_coluna = session.scalar(select(ColunaModel).where(ColunaModel.nome == coluna.nome and ColunaModel.tabela_id == coluna.tabela_id))
        if db_coluna:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Coluna already exists")

        db_instance = ColunaModel(**coluna.dict())
        session.add(db_instance)

        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Coluna insertion failed")

        session.refresh(db_instance)

    return {
        "id": db_instance.id,
        "nome": db_instance.nome,
        "tipo_dado": db_instance.tipo_dado,
        "descricao": db_instance.descricao,
        "tabela_id": db_instance.tabela_id,
    }


@router.delete("/{coluna_id}", status_code=HTTPStatus.NO_CONTENT)
def delete_coluna(coluna_id: int, session: Session = Depends(get_session)):
    with session as session:
        db_coluna = session.scalar(select(ColunaModel).where(ColunaModel.id == coluna_id))
        if not db_coluna:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Coluna not found")
        session.delete(db_coluna)
        session.commit()
    return {"message": "Coluna deleted successfully"}


@router.put("/{coluna_id}", status_code=HTTPStatus.OK, response_model=ColunaPublic)
def update_coluna(coluna_id: int, coluna: Coluna, session: Session = Depends(get_session)):
    with session as session:
        db_coluna = session.scalar(select(ColunaModel).where(ColunaModel.id == coluna_id))
        if not db_coluna:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Coluna not found")

        # Atualiza os dados da coluna
        update_data = coluna.dict()
        for key, value in update_data.items():
            setattr(db_coluna, key, value)

        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Coluna update failed")

        session.refresh(db_coluna)

    return db_coluna



@router.get("/colunas", status_code=HTTPStatus.OK)
def count_databases(session: Session = Depends(get_session)):
    """
    Endpoint para contar o número de registros na tabela 'colunas'.
    """
    quantidade = session.scalar(select(func.count()).select_from(ColunaModel))
    return {"quantidade": quantidade}
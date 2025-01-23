from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from http import HTTPStatus
from typing import List
from infogrid.database import get_session
from infogrid.models import Coluna as ColunaModel
from infogrid.schemas import Coluna, ColunaPublic
import logging

logger = logging.getLogger("app_logger")

router = APIRouter(prefix='/api/v1/coluna', tags=['coluna'])


@router.get("/", status_code=HTTPStatus.OK, response_model=List[ColunaPublic])
def list_colunas(session: Session = Depends(get_session)):
    logger.info("Endpoint /coluna acessado")
    colunas = session.scalars(select(ColunaModel)).all()
    logger.info(f"{len(colunas)} colunas encontradas")
    return colunas


@router.get("/pagined/", status_code=HTTPStatus.OK, response_model=List[ColunaPublic])
def list_colunas_paged(limit: int = 5, skip: int = 0, session: Session = Depends(get_session)):
    logger.info(f"Endpoint /coluna/pagined acessado com limite {limit} e offset {skip}")
    colunas = session.scalars(select(ColunaModel).limit(limit).offset(skip)).all()
    logger.info(f"{len(colunas)} colunas encontradas")
    return colunas


@router.post("/", status_code=HTTPStatus.CREATED, response_model=ColunaPublic)
def create_coluna(coluna: Coluna, session: Session = Depends(get_session)):
    """
    Cria uma nova coluna
    """
    logger.info("Tentativa de criação de uma nova coluna")
    with session as session:
        db_coluna = session.scalar(select(ColunaModel).where(ColunaModel.nome == coluna.nome and ColunaModel.tabela_id == coluna.tabela_id))
        if db_coluna:
            logger.warning("Tentativa de criação de coluna falhou: coluna já existe")
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Coluna already exists")

        db_instance = ColunaModel(**coluna.dict())
        session.add(db_instance)

        try:
            session.commit()
            logger.info(f"Coluna '{db_instance.nome}' inserida com sucesso")
        except IntegrityError:
            session.rollback()
            logger.error("Falha na inserção da coluna", exc_info=True)
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
    logger.info(f"Tentativa de exclusão da coluna com ID {coluna_id}")
    with session as session:
        db_coluna = session.scalar(select(ColunaModel).where(ColunaModel.id == coluna_id))
        if not db_coluna:
            logger.warning(f"Tentativa de exclusão falhou: coluna com ID {coluna_id} não encontrada")
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Coluna not found")
        session.delete(db_coluna)
        try:
            session.commit()
            logger.info(f"Coluna com ID {coluna_id} excluída com sucesso")
        except IntegrityError:
            session.rollback()
            logger.error(f"Falha na exclusão da coluna com ID {coluna_id}", exc_info=True)
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Coluna deletion failed")
    return {"message": "Coluna deleted successfully"}

        # session.commit()
    # return {"message": "Coluna deleted successfully"}


@router.put("/{coluna_id}", status_code=HTTPStatus.OK, response_model=ColunaPublic)
def update_coluna(coluna_id: int, coluna: Coluna, session: Session = Depends(get_session)):
    logger.info(f"Tentativa de atualização da coluna com ID {coluna_id}")
    with session as session:
        db_coluna = session.scalar(select(ColunaModel).where(ColunaModel.id == coluna_id))
        if not db_coluna:
            logger.warning(f"Tentativa de atualização falhou: coluna com ID {coluna_id} não encontrada")
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Coluna not found")

        # Atualiza os dados da coluna
        update_data = coluna.dict()
        for key, value in update_data.items():
            setattr(db_coluna, key, value)

        try:
            session.commit()
            logger.info(f"Coluna com ID {coluna_id} atualizada com sucesso")
        except IntegrityError:
            session.rollback()
            logger.error(f"Falha na atualização da coluna com ID {coluna_id}", exc_info=True)
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Coluna update failed")

        session.refresh(db_coluna)

    return db_coluna



@router.get("/colunas", status_code=HTTPStatus.OK)
def count_databases(session: Session = Depends(get_session)):
    """
    Endpoint para contar o número de registros na tabela 'colunas'.
    """
    logger.info("Endpoint /coluna/colunas acessado para contar registros")
    quantidade = session.scalar(select(func.count()).select_from(ColunaModel))
    logger.info(f"Quantidade de colunas: {quantidade}")
    return {"quantidade": quantidade}
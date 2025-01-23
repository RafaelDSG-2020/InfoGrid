from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload
from http import HTTPStatus
from typing import List
from infogrid.database import get_session
from infogrid.models import Database as DatabaseModel
from infogrid.schemas import Database, DatabasePublic
import logging

logger = logging.getLogger("app_logger")

router = APIRouter(prefix='/api/v1/database', tags=['routerdatabase'])




@router.get("/", status_code=HTTPStatus.OK, response_model=List[DatabasePublic])
def list_databases(session: Session = Depends(get_session)):
    logger.info("Endpoint /routerdatabase/dados acessado")
    databases = session.scalars(select(DatabaseModel)).all()
    logger.info(f"{len(databases)} bancos de dados encontrados")
    return databases


@router.get("/pagined/", status_code=HTTPStatus.OK, response_model=List[DatabasePublic])
def list_databases_paged(limit: int = 5, skip: int = 0, session: Session = Depends(get_session)):
    logger.info(f"Endpoint /routerdatabase/pagined acessado com limite {limit} e offset {skip}")
    databases = session.scalars(select(DatabaseModel).limit(limit).offset(skip)).all()
    logger.info(f"{len(databases)} bancos de dados encontrados")
    return databases


@router.post("/", status_code=HTTPStatus.CREATED, response_model=DatabasePublic)
def create_database(database: Database, session: Session = Depends(get_session)):
    """
    Cria um novo banco de dados ignorando os responsáveis, tabelas e tópicos Kafka associados
    
    """
    logger.info("Tentativa de criação de um novo banco de dados")
    with session as session:
        db_database = session.scalar(select(DatabaseModel).where(DatabaseModel.nome == database.nome))
        if db_database:
            logger.warning("Tentativa de criação de banco de dados falhou: banco de dados já existe")
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Database already exists")
        data = database.dict(exclude={"responsaveis", "tabelas", "topicos_kafka"})
        db_instance = DatabaseModel(**data)

        # db_instance = DatabaseModel(**database.dict(exclude_unset=True))
        session.add(db_instance)
        try:
            session.commit()
            logger.info(f"Banco de dados '{db_instance.nome}' inserido com sucesso")
        except IntegrityError:
            session.rollback()
            logger.error("Falha na inserção do banco de dados", exc_info=True)
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Database insertion failed")
        session.refresh(db_instance)
        # session.execute(insert(DatabaseModel).values(database.dict(exclude_unset=True)))
        # session.commit()
        # session.refresh(db_instance)
    return {
        "id": db_instance.id,
        "nome": db_instance.nome,
        "tecnologia": db_instance.tecnologia,
        "descricao": db_instance.descricao,
        "responsaveis": []
    }
    # return database


@router.delete("/{database_id}", status_code=HTTPStatus.NO_CONTENT)
def delete_database(database_id: int, session: Session = Depends(get_session)):
    logger.info(f"Tentativa de exclusão do banco de dados com ID {database_id}")
    with session as session:
        db_database = session.scalar(select(DatabaseModel).where(DatabaseModel.id == database_id))
        if not db_database:
            logger.warning(f"Tentativa de exclusão falhou: banco de dados com ID {database_id} não encontrado")
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Database not found")
        session.delete(db_database)
        try:
            session.commit()
            logger.info(f"Banco de dados com ID {database_id} excluído com sucesso")
        except IntegrityError:
            session.rollback()
            logger.error(f"Falha na exclusão do banco de dados com ID {database_id}", exc_info=True)
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Database deletion failed")
    return {"message": "Database deleted successfully"}

    #     session.commit()
    # return {"message": "Database deleted successfully"}


@router.put("/{database_id}", status_code=HTTPStatus.OK, response_model=DatabasePublic)
def update_database(database_id: int, database: Database, session: Session = Depends(get_session)):
    logger.info(f"Tentativa de atualização do banco de dados com ID {database_id}")
    with session as session:
        # Carrega o database com os relacionamentos necessários
        db_database = session.scalar(
            select(DatabaseModel)
            .where(DatabaseModel.id == database_id)
            .options(joinedload(DatabaseModel.responsaveis))  # Carrega responsaveis
        )
        if not db_database:
            logger.warning(f"Tentativa de atualização falhou: banco de dados com ID {database_id} não encontrado")
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Database not found")

        # Atualiza os dados do database
        update_data = database.dict(exclude={"responsaveis"})
        for key, value in update_data.items():
            setattr(db_database, key, value)

        try:
            session.commit()
            logger.info(f"Banco de dados com ID {database_id} atualizado com sucesso")
        except IntegrityError:
            session.rollback()
            logger.error(f"Falha na atualização do banco de dados com ID {database_id}", exc_info=True)
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Database update failed")

        # Atualiza o objeto para refletir as mudanças
        session.refresh(db_database)

    return db_database


@router.get("/databases", status_code=HTTPStatus.OK)
def count_databases(session: Session = Depends(get_session)):
    """
    Endpoint para contar o número de registros na tabela 'databases'.
    """
    logger.info("Endpoint /routerdatabase/databases acessado para contar registros")
    quantidade = session.scalar(select(func.count()).select_from(DatabaseModel))
    logger.info(f"Quantidade de bancos de dados: {quantidade}")
    return {"quantidade": quantidade}

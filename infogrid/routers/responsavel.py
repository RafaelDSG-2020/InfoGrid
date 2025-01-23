from http import HTTPStatus
from typing import List
from fastapi import APIRouter, HTTPException , Depends
from sqlalchemy import create_engine, insert, select, func
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from infogrid.database import get_session
from infogrid.models import Responsavel as ResponsavelModel
from infogrid.schemas import Responsavel, ResponsavelPublic
from infogrid.settings import Settings
import logging

logger = logging.getLogger("app_logger")



router = APIRouter(prefix='/api/v1/responsavel', tags=['responsavel'])



@router.get("/", status_code=HTTPStatus.OK, response_model=List[ResponsavelPublic])
def list_responsavel(session: Session = Depends(get_session)):
    logger.info("Endpoint /responsavel acessado")
    responsavel = session.scalars(select(ResponsavelModel)).all()
    logger.info(f"{len(responsavel)} responsáveis encontrados")
    return responsavel


@router.get("/pagined/", status_code=HTTPStatus.OK, response_model=List[ResponsavelPublic]) 
def list_responsavel_paged(limit: int = 5, skip: int = 0, session: Session = Depends(get_session)):
    logger.info(f"Endpoint /responsavel/pagined acessado com limite {limit} e offset {skip}")
    responsavel = session.scalars(select(ResponsavelModel).limit(limit).offset(skip)).all()
    logger.info(f"{len(responsavel)} responsáveis encontrados")
    return responsavel




@router.post("/", status_code=HTTPStatus.CREATED, response_model=ResponsavelPublic)
def create_responsavel(responsavel: Responsavel):
    logger.info("Tentativa de criação de um novo responsável")
    engine = create_engine(Settings().DATABASE_URL)
    with Session(engine) as session:
        db_responsavel = session.scalar(select(ResponsavelModel).where(ResponsavelModel.email == responsavel.email))
        if db_responsavel:
            logger.warning("Tentativa de criação de responsável falhou: responsável já existe")
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Responsavel already exists")
        data = responsavel.dict(exclude={"responsaveis"})
        db_instance = ResponsavelModel(**data)
        session.add(db_instance)
        try:
            session.commit()
            logger.info(f"Responsável '{db_instance.nome}' criado com sucesso")
        except IntegrityError:
            session.rollback()
            logger.error("Erro ao inserir responsável", exc_info=True)
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Responsavel insertion failed")
        session.refresh(db_instance)

    # Ensure all required fields are included
    return {
        "id": db_instance.id,
        "nome": db_instance.nome,
        "email": db_instance.email,
        "responsaveis": [],
        "cargo": db_instance.cargo,  
        "telefone": db_instance.telefone,  
    }

@router.delete("/{responsavel_id}", status_code=HTTPStatus.NO_CONTENT)
def delete_responsavel(responsavel_id: int, session: Session = Depends(get_session)):
    logger.info(f"Tentativa de exclusão do responsável com ID {responsavel_id}")
    with session as session:
        db_database = session.scalar(select(ResponsavelModel).where(ResponsavelModel.id == responsavel_id))
        if not db_database:
            logger.warning(f"Tentativa de exclusão falhou: responsável com ID {responsavel_id} não encontrado")
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Responsavel not found")
        session.delete(db_database)
        try:
            session.commit()
            logger.info(f"Responsável com ID {responsavel_id} excluído com sucesso")
        except IntegrityError as e:
            session.rollback()
            logger.error(f"Erro ao excluir responsável com ID {responsavel_id}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=f"Responsavel deletion failed: {str(e)}")
    return {"message": "Responsavel deleted successfully"}

    #     session.commit()
    # return {"message": "Responsavel deleted successfully"}




@router.put("/{responsavel_id}", status_code=HTTPStatus.OK, response_model=ResponsavelPublic)
def update_responsavel(responsavel_id: int, responsavel: Responsavel, session: Session = Depends(get_session)):
    logger.info(f"Tentativa de atualização do responsável com ID {responsavel_id}")
    with session as session:
        # Carrega o responsável com os relacionamentos necessários
        db_responsavel = session.scalar(
            select(ResponsavelModel)
            .where(ResponsavelModel.id == responsavel_id)
            .options(
                joinedload(ResponsavelModel.databases),  # Carrega relacionamentos com databases
                joinedload(ResponsavelModel.tabelas),  # Carrega relacionamentos com tabelas
                joinedload(ResponsavelModel.topicos_kafka)  # Carrega relacionamentos com tópicos Kafka
            )
        )
        if not db_responsavel:
            logger.warning(f"Tentativa de atualização falhou: responsável com ID {responsavel_id} não encontrado")
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Responsável not found")

        # Atualiza os dados do responsável
        update_data = responsavel.dict(exclude={"databases", "tabelas", "topicos_kafka"})
        for key, value in update_data.items():
            setattr(db_responsavel, key, value)

        try:
            session.commit()
            logger.info(f"Responsável com ID {responsavel_id} atualizado com sucesso")
        except IntegrityError:
            session.rollback()
            logger.error(f"Erro ao atualizar responsável com ID {responsavel_id}", exc_info=True)
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Responsável update failed")

        # Atualiza o objeto para refletir as mudanças
        session.refresh(db_responsavel)

    return db_responsavel



@router.get("/responsaveis", status_code=HTTPStatus.OK)
def count_responsaveis(session: Session = Depends(get_session)):
    """
    Endpoint para contar o número de registros na tabela 'responsaveis'.
    """
    logger.info("Endpoint /responsavel/responsaveis acessado para contar registros")
    quantidade = session.scalar(select(func.count()).select_from(ResponsavelModel))
    logger.info(f"Quantidade de responsáveis: {quantidade}")
    return {"quantidade": quantidade}


    

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
logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)


router = APIRouter(prefix='/api/v1/responsavel', tags=['responsavel'])



@router.get("/", status_code=HTTPStatus.OK, response_model=List[ResponsavelPublic])
def list_responsavel(session: Session = Depends(get_session)):
    responsavel = session.scalars(select(ResponsavelModel)).all()
    return responsavel


@router.get("/pagined/", status_code=HTTPStatus.OK, response_model=List[ResponsavelPublic]) 
def list_responsavel_paged(limit: int = 5, skip: int = 0, session: Session = Depends(get_session)):
    responsavel = session.scalars(select(ResponsavelModel).limit(limit).offset(skip)).all()
    return responsavel




@router.post("/", status_code=HTTPStatus.CREATED, response_model=ResponsavelPublic)
def create_responsavel(responsavel: Responsavel):
    engine = create_engine(Settings().DATABASE_URL)
    with Session(engine) as session:
        db_responsavel = session.scalar(select(ResponsavelModel).where(ResponsavelModel.email == responsavel.email))
        if db_responsavel:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Responsavel already exists")
        data = responsavel.dict(exclude={"responsaveis"})
        db_instance = ResponsavelModel(**data)
        session.add(db_instance)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
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
    with session as session:
        db_database = session.scalar(select(ResponsavelModel).where(ResponsavelModel.id == responsavel_id))
        if not db_database:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Responsavel not found")
        session.delete(db_database)
        session.commit()
    return {"message": "Responsavel deleted successfully"}




@router.put("/{responsavel_id}", status_code=HTTPStatus.OK, response_model=ResponsavelPublic)
def update_responsavel(responsavel_id: int, responsavel: Responsavel, session: Session = Depends(get_session)):
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
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Responsável not found")

        # Atualiza os dados do responsável
        update_data = responsavel.dict(exclude={"databases", "tabelas", "topicos_kafka"})
        for key, value in update_data.items():
            setattr(db_responsavel, key, value)

        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Responsável update failed")

        # Atualiza o objeto para refletir as mudanças
        session.refresh(db_responsavel)

    return db_responsavel



@router.get("/responsaveis", status_code=HTTPStatus.OK)
def count_responsaveis(session: Session = Depends(get_session)):
    """
    Endpoint para contar o número de registros na tabela 'responsaveis'.
    """
    quantidade = session.scalar(select(func.count()).select_from(ResponsavelModel))
    return {"quantidade": quantidade}


    

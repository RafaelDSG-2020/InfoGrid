from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from http import HTTPStatus
from typing import List
from infogrid.database import get_session
from infogrid.models import ColunaTopicoKafka as ColunaTopicoKafkaModel
from infogrid.schemas import ColunaTopicoKafka, ColunaTopicoKafkaPublic
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/api/v1/colunatopicokafka', tags=['colunatopicokafka'])


@router.get("/", status_code=HTTPStatus.OK, response_model=List[ColunaTopicoKafkaPublic])
def list_colunas_topico_kafka(session: Session = Depends(get_session)):
    colunas = session.scalars(select(ColunaTopicoKafkaModel)).all()
    return colunas


@router.get("/pagined/", status_code=HTTPStatus.OK, response_model=List[ColunaTopicoKafkaPublic])
def list_colunas_topico_kafka_paged(limit: int = 5, skip: int = 0, session: Session = Depends(get_session)):
    colunas = session.scalars(select(ColunaTopicoKafkaModel).limit(limit).offset(skip)).all()
    return colunas


@router.post("/", status_code=HTTPStatus.CREATED, response_model=ColunaTopicoKafkaPublic)
def create_coluna_topico_kafka(coluna: ColunaTopicoKafka, session: Session = Depends(get_session)):
    """
    Cria uma nova coluna associada a um tópico Kafka
    """
    with session as session:
        db_coluna = session.scalar(
            select(ColunaTopicoKafkaModel)
            .where(
                (ColunaTopicoKafkaModel.nome == coluna.nome) &
                (ColunaTopicoKafkaModel.topico_kafka_id == coluna.topico_kafka_id)
            )
        )
        if db_coluna:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Coluna do Tópico Kafka already exists")

        db_instance = ColunaTopicoKafkaModel(**coluna.dict())
        session.add(db_instance)

        try:
            session.commit()
        except IntegrityError as e:
            session.rollback()
            logger.error(f"Erro ao inserir coluna: {str(e)}")  # Registra o erro detalhado
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=f"Coluna do Tópico Kafka insertion failed: {str(e)}")

        session.refresh(db_instance)

    return {
        "id": db_instance.id,
        "nome": db_instance.nome,
        "tipo_dado": db_instance.tipo_dado,
        "descricao": db_instance.descricao,
        "topico_kafka_id": db_instance.topico_kafka_id,
    }


@router.delete("/{coluna_id}", status_code=HTTPStatus.NO_CONTENT)
def delete_coluna_topico_kafka(coluna_id: int, session: Session = Depends(get_session)):
    with session as session:
        db_coluna = session.scalar(select(ColunaTopicoKafkaModel).where(ColunaTopicoKafkaModel.id == coluna_id))
        if not db_coluna:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Coluna do Tópico Kafka not found")
        session.delete(db_coluna)
        session.commit()
    return {"message": "Coluna do Tópico Kafka deleted successfully"}


@router.put("/{coluna_id}", status_code=HTTPStatus.OK, response_model=ColunaTopicoKafkaPublic)
def update_coluna_topico_kafka(coluna_id: int, coluna: ColunaTopicoKafka, session: Session = Depends(get_session)):
    with session as session:
        db_coluna = session.scalar(select(ColunaTopicoKafkaModel).where(ColunaTopicoKafkaModel.id == coluna_id))
        if not db_coluna:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Coluna do Tópico Kafka not found")

        # Atualiza os dados da coluna
        update_data = coluna.dict()
        for key, value in update_data.items():
            setattr(db_coluna, key, value)

        try:
            session.commit()
        except IntegrityError as e:
            session.rollback()
            logger.error(f"Erro ao inserir coluna: {str(e)}")  # Registra o erro detalhado
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Coluna do Tópico Kafka update failed")

        session.refresh(db_coluna)

    return db_coluna




@router.get("/colunastopicoskafka", status_code=HTTPStatus.OK)
def count_databases(session: Session = Depends(get_session)):
    """
    Endpoint para contar o número de registros na tabela 'colunastopicoskafka'.
    """
    quantidade = session.scalar(select(func.count()).select_from(ColunaTopicoKafkaModel))
    return {"quantidade": quantidade}
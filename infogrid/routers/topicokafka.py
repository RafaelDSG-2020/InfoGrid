from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload
from http import HTTPStatus
from typing import List
from infogrid.database import get_session
from infogrid.models import TopicoKafka as TopicoKafkaModel
from infogrid.schemas import TopicoKafka, TopicoKafkaPublic

router = APIRouter(prefix='/api/v1/topicokafka', tags=['topicokafka'])


@router.get("/", status_code=HTTPStatus.OK, response_model=List[TopicoKafkaPublic])
def list_topicos_kafka(session: Session = Depends(get_session)):
    topicos = session.scalars(select(TopicoKafkaModel)).all()
    return topicos


@router.get("/pagined/", status_code=HTTPStatus.OK, response_model=List[TopicoKafkaPublic])
def list_topicos_kafka_paged(limit: int = 5, skip: int = 0, session: Session = Depends(get_session)):
    topicos = session.scalars(select(TopicoKafkaModel).limit(limit).offset(skip)).all()
    return topicos


@router.post("/", status_code=HTTPStatus.CREATED, response_model=TopicoKafkaPublic)
def create_topico_kafka(topico: TopicoKafka, session: Session = Depends(get_session)):
    """
    Cria um novo tópico Kafka ignorando os responsáveis associados
    """
    with session as session:
        db_topico = session.scalar(select(TopicoKafkaModel).where(TopicoKafkaModel.nome == topico.nome))
        if db_topico:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Tópico Kafka already exists")

        data = topico.dict(exclude={"responsaveis"})
        db_instance = TopicoKafkaModel(**data)
        session.add(db_instance)

        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Tópico Kafka insertion failed")

        session.refresh(db_instance)

    return {
        "id": db_instance.id,
        "nome": db_instance.nome,
        "descricao": db_instance.descricao,
        "responsaveis": [],
        "estado_atual": db_instance.estado_atual,
        "conformidade": db_instance.conformidade,
    }


@router.delete("/{topico_id}", status_code=HTTPStatus.NO_CONTENT)
def delete_topico_kafka(topico_id: int, session: Session = Depends(get_session)):
    with session as session:
        db_topico = session.scalar(select(TopicoKafkaModel).where(TopicoKafkaModel.id == topico_id))
        if not db_topico:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Tópico Kafka not found")
        session.delete(db_topico)
        session.commit()
    return {"message": "Tópico Kafka deleted successfully"}


@router.put("/{topico_id}", status_code=HTTPStatus.OK, response_model=TopicoKafkaPublic)
def update_topico_kafka(topico_id: int, topico: TopicoKafka, session: Session = Depends(get_session)):
    with session as session:
        db_topico = session.scalar(
            select(TopicoKafkaModel)
            .where(TopicoKafkaModel.id == topico_id)
            .options(joinedload(TopicoKafkaModel.responsaveis))  # Carrega responsaveis
        )
        if not db_topico:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Tópico Kafka not found")

        # Atualiza os dados do tópico Kafka
        update_data = topico.dict(exclude={"responsaveis"})
        for key, value in update_data.items():
            setattr(db_topico, key, value)

        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Tópico Kafka update failed")

        session.refresh(db_topico)

    return db_topico



@router.get("/topicoskafka", status_code=HTTPStatus.OK)
def count_databases(session: Session = Depends(get_session)):
    """
    Endpoint para contar o número de registros na tabela 'topicoskafka'.
    """
    quantidade = session.scalar(select(func.count()).select_from(TopicoKafkaModel))
    return {"quantidade": quantidade}

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload
from http import HTTPStatus
from typing import List
from infogrid.database import get_session
from infogrid.models import TopicoKafka as TopicoKafkaModel
from infogrid.schemas import TopicoKafka, TopicoKafkaPublic
import logging

logger = logging.getLogger("app_logger")

router = APIRouter(prefix='/api/v1/topicokafka', tags=['topicokafka'])


@router.get("/", status_code=HTTPStatus.OK, response_model=List[TopicoKafkaPublic])
def list_topicos_kafka(session: Session = Depends(get_session)):
    logger.info("Endpoint /topicokafka acessado")
    topicos = session.scalars(select(TopicoKafkaModel)).all()
    logger.info(f"{len(topicos)} tópicos Kafka encontrados")
    return topicos


@router.get("/pagined/", status_code=HTTPStatus.OK, response_model=List[TopicoKafkaPublic])
def list_topicos_kafka_paged(limit: int = 5, skip: int = 0, session: Session = Depends(get_session)):
    logger.info(f"Endpoint /topicokafka/pagined acessado com limite {limit} e offset {skip}")
    topicos = session.scalars(select(TopicoKafkaModel).limit(limit).offset(skip)).all()
    logger.info(f"{len(topicos)} tópicos Kafka encontrados")
    return topicos


@router.post("/", status_code=HTTPStatus.CREATED, response_model=TopicoKafkaPublic)
def create_topico_kafka(topico: TopicoKafka, session: Session = Depends(get_session)):
    """
    Cria um novo tópico Kafka ignorando os responsáveis associados
    """
    with session as session:
        db_topico = session.scalar(select(TopicoKafkaModel).where(TopicoKafkaModel.nome == topico.nome))
        if db_topico:
            logger.warning("Tentativa de criação de tópico Kafka falhou: tópico já existe")
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Tópico Kafka already exists")

        data = topico.dict(exclude={"responsaveis"})
        db_instance = TopicoKafkaModel(**data)
        session.add(db_instance)

        try:
            session.commit()
            logger.info(f"Tópico Kafka '{db_instance.nome}' criado com sucesso")
        except IntegrityError:
            session.rollback()
            logger.error("Erro ao inserir tópico Kafka", exc_info=True)
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
    logger.info(f"Tentativa de exclusão do tópico Kafka com ID {topico_id}")
    with session as session:
        db_topico = session.scalar(select(TopicoKafkaModel).where(TopicoKafkaModel.id == topico_id))
        if not db_topico:
            logger.warning(f"Tentativa de exclusão falhou: tópico Kafka com ID {topico_id} não encontrado")
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Tópico Kafka not found")
        session.delete(db_topico)
        try:
            session.commit()
            logger.info(f"Tópico Kafka com ID {topico_id} excluído com sucesso")
        except IntegrityError as e:
            session.rollback()
            logger.error(f"Erro ao excluir tópico Kafka com ID {topico_id}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=f"Tópico Kafka deletion failed: {str(e)}")
    return {"message": "Tópico Kafka deleted successfully"}

    #     session.commit()
    # return {"message": "Tópico Kafka deleted successfully"}


@router.put("/{topico_id}", status_code=HTTPStatus.OK, response_model=TopicoKafkaPublic)
def update_topico_kafka(topico_id: int, topico: TopicoKafka, session: Session = Depends(get_session)):
    logger.info(f"Tentativa de atualização do tópico Kafka com ID {topico_id}")
    with session as session:
        db_topico = session.scalar(
            select(TopicoKafkaModel)
            .where(TopicoKafkaModel.id == topico_id)
            .options(joinedload(TopicoKafkaModel.responsaveis))  # Carrega responsaveis
        )
        if not db_topico:
            logger.warning(f"Tentativa de atualização falhou: tópico Kafka com ID {topico_id} não encontrado")
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Tópico Kafka not found")

        # Atualiza os dados do tópico Kafka
        update_data = topico.dict(exclude={"responsaveis"})
        for key, value in update_data.items():
            setattr(db_topico, key, value)

        try:
            session.commit()
            logger.info(f"Tópico Kafka com ID {topico_id} atualizado com sucesso")
        except IntegrityError:
            session.rollback()
            logger.error(f"Erro ao atualizar tópico Kafka com ID {topico_id}", exc_info=True)
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Tópico Kafka update failed")

        session.refresh(db_topico)

    return db_topico



@router.get("/topicoskafka", status_code=HTTPStatus.OK)
def count_databases(session: Session = Depends(get_session)):
    """
    Endpoint para contar o número de registros na tabela 'topicoskafka'.
    """
    logger.info("Endpoint /topicokafka/topicoskafka acessado para contar registros")
    quantidade = session.scalar(select(func.count()).select_from(TopicoKafkaModel))
    logger.info(f"Quantidade de tópicos Kafka: {quantidade}")
    return {"quantidade": quantidade}

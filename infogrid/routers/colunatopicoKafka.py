from fastapi import APIRouter, Depends, HTTPException
from http import HTTPStatus
from typing import List
import logging
from beanie import PydanticObjectId
from infogrid.models import ColunaTopicoKafka, TopicoKafka
from infogrid.schemas import ColunaTopicoKafka as ColunaTopicoKafkaSchema, ColunaTopicoKafkaPublic

logger = logging.getLogger("app_logger")

router = APIRouter(prefix="/api/v1/colunatopicokafka", tags=["colunatopicokafka"])


@router.get("/", status_code=HTTPStatus.OK, response_model=List[ColunaTopicoKafkaPublic])
async def list_colunas_topico_kafka():
    """Lista todas as colunas de tópicos Kafka"""
    logger.info("Endpoint /colunatopicokafka acessado")
    
    # Buscar colunas carregando os links corretamente
    colunas = await ColunaTopicoKafka.find(fetch_links=True).to_list()
    
    return [
        ColunaTopicoKafkaPublic(
            id=str(col.id),
            nome=col.nome,
            tipo_dado=col.tipo_dado,
            descricao=col.descricao,
            # Se o link foi carregado, acessar o atributo id corretamente
            topico_kafka_id=str(col.topico_kafka.id) if hasattr(col.topico_kafka, "id") else str(col.topico_kafka),
        )
        for col in colunas
    ]



@router.get("/pagined/", status_code=HTTPStatus.OK, response_model=List[ColunaTopicoKafkaPublic])
async def list_colunas_topico_kafka_paged(limit: int = 5, skip: int = 0):
    """Lista colunas de tópicos Kafka com paginação"""
    logger.info(f"Endpoint /colunatopicokafka/pagined acessado com limite {limit} e offset {skip}")
    
    # Buscar colunas com paginação carregando os links corretamente
    colunas = await ColunaTopicoKafka.find(fetch_links=True).skip(skip).limit(limit).to_list()
    
    return [
        ColunaTopicoKafkaPublic(
            id=str(col.id),
            nome=col.nome,
            tipo_dado=col.tipo_dado,
            descricao=col.descricao,
            topico_kafka_id=str(col.topico_kafka.id) if hasattr(col.topico_kafka, "id") else str(col.topico_kafka),
        )
        for col in colunas
    ]



@router.post("/", status_code=HTTPStatus.CREATED, response_model=ColunaTopicoKafkaPublic)
async def create_coluna_topico_kafka(coluna: ColunaTopicoKafkaSchema):
    """Cria uma nova coluna associada a um tópico Kafka"""
    logger.info("Tentativa de criação de uma nova coluna de tópico Kafka")

    # Verificar se o tópico Kafka existe
    topico_kafka = await TopicoKafka.get(PydanticObjectId(coluna.topico_kafka_id))
    if not topico_kafka:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Tópico Kafka não encontrado")

    # Verificar se já existe uma coluna com o mesmo nome no mesmo tópico
    db_coluna = await ColunaTopicoKafka.find_one(
        ColunaTopicoKafka.nome == coluna.nome,
        ColunaTopicoKafka.topico_kafka == topico_kafka.id
    )
    if db_coluna:
        logger.warning("Coluna já existe para este tópico Kafka")
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Coluna do Tópico Kafka já existe")

    # Criar a nova coluna associada ao tópico Kafka
    nova_coluna = ColunaTopicoKafka(
        nome=coluna.nome,
        tipo_dado=coluna.tipo_dado,
        descricao=coluna.descricao,
        topico_kafka=topico_kafka.id  # Apenas o ID
    )
    await nova_coluna.insert()

    logger.info(f"Coluna de tópico Kafka '{nova_coluna.nome}' criada com sucesso")
    return ColunaTopicoKafkaPublic(
        id=str(nova_coluna.id),
        nome=nova_coluna.nome,
        tipo_dado=nova_coluna.tipo_dado,
        descricao=nova_coluna.descricao,
        topico_kafka_id=str(nova_coluna.topico_kafka),
    )


@router.delete("/{coluna_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_coluna_topico_kafka(coluna_id: str):
    """Exclui uma coluna de tópico Kafka pelo ID"""
    logger.info(f"Tentativa de exclusão da coluna de tópico Kafka com ID {coluna_id}")

    db_coluna = await ColunaTopicoKafka.get(PydanticObjectId(coluna_id))
    if not db_coluna:
        logger.warning(f"Coluna com ID {coluna_id} não encontrada")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Coluna do Tópico Kafka não encontrada")

    await db_coluna.delete()

    logger.info(f"Coluna de tópico Kafka com ID {coluna_id} excluída com sucesso")
    return {"message": "Coluna do Tópico Kafka deletada com sucesso"}


@router.put("/{coluna_id}", status_code=HTTPStatus.OK, response_model=ColunaTopicoKafkaPublic)
async def update_coluna_topico_kafka(coluna_id: str, coluna: ColunaTopicoKafkaSchema):
    """Atualiza uma coluna de tópico Kafka pelo ID"""
    logger.info(f"Tentativa de atualização da coluna de tópico Kafka com ID {coluna_id}")

    db_coluna = await ColunaTopicoKafka.get(PydanticObjectId(coluna_id), fetch_links=True)
    if not db_coluna:
        logger.warning(f"Coluna com ID {coluna_id} não encontrada")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Coluna do Tópico Kafka não encontrada")

    # Se um novo `topico_kafka_id` for passado, verificar se o tópico existe
    if coluna.topico_kafka_id:
        topico_kafka = await TopicoKafka.get(PydanticObjectId(coluna.topico_kafka_id))
        if not topico_kafka:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Tópico Kafka não encontrado")
        topico_kafka_id = topico_kafka.id
    else:
        topico_kafka_id = db_coluna.topico_kafka.id if db_coluna.topico_kafka else None

    # Criar dicionário de atualização apenas com os campos preenchidos
    update_data = {
        "nome": coluna.nome if coluna.nome else db_coluna.nome,
        "tipo_dado": coluna.tipo_dado if coluna.tipo_dado else db_coluna.tipo_dado,
        "descricao": coluna.descricao if coluna.descricao else db_coluna.descricao,
        "topico_kafka": topico_kafka_id,
    }
    
    # Aplicar a atualização no banco
    await db_coluna.set(update_data)

    logger.info(f"Coluna de tópico Kafka com ID {coluna_id} atualizada com sucesso")
    return ColunaTopicoKafkaPublic(
        id=str(db_coluna.id),
        nome=db_coluna.nome,
        tipo_dado=db_coluna.tipo_dado,
        descricao=db_coluna.descricao,
        topico_kafka_id=str(db_coluna.topico_kafka.id) if db_coluna.topico_kafka else None,
    )


@router.get("/count", status_code=HTTPStatus.OK)
async def count_colunas_topico_kafka():
    """Conta o número total de colunas de tópicos Kafka"""
    logger.info("Endpoint /colunatopicokafka/count acessado")
    quantidade = await ColunaTopicoKafka.find().count()
    logger.info(f"Quantidade de colunas de tópicos Kafka: {quantidade}")
    return {"quantidade": quantidade}


@router.get("/coluna-topico-kafka/{coluna_topico_id}", status_code=HTTPStatus.OK)
async def get_coluna_topico_kafka_by_id(coluna_topico_id: str):
    """Busca uma Coluna de um Tópico Kafka pelo ID"""
    coluna_topico = await ColunaTopicoKafka.get(PydanticObjectId(coluna_topico_id))
    if not coluna_topico:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Coluna de Tópico Kafka não encontrada")
    return coluna_topico

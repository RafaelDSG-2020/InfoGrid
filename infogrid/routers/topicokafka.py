from fastapi import APIRouter, Depends, HTTPException
from http import HTTPStatus
from typing import List
import logging
from beanie import PydanticObjectId
from infogrid.models import TopicoKafka as TopicoKafkaModel, Usuario
from infogrid.database import get_db
from infogrid.schemas import TopicoKafka as TopicoKafkaSchema, TopicoKafkaPublic

logger = logging.getLogger("app_logger")

router = APIRouter(prefix="/api/v1/topicokafka", tags=["topicokafka"])


# ==========================
# LISTAR TODOS OS TÓPICOS KAFKA
# ==========================

@router.get("/", status_code=HTTPStatus.OK, response_model=List[TopicoKafkaPublic])
async def list_topicos_kafka():
    """Lista todos os tópicos Kafka"""
    logger.info("Endpoint /topicokafka acessado")
    
    # Buscar os tópicos e carregar os links corretamente
    topicos = await TopicoKafkaModel.find(fetch_links=True).to_list(100)
    
    return [
        TopicoKafkaPublic(
            id=str(topico.id),
            nome=topico.nome,
            descricao=topico.descricao,
            responsaveis=[
                str(res.id) if hasattr(res, "id") else str(res) for res in topico.responsaveis
            ] if topico.responsaveis else [],
            estado_atual=topico.estado_atual,
            conformidade=topico.conformidade,
        )
        for topico in topicos
    ]


@router.get("/pagined/", status_code=HTTPStatus.OK, response_model=List[TopicoKafkaPublic])
async def list_topicos_kafka_paged(limit: int = 5, skip: int = 0):
    """Lista tópicos Kafka com paginação"""
    logger.info(f"Endpoint /topicokafka/pagined acessado com limite {limit} e offset {skip}")
    
    # Buscar os tópicos e carregar os links corretamente
    topicos = await TopicoKafkaModel.find(fetch_links=True).skip(skip).limit(limit).to_list()
    
    return [
        TopicoKafkaPublic(
            id=str(topico.id),
            nome=topico.nome,
            descricao=topico.descricao,
            responsaveis=[
                str(res.id) if hasattr(res, "id") else str(res) for res in topico.responsaveis
            ] if topico.responsaveis else [],
            estado_atual=topico.estado_atual,
            conformidade=topico.conformidade,
        )
        for topico in topicos
    ]


# ==========================
# CRIAR UM NOVO TÓPICO KAFKA
# ==========================

@router.post("/", status_code=HTTPStatus.CREATED, response_model=TopicoKafkaPublic)
async def create_topico_kafka(topico: TopicoKafkaSchema, db=Depends(get_db)):
    """Cria um novo tópico Kafka"""
    logger.info("Endpoint /topicokafka acessado para criação")

    # Converter IDs dos responsáveis para PydanticObjectId
    responsaveis_ids = [PydanticObjectId(res_id) for res_id in topico.responsaveis]

    novo_topico = TopicoKafkaModel(
        nome=topico.nome,
        descricao=topico.descricao,
        responsaveis=responsaveis_ids,  # Armazena apenas os IDs
        estado_atual=topico.estado_atual,
        conformidade=topico.conformidade,
    )
    await novo_topico.insert()

    return TopicoKafkaPublic(
        id=str(novo_topico.id),
        nome=novo_topico.nome,
        descricao=novo_topico.descricao,
        responsaveis=[str(res) for res in novo_topico.responsaveis],  # Retorna os IDs como strings
        estado_atual=novo_topico.estado_atual,
        conformidade=novo_topico.conformidade,
    )



# ==========================
# DELETAR UM TÓPICO KAFKA
# ==========================

@router.delete("/{topico_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_topico_kafka(topico_id: str):
    """Exclui um tópico Kafka pelo ID"""
    logger.info(f"Tentativa de exclusão do tópico Kafka com ID {topico_id}")

    db_topico = await TopicoKafkaModel.get(PydanticObjectId(topico_id))
    if not db_topico:
        logger.warning(f"Tópico Kafka com ID {topico_id} não encontrado")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Tópico Kafka not found")

    await db_topico.delete()

    logger.info(f"Tópico Kafka com ID {topico_id} excluído com sucesso")
    return {"message": "Tópico Kafka deleted successfully"}


# ==========================
# ATUALIZAR UM TÓPICO KAFKA
# ==========================

@router.put("/{topico_id}", status_code=HTTPStatus.OK, response_model=TopicoKafkaPublic)
async def update_topico_kafka(topico_id: str, topico: TopicoKafkaSchema):
    """Atualiza um tópico Kafka pelo ID"""
    logger.info(f"Tentativa de atualização do tópico Kafka com ID {topico_id}")

    # Buscar o tópico no banco de dados
    db_topico = await TopicoKafkaModel.get(PydanticObjectId(topico_id), fetch_links=True)
    if not db_topico:
        logger.warning(f"Tópico Kafka com ID {topico_id} não encontrado")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Tópico Kafka not found")

    # Atualizar responsáveis corretamente
    if topico.responsaveis:
        responsaveis_links = [PydanticObjectId(res_id) for res_id in topico.responsaveis]
    else:
        responsaveis_links = db_topico.responsaveis  # Mantém os responsáveis existentes

    # Criar dicionário de atualização apenas com os campos preenchidos
    update_data = {
        "nome": topico.nome if topico.nome else db_topico.nome,
        "descricao": topico.descricao if topico.descricao else db_topico.descricao,
        "responsaveis": responsaveis_links,
        "estado_atual": topico.estado_atual if topico.estado_atual else db_topico.estado_atual,
        "conformidade": topico.conformidade if topico.conformidade is not None else db_topico.conformidade,
    }

    # Aplicar a atualização no banco
    await db_topico.set(update_data)

    logger.info(f"Tópico Kafka com ID {topico_id} atualizado com sucesso")

    # Retornar o objeto atualizado corretamente formatado
    return TopicoKafkaPublic(
        id=str(db_topico.id),
        nome=db_topico.nome,
        descricao=db_topico.descricao,
        responsaveis=[str(res.id) if hasattr(res, "id") else str(res) for res in db_topico.responsaveis] if db_topico.responsaveis else [],
        estado_atual=db_topico.estado_atual,
        conformidade=db_topico.conformidade,
    )



# ==========================
# CONTAR TÓPICOS KAFKA
# ==========================

@router.get("/count", status_code=HTTPStatus.OK)
async def count_topicos_kafka():
    """Conta o número total de tópicos Kafka"""
    logger.info("Endpoint /topicokafka/count acessado")
    quantidade = await TopicoKafkaModel.find().count()
    logger.info(f"Quantidade de tópicos Kafka: {quantidade}")
    return {"quantidade": quantidade}

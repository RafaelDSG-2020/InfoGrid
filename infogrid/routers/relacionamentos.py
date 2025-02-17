from fastapi import APIRouter, HTTPException
from http import HTTPStatus
import logging
from beanie import PydanticObjectId
from infogrid.models import Responsavel, Database, Tabela, TopicoKafka

logger = logging.getLogger("app_logger")

router = APIRouter(prefix="/api/v1/relacionamentos", tags=["relacionamentos"])


# ==========================
# RELACIONAMENTOS RESPONSÁVEIS X DATABASES
# ==========================

@router.post("/responsaveis_databases/", status_code=HTTPStatus.CREATED)
async def create_responsavel_database(responsavel_id: str, database_id: str):
    """Cria um relacionamento entre Responsável e Database"""
    responsavel = await Responsavel.get(PydanticObjectId(responsavel_id))
    database = await Database.get(PydanticObjectId(database_id))

    if not responsavel or not database:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Responsável ou Database não encontrado")

    if database.id in responsavel.databases:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Relacionamento já existe")

    responsavel.databases.append(database.id)
    await responsavel.save()

    return {"message": "Relacionamento criado com sucesso"}


@router.delete("/responsaveis_databases/", status_code=HTTPStatus.NO_CONTENT)
async def delete_responsavel_database(responsavel_id: str, database_id: str):
    """Remove um relacionamento entre Responsável e Database"""
    responsavel = await Responsavel.get(PydanticObjectId(responsavel_id))

    if not responsavel or database_id not in responsavel.databases:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Relacionamento não encontrado")

    responsavel.databases.remove(database_id)
    await responsavel.save()

    return {"message": "Relacionamento excluído com sucesso"}


@router.get("/responsaveis_databases/", status_code=HTTPStatus.OK)
async def get_responsavel_databases():
    """Lista todos os relacionamentos de Responsáveis com Databases"""
    responsaveis = await Responsavel.find().to_list()
    relacionamentos = []
    
    for r in responsaveis:
        for db_id in r.databases:
            database = await Database.get(db_id)
            if database:
                relacionamentos.append({
                    "responsavel_id": str(r.id),
                    "responsavel_nome": r.nome,
                    "database_id": str(database.id),
                    "database_nome": database.nome
                })

    return relacionamentos


# ==========================
# RELACIONAMENTOS RESPONSÁVEIS X TABELAS
# ==========================

@router.post("/responsaveis_tabelas/", status_code=HTTPStatus.CREATED)
async def create_responsavel_tabela(responsavel_id: str, tabela_id: str):
    """Cria um relacionamento entre Responsável e Tabela"""
    responsavel = await Responsavel.get(PydanticObjectId(responsavel_id))
    tabela = await Tabela.get(PydanticObjectId(tabela_id))

    if not responsavel or not tabela:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Responsável ou Tabela não encontrado")

    if tabela.id in responsavel.tabelas:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Relacionamento já existe")

    responsavel.tabelas.append(tabela.id)
    await responsavel.save()

    return {"message": "Relacionamento criado com sucesso"}


@router.delete("/responsaveis_tabelas/", status_code=HTTPStatus.NO_CONTENT)
async def delete_responsavel_tabela(responsavel_id: str, tabela_id: str):
    """Remove um relacionamento entre Responsável e Tabela"""
    responsavel = await Responsavel.get(PydanticObjectId(responsavel_id))

    if not responsavel or tabela_id not in responsavel.tabelas:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Relacionamento não encontrado")

    responsavel.tabelas.remove(tabela_id)
    await responsavel.save()

    return {"message": "Relacionamento excluído com sucesso"}


@router.get("/responsaveis_tabelas/", status_code=HTTPStatus.OK)
async def get_responsavel_tabelas():
    """Lista todos os relacionamentos de Responsáveis com Tabelas"""
    responsaveis = await Responsavel.find().to_list()
    relacionamentos = []
    
    for r in responsaveis:
        for tb_id in r.tabelas:
            tabela = await Tabela.get(tb_id)
            if tabela:
                relacionamentos.append({
                    "responsavel_id": str(r.id),
                    "responsavel_nome": r.nome,
                    "tabela_id": str(tabela.id),
                    "tabela_nome": tabela.nome
                })

    return relacionamentos


# ==========================
# RELACIONAMENTOS RESPONSÁVEIS X TÓPICOS KAFKA
# ==========================

@router.post("/responsaveis_topicos_kafka/", status_code=HTTPStatus.CREATED)
async def create_responsavel_topico_kafka(responsavel_id: str, topico_kafka_id: str):
    """Cria um relacionamento entre Responsável e Tópico Kafka"""
    responsavel = await Responsavel.get(PydanticObjectId(responsavel_id))
    topico = await TopicoKafka.get(PydanticObjectId(topico_kafka_id))

    if not responsavel or not topico:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Responsável ou Tópico Kafka não encontrado")

    if topico.id in responsavel.topicos_kafka:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Relacionamento já existe")

    responsavel.topicos_kafka.append(topico.id)
    await responsavel.save()

    return {"message": "Relacionamento criado com sucesso"}


@router.delete("/responsaveis_topicos_kafka/", status_code=HTTPStatus.NO_CONTENT)
async def delete_responsavel_topico_kafka(responsavel_id: str, topico_kafka_id: str):
    """Remove um relacionamento entre Responsável e Tópico Kafka"""
    responsavel = await Responsavel.get(PydanticObjectId(responsavel_id))

    if not responsavel or topico_kafka_id not in responsavel.topicos_kafka:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Relacionamento não encontrado")

    responsavel.topicos_kafka.remove(topico_kafka_id)
    await responsavel.save()

    return {"message": "Relacionamento excluído com sucesso"}


@router.get("/responsaveis_topicos_kafka/", status_code=HTTPStatus.OK)
async def get_responsavel_topicos_kafka():
    """Lista todos os relacionamentos de Responsáveis com Tópicos Kafka"""
    responsaveis = await Responsavel.find().to_list()
    relacionamentos = []
    
    for r in responsaveis:
        for tk_id in r.topicos_kafka:
            topico = await TopicoKafka.get(tk_id)
            if topico:
                relacionamentos.append({
                    "responsavel_id": str(r.id),
                    "responsavel_nome": r.nome,
                    "topico_kafka_id": str(topico.id),
                    "topico_kafka_nome": topico.nome
                })

    return relacionamentos

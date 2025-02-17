from fastapi import APIRouter, HTTPException, Query
from http import HTTPStatus
import logging
from typing import List, Optional
from infogrid.models import Responsavel, Database, Tabela, TopicoKafka

logger = logging.getLogger("app_logger")

router = APIRouter(prefix="/api/v1/entidades", tags=["entidades"])


@router.get("/responsaveis/", status_code=HTTPStatus.OK)
async def get_responsaveis(
    nome: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
):
    """Filtra Responsáveis por nome ou email"""
    query = {}

    if nome:
        query["nome"] = {"$regex": nome, "$options": "i"}
    if email:
        query["email"] = {"$regex": email, "$options": "i"}

    responsaveis = await Responsavel.find(query).to_list(100)

    if not responsaveis:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Responsáveis não encontrados")

    return responsaveis


@router.get("/databases/", status_code=HTTPStatus.OK)
async def get_databases(
    nome: Optional[str] = Query(None),
    tecnologia: Optional[str] = Query(None),
):
    """Filtra Bancos de Dados por nome ou tecnologia"""
    query = {}

    if nome:
        query["nome"] = {"$regex": nome, "$options": "i"}
    if tecnologia:
        query["tecnologia"] = {"$regex": tecnologia, "$options": "i"}

    databases = await Database.find(query).to_list(100)

    if not databases:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Databases não encontrados")

    return databases


@router.get("/tabelas/", status_code=HTTPStatus.OK)
async def get_tabelas(
    nome: Optional[str] = Query(None),
    descricao: Optional[str] = Query(None),
):
    """Filtra Tabelas por nome ou descrição"""
    query = {}

    if nome:
        query["nome"] = {"$regex": nome, "$options": "i"}
    if descricao:
        query["descricao"] = {"$regex": descricao, "$options": "i"}

    tabelas = await Tabela.find(query).to_list(100)

    if not tabelas:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Tabelas não encontradas")

    return tabelas


@router.get("/topicos_kafka/", status_code=HTTPStatus.OK)
async def get_topicos_kafka(
    nome: Optional[str] = Query(None),
    descricao: Optional[str] = Query(None),
):
    """Filtra Tópicos Kafka por nome ou descrição"""
    query = {}

    if nome:
        query["nome"] = {"$regex": nome, "$options": "i"}
    if descricao:
        query["descricao"] = {"$regex": descricao, "$options": "i"}

    topicos_kafka = await TopicoKafka.find(query).to_list(100)

    if not topicos_kafka:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Tópicos Kafka não encontrados")

    return topicos_kafka

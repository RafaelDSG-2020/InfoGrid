from fastapi import APIRouter, HTTPException, Query
from http import HTTPStatus
import logging
from typing import List, Optional
from infogrid.models import Responsavel, Database, Tabela, TopicoKafka, Coluna

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



@router.get("/databases/", status_code=HTTPStatus.OK)
async def sort_databases(
    order_by: str = Query("nome", description="Campo para ordenação (nome ou tecnologia)"),
    order: str = Query("asc", description="Ordem: asc (crescente) ou desc (decrescente)")
):
    """Lista bancos de dados ordenados por nome ou tecnologia"""
    order_direction = 1 if order == "asc" else -1
    databases = await Database.find().sort((order_by, order_direction)).to_list(100)

    if not databases:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Nenhum banco de dados encontrado")

    return databases


# 🔹 2️⃣ Ordenar Tabelas
@router.get("/tabelas/", status_code=HTTPStatus.OK)
async def sort_tabelas(
    order_by: str = Query("nome", description="Campo para ordenação (nome ou descricao)"),
    order: str = Query("asc", description="Ordem: asc (crescente) ou desc (decrescente)")
):
    """Lista tabelas ordenadas por nome ou descrição"""
    order_direction = 1 if order == "asc" else -1
    tabelas = await Tabela.find().sort((order_by, order_direction)).to_list(100)

    if not tabelas:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Nenhuma tabela encontrada")

    return tabelas


# 🔹 3️⃣ Ordenar Colunas
@router.get("/colunas/", status_code=HTTPStatus.OK)
async def sort_colunas(
    order_by: str = Query("nome", description="Campo para ordenação (nome ou tipo_dado)"),
    order: str = Query("asc", description="Ordem: asc (crescente) ou desc (decrescente)")
):
    """Lista colunas ordenadas por nome ou tipo de dado"""
    order_direction = 1 if order == "asc" else -1
    colunas = await Coluna.find().sort((order_by, order_direction)).to_list(100)

    if not colunas:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Nenhuma coluna encontrada")

    return colunas


# 🔹 4️⃣ Ordenar Tópicos Kafka
@router.get("/topicos-kafka/", status_code=HTTPStatus.OK)
async def sort_topicos_kafka(
    order_by: str = Query("nome", description="Campo para ordenação (nome ou estado_atual)"),
    order: str = Query("asc", description="Ordem: asc (crescente) ou desc (decrescente)")
):
    """Lista tópicos Kafka ordenados por nome ou estado atual"""
    order_direction = 1 if order == "asc" else -1
    topicos = await TopicoKafka.find().sort((order_by, order_direction)).to_list(100)

    if not topicos:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Nenhum tópico Kafka encontrado")

    return topicos
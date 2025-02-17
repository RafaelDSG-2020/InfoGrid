from fastapi import APIRouter, HTTPException
from typing import List
from http import HTTPStatus
import logging
from beanie import PydanticObjectId
from bson import ObjectId
from infogrid.models import Tabela, Database, Responsavel
from infogrid.schemas import Tabela as TabelaSchema, TabelaPublic

logger = logging.getLogger("app_logger")

router = APIRouter(prefix="/api/v1/tabela", tags=["tabela"])


@router.get("/", status_code=HTTPStatus.OK, response_model=List[TabelaPublic])
async def list_tabelas():
    """Lista todas as tabelas"""
    logger.info("Endpoint /tabela acessado")
    tabelas = await Tabela.find().to_list(100)

    return [
        TabelaPublic(
            id=str(tb.id),
            nome=tb.nome,
            descricao=tb.descricao,
            database_id=str(tb.database.ref.id) if tb.database else None,  # Acessando o ID corretamente
            responsaveis=[str(resp.ref.id) for resp in tb.responsaveis] if tb.responsaveis else [],
            estado_atual=tb.estado_atual,
            qualidade=tb.qualidade,
            conformidade=tb.conformidade
            
        )
        for tb in tabelas
    ]



@router.get("/pagined/", status_code=HTTPStatus.OK, response_model=List[TabelaPublic])
async def list_tabelas_paged(limit: int = 5, skip: int = 0):
    """Lista tabelas com paginação"""
    logger.info(f"Endpoint /tabela/pagined acessado com limite {limit} e offset {skip}")
    tabelas = await Tabela.find().skip(skip).limit(limit).to_list()
    return [
        TabelaPublic(
            id=str(tb.id),
            nome=tb.nome,
            descricao=tb.descricao,
            database_id=str(tb.database.ref.id) if tb.database else None,  # Acessando o ID corretamente
            responsaveis=[str(resp.ref.id) for resp in tb.responsaveis] if tb.responsaveis else [],
            estado_atual=tb.estado_atual,
            qualidade=tb.qualidade,
            conformidade=tb.conformidade
            
        )
        for tb in tabelas
    ]


@router.post("/", status_code=HTTPStatus.CREATED, response_model=TabelaPublic)
async def create_tabela(tabela: TabelaSchema):
    """Cria uma nova tabela"""
    logger.info("Tentativa de criação de uma nova tabela")

    # 🔍 Verifica se já existe uma tabela com o mesmo nome
    db_tabela = await Tabela.find_one(Tabela.nome == tabela.nome)
    if db_tabela:
        logger.warning("Tabela já existe")
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Tabela already exists")

    # 🔍 Valida se o database_id é um ObjectId válido
    if not ObjectId.is_valid(tabela.database_id):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Invalid database_id format")

    # 🔍 Busca o Database correspondente pelo ID
    db_database = await Database.get(PydanticObjectId(tabela.database_id))
    if not db_database:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Database not found")

    # 🔍 Valida e busca os responsáveis
    responsaveis = []
    for resp_id in tabela.responsaveis:
        if not ObjectId.is_valid(resp_id):
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=f"Invalid responsavel_id format: {resp_id}")

        usuario = await Responsavel.get(PydanticObjectId(resp_id))
        if not usuario:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Responsavel not found: {resp_id}")

        responsaveis.append(usuario)

    # 🔍 Criando a nova tabela corretamente com o Link[Database]
    nova_tabela = Tabela(
        nome=tabela.nome,
        descricao=tabela.descricao,
        database=db_database,
        responsaveis=responsaveis,
        estado_atual=tabela.estado_atual,
        qualidade=tabela.qualidade,
        conformidade=tabela.conformidade,
    )

    await nova_tabela.insert()

    logger.info(f"Tabela '{nova_tabela.nome}' criada com sucesso")
    return TabelaPublic(
        id=str(nova_tabela.id),
        nome=nova_tabela.nome,
        descricao=nova_tabela.descricao,
        database_id=str(nova_tabela.database.id),
        responsaveis=[str(resp.id) for resp in nova_tabela.responsaveis],
        estado_atual=nova_tabela.estado_atual,
        qualidade=nova_tabela.qualidade,
        conformidade=nova_tabela.conformidade,
    )



@router.delete("/{tabela_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_tabela(tabela_id: str):
    """Exclui uma tabela pelo ID"""
    logger.info(f"Tentativa de exclusão da tabela com ID {tabela_id}")

    db_tabela = await Tabela.get(PydanticObjectId(tabela_id))
    if not db_tabela:
        logger.warning(f"Tabela com ID {tabela_id} não encontrada")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Tabela not found")

    await db_tabela.delete()

    logger.info(f"Tabela com ID {tabela_id} excluída com sucesso")
    return {"message": "Tabela deleted successfully"}


@router.put("/{tabela_id}", status_code=HTTPStatus.OK, response_model=TabelaPublic)
async def update_tabela(tabela_id: str, tabela: TabelaSchema):
    """Atualiza uma tabela pelo ID"""
    logger.info(f"Tentativa de atualização da tabela com ID {tabela_id}")

    db_tabela = await Tabela.get(PydanticObjectId(tabela_id))
    if not db_tabela:
        logger.warning(f"Tabela com ID {tabela_id} não encontrada")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Tabela not found")

    update_data = {k: v for k, v in tabela.dict(exclude={"responsaveis"}).items() if v is not None}
    await db_tabela.set(update_data)

    logger.info(f"Tabela com ID {tabela_id} atualizada com sucesso")
    return TabelaPublic(
        id=str(db_tabela.id),
            nome=db_tabela.nome,
            descricao=db_tabela.descricao,
            database_id=str(db_tabela.database.ref.id) if db_tabela.database else None,  # Acessando o ID corretamente
            responsaveis=[str(resp.ref.id) for resp in db_tabela.responsaveis] if db_tabela.responsaveis else [],
            estado_atual=db_tabela.estado_atual,
            qualidade=db_tabela.qualidade,
            conformidade=db_tabela.conformidade
    )


@router.get("/count", status_code=HTTPStatus.OK)
async def count_tabelas():
    """Conta o número total de tabelas"""
    logger.info("Endpoint /tabela/count acessado")
    quantidade = await Tabela.find().count()
    logger.info(f"Quantidade de tabelas: {quantidade}")
    return {"quantidade": quantidade}



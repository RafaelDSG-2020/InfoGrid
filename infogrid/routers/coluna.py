from fastapi import APIRouter, Depends, HTTPException
from http import HTTPStatus
from typing import List
import logging
from beanie import PydanticObjectId
from infogrid.models import Coluna, Tabela
from infogrid.database import get_db
from infogrid.schemas import Coluna as ColunaSchema, ColunaPublic

logger = logging.getLogger("app_logger")

router = APIRouter(prefix="/api/v1/coluna", tags=["coluna"])


@router.get("/", status_code=HTTPStatus.OK, response_model=List[ColunaPublic])
async def list_colunas():
    """Lista todas as colunas"""
    logger.info("Endpoint /coluna acessado")
    colunas = await Coluna.find().to_list(100)
    return [
        ColunaPublic(
            id=str(col.id),
            nome=col.nome,
            tipo_dado=col.tipo_dado,
            descricao=col.descricao,
            tabela_id=str(col.tabela.ref.id) if col.tabela else None,  
        )
        for col in colunas
    ]


@router.get("/pagined/", status_code=HTTPStatus.OK, response_model=List[ColunaPublic])
async def list_colunas_paged(limit: int = 5, skip: int = 0):
    """Lista colunas com paginação"""
    logger.info(f"Endpoint /coluna/pagined acessado com limite {limit} e offset {skip}")
    colunas = await Coluna.find().skip(skip).limit(limit).to_list()
    return [
        ColunaPublic(
            id=str(col.id),
            nome=col.nome,
            tipo_dado=col.tipo_dado,
            descricao=col.descricao,
            tabela_id=str(col.tabela.ref.id) if col.tabela else None,  
        )
        for col in colunas
    ]


@router.post("/", status_code=HTTPStatus.CREATED, response_model=ColunaSchema)
async def create_coluna(coluna: ColunaSchema, db=Depends(get_db)):
    """Cria uma nova coluna"""
    logger.info("Endpoint /coluna acessado para criação")
    
    # Verifique se a tabela existe
    tabela = await Tabela.get(coluna.tabela_id)
    if not tabela:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Tabela não encontrada")

    nova_coluna = Coluna(
        nome=coluna.nome,
        tipo_dado=coluna.tipo_dado,
        descricao=coluna.descricao,
        tabela=tabela  # Fornecendo o campo tabela corretamente
    )
    await nova_coluna.insert()
    return ColunaSchema(
        id=str(nova_coluna.id),
        nome=nova_coluna.nome,
        tipo_dado=nova_coluna.tipo_dado,
        descricao=nova_coluna.descricao,
        tabela_id=str(nova_coluna.tabela.id)  # Incluindo o campo tabela_id na resposta
    )

@router.delete("/{coluna_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_coluna(coluna_id: str):
    """Exclui uma coluna pelo ID"""
    logger.info(f"Tentativa de exclusão da coluna com ID {coluna_id}")

    db_coluna = await Coluna.get(PydanticObjectId(coluna_id))
    if not db_coluna:
        logger.warning(f"Coluna com ID {coluna_id} não encontrada")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Coluna not found")

    await db_coluna.delete()

    logger.info(f"Coluna com ID {coluna_id} excluída com sucesso")
    return {"message": "Coluna deleted successfully"}


@router.put("/{coluna_id}", status_code=HTTPStatus.OK, response_model=ColunaPublic)
async def update_coluna(coluna_id: str, coluna: ColunaSchema):
    """Atualiza uma coluna pelo ID"""
    logger.info(f"Tentativa de atualização da coluna com ID {coluna_id}")

    db_coluna = await Coluna.get(PydanticObjectId(coluna_id))
    if not db_coluna:
        logger.warning(f"Coluna com ID {coluna_id} não encontrada")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Coluna not found")

    update_data = {k: v for k, v in coluna.dict().items() if v is not None}
    await db_coluna.set(update_data)

    logger.info(f"Coluna com ID {coluna_id} atualizada com sucesso")
    return ColunaPublic(
        id=str(db_coluna.id),
            nome=db_coluna.nome,
            tipo_dado=db_coluna.tipo_dado,
            descricao=db_coluna.descricao,
            tabela_id=str(db_coluna.tabela.ref.id) if db_coluna.tabela else None,  # Acessando o ID corretamente
    )


@router.get("/count", status_code=HTTPStatus.OK)
async def count_colunas():
    """Conta o número total de colunas"""
    logger.info("Endpoint /coluna/count acessado")
    quantidade = await Coluna.find().count()
    logger.info(f"Quantidade de colunas: {quantidade}")
    return {"quantidade": quantidade}

from fastapi import APIRouter, Depends, HTTPException
from http import HTTPStatus
from typing import List
import logging
from beanie import PydanticObjectId
from bson.errors import InvalidId
from infogrid.models import Database
from infogrid.schemas import Database as DatabaseSchema, DatabasePublic

logger = logging.getLogger("app_logger")

router = APIRouter(prefix="/api/v1/database", tags=["routerdatabase"])


@router.get("/", status_code=HTTPStatus.OK, response_model=List[DatabasePublic])
async def list_databases():
    """Lista todos os bancos de dados"""
    logger.info("Endpoint /database acessado")
    databases = await Database.find().to_list(100)
    return [
        DatabasePublic(id=str(db.id), nome=db.nome, tecnologia=db.tecnologia, descricao=db.descricao, responsaveis=[])
        for db in databases
    ]


@router.get("/pagined/", status_code=HTTPStatus.OK, response_model=List[DatabasePublic])
async def list_databases_paged(limit: int = 5, skip: int = 0):
    """Lista bancos de dados com paginação"""
    logger.info(f"Endpoint /database/pagined acessado com limite {limit} e offset {skip}")
    databases = await Database.find().skip(skip).limit(limit).to_list()
    return [
        DatabasePublic(id=str(db.id), nome=db.nome, tecnologia=db.tecnologia, descricao=db.descricao, responsaveis=[])
        for db in databases
    ]


@router.post("/", status_code=HTTPStatus.CREATED, response_model=DatabasePublic)
async def create_database(database: DatabaseSchema):
    """Cria um novo banco de dados"""
    logger.info("Tentativa de criação de um novo banco de dados")

    # Verifica se já existe um banco de dados com o mesmo nome
    db_database = await Database.find_one(Database.nome == database.nome)
    if db_database:
        logger.warning("Banco de dados já existe")
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Database already exists")

    # Converte IDs de responsaveis para PydanticObjectId, ignorando inválidos
    database_dict = database.dict(exclude_unset=True)
    valid_responsaveis = []
    
    for responsavel_id in database_dict.get("responsaveis", []):
        try:
            valid_responsaveis.append(PydanticObjectId(responsavel_id))
        except InvalidId:
            logger.error(f"ID inválido encontrado: {responsavel_id}")
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=f"Invalid ID format: {responsavel_id}")

    database_dict["responsaveis"] = valid_responsaveis

    # Cria e insere o banco de dados
    novo_db = Database(**database_dict)
    await novo_db.insert()

    logger.info(f"Banco de dados '{novo_db.nome}' criado com sucesso")
    return DatabasePublic(
        id=str(novo_db.id),
        nome=novo_db.nome,
        tecnologia=novo_db.tecnologia,
        descricao=novo_db.descricao,
        responsaveis=[str(responsavel) for responsavel in novo_db.responsaveis]  # Retorna IDs como strings
    )

@router.delete("/{database_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_database(database_id: str):
    """Exclui um banco de dados pelo ID"""
    logger.info(f"Tentativa de exclusão do banco de dados com ID {database_id}")

    db_database = await Database.get(PydanticObjectId(database_id))
    if not db_database:
        logger.warning(f"Banco de dados com ID {database_id} não encontrado")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Database not found")

    await db_database.delete()

    logger.info(f"Banco de dados com ID {database_id} excluído com sucesso")
    return {"message": "Database deleted successfully"}


@router.put("/{database_id}", status_code=HTTPStatus.OK, response_model=DatabasePublic)
async def update_database(database_id: str, database: DatabaseSchema):
    """Atualiza um banco de dados pelo ID"""
    logger.info(f"Tentativa de atualização do banco de dados com ID {database_id}")

    db_database = await Database.get(PydanticObjectId(database_id))
    if not db_database:
        logger.warning(f"Banco de dados com ID {database_id} não encontrado")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Database not found")

    update_data = {k: v for k, v in database.dict(exclude={"responsaveis"}).items() if v is not None}
    await db_database.set(update_data)

    logger.info(f"Banco de dados com ID {database_id} atualizado com sucesso")
    return DatabasePublic(id=str(db_database.id), nome=db_database.nome, tecnologia=db_database.tecnologia, descricao=db_database.descricao, responsaveis=[])


@router.get("/count", status_code=HTTPStatus.OK)
async def count_databases():
    """Conta o número total de bancos de dados"""
    logger.info("Endpoint /database/count acessado")
    quantidade = await Database.find().count()
    logger.info(f"Quantidade de bancos de dados: {quantidade}")
    return {"quantidade": quantidade}

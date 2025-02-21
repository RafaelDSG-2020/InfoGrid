from fastapi import APIRouter, Depends, HTTPException
from http import HTTPStatus
from typing import List
import logging
from beanie import PydanticObjectId
from bson.errors import InvalidId
from bson import ObjectId, DBRef
from infogrid.models import Database, Tabela
from infogrid.schemas import Database as DatabaseSchema, DatabasePublic

logger = logging.getLogger("app_logger")

router = APIRouter(prefix="/api/v1/database", tags=["routerdatabase"])


@router.get("/", status_code=HTTPStatus.OK, response_model=List[DatabasePublic])
async def list_databases():
    """Lista todos os bancos de dados"""
    logger.info("Endpoint /database acessado")
    
    # Buscar os bancos de dados
    databases = await Database.find().to_list(100)

    return [
        DatabasePublic(
            id=str(db.id),
            nome=db.nome,
            tecnologia=db.tecnologia,
            descricao=db.descricao,
            responsaveis=[str(resp.ref.id) for resp in db.responsaveis] if db.responsaveis else []
        )
        for db in databases
    ]



@router.get("/pagined/", status_code=HTTPStatus.OK, response_model=List[DatabasePublic])
async def list_databases_paged(limit: int = 5, skip: int = 0):
    """Lista bancos de dados com paginação"""
    logger.info(f"Endpoint /database/pagined acessado com limite {limit} e offset {skip}")
    databases = await Database.find().skip(skip).limit(limit).to_list()
    return [
        DatabasePublic(
            id=str(db.id),
            nome=db.nome,
            tecnologia=db.tecnologia,
            descricao=db.descricao,
            responsaveis=[str(resp.ref.id) for resp in db.responsaveis] if db.responsaveis else []
        )
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
            responsaveis=[str(resp.ref.id) for resp in novo_db.responsaveis] if novo_db.responsaveis else []
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




@router.get("/with-tables-columns-optimized/", status_code=HTTPStatus.OK)
async def list_databases_with_tables_and_columns_optimized():
    """Lista Bancos de Dados que possuem tabelas associadas, incluindo suas colunas, usando agregação"""
    logger.info("Endpoint /api/v1/database/with-tables-columns-optimized acessado")

    # 🔹 Obtém todos os IDs dos bancos de dados usando agregação
    pipeline_ids = [{"$project": {"_id": 1}}]  # Apenas projeta o campo _id
    database_ids_cursor = await Database.aggregate(pipeline_ids).to_list(1000)
    database_ids = [db["_id"] for db in database_ids_cursor]  # Extrai apenas os IDs

    # 🔹 Certifica que os IDs são ObjectId (evita erro de comparação)
    database_ids = [ObjectId(db) if isinstance(db, str) else db for db in database_ids]

    pipeline = [
        {
            "$match": {"database.$id": {"$in": database_ids}}  # ✅ Corrigido para DBRef
        },
        {
            "$lookup": {
                "from": "Coluna",  # 🔹 Associa colunas às tabelas
                "localField": "_id",
                "foreignField": "tabela.$id",  # ✅ Correção para DBRef
                "as": "colunas"
            }
        },
        {
            "$group": {
                "_id": "$database",  # ✅ Agrupa tabelas pelo DBRef
                "tabelas": {
                    "$push": {
                        "_id": "$_id",
                        "nome": "$nome",
                        "descricao": "$descricao",
                        "colunas": "$colunas"  # 🔹 Agora colunas são associadas corretamente
                    }
                }
            }
        },
        {
            "$lookup": {
                "from": "Database",  # 🔹 Associa os bancos de dados corretamente
                "localField": "_id.$id",  # ✅ Pegando o ID correto dentro do DBRef
                "foreignField": "_id",
                "as": "database"
            }
        },
        {
            "$unwind": "$database"
        },
        {
            "$project": {
                "_id": "$database._id",
                "nome": "$database.nome",
                "tecnologia": "$database.tecnologia",
                "descricao": "$database.descricao",
                "tabelas": 1
            }
        }
    ]

    result = await Tabela.aggregate(pipeline).to_list(100)

    if not result:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Nenhum banco de dados com tabelas encontrado")

    # ✅ Função para converter DBRef e ObjectId para string
    def clean_objectid_dbref(obj):
        """Converte ObjectId para string e extrai IDs de DBRef"""
        if isinstance(obj, ObjectId):
            return str(obj)  # Converte ObjectId para string
        if isinstance(obj, DBRef):
            return str(obj.id)  # Extrai apenas o ObjectId do DBRef
        if isinstance(obj, dict):
            return {k: clean_objectid_dbref(v) for k, v in obj.items()}  # Converte recursivamente
        if isinstance(obj, list):
            return [clean_objectid_dbref(v) for v in obj]  # Converte listas recursivamente
        return obj

    # 🔹 Aplica a conversão para toda a resposta
    result = clean_objectid_dbref(result)

    return result



@router.get("/database/{database_id}", status_code=HTTPStatus.OK)
async def get_database_by_id(database_id: str):
    """Busca um Banco de Dados pelo ID"""
    database = await Database.get(PydanticObjectId(database_id))
    if not database:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Database não encontrado")
    return database

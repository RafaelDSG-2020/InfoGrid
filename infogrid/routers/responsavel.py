from fastapi import APIRouter, HTTPException, Depends
from http import HTTPStatus
from typing import List
import logging
from beanie import PydanticObjectId
from infogrid.models import Responsavel
from infogrid.schemas import Responsavel as ResponsavelSchema, ResponsavelPublic

logger = logging.getLogger("app_logger")

router = APIRouter(prefix="/api/v1/responsavel", tags=["responsavel"])


@router.get("/", status_code=HTTPStatus.OK, response_model=List[ResponsavelPublic])
async def list_responsavel():
    """Lista todos os responsáveis"""
    logger.info("Endpoint /responsavel acessado")
    responsaveis = await Responsavel.find().to_list(100)
    return [
        ResponsavelPublic(
            id=str(resp.id),
            nome=resp.nome,
            email=resp.email,
            cargo=resp.cargo,
            telefone=resp.telefone
        )
        for resp in responsaveis
    ]


@router.get("/pagined/", status_code=HTTPStatus.OK, response_model=List[ResponsavelPublic])
async def list_responsavel_paged(limit: int = 5, skip: int = 0):
    """Lista responsáveis com paginação"""
    logger.info(f"Endpoint /responsavel/pagined acessado com limite {limit} e offset {skip}")
    responsaveis = await Responsavel.find().skip(skip).limit(limit).to_list()
    return [
        ResponsavelPublic(
            id=str(resp.id),
            nome=resp.nome,
            email=resp.email,
            cargo=resp.cargo,
            telefone=resp.telefone
        )
        for resp in responsaveis
    ]


@router.post("/", status_code=HTTPStatus.CREATED, response_model=ResponsavelPublic)
async def create_responsavel(responsavel: ResponsavelSchema):
    """Cria um novo responsável"""
    logger.info("Tentativa de criação de um novo responsável")

    # Verifica se já existe um responsável com o mesmo email
    try:
        db_responsavel = await Responsavel.find_one(Responsavel.email == responsavel.email)
    except Exception as e:
        logger.error(f"Erro ao buscar responsável por email: {str(e)}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Database query failed")

    if db_responsavel:
        logger.warning("Responsável já existe")
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Responsavel already exists")

    # Criando o novo responsável
    novo_responsavel = Responsavel(**responsavel.dict())
    await novo_responsavel.insert()

    logger.info(f"Responsável '{novo_responsavel.nome}' criado com sucesso")
    return ResponsavelPublic(
        id=str(novo_responsavel.id),
        nome=novo_responsavel.nome,
        email=novo_responsavel.email,
        cargo=novo_responsavel.cargo,
        telefone=novo_responsavel.telefone
    )


@router.delete("/{responsavel_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_responsavel(responsavel_id: str):
    """Exclui um responsável pelo ID"""
    logger.info(f"Tentativa de exclusão do responsável com ID {responsavel_id}")

    db_responsavel = await Responsavel.get(PydanticObjectId(responsavel_id))
    if not db_responsavel:
        logger.warning(f"Responsável com ID {responsavel_id} não encontrado")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Responsavel not found")

    await db_responsavel.delete()

    logger.info(f"Responsável com ID {responsavel_id} excluído com sucesso")
    return {"message": "Responsavel deleted successfully"}


@router.put("/{responsavel_id}", status_code=HTTPStatus.OK, response_model=ResponsavelPublic)
async def update_responsavel(responsavel_id: str, responsavel: ResponsavelSchema):
    """Atualiza um responsável pelo ID"""
    logger.info(f"Tentativa de atualização do responsável com ID {responsavel_id}")

    db_responsavel = await Responsavel.get(PydanticObjectId(responsavel_id))
    if not db_responsavel:
        logger.warning(f"Responsável com ID {responsavel_id} não encontrado")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Responsável not found")

    update_data = {k: v for k, v in responsavel.dict().items() if v is not None}
    await db_responsavel.set(update_data)

    logger.info(f"Responsável com ID {responsavel_id} atualizado com sucesso")
    return ResponsavelPublic(
        id=str(db_responsavel.id),
        nome=db_responsavel.nome,
        email=db_responsavel.email,
        cargo=db_responsavel.cargo,
        telefone=db_responsavel.telefone
    )


@router.get("/count", status_code=HTTPStatus.OK)
async def count_responsaveis():
    """Conta o número total de responsáveis"""
    logger.info("Endpoint /responsavel/count acessado")
    quantidade = await Responsavel.find().count()
    logger.info(f"Quantidade de responsáveis: {quantidade}")
    return {"quantidade": quantidade}


@router.get("/debug", status_code=HTTPStatus.OK)
async def debug_mongo():
    """Verifica a conexão com o banco e lista IDs disponíveis"""
    responsaveis = await Responsavel.find().to_list()
    
    return {
        "total_responsaveis": len(responsaveis),
        "ids": [str(r.id) for r in responsaveis]
    }

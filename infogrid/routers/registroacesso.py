from fastapi import APIRouter, HTTPException, Query
from http import HTTPStatus
from typing import List, Optional
import logging
from datetime import datetime
from beanie import PydanticObjectId
from infogrid.models import RegistroAcesso
from infogrid.schemas import RegistroAcesso as RegistroAcessoSchema, RegistroAcessoPublic

logger = logging.getLogger("app_logger")

router = APIRouter(prefix="/api/v1/registroacesso", tags=["registroacesso"])


# ==========================
# LISTAR TODOS OS REGISTROS DE ACESSO
# ==========================

@router.get("/", status_code=HTTPStatus.OK, response_model=List[RegistroAcessoPublic])
async def list_registros_acesso():
    """Lista todos os registros de acesso"""
    logger.info("Endpoint /registroacesso acessado")
    
    registros = await RegistroAcesso.find(fetch_links=True).to_list()
    
    return [
        RegistroAcessoPublic(
            id=str(reg.id),
            usuario_id=str(reg.usuario_id.id) if hasattr(reg.usuario_id, "id") else str(reg.usuario_id),
            conjunto_dados=reg.conjunto_dados,
            data_solicitacao=reg.data_solicitacao,
            finalidade_uso=reg.finalidade_uso,
            permissoes_concedidas=reg.permissoes_concedidas or [],
            status=reg.status
        )
        for reg in registros
    ]


# ==========================
# LISTAR REGISTROS COM PAGINAÇÃO
# ==========================

@router.get("/pagined/", status_code=HTTPStatus.OK, response_model=List[RegistroAcessoPublic])
async def list_registros_acesso_paged(limit: int = 5, skip: int = 0):
    """Lista registros de acesso com paginação"""
    logger.info(f"Endpoint /registroacesso/pagined acessado com limite {limit} e offset {skip}")

    registros = await RegistroAcesso.find(fetch_links=True).skip(skip).limit(limit).to_list()
    
    return [
        RegistroAcessoPublic(
            id=str(reg.id),
            usuario_id=str(reg.usuario_id.id) if hasattr(reg.usuario_id, "id") else str(reg.usuario_id),
            conjunto_dados=reg.conjunto_dados,
            data_solicitacao=reg.data_solicitacao,
            finalidade_uso=reg.finalidade_uso,
            permissoes_concedidas=reg.permissoes_concedidas or [],
            status=reg.status
        )
        for reg in registros
    ]


# ==========================
# CRIAR UM NOVO REGISTRO DE ACESSO
# ==========================

@router.post("/", status_code=HTTPStatus.CREATED, response_model=RegistroAcessoPublic)
async def create_registro_acesso(registro: RegistroAcessoSchema):
    """Cria um novo registro de acesso"""
    logger.info("Tentativa de criação de um novo registro de acesso")

    # Verifica se já existe um registro com os mesmos dados
    db_registro = await RegistroAcesso.find_one(
        RegistroAcesso.usuario_id == registro.usuario_id,
        RegistroAcesso.conjunto_dados == registro.conjunto_dados,
        RegistroAcesso.data_solicitacao == registro.data_solicitacao
    )
    if db_registro:
        logger.warning("Registro de acesso já existe")
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Registro de Acesso já existe para os critérios fornecidos"
        )

    novo_registro = RegistroAcesso(**registro.dict())
    await novo_registro.insert()

    logger.info(f"Registro de acesso '{novo_registro.id}' criado com sucesso")
    return RegistroAcessoPublic(
        id=str(novo_registro.id),
        usuario_id=str(novo_registro.usuario_id.id) if hasattr(novo_registro.usuario_id, "id") else str(novo_registro.usuario_id),
        conjunto_dados=novo_registro.conjunto_dados,
        data_solicitacao=novo_registro.data_solicitacao,
        finalidade_uso=novo_registro.finalidade_uso,
        permissoes_concedidas=novo_registro.permissoes_concedidas or [],
        status=novo_registro.status
    )


# ==========================
# DELETAR UM REGISTRO DE ACESSO
# ==========================

@router.delete("/{registro_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_registro_acesso(registro_id: str):
    """Exclui um registro de acesso pelo ID"""
    logger.info(f"Tentativa de exclusão do registro de acesso com ID {registro_id}")

    db_registro = await RegistroAcesso.get(PydanticObjectId(registro_id))
    if not db_registro:
        logger.warning(f"Registro de acesso com ID {registro_id} não encontrado")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Registro de Acesso não encontrado")

    await db_registro.delete()

    logger.info(f"Registro de acesso com ID {registro_id} excluído com sucesso")
    return {"message": "Registro de Acesso deletado com sucesso"}


# ==========================
# ATUALIZAR UM REGISTRO DE ACESSO
# ==========================

@router.put("/{registro_id}", status_code=HTTPStatus.OK, response_model=RegistroAcessoPublic)
async def update_registro_acesso(registro_id: str, registro: RegistroAcessoSchema):
    """Atualiza um registro de acesso pelo ID"""
    logger.info(f"Tentativa de atualização do registro de acesso com ID {registro_id}")

    db_registro = await RegistroAcesso.get(PydanticObjectId(registro_id))
    if not db_registro:
        logger.warning(f"Registro de acesso com ID {registro_id} não encontrado")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Registro de Acesso não encontrado")

    update_data = {k: v for k, v in registro.dict().items() if v is not None}
    await db_registro.set(update_data)

    logger.info(f"Registro de acesso com ID {registro_id} atualizado com sucesso")
    return RegistroAcessoPublic(
        id=str(db_registro.id),
        usuario_id=str(db_registro.usuario_id.id) if hasattr(db_registro.usuario_id, "id") else str(db_registro.usuario_id),
        conjunto_dados=db_registro.conjunto_dados,
        data_solicitacao=db_registro.data_solicitacao,
        finalidade_uso=db_registro.finalidade_uso,
        permissoes_concedidas=db_registro.permissoes_concedidas or [],
        status=db_registro.status
    )


# ==========================
# CONTAR REGISTROS DE ACESSO
# ==========================

@router.get("/count", status_code=HTTPStatus.OK)
async def count_registros_acesso():
    """Conta o número total de registros de acesso"""
    logger.info("Endpoint /registroacesso/count acessado")
    quantidade = await RegistroAcesso.find().count()
    logger.info(f"Quantidade de registros de acesso: {quantidade}")
    return {"quantidade": quantidade}


@router.get("/filter-by-date/", status_code=HTTPStatus.OK)
async def filter_registros_by_date(
    start_date: Optional[str] = Query(None, description="Data inicial (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Data final (YYYY-MM-DD)"),
    year: Optional[int] = Query(None, description="Ano específico (YYYY)")
):
    """
    Filtra Registros de Acesso por intervalo de data ou por ano específico.
    """
    query = {}

    try:
        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")

        if start_date and end_date:
            query["data_solicitacao"] = {"$gte": start_date, "$lte": end_date}
        elif start_date:
            query["data_solicitacao"] = {"$gte": start_date}
        elif end_date:
            query["data_solicitacao"] = {"$lte": end_date}

        if year:
            start_of_year = datetime(year, 1, 1)
            end_of_year = datetime(year, 12, 31, 23, 59, 59)
            query["data_solicitacao"] = {"$gte": start_of_year, "$lte": end_of_year}

        registros = await RegistroAcesso.find(query).to_list(100)

        if not registros:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Nenhum registro encontrado para o período informado.")

        return registros

    except ValueError:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Formato de data inválido. Use YYYY-MM-DD.")
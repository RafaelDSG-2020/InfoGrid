from fastapi import APIRouter, Depends, HTTPException
from http import HTTPStatus
from typing import List
from infogrid.database import get_db
from infogrid.models import Usuario
from infogrid.schemas import Usuario as UsuarioSchema, UsuarioPublic
import logging
from bson import ObjectId
from beanie import PydanticObjectId

logger = logging.getLogger("app_logger")

router = APIRouter(prefix="/api/v1/usuario", tags=["usuario"])


@router.get("/", response_model=List[UsuarioPublic])
async def list_usuarios():
    """Lista todos os usuários do banco."""
    logger.info("Endpoint /usuario acessado")
    usuarios = await Usuario.find().to_list(100)
    return [
        UsuarioPublic(id=str(usuario.id), nome=usuario.nome, email=usuario.email, cargo=usuario.cargo, telefone=usuario.telefone)
        for usuario in usuarios
    ]


@router.post("/", response_model=UsuarioPublic, status_code=HTTPStatus.CREATED)
async def create_usuario(usuario: UsuarioSchema):
    """Cria um novo usuário no banco."""
    logger.info("Tentativa de criação de um novo usuário")

    # Verifica se o usuário já existe pelo email
    db_usuario = await Usuario.find_one(Usuario.email == usuario.email)
    if db_usuario:
        logger.warning(f"Usuário com e-mail {usuario.email} já existe")
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Usuário já existe")

    novo_usuario = Usuario(**usuario.dict())
    await novo_usuario.insert()

    logger.info(f"Usuário '{usuario.nome}' criado com sucesso")
    return UsuarioPublic(id=str(novo_usuario.id), **usuario.dict())


@router.delete("/{usuario_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_usuario(usuario_id: str):
    """Deleta um usuário pelo ID."""
    logger.info(f"Tentativa de exclusão do usuário com ID {usuario_id}")

    resultado = await Usuario.find_one(Usuario.id == PydanticObjectId(usuario_id))
    if not resultado:
        logger.warning(f"Usuário com ID {usuario_id} não encontrado")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Usuário não encontrado")

    await resultado.delete()

    logger.info(f"Usuário com ID {usuario_id} excluído com sucesso")
    return {"message": "Usuário deletado com sucesso"}


@router.put("/{usuario_id}", response_model=UsuarioPublic)
async def update_usuario(usuario_id: str, usuario: UsuarioSchema):
    """Atualiza um usuário pelo ID."""
    logger.info(f"Tentativa de atualização do usuário com ID {usuario_id}")

    update_data = {k: v for k, v in usuario.dict().items() if v is not None}

    resultado = await Usuario.find_one(Usuario.id == PydanticObjectId(usuario_id))
    if not resultado:
        logger.warning(f"Usuário com ID {usuario_id} não encontrado")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Usuário não encontrado")

    await resultado.set(update_data)

    logger.info(f"Usuário com ID {usuario_id} atualizado com sucesso")
    return UsuarioPublic(id=str(resultado.id), **update_data)


@router.get("/quantidade", status_code=HTTPStatus.OK)
async def count_usuarios():
    """Conta o número total de usuários no banco."""
    logger.info("Endpoint /usuario/quantidade acessado")
    quantidade = await Usuario.find().count()
    logger.info(f"Quantidade de usuários: {quantidade}")
    return {"quantidade": quantidade}

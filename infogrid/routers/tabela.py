from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload
from http import HTTPStatus
from typing import List
from infogrid.database import get_session
from infogrid.models import Tabela as TabelaModel
from infogrid.schemas import Tabela, TabelaPublic
import logging

logger = logging.getLogger("app_logger")

router = APIRouter(prefix='/api/v1/tabela', tags=['tabela'])


@router.get("/", status_code=HTTPStatus.OK, response_model=List[TabelaPublic])
def list_tabelas(session: Session = Depends(get_session)):
    logger.info("Endpoint /tabela acessado")
    tabelas = session.scalars(select(TabelaModel)).all()
    logger.info(f"{len(tabelas)} tabelas encontradas")
    return tabelas


@router.get("/pagined/", status_code=HTTPStatus.OK, response_model=List[TabelaPublic])
def list_tabelas_paged(limit: int = 5, skip: int = 0, session: Session = Depends(get_session)):
    logger.info(f"Endpoint /tabela/pagined acessado com limite {limit} e offset {skip}")
    tabelas = session.scalars(select(TabelaModel).limit(limit).offset(skip)).all()
    logger.info(f"{len(tabelas)} tabelas encontradas")
    return tabelas


@router.post("/", status_code=HTTPStatus.CREATED, response_model=TabelaPublic)
def create_tabela(tabela: Tabela, session: Session = Depends(get_session)):
    """
    Cria uma nova tabela ignorando os responsáveis associados
    """
    logger.info("Tentativa de criação de uma nova tabela")
    with session as session:
        db_tabela = session.scalar(select(TabelaModel).where(TabelaModel.nome == tabela.nome))
        if db_tabela:
            logger.warning("Tentativa de criação de tabela falhou: tabela já existe")
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Tabela already exists")

        data = tabela.dict(exclude={"responsaveis"})
        db_instance = TabelaModel(**data)
        session.add(db_instance)

        try:
            session.commit()
            logger.info(f"Tabela '{db_instance.nome}' criada com sucesso")
        except IntegrityError:
            session.rollback()
            logger.error("Erro ao inserir tabela", exc_info=True)
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Tabela insertion failed")

        session.refresh(db_instance)

    return {
        "id": db_instance.id,
        "nome": db_instance.nome,
        "descricao": db_instance.descricao,
        "database_id": db_instance.database_id,
        "responsaveis": [],
        "estado_atual": db_instance.estado_atual,
        "qualidade": db_instance.qualidade,
        "conformidade": db_instance.conformidade,
    }


@router.delete("/{tabela_id}", status_code=HTTPStatus.NO_CONTENT)
def delete_tabela(tabela_id: int, session: Session = Depends(get_session)):
    logger.info(f"Tentativa de exclusão da tabela com ID {tabela_id}")
    with session as session:
        db_tabela = session.scalar(select(TabelaModel).where(TabelaModel.id == tabela_id))
        if not db_tabela:
            logger.warning(f"Tentativa de exclusão falhou: tabela com ID {tabela_id} não encontrada")
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Tabela not found")
        session.delete(db_tabela)
        try:
            session.commit()
            logger.info(f"Tabela com ID {tabela_id} excluída com sucesso")
        except IntegrityError as e:
            session.rollback()
            logger.error(f"Erro ao excluir tabela com ID {tabela_id}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=f"Tabela deletion failed: {str(e)}")
    return {"message": "Tabela deleted successfully"}

    #     session.commit()
    # return {"message": "Tabela deleted successfully"}


@router.put("/{tabela_id}", status_code=HTTPStatus.OK, response_model=TabelaPublic)
def update_tabela(tabela_id: int, tabela: Tabela, session: Session = Depends(get_session)):
    logger.info(f"Tentativa de atualização da tabela com ID {tabela_id}")
    with session as session:
        # Carrega a tabela com os relacionamentos necessários
        db_tabela = session.scalar(
            select(TabelaModel)
            .where(TabelaModel.id == tabela_id)
            .options(joinedload(TabelaModel.responsaveis))  # Carrega responsaveis
        )
        if not db_tabela:
            logger.warning(f"Tentativa de atualização falhou: tabela com ID {tabela_id} não encontrada")
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Tabela not found")

        # Atualiza os dados da tabela
        update_data = tabela.dict(exclude={"responsaveis"})
        for key, value in update_data.items():
            setattr(db_tabela, key, value)

        try:
            session.commit()
            logger.info(f"Tabela com ID {tabela_id} atualizada com sucesso")
        except IntegrityError:
            session.rollback()
            logger.error(f"Erro ao atualizar tabela com ID {tabela_id}", exc_info=True)
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Tabela update failed")

        # Atualiza o objeto para refletir as mudanças
        session.refresh(db_tabela)

    return db_tabela




@router.get("/tabelas", status_code=HTTPStatus.OK)
def count_databases(session: Session = Depends(get_session)):
    """
    Endpoint para contar o número de registros na tabela 'tabelas'.
    """
    logger.info("Endpoint /tabela/tabelas acessado para contar registros")
    quantidade = session.scalar(select(func.count()).select_from(TabelaModel))
    logger.info(f"Quantidade de tabelas: {quantidade}")
    return {"quantidade": quantidade}
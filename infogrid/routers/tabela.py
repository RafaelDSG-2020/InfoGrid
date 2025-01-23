from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload
from http import HTTPStatus
from typing import List
from infogrid.database import get_session
from infogrid.models import Tabela as TabelaModel
from infogrid.schemas import Tabela, TabelaPublic

router = APIRouter(prefix='/api/v1/tabela', tags=['tabela'])


@router.get("/", status_code=HTTPStatus.OK, response_model=List[TabelaPublic])
def list_tabelas(session: Session = Depends(get_session)):
    tabelas = session.scalars(select(TabelaModel)).all()
    return tabelas


@router.get("/pagined/", status_code=HTTPStatus.OK, response_model=List[TabelaPublic])
def list_tabelas_paged(limit: int = 5, skip: int = 0, session: Session = Depends(get_session)):
    tabelas = session.scalars(select(TabelaModel).limit(limit).offset(skip)).all()
    return tabelas


@router.post("/", status_code=HTTPStatus.CREATED, response_model=TabelaPublic)
def create_tabela(tabela: Tabela, session: Session = Depends(get_session)):
    """
    Cria uma nova tabela ignorando os responsáveis associados
    """
    with session as session:
        db_tabela = session.scalar(select(TabelaModel).where(TabelaModel.nome == tabela.nome))
        if db_tabela:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Tabela already exists")

        data = tabela.dict(exclude={"responsaveis"})
        db_instance = TabelaModel(**data)
        session.add(db_instance)

        try:
            session.commit()
        except IntegrityError:
            session.rollback()
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
    with session as session:
        db_tabela = session.scalar(select(TabelaModel).where(TabelaModel.id == tabela_id))
        if not db_tabela:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Tabela not found")
        session.delete(db_tabela)
        session.commit()
    return {"message": "Tabela deleted successfully"}


@router.put("/{tabela_id}", status_code=HTTPStatus.OK, response_model=TabelaPublic)
def update_tabela(tabela_id: int, tabela: Tabela, session: Session = Depends(get_session)):
    with session as session:
        # Carrega a tabela com os relacionamentos necessários
        db_tabela = session.scalar(
            select(TabelaModel)
            .where(TabelaModel.id == tabela_id)
            .options(joinedload(TabelaModel.responsaveis))  # Carrega responsaveis
        )
        if not db_tabela:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Tabela not found")

        # Atualiza os dados da tabela
        update_data = tabela.dict(exclude={"responsaveis"})
        for key, value in update_data.items():
            setattr(db_tabela, key, value)

        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Tabela update failed")

        # Atualiza o objeto para refletir as mudanças
        session.refresh(db_tabela)

    return db_tabela




@router.get("/tabelas", status_code=HTTPStatus.OK)
def count_databases(session: Session = Depends(get_session)):
    """
    Endpoint para contar o número de registros na tabela 'tabelas'.
    """
    quantidade = session.scalar(select(func.count()).select_from(TabelaModel))
    return {"quantidade": quantidade}
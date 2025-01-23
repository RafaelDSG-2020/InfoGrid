from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, insert, delete, join
from infogrid.database import get_session
# from infogrid.models import responsaveis_databases, responsaveis_tabelas, responsaveis_topicos_kafka
from infogrid.models import responsaveis_databases, responsaveis_tabelas, responsaveis_topicos_kafka, Responsavel, Database, TopicoKafka, Tabela

from http import HTTPStatus

router = APIRouter(prefix='/api/v1/relacionamentos', tags=['relacionamentos'])

# Endpoints para responsaveis_databases
@router.post("/responsaveis_databases/", status_code=HTTPStatus.CREATED)
def create_responsavel_database(responsavel_id: int, database_id: int, session: Session = Depends(get_session)):
    stmt = insert(responsaveis_databases).values(responsavel_id=responsavel_id, database_id=database_id)
    try:
        session.execute(stmt)
        session.commit()
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Relacionamento já existe")
    return {"message": "Relacionamento criado com sucesso"}

@router.delete("/responsaveis_databases/", status_code=HTTPStatus.NO_CONTENT)
def delete_responsavel_database(responsavel_id: int, database_id: int, session: Session = Depends(get_session)):
    stmt = delete(responsaveis_databases).where(
        responsaveis_databases.c.responsavel_id == responsavel_id,
        responsaveis_databases.c.database_id == database_id
    )
    result = session.execute(stmt)
    if result.rowcount == 0:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Relacionamento não encontrado")
    session.commit()
    return {"message": "Relacionamento excluído com sucesso"}

@router.get("/responsaveis_databases/", status_code=HTTPStatus.OK)
def get_responsavel_databases(session: Session = Depends(get_session)):
    stmt = select(
        Responsavel.id, Responsavel.nome, Database.id, Database.nome
    ).select_from(
        join(responsaveis_databases, Responsavel, responsaveis_databases.c.responsavel_id == Responsavel.id)
    ).join(
        Database, responsaveis_databases.c.database_id == Database.id
    )
    result = session.execute(stmt).fetchall()
    if not result:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Relacionamentos não encontrados")
    return [{"responsavel_id": row[0], "responsavel_nome": row[1], "database_id": row[2], "database_nome": row[3]} for row in result]

# Endpoints par

# @router.get("/responsaveis_databases/", status_code=HTTPStatus.OK)
# def get_responsavel_databases(session: Session = Depends(get_session)):
#     stmt = select(responsaveis_databases)
#     result = session.execute(stmt).fetchall()
#     if not result:
#         raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Relacionamentos não encontrados")
#     return [{"responsavel_id": row.responsavel_id, "database_id": row.database_id} for row in result]


# @router.get("/responsaveis_tabelas/", status_code=HTTPStatus.OK)
# def get_responsavel_tabelas(session: Session = Depends(get_session)):
#     stmt = select(responsaveis_tabelas)
#     result = session.execute(stmt).fetchall()
#     if not result:
#         raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Relacionamentos não encontrados")
#     return [dict(row) for row in result]



# Endpoints para responsaveis_tabelas
@router.post("/responsaveis_tabelas/", status_code=HTTPStatus.CREATED)
def create_responsavel_tabela(responsavel_id: int, tabela_id: int, session: Session = Depends(get_session)):
    stmt = insert(responsaveis_tabelas).values(responsavel_id=responsavel_id, tabela_id=tabela_id)
    try:
        session.execute(stmt)
        session.commit()
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Relacionamento já existe")
    return {"message": "Relacionamento criado com sucesso"}

@router.delete("/responsaveis_tabelas/", status_code=HTTPStatus.NO_CONTENT)
def delete_responsavel_tabela(responsavel_id: int, tabela_id: int, session: Session = Depends(get_session)):
    stmt = delete(responsaveis_tabelas).where(
        responsaveis_tabelas.c.responsavel_id == responsavel_id,
        responsaveis_tabelas.c.tabela_id == tabela_id
    )
    result = session.execute(stmt)
    if result.rowcount == 0:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Relacionamento não encontrado")
    session.commit()
    return {"message": "Relacionamento excluído com sucesso"}

@router.get("/responsaveis_tabelas/", status_code=HTTPStatus.OK)
def get_responsavel_tabelas(session: Session = Depends(get_session)):
    stmt = select(
        Responsavel.id, Responsavel.nome, Tabela.id, Tabela.nome
    ).select_from(
        join(responsaveis_tabelas, Responsavel, responsaveis_tabelas.c.responsavel_id == Responsavel.id)
    ).join(
        Tabela, responsaveis_tabelas.c.tabela_id == Tabela.id
    )
    result = session.execute(stmt).fetchall()
    if not result:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Relacionamentos não encontrados")
    return [{"responsavel_id": row[0], "responsavel_nome": row[1], "tabela_id": row[2], "tabela_nome": row[3]} for row in result]



# Endpoints para responsaveis_topicos_kafka
@router.post("/responsaveis_topicos_kafka/", status_code=HTTPStatus.CREATED)
def create_responsavel_topico_kafka(responsavel_id: int, topico_kafka_id: int, session: Session = Depends(get_session)):
    stmt = insert(responsaveis_topicos_kafka).values(responsavel_id=responsavel_id, topico_kafka_id=topico_kafka_id)
    try:
        session.execute(stmt)
        session.commit()
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Relacionamento já existe")
    return {"message": "Relacionamento criado com sucesso"}

@router.delete("/responsaveis_topicos_kafka/", status_code=HTTPStatus.NO_CONTENT)
def delete_responsavel_topico_kafka(responsavel_id: int, topico_kafka_id: int, session: Session = Depends(get_session)):
    stmt = delete(responsaveis_topicos_kafka).where(
        responsaveis_topicos_kafka.c.responsavel_id == responsavel_id,
        responsaveis_topicos_kafka.c.topico_kafka_id == topico_kafka_id
    )
    result = session.execute(stmt)
    if result.rowcount == 0:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Relacionamento não encontrado")
    session.commit()
    return {"message": "Relacionamento excluído com sucesso"}

@router.get("/responsaveis_topicos_kafka/", status_code=HTTPStatus.OK)
def get_responsavel_topicos_kafka(session: Session = Depends(get_session)):
    stmt = select(
        Responsavel.id, Responsavel.nome, TopicoKafka.id, TopicoKafka.nome
    ).select_from(
        join(responsaveis_topicos_kafka, Responsavel, responsaveis_topicos_kafka.c.responsavel_id == Responsavel.id)
    ).join(
        TopicoKafka, responsaveis_topicos_kafka.c.topico_kafka_id == TopicoKafka.id
    )
    result = session.execute(stmt).fetchall()
    if not result:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Relacionamentos não encontrados")
    return [{"responsavel_id": row[0], "responsavel_nome": row[1], "topico_kafka_id": row[2], "topico_kafka_nome": row[3]} for row in result]
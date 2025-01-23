from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from infogrid.database import get_session
from infogrid.models import Responsavel, Database, Tabela, TopicoKafka
from http import HTTPStatus

router = APIRouter(prefix='/api/v1/entidades', tags=['entidades'])

# Endpoint para filtrar Responsaveis
@router.get("/responsaveis/", status_code=HTTPStatus.OK)
def get_responsaveis(
    nome: str = Query(None),
    email: str = Query(None),
    session: Session = Depends(get_session)
):
    stmt = select(Responsavel)
    
    if nome:
        stmt = stmt.where(Responsavel.nome.ilike(f"%{nome}%"))
    if email:
        stmt = stmt.where(Responsavel.email.ilike(f"%{email}%"))

    result = session.execute(stmt).scalars().all()
    if not result:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Responsáveis não encontrados")
    return result

# Endpoint para filtrar Databases
@router.get("/databases/", status_code=HTTPStatus.OK)
def get_databases(
    nome: str = Query(None),
    tecnologia: str = Query(None),
    session: Session = Depends(get_session)
):
    stmt = select(Database)
    
    if nome:
        stmt = stmt.where(Database.nome.ilike(f"%{nome}%"))
    if tecnologia:
        stmt = stmt.where(Database.tecnologia.ilike(f"%{tecnologia}%"))

    result = session.execute(stmt).scalars().all()
    if not result:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Databases não encontrados")
    return result

# Endpoint para filtrar Tabelas
@router.get("/tabelas/", status_code=HTTPStatus.OK)
def get_tabelas(
    nome: str = Query(None),
    descricao: str = Query(None),
    session: Session = Depends(get_session)
):
    stmt = select(Tabela)
    
    if nome:
        stmt = stmt.where(Tabela.nome.ilike(f"%{nome}%"))
    if descricao:
        stmt = stmt.where(Tabela.descricao.ilike(f"%{descricao}%"))

    result = session.execute(stmt).scalars().all()
    if not result:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Tabelas não encontradas")
    return result

# Endpoint para filtrar TopicosKafka
@router.get("/topicos_kafka/", status_code=HTTPStatus.OK)
def get_topicos_kafka(
    nome: str = Query(None),
    descricao: str = Query(None),
    session: Session = Depends(get_session)
):
    stmt = select(TopicoKafka)
    
    if nome:
        stmt = stmt.where(TopicoKafka.nome.ilike(f"%{nome}%"))
    if descricao:
        stmt = stmt.where(TopicoKafka.descricao.ilike(f"%{descricao}%"))

    result = session.execute(stmt).scalars().all()
    if not result:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Tópicos Kafka não encontrados")
    return result

# from fastapi import APIRouter, HTTPException, Depends, Query
# from sqlalchemy.orm import Session
# from sqlalchemy import select, join
# from infogrid.database import get_session
# from infogrid.models import Responsavel, Database, Tabela, TopicoKafka, responsaveis_databases, responsaveis_tabelas, responsaveis_topicos_kafka
# from http import HTTPStatus

# router = APIRouter(prefix='/api/v1/entidades', tags=['entidades'])

# # Endpoint para filtrar Responsaveis com Databases
# @router.get("/responsaveis_databases/", status_code=HTTPStatus.OK)
# def get_responsaveis_databases(
#     responsavel_nome: str = Query(None),
#     database_nome: str = Query(None),
#     session: Session = Depends(get_session)
# ):
#     stmt = select(
#         Responsavel.id, Responsavel.nome, Database.id, Database.nome
#     ).select_from(
#         join(responsaveis_databases, Responsavel, responsaveis_databases.c.responsavel_id == Responsavel.id)
#     ).join(
#         Database, responsaveis_databases.c.database_id == Database.id
#     )

#     if responsavel_nome:
#         stmt = stmt.where(Responsavel.nome.ilike(f"%{responsavel_nome}%"))
#     if database_nome:
#         stmt = stmt.where(Database.nome.ilike(f"%{database_nome}%"))

#     result = session.execute(stmt).fetchall()
#     if not result:
#         raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Relacionamentos não encontrados")
#     return [{"responsavel_id": row[0], "responsavel_nome": row[1], "database_id": row[2], "database_nome": row[3]} for row in result]

# # Endpoint para filtrar Responsaveis com Tabelas
# @router.get("/responsaveis_tabelas/", status_code=HTTPStatus.OK)
# def get_responsaveis_tabelas(
#     responsavel_nome: str = Query(None),
#     tabela_nome: str = Query(None),
#     session: Session = Depends(get_session)
# ):
#     stmt = select(
#         Responsavel.id, Responsavel.nome, Tabela.id, Tabela.nome
#     ).select_from(
#         join(responsaveis_tabelas, Responsavel, responsaveis_tabelas.c.responsavel_id == Responsavel.id)
#     ).join(
#         Tabela, responsaveis_tabelas.c.tabela_id == Tabela.id
#     )

#     if responsavel_nome:
#         stmt = stmt.where(Responsavel.nome.ilike(f"%{responsavel_nome}%"))
#     if tabela_nome:
#         stmt = stmt.where(Tabela.nome.ilike(f"%{tabela_nome}%"))

#     result = session.execute(stmt).fetchall()
#     if not result:
#         raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Relacionamentos não encontrados")
#     return [{"responsavel_id": row[0], "responsavel_nome": row[1], "tabela_id": row[2], "tabela_nome": row[3]} for row in result]

# # Endpoint para filtrar Responsaveis com TopicosKafka
# @router.get("/responsaveis_topicos_kafka/", status_code=HTTPStatus.OK)
# def get_responsaveis_topicos_kafka(
#     responsavel_nome: str = Query(None),
#     topico_kafka_nome: str = Query(None),
#     session: Session = Depends(get_session)
# ):
#     stmt = select(
#         Responsavel.id, Responsavel.nome, TopicoKafka.id, TopicoKafka.nome
#     ).select_from(
#         join(responsaveis_topicos_kafka, Responsavel, responsaveis_topicos_kafka.c.responsavel_id == Responsavel.id)
#     ).join(
#         TopicoKafka, responsaveis_topicos_kafka.c.topico_kafka_id == TopicoKafka.id
#     )

#     if responsavel_nome:
#         stmt = stmt.where(Responsavel.nome.ilike(f"%{responsavel_nome}%"))
#     if topico_kafka_nome:
#         stmt = stmt.where(TopicoKafka.nome.ilike(f"%{topico_kafka_nome}%"))

#     result = session.execute(stmt).fetchall()
#     if not result:
#         raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Relacionamentos não encontrados")
#     return [{"responsavel_id": row[0], "responsavel_nome": row[1], "topico_kafka_id": row[2], "topico_kafka_nome": row[3]} for row in result]

# # Endpoint para filtrar Databases com Tabelas
# @router.get("/databases_tabelas/", status_code=HTTPStatus.OK)
# def get_databases_tabelas(
#     database_nome: str = Query(None),
#     tabela_nome: str = Query(None),
#     session: Session = Depends(get_session)
# ):
#     stmt = select(
#         Database.id, Database.nome, Tabela.id, Tabela.nome
#     ).select_from(
#         join(responsaveis_databases, Database, responsaveis_databases.c.database_id == Database.id)
#     ).join(
#         responsaveis_tabelas, responsaveis_databases.c.responsavel_id == responsaveis_tabelas.c.responsavel_id
#     ).join(
#         Tabela, responsaveis_tabelas.c.tabela_id == Tabela.id
#     )

#     if database_nome:
#         stmt = stmt.where(Database.nome.ilike(f"%{database_nome}%"))
#     if tabela_nome:
#         stmt = stmt.where(Tabela.nome.ilike(f"%{tabela_nome}%"))

#     result = session.execute(stmt).fetchall()
#     if not result:
#         raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Relacionamentos não encontrados")
#     return [{"database_id": row[0], "database_nome": row[1], "tabela_id": row[2], "tabela_nome": row[3]} for row in result]

# # Endpoint para filtrar Responsaveis com Databases, Tabelas e TopicosKafka
# @router.get("/responsaveis_completos/", status_code=HTTPStatus.OK)
# def get_responsaveis_completos(
#     responsavel_nome: str = Query(None),
#     database_nome: str = Query(None),
#     tabela_nome: str = Query(None),
#     topico_kafka_nome: str = Query(None),
#     session: Session = Depends(get_session)
# ):
#     stmt = select(
#         Responsavel.id, Responsavel.nome, Database.id, Database.nome, Tabela.id, Tabela.nome, TopicoKafka.id, TopicoKafka.nome
#     ).select_from(
#         join(responsaveis_databases, Responsavel, responsaveis_databases.c.responsavel_id == Responsavel.id)
#     ).join(
#         Database, responsaveis_databases.c.database_id == Database.id
#     ).join(
#         responsaveis_tabelas, responsaveis_databases.c.responsavel_id == responsaveis_tabelas.c.responsavel_id
#     ).join(
#         Tabela, responsaveis_tabelas.c.tabela_id == Tabela.id
#     ).join(
#         responsaveis_topicos_kafka, responsaveis_databases.c.responsavel_id == responsaveis_topicos_kafka.c.responsavel_id
#     ).join(
#         TopicoKafka, responsaveis_topicos_kafka.c.topico_kafka_id == TopicoKafka.id
#     )

#     if responsavel_nome:
#         stmt = stmt.where(Responsavel.nome.ilike(f"%{responsavel_nome}%"))
#     if database_nome:
#         stmt = stmt.where(Database.nome.ilike(f"%{database_nome}%"))
#     if tabela_nome:
#         stmt = stmt.where(Tabela.nome.ilike(f"%{tabela_nome}%"))
#     if topico_kafka_nome:
#         stmt = stmt.where(TopicoKafka.nome.ilike(f"%{topico_kafka_nome}%"))

#     result = session.execute(stmt).fetchall()
#     if not result:
#         raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Relacionamentos não encontrados")
#     return [{
#         "responsavel_id": row[0], "responsavel_nome": row[1],
#         "database_id": row[2], "database_nome": row[3],
#         "tabela_id": row[4], "tabela_nome": row[5],
#         "topico_kafka_id": row[6], "topico_kafka_nome": row[7]
#     } for row in result]
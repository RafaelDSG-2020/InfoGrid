from http import HTTPStatus
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from infogrid.models import DatabaseModel, TabelaModel, ColunaModel, TopicoKafkaModel, ColunaTopicoKafkaModel
from infogrid.settings import Settings
from infogrid.schemas import Message, Responsavel, Database, Tabela, Coluna, TopicoKafka, ColunaTopicoKafka
from sqlalchemy import create_engine, select, insert, update, delete
from sqlalchemy.orm import Session
app = FastAPI()



@app.get("/hello-world", status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {"message": "Hello World"}


@app.post("/database", status_code=HTTPStatus.CREATED, response_model=Database)
def create_database(database: Database):
    engine = create_engine(Settings().DATABASE_URL)
    with Session(engine) as session:
        session.execute(insert(DatabaseModel).values(database.dict()))
        session.commit()
        session.refresh(database)
    return database
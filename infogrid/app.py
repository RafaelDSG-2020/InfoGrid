from http import HTTPStatus

from fastapi import FastAPI

from infogrid.routers import (
    responsavel,
    routerdatabase, 
    tabela, 
    coluna, 
    topicokafka, 
    colunatopicoKafka,
    registroacesso,
    usuario)
from infogrid.schemas import Message

app = FastAPI()
app.include_router(routerdatabase.router)
app.include_router(responsavel.router)
app.include_router(tabela.router)
app.include_router(coluna.router)
app.include_router(topicokafka.router)
app.include_router(colunatopicoKafka.router)
app.include_router(registroacesso.router)
app.include_router(usuario.router)


@app.get("/hello-world", status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {"message": "Hello World"}


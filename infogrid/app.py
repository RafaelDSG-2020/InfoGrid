from http import HTTPStatus
from fastapi import FastAPI, Request
import logging
from logging.handlers import RotatingFileHandler
from infogrid.database import init_db
from infogrid.routers import (
    responsavel,
    routerdatabase, 
    tabela, 
    coluna, 
    topicokafka, 
    colunatopicoKafka,
    registroacesso,
    usuario,
    relacionamentos,
    entidades
)
from infogrid.schemas import Message

# Configuração de logs
LOG_FILE = "app.log"
logger = logging.getLogger("app_logger")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(LOG_FILE, maxBytes=1000000, backupCount=5)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

app = FastAPI()

# Middleware global para registrar requisições em todos os routers
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Recebendo requisição: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Resposta gerada com status: {response.status_code}")
    return response

@app.on_event("startup")
async def startup():
    await init_db() 

# Inclusão de routers
app.include_router(routerdatabase.router)
app.include_router(responsavel.router)
app.include_router(tabela.router)
app.include_router(coluna.router)
app.include_router(topicokafka.router)
app.include_router(colunatopicoKafka.router)
app.include_router(registroacesso.router)
app.include_router(usuario.router)
app.include_router(relacionamentos.router)
app.include_router(entidades.router)

# app.include_router(routerdatabase.router, prefix="/routerdatabase", tags=["RouterDatabase"])
# app.include_router(responsavel.router, prefix="/responsavel", tags=["Responsável"])
# app.include_router(tabela.router, prefix="/tabela", tags=["Tabela"])
# app.include_router(coluna.router, prefix="/coluna", tags=["Coluna"])
# app.include_router(topicokafka.router, prefix="/topicokafka", tags=["TópicoKafka"])
# app.include_router(colunatopicoKafka.router, prefix="/colunatopicoKafka", tags=["ColunaTópicoKafka"])
# app.include_router(registroacesso.router, prefix="/registroacesso", tags=["RegistroAcesso"])
# app.include_router(usuario.router, prefix="/usuario", tags=["Usuário"])
# app.include_router(relacionamentos.router, prefix="/relacionamentos", tags=["Relacionamentos"])

# Exemplo de endpoint básico
@app.get("/hello-world", status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    logger.info("Endpoint /hello-world acessado")
    return {"message": "Hello World"}

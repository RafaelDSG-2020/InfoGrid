# from sqlalchemy import create_engine
# from sqlalchemy.orm import Session

# from infogrid.settings import Settings

# engine = create_engine(Settings().DATABASE_URL)


# def get_session():
#     with Session(engine) as session:
#         yield session


from motor.motor_asyncio import AsyncIOMotorClient
from infogrid.settings import Settings
from beanie import init_beanie
from infogrid.models import Usuario, Database, Tabela, Coluna, TopicoKafka, ColunaTopicoKafka, RegistroAcesso, Responsavel

# Criar a instância do banco de dados
settings = Settings()
client = AsyncIOMotorClient(settings.DATABASE_URL)
db = client.get_database()

async def init_db():
    """Inicializa o Beanie com os modelos"""
    await init_beanie(
        database=db,
        document_models=[Usuario, Database,Responsavel ,Tabela, Coluna, TopicoKafka, ColunaTopicoKafka, RegistroAcesso]
    )

async def get_db():
    """Retorna a conexão com o banco de dados"""
    yield db



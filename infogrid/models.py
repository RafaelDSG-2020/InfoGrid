from beanie import Document, Link
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Modelo de Usuário
class Usuario(Document):
    nome: str
    email: str
    cargo: Optional[str]
    telefone: Optional[str]

    class Settings:
        collection = "usuarios"

# Modelo de Registro de Acesso
class RegistroAcesso(Document):
    usuario_id: str  # ID será armazenado como string (MongoDB usa ObjectId)
    conjunto_dados: str
    data_solicitacao: datetime
    finalidade_uso: str
    permissoes_concedidas: List[str]
    status: Optional[str]

    class Settings:
        collection = "registros_acesso"

# Modelo de Database (Bancos de Dados)
class Database(Document):
    nome: str
    tecnologia: str
    descricao: Optional[str]
    responsaveis: List[Link[Usuario]]  # Relacionamento com usuários

    class Settings:
        collection = "databases"

class Responsavel(Document):
    nome: str
    email: str
    cargo: Optional[str]
    telefone: Optional[str]

    class Settings:
        collection = "responsaveis"        

# Modelo de Tabela
class Tabela(Document):
    nome: str
    descricao: Optional[str]
    database: Link[Database]  # Relacionamento com Database
    responsaveis: List[Link[Responsavel]] = Field(default_factory=list)
    estado_atual: Optional[str]
    qualidade: Optional[str]
    conformidade: Optional[bool]

    class Settings:
        collection = "tabelas"

# Modelo de Coluna
class Coluna(Document):
    nome: str
    tipo_dado: str
    descricao: Optional[str]
    tabela: Link[Tabela]  # Relacionamento com Tabela

    class Settings:
        collection = "colunas"

# Modelo de Tópico Kafka
class TopicoKafka(Document):
    nome: str
    descricao: Optional[str]
    responsaveis: List[Link[Responsavel]] = Field(default_factory=list)
    estado_atual: Optional[str]
    conformidade: Optional[bool]

    class Settings:
        collection = "topicos_kafka"

# Modelo de Coluna dentro de um Tópico Kafka
class ColunaTopicoKafka(Document):
    nome: str
    tipo_dado: str
    descricao: Optional[str]
    topico_kafka: Link[TopicoKafka]

    class Settings:
        collection = "colunas_topicos_kafka"


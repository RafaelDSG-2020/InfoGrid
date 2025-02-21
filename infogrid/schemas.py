from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# Modelo de resposta genérica para mensagens de API
class Message(BaseModel):
    message: str


# Schema para Usuário
class Usuario(BaseModel):
    nome: str
    email: str
    cargo: Optional[str]
    telefone: Optional[str]

class UsuarioPublic(BaseModel):
    id: str  # MongoDB usa ObjectId como string
    nome: str
    email: str
    cargo: Optional[str]
    telefone: Optional[str]

# Schema para Registro de Acesso
class RegistroAcesso(BaseModel):
    usuario_id: str
    conjunto_dados: str
    data_solicitacao: datetime
    finalidade_uso: str
    permissoes_concedidas: List[str]
    status: Optional[str]

class RegistroAcessoPublic(BaseModel):
    id: str
    usuario_id: str
    conjunto_dados: str
    data_solicitacao: datetime
    finalidade_uso: str
    permissoes_concedidas: List[str]
    status: Optional[str]

# Schema para Database (Banco de Dados)
class Database(BaseModel):
    nome: str
    tecnologia: str
    descricao: Optional[str]
    responsaveis: List[str]  # Lista de IDs dos usuários responsáveis

class DatabasePublic(BaseModel):
    id: str
    nome: str
    tecnologia: str
    descricao: Optional[str]
    responsaveis: List[str]

# Schema para Tabela
class Tabela(BaseModel):
    nome: str
    descricao: Optional[str]
    database_id: str
    responsaveis: List[str]
    estado_atual: Optional[str]
    qualidade: Optional[str]
    conformidade: Optional[bool]

class TabelaPublic(BaseModel):
    id: str
    nome: str
    descricao: Optional[str]
    database_id: str
    responsaveis: List[str]
    estado_atual: Optional[str] = None
    qualidade: Optional[str] = None
    conformidade: Optional[bool] = None

    class Config:
        orm_mode = True

# Schema para Coluna dentro de uma Tabela
class Coluna(BaseModel):
    nome: str
    tipo_dado: str
    descricao: Optional[str]
    tabela_id: str

class ColunaPublic(BaseModel):
    id: str
    nome: str
    tipo_dado: str
    descricao: Optional[str]
    tabela_id: str

# Schema para Tópico Kafka
class TopicoKafka(BaseModel):
    nome: str
    descricao: Optional[str]
    responsaveis: List[str]
    estado_atual: Optional[str]
    conformidade: Optional[bool]

class TopicoKafkaPublic(BaseModel):
    id: str
    nome: str
    descricao: Optional[str]
    responsaveis: List[str]
    estado_atual: Optional[str]
    conformidade: Optional[bool]

# Schema para Coluna dentro de um Tópico Kafka
class ColunaTopicoKafka(BaseModel):
    nome: str
    tipo_dado: str
    descricao: Optional[str]
    topico_kafka_id: str

class ColunaTopicoKafkaPublic(BaseModel):
    id: str
    nome: str
    tipo_dado: str
    descricao: Optional[str]
    topico_kafka_id: str

class Responsavel(BaseModel):
    nome: str
    email: str
    cargo: Optional[str] = None
    telefone: Optional[str] = None

class ResponsavelPublic(BaseModel):
    id: str 
    nome: str
    email: str
    cargo: Optional[str] = None
    telefone: Optional[str] = None




# # 🔹 Modelo de Perfil do Usuário (usado dentro do Usuario)
# class PerfilUsuarioSchema(BaseModel):
#     idade: Optional[int]
#     endereco: Optional[str]
#     biografia: Optional[str]

# # 🔹 Modelo para Atualizar o Perfil
# class PerfilUsuarioUpdateSchema(BaseModel):
#     idade: Optional[int] = None
#     endereco: Optional[str] = None
#     biografia: Optional[str] = None

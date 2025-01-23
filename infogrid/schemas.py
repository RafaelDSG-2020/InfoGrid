from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class Message(BaseModel):
    message: str


# Classe para os responsáveis ou equipes associadas aos dados
class Responsavel(BaseModel):
    nome: str
    email: str
    cargo: Optional[str]
    telefone: Optional[str]

class ResponsavelPublic(BaseModel):
    id: int
    nome: str
    email: str
    cargo: Optional[str]
    telefone: Optional[str]


# Classe para os bancos de dados (Databases)
class Database(BaseModel):
    # id: int
    nome: str
    tecnologia: str
    descricao: Optional[str]
    responsaveis: List[Responsavel]


class DatabasePublic(BaseModel):
    id: int
    nome: str
    tecnologia: str
    descricao: Optional[str]
    responsaveis: List[Responsavel]


# Classe para tabelas em um Database
class Tabela(BaseModel):
    nome: str
    descricao: Optional[str]
    database_id: int
    responsaveis: List[Responsavel]
    estado_atual: Optional[str]  # Exemplo: "Em conformidade", "Pendência de qualidade"
    qualidade: Optional[str]  # Exemplo: "Alta", "Média", "Baixa"
    conformidade: Optional[bool]  # True/False para indicar se está em conformidade


class TabelaPublic(BaseModel):
    id: int
    nome: str
    descricao: Optional[str]
    database_id: int
    responsaveis: List[Responsavel]
    estado_atual: Optional[str]  # Exemplo: "Em conformidade", "Pendência de qualidade"
    qualidade: Optional[str]  # Exemplo: "Alta", "Média", "Baixa"
    conformidade: Optional[bool]  # True/False para indicar se está em conformidade


# Classe para colunas dentro de uma tabela
class Coluna(BaseModel):
    nome: str
    tipo_dado: str
    descricao: Optional[str]
    tabela_id: int


class ColunaPublic(BaseModel):
    id: int
    nome: str
    tipo_dado: str
    descricao: Optional[str]
    tabela_id: int


# Classe para Tópicos Kafka
class TopicoKafka(BaseModel):
    nome: str
    descricao: Optional[str]
    responsaveis: List[Responsavel]
    estado_atual: Optional[str]  # Exemplo: "Ativo", "Inativo"
    conformidade: Optional[bool]  # True/False para indicar conformidade


class TopicoKafkaPublic(BaseModel):
    id: int
    nome: str
    descricao: Optional[str]
    responsaveis: List[Responsavel]
    estado_atual: Optional[str]  # Exemplo: "Ativo", "Inativo"
    conformidade: Optional[bool]  # True/False para indicar conformidade


# Classe para colunas de Tópicos Kafka
class ColunaTopicoKafka(BaseModel):
    nome: str
    tipo_dado: str
    descricao: Optional[str]
    topico_kafka_id: int


class ColunaTopicoKafkaPublic(BaseModel):
    id: int
    nome: str
    tipo_dado: str
    descricao: Optional[str]
    topico_kafka_id: int


# Classe para registrar acessos aos dados
class RegistroAcesso(BaseModel):
    usuario_id: int
    conjunto_dados: str  # Pode ser o nome do Database, Tabela, ou Tópico Kafka
    data_solicitacao: datetime
    finalidade_uso: str
    permissoes_concedidas: List[str]  # Exemplo: ["leitura", "escrita"]
    status: Optional[str]  # Exemplo: "Aprovado", "Negado", "Pendente"


class RegistroAcessoPublic(BaseModel):
    id: int
    usuario_id: int
    conjunto_dados: str  # Pode ser o nome do Database, Tabela, ou Tópico Kafka
    data_solicitacao: datetime
    finalidade_uso: str
    permissoes_concedidas: List[str]  # Exemplo: ["leitura", "escrita"]
    status: Optional[str]  # Exemplo: "Aprovado", "Negado", "Pendente"


# Classe para os usuários que acessam os dados
class Usuario(BaseModel):
    nome: str
    email: str
    cargo: Optional[str]
    telefone: Optional[str]
    # registros_acesso: List[RegistroAcesso]


class UsuarioPublic(BaseModel):
    id: int
    nome: str
    email: str
    cargo: Optional[str]
    telefone: Optional[str]
    # registros_acesso: List[RegistroAcesso]

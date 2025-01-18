from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import registry, relationship
from sqlalchemy.dialects.postgresql import JSON


table_registry = registry()

# Base = declarative_base()

Base = table_registry.generate_base()


# Relacionamentos Muitos-para-Muitos
responsaveis_databases = Table(
    'responsaveis_databases',
    Base.metadata,
    Column('responsavel_id', Integer, ForeignKey('responsaveis.id'), primary_key=True),
    Column('database_id', Integer, ForeignKey('databases.id'), primary_key=True),
)

responsaveis_tabelas = Table(
    'responsaveis_tabelas',
    Base.metadata,
    Column('responsavel_id', Integer, ForeignKey('responsaveis.id'), primary_key=True),
    Column('tabela_id', Integer, ForeignKey('tabelas.id'), primary_key=True),
)

responsaveis_topicos_kafka = Table(
    'responsaveis_topicos_kafka',
    Base.metadata,
    Column('responsavel_id', Integer, ForeignKey('responsaveis.id'), primary_key=True),
    Column('topico_kafka_id', Integer, ForeignKey('topicos_kafka.id'), primary_key=True),
)


# Model Responsavel
class Responsavel(Base):
    __tablename__ = 'responsaveis'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    cargo = Column(String(100), nullable=True)
    telefone = Column(String(15), nullable=True)

    # Relacionamento com Database
    databases = relationship(
        'Database', secondary=responsaveis_databases, back_populates="responsaveis"
    )

    # Relacionamento com Tabela
    tabelas = relationship(
        'Tabela', secondary=responsaveis_tabelas, back_populates="responsaveis"
    )

    # Relacionamento com TopicoKafka
    topicos_kafka = relationship(
        'TopicoKafka', secondary=responsaveis_topicos_kafka, back_populates="responsaveis"
    )


# Model Database
class Database(Base):
    __tablename__ = 'databases'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String(255), nullable=False, unique=True)
    tecnologia = Column(String(50), nullable=False)
    descricao = Column(Text, nullable=True)
    estado_atual = Column(String(50), nullable=True)

    responsaveis = relationship(
        'Responsavel', secondary=responsaveis_databases, back_populates="databases"
    )


# Model Tabela
class Tabela(Base):
    __tablename__ = 'tabelas'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String(255), nullable=False)
    descricao = Column(Text, nullable=True)
    database_id = Column(Integer, ForeignKey('databases.id'))
    estado_atual = Column(String(50), nullable=True)
    qualidade = Column(String(50), nullable=True)
    conformidade = Column(Boolean, nullable=True)

    responsaveis = relationship(
        'Responsavel', secondary=responsaveis_tabelas, back_populates="tabelas"
    )


# Model Coluna
class Coluna(Base):
    __tablename__ = 'colunas'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String(255), nullable=False)
    tipo_dado = Column(String(50), nullable=False)
    descricao = Column(Text, nullable=True)
    tabela_id = Column(Integer, ForeignKey('tabelas.id'))


# Model TopicoKafka
class TopicoKafka(Base):
    __tablename__ = 'topicos_kafka'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String(255), nullable=False)
    descricao = Column(Text, nullable=True)
    estado_atual = Column(String(50), nullable=True)
    conformidade = Column(Boolean, nullable=True)

    responsaveis = relationship(
        'Responsavel', secondary=responsaveis_topicos_kafka, back_populates="topicos_kafka"
    )


# Model ColunaTopicoKafka
class ColunaTopicoKafka(Base):
    __tablename__ = 'colunas_topicos_kafka'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String(255), nullable=False)
    tipo_dado = Column(String(50), nullable=False)
    descricao = Column(Text, nullable=True)
    topico_kafka_id = Column(Integer, ForeignKey('topicos_kafka.id'))


# Model Usuario
class Usuario(Base):
    __tablename__ = 'usuarios'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    cargo = Column(String(100), nullable=True)
    telefone = Column(String(15), nullable=True)


# Model RegistroAcesso
class RegistroAcesso(Base):
    __tablename__ = 'registros_acesso'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    conjunto_dados = Column(String(255), nullable=False)
    data_solicitacao = Column(DateTime, nullable=False)
    finalidade_uso = Column(Text, nullable=False)
    permissoes_concedidas = Column(JSON, nullable=True)  # Change to JSON
    status = Column(String(50), nullable=True)
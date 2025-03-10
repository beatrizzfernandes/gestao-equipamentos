# -*- coding: utf-8 -*-
from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# Conexão com o banco de dados SQLite
engine = create_engine('sqlite:///gestao_equipamentos.db')
Base = declarative_base()

# Modelo de Usuário
class Usuario(Base):
    __tablename__ = 'usuarios'

    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    senha = Column(String, nullable=False)
    perfil = Column(String, nullable=False)  # 'professor' ou 'administrador'

    reservas = relationship('Reserva', back_populates='usuario')

# Modelo de Equipamento
class Equipamento(Base):
    __tablename__ = 'equipamentos'

    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    tipo = Column(String, nullable=False)  # 'equipamento' ou 'recurso'
    descricao = Column(String)
    status = Column(String, default='disponível')  # 'disponível', 'emprestado', 'manutenção'

    reservas = relationship('Reserva', back_populates='equipamento')
    manutencoes = relationship('Manutencao', back_populates='equipamento')

# Modelo de Reserva
class Reserva(Base):
    __tablename__ = 'reservas'

    id = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, ForeignKey('usuarios.id'))
    id_equipamento = Column(Integer, ForeignKey('equipamentos.id'))
    data_reserva = Column(Date)
    data_emprestimo = Column(Date)
    data_devolucao = Column(Date)
    status = Column(String, default='reservado')  # 'reservado', 'emprestado', 'devolvido', 'cancelado'

    usuario = relationship('Usuario', back_populates='reservas')
    equipamento = relationship('Equipamento', back_populates='reservas')

# Modelo de Manutenção
class Manutencao(Base):
    __tablename__ = 'manutencao'

    id = Column(Integer, primary_key=True)
    id_equipamento = Column(Integer, ForeignKey('equipamentos.id'))
    descricao_problema = Column(String)
    data_registro = Column(Date)

    equipamento = relationship('Equipamento', back_populates='manutencoes')

# Criação das tabelas no banco de dados
Base.metadata.create_all(engine)

# Configuração da sessão
Session = sessionmaker(bind=engine)
session = Session()

print('Banco de dados e tabelas criados com sucesso!')


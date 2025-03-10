# -*- coding: utf-8 -*-
from sqlalchemy.orm import sessionmaker
from projeto import engine, Usuario, Equipamento  # Importa as classes e o engine

# Cria uma sessão
Session = sessionmaker(bind=engine)
session = Session()

# Teste 1: Inserir um usuário
novo_usuario = Usuario(nome='Beatriz Fernandes', email='beatriz.fernandes@gmail.com', senha='12345', perfil='administrador')

# Teste 2: Inserir um equipamento
novo_equipamento = Equipamento(nome='Projetor Epson', tipo='projetor', status='disponivel')

# Adiciona e confirma no banco
session.add(novo_usuario)
session.add(novo_equipamento)
session.commit()

# Teste 3: Consultar dados
usuarios = session.query(Usuario).all()
equipamentos = session.query(Equipamento).all()

print('Usuários cadastrados:')
for usuario in usuarios:
    print(f'ID: {usuario.id}, Nome: {usuario.nome}, Email: {usuario.email}, Perfil: {usuario.perfil}')

print('\nEquipamentos cadastrados:')
for equipamento in equipamentos:
    print(f'ID: {equipamento.id}, Nome: {equipamento.nome}, Tipo: {equipamento.tipo}, Status: {equipamento.status}')

# Fecha a sessão
session.close()

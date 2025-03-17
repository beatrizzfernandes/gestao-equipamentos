# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime, timedelta
import re
from tkcalendar import DateEntry

# ----------------------------------------------
# Classe para manipulaÃ§Ã£o de dados
# ----------------------------------------------
class DataHandler:
    @staticmethod
    def carregar_dados(arquivo):
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    @staticmethod
    def salvar_dados(arquivo, dados):
        with open(arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)

# ----------------------------------------------
# Classe principal da aplicaÃ§Ã£o
# ----------------------------------------------
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de GestÃ£o de Equipamentos")
        self.root.geometry("1000x700")
        
        # Carregar dados
        self.usuarios = DataHandler.carregar_dados('usuarios.json')
        self.equipamentos = DataHandler.carregar_dados('equipamentos.json')
        self.recursos = DataHandler.carregar_dados('recursos.json')
        self.reservas = DataHandler.carregar_dados('reservas.json')
        self.manutencoes = DataHandler.carregar_dados('manutencoes.json')
        
        # ConfiguraÃ§Ãµes de e-mail
        self.email_config = {
        'servidor': 'smtp.gmail.com',
        'porta': 587,
        'usuario': 'seuemail@gmail.com',  # Seu e-mail completo
        'senha': 'senha_de_16_caracteres',  # Senha de App gerada
        'from': 'seuemail@gmail.com'
        }
        
        self.usuario_atual = None
        self.tela_login()

            # Configurar estilos
        self.style = ttk.Style()
        self.style.configure('danger.TButton', foreground='white', background='#dc3545')

    # ----------------------------------------------
    # MÃ©todos de navegaÃ§Ã£o
    # ----------------------------------------------
    def limpar_tela(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def tela_login(self):
        self.limpar_tela()
        
        tk.Label(self.root, text="Login", font=("Arial", 14)).pack(pady=20)

        # Campos de entrada
        tk.Label(self.root, text="Email:").pack()
        self.entry_email = tk.Entry(self.root, width=30)
        self.entry_email.pack(pady=5)

        tk.Label(self.root, text="Senha:").pack()
        self.entry_senha = tk.Entry(self.root, show="*", width=30)
        self.entry_senha.pack(pady=5)

        # BotÃµes
        tk.Button(self.root, text="Entrar", command=self.fazer_login, width=15).pack(pady=10)
        tk.Button(self.root, text="Cadastrar", command=self.tela_cadastro, width=15).pack(pady=5)

    def tela_cadastro(self):
        self.limpar_tela()
        
        tk.Label(self.root, text="Cadastro de UsuÃ¡rio", font=("Arial", 14)).pack(pady=20)

        # Campos do formulÃ¡rio
        campos = [
            ("Nome Completo:", "entry_nome"),
            ("Email Institucional:", "entry_email"),
            ("Senha (mÃ­nimo 6 caracteres):", "entry_senha")
        ]

        self.entries = {}
        for texto, nome in campos:
            tk.Label(self.root, text=texto).pack()
            entry = tk.Entry(self.root, show="*" if "Senha" in texto else None, width=30)
            entry.pack(pady=2)
            self.entries[nome] = entry

        # SeleÃ§Ã£o de perfil
        tk.Label(self.root, text="Perfil:").pack(pady=5)
        self.perfil_var = tk.StringVar(value="Professor")
        tk.Radiobutton(self.root, text="Professor", variable=self.perfil_var, value="Professor").pack()
        tk.Radiobutton(self.root, text="Administrador", variable=self.perfil_var, value="Administrador").pack()

        # BotÃµes
        tk.Button(self.root, text="Confirmar", command=self.validar_cadastro, width=15).pack(pady=15)
        tk.Button(self.root, text="Voltar", command=self.tela_login, width=15).pack()

    # ----------------------------------------------
    # MÃ©todos de usuÃ¡rio
    # ----------------------------------------------
    def fazer_login(self):
        email = self.entry_email.get().strip().lower()
        senha = self.entry_senha.get().strip()

        for usuario in self.usuarios:
            if usuario['email'].lower() == email and usuario['senha'] == senha:
                self.usuario_atual = usuario
                self.tela_principal()
                return
        
        messagebox.showerror("Erro", "Credenciais invÃ¡lidas!")

    def validar_cadastro(self):
        nome = self.entries['entry_nome'].get().strip()
        email = self.entries['entry_email'].get().strip().lower()
        senha = self.entries['entry_senha'].get().strip()

        erros = []
        if len(nome) < 3:
            erros.append("Nome deve ter pelo menos 3 caracteres")
        if not re.match(r'^[\w\.-]+@[\w-]+\.[\w-]{2,}$', email):
            erros.append("Formato de e-mail invÃ¡lido")
        if len(senha) < 6:
            erros.append("Senha deve ter pelo menos 6 caracteres")
        if any(u['email'].lower() == email for u in self.usuarios):
            erros.append("Email jÃ¡ cadastrado")

        if erros:
            messagebox.showerror("Erros no Cadastro", "\n".join(erros))
            return

        novo_usuario = {
            "nome": nome,
            "email": email,
            "senha": senha,
            "perfil": self.perfil_var.get()
        }

        self.usuarios.append(novo_usuario)
        DataHandler.salvar_dados('usuarios.json', self.usuarios)
        messagebox.showinfo("Sucesso", "Cadastro realizado com sucesso!")
        self.tela_login()

    # ----------------------------------------------
    # Telas principais
    # ----------------------------------------------
    def tela_principal(self):
        self.limpar_tela()
        self.verificar_pendencias()  # Verifica reservas perto do vencimento
        
        tk.Label(self.root, text=f"Bem-vindo, {self.usuario_atual['nome']}",
                font=("Arial", 14, "bold")).pack(pady=20)

        # Container principal
        frame_principal = tk.Frame(self.root)
        frame_principal.pack(pady=20, padx=30, fill='both', expand=True)

        # OpÃ§Ãµes para Administradores
        if self.usuario_atual['perfil'] == "Administrador":
            ttk.Button(
                frame_principal,
                text="Cadastro de Equipamentos/Recursos",
                command=self.tela_cadastro_equipamentos,
                width=30
            ).pack(pady=10)

        # OpÃ§Ãµes para todos os usuÃ¡rios
        botoes_comuns = [
            ("GestÃ£o de Reservas", self.tela_gestao_reservas),
            ("ManutenÃ§Ã£o e Suporte", self.tela_manutencao_suporte)
        ]

        for texto, comando in botoes_comuns:
            ttk.Button(
                frame_principal,
                text=texto,
                command=comando,
                width=30
            ).pack(pady=10)

        # BotÃ£o de sair
        ttk.Button(
            frame_principal,
            text="Sair",
            command=self.tela_login,
            style='danger.TButton'
        ).pack(pady=20)

    # ----------------------------------------------
    # GestÃ£o de Equipamentos e Recursos
    # ----------------------------------------------
    def tela_cadastro_equipamentos(self):
        self.limpar_tela()
        tk.Label(self.root, text="Cadastro de Itens", font=("Arial", 14)).pack(pady=10)

        opcoes = [
            ("Equipamento Principal", self.cadastrar_equipamento),
            ("Recurso de Apoio", self.cadastrar_recurso_apoio),
            ("Voltar", self.tela_principal)
        ]

        for texto, comando in opcoes:
            ttk.Button(self.root, text=texto, command=comando).pack(pady=5)

    def cadastrar_equipamento(self):
        janela = tk.Toplevel(self.root)
        janela.title("Novo Equipamento")
        
        campos = [
            ('Nome:', 'entry_nome'),
            ('Tipo:', 'entry_tipo'),
            ('Quantidade:', 'entry_quantidade'),
            ('DescriÃ§Ã£o:', 'entry_descricao')
        ]
        
        entries = {}
        for idx, (texto, nome) in enumerate(campos):
            ttk.Label(janela, text=texto).grid(row=idx, column=0, padx=5, pady=5)
            if 'DescriÃ§Ã£o' in texto:
                entry = tk.Text(janela, height=4, width=30)
            else:
                entry = ttk.Entry(janela)
            entry.grid(row=idx, column=1, padx=5, pady=5)
            entries[nome] = entry
        
        def confirmar():
            try:
                novo_item = {
                    'id': len(self.equipamentos) + 1,
                    'nome': entries['entry_nome'].get(),
                    'tipo': entries['entry_tipo'].get(),
                    'quantidade': int(entries['entry_quantidade'].get()),
                    'descricao': entries['entry_descricao'].get("1.0", tk.END).strip(),
                    'disponivel': True,
                    'manutencao': False
                }
                self.equipamentos.append(novo_item)
                DataHandler.salvar_dados('equipamentos.json', self.equipamentos)
                messagebox.showinfo("Sucesso", "Equipamento cadastrado!")
                janela.destroy()
            except ValueError:
                messagebox.showerror("Erro", "Quantidade deve ser um nÃºmero vÃ¡lido!")
        
        ttk.Button(janela, text="Confirmar", command=confirmar).grid(row=len(campos)+1, columnspan=2)

    def cadastrar_recurso_apoio(self):
        janela = tk.Toplevel(self.root)
        janela.title("Novo Recurso de Apoio")
        
        campos = [
            ('Nome:', 'entry_nome'),
            ('Tipo:', 'entry_tipo'),
            ('Quantidade:', 'entry_quantidade'),
            ('DescriÃ§Ã£o:', 'entry_descricao')
        ]
        
        entries = {}
        for idx, (texto, nome) in enumerate(campos):
            ttk.Label(janela, text=texto).grid(row=idx, column=0, padx=5, pady=5)
            if 'DescriÃ§Ã£o' in texto:
                entry = tk.Text(janela, height=4, width=30)
            else:
                entry = ttk.Entry(janela)
            entry.grid(row=idx, column=1, padx=5, pady=5)
            entries[nome] = entry
        
        def confirmar():
            try:
                novo_item = {
                    'id': len(self.recursos) + 1,
                    'nome': entries['entry_nome'].get(),
                    'tipo': entries['entry_tipo'].get(),
                    'quantidade': int(entries['entry_quantidade'].get()),
                    'descricao': entries['entry_descricao'].get("1.0", tk.END).strip(),
                    'disponivel': True
                }
                self.recursos.append(novo_item)
                DataHandler.salvar_dados('recursos.json', self.recursos)
                messagebox.showinfo("Sucesso", "Recurso cadastrado!")
                janela.destroy()
            except ValueError:
                messagebox.showerror("Erro", "Quantidade deve ser um nÃºmero vÃ¡lido!")
        
        ttk.Button(janela, text="Confirmar", command=confirmar).grid(row=len(campos)+1, columnspan=2)

   # ----------------------------------------------
    # GestÃ£o de Reservas
    # ----------------------------------------------
    def tela_gestao_reservas(self):
        self.limpar_tela()
        tk.Label(self.root, text="GestÃ£o de Reservas", font=("Arial", 14)).pack(pady=10)

        opcoes = [
            ("Nova Reserva", self.reservar_equipamento),
            ("Realizar EmprÃ©stimo", self.fazer_emprestimo),
            ("DevoluÃ§Ã£o", self.devolver_equipamento),
            ("RelatÃ³rios", self.gerar_relatorios),
            ("Cancelar Reserva", self.cancelar_reserva),
            ("Renovar EmprÃ©stimo", self.renovar_emprestimo),
            ("Voltar", self.tela_principal)
        ]

        for texto, comando in opcoes:
            ttk.Button(self.root, text=texto, command=comando).pack(pady=2)

    def reservar_equipamento(self):
        janela = tk.Toplevel(self.root)
        janela.title("Nova Reserva")
    
        # Listar equipamentos disponÃ­veis
        disponiveis = [eq for eq in self.equipamentos if eq['disponivel']]
    
        ttk.Label(janela, text="Selecione o equipamento:").pack(pady=5)
        self.combo_equip = ttk.Combobox(janela, values=[eq['nome'] for eq in disponiveis])
        self.combo_equip.pack(pady=5)

        ttk.Label(janela, text="Data de DevoluÃ§Ã£o:").pack(pady=5)
    
        # Widget de calendÃ¡rio corrigido
        self.cal_devolucao = DateEntry(
            janela,
            date_pattern='dd/mm/yyyy',  # Formato brasileiro
            locale='pt_BR',             # ConfiguraÃ§Ã£o regional
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2
        )
        self.cal_devolucao.pack(pady=5)

        ttk.Button(janela, text="Confirmar", command=lambda: self.processar_reserva(janela)).pack(pady=10)

    def processar_reserva(self, janela):
        equip_nome = self.combo_equip.get()
        equip = next((eq for eq in self.equipamentos if eq['nome'] == equip_nome), None)
    
        if not equip:
            messagebox.showerror("Erro", "Selecione um equipamento vÃ¡lido!")
            return

        try:
            data_devolucao = self.cal_devolucao.get_date().strftime("%d/%m/%Y")
        except Exception as e:
            messagebox.showerror("Erro", f"Data invÃ¡lida: {str(e)}")
            return

        nova_reserva = {
            'id': len(self.reservas) + 1,
            'equipamento_id': equip['id'],
            'usuario': self.usuario_atual['email'],
            'data': datetime.now().strftime("%d/%m/%Y %H:%M"),
            'devolucao': data_devolucao,
            'status': 'reservado'
        }
    
        # Verificar se jÃ¡ existe reserva ativa para o equipamento
        reserva_ativa = any(
            r for r in self.reservas 
            if r['equipamento_id'] == equip['id'] 
            and r['status'] in ['reservado', 'emprestado']
        )
    
        if reserva_ativa:
            messagebox.showerror("Erro", "Este equipamento jÃ¡ estÃ¡ reservado!")
            return

        equip['disponivel'] = False
        self.reservas.append(nova_reserva)
    
        # Salvar alteraÃ§Ãµes nos arquivos
        DataHandler.salvar_dados('reservas.json', self.reservas)
        DataHandler.salvar_dados('equipamentos.json', self.equipamentos)
    
        # Feedback visual
        messagebox.showinfo("Sucesso", 
            f"Reserva confirmada!\nEquipamento: {equip['nome']}\nDevoluÃ§Ã£o: {data_devolucao}")
        
        # Na linha onde o e-mail Ã© enviado:
        self.enviar_email(
            self.usuario_atual['email'],
            "ConfirmaÃ§Ã£o de Reserva",
            f"Reserva realizada para {equip['nome']}",
            mostrar_popup=True  # Popup habilitado aqui
)
    
        # Atualizar interface e fechar janela
        janela.destroy()
        self.tela_gestao_reservas()  # Recarrega a tela de gestÃ£o

    # ----------------------------------------------
    # MÃ©todos de EmprÃ©stimo
    # ----------------------------------------------
    def fazer_emprestimo(self):
        janela = tk.Toplevel(self.root)
        janela.title("Realizar EmprÃ©stimo")
        
        # Listar equipamentos disponÃ­veis
        disponiveis = [eq for eq in self.equipamentos if eq['disponivel']]
        
        ttk.Label(janela, text="Selecione o equipamento:").pack(pady=5)
        self.combo_equip_emprestimo = ttk.Combobox(janela, values=[eq['nome'] for eq in disponiveis])
        self.combo_equip_emprestimo.pack(pady=5)

        ttk.Label(janela, text="Data de DevoluÃ§Ã£o:").pack(pady=5)
        self.cal_emprestimo = DateEntry(janela, date_pattern='dd/mm/yyyy')
        self.cal_emprestimo.pack(pady=5)

        ttk.Button(janela, text="Confirmar", command=lambda: self.processar_emprestimo(janela)).pack(pady=10)

    def processar_emprestimo(self, janela):
        equip_nome = self.combo_equip_emprestimo.get()
        equip = next((eq for eq in self.equipamentos if eq['nome'] == equip_nome), None)
        
        if not equip:
            messagebox.showerror("Erro", "Selecione um equipamento vÃ¡lido!")
            return

        novo_emprestimo = {
            'id': len(self.reservas) + 1,
            'equipamento_id': equip['id'],
            'usuario': self.usuario_atual['email'],
            'data': datetime.now().strftime("%d/%m/%Y %H:%M"),
            'devolucao': self.cal_emprestimo.get_date().strftime("%d/%m/%Y"),
            'status': 'emprestado'
        }
        
        equip['disponivel'] = False
        self.reservas.append(novo_emprestimo)
        DataHandler.salvar_dados('reservas.json', self.reservas)
        DataHandler.salvar_dados('equipamentos.json', self.equipamentos)
        
        # Envia e-mail de confirmaÃ§Ã£o
        mensagem = f"""
        EmprÃ©stimo confirmado:
        Equipamento: {equip['nome']}
        Data DevoluÃ§Ã£o: {novo_emprestimo['devolucao']}
        """
        self.enviar_email(
            self.usuario_atual['email'],
            "ConfirmaÃ§Ã£o de EmprÃ©stimo",
            f"EmprÃ©stimo realizado para {equip['nome']}",
            mostrar_popup=True  # Popup habilitado aqui
)
        
        messagebox.showinfo("Sucesso", "EmprÃ©stimo realizado com sucesso!")
        janela.destroy()

    # ----------------------------------------------
    # MÃ©todos de DevoluÃ§Ã£o
    # ----------------------------------------------
    def devolver_equipamento(self):
        janela = tk.Toplevel(self.root)
        janela.title("DevoluÃ§Ã£o de Equipamento")
        
        # Obter emprÃ©stimos ativos do usuÃ¡rio
        emprestimos_ativos = [
            r for r in self.reservas 
            if r['status'] == 'emprestado' 
            and r['usuario'] == self.usuario_atual['email']
        ]

        if not emprestimos_ativos:
            tk.Label(janela, text="Nenhum emprÃ©stimo ativo para devolver", fg="red").pack(pady=20)
            tk.Button(janela, text="Fechar", command=janela.destroy).pack()
            return

        tk.Label(janela, text="Selecione o emprÃ©stimo:").pack(pady=10)
        
        # Criar lista formatada
        lista_emprestimos = [
            f"{self.obter_nome_equipamento(r['equipamento_id'])} | DevoluÃ§Ã£o: {r['devolucao']}"
            for r in emprestimos_ativos
        ]
        
        self.combo_emprestimos = ttk.Combobox(janela, values=lista_emprestimos, width=40)
        self.combo_emprestimos.pack(pady=5)

        tk.Button(janela, text="Confirmar DevoluÃ§Ã£o", 
                 command=lambda: self.processar_devolucao(janela, emprestimos_ativos)).pack(pady=15)

    def processar_devolucao(self, janela, emprestimos):
        selecao = self.combo_emprestimos.current()
        if selecao == -1:
            messagebox.showerror("Erro", "Selecione um emprÃ©stimo!")
            return
            
        emprestimo = emprestimos[selecao]
        equipamento = next(eq for eq in self.equipamentos if eq['id'] == emprestimo['equipamento_id'])
        
        # Atualizar status
        equipamento['disponivel'] = True
        emprestimo['status'] = 'devolvido'
        emprestimo['data_devolucao_real'] = datetime.now().strftime("%d/%m/%Y")
        
        # Verificar atraso
        data_prevista = datetime.strptime(emprestimo['devolucao'], "%d/%m/%Y")
        data_real = datetime.strptime(emprestimo['data_devolucao_real'], "%d/%m/%Y")
        
        if data_real > data_prevista:
            dias_atraso = (data_real - data_prevista).days
            mensagem = f"DevoluÃ§Ã£o com {dias_atraso} dias de atraso!"
            self.enviar_email(
                self.usuario_atual['email'],
                "Atraso na DevoluÃ§Ã£o",
                f"Multa aplicada: R${dias_atraso * 10:.2f}",
                mostrar_popup=False  # Popup desabilitado
)
        else:
            mensagem = "DevoluÃ§Ã£o realizada com sucesso!"
        
        # Salvar alteraÃ§Ãµes
        DataHandler.salvar_dados('equipamentos.json', self.equipamentos)
        DataHandler.salvar_dados('reservas.json', self.reservas)
        
        messagebox.showinfo("Resultado", mensagem)
        janela.destroy()

    # ----------------------------------------------
    # MÃ©todos auxiliares
    # ----------------------------------------------
    def verificar_pendencias(self):
        hoje = datetime.now()
        for reserva in self.reservas:
            if reserva['status'] in ['reservado', 'emprestado']:
                try:
                    data_devolucao = datetime.strptime(reserva['devolucao'], "%d/%m/%Y")
                    if (data_devolucao - hoje).days == 1:
                        self.enviar_lembrete(reserva)
                    elif data_devolucao < hoje:
                        self.enviar_alerta_atraso(reserva)
                except:
                    continue

    def enviar_lembrete(self, reserva):
        equip = next(eq for eq in self.equipamentos if eq['id'] == reserva['equipamento_id'])
        mensagem = f"""
        Lembrete de DevoluÃ§Ã£o:
        Equipamento: {equip['nome']}
        Data Limite: {reserva['devolucao']}
        """
        self.enviar_email(
            reserva['usuario'],
            "Lembrete de DevoluÃ§Ã£o",
            mensagem,
            mostrar_popup=False  # Popup desabilitado
)

    def obter_nome_equipamento(self, equip_id):
        for eq in self.equipamentos:
            if eq['id'] == equip_id:
                return eq['nome']
        return "Equipamento NÃ£o Encontrado"

    def enviar_email(self, destinatario, assunto, mensagem, mostrar_popup=False):  # Alterado padrÃ£o para False
        """Simula o envio de e-mail com controle de exibiÃ§Ã£o"""
        mensagem_simulada = f"""
        [SIMULAÃÃO] E-mail enviado com sucesso!
        ========================================
        Para: {destinatario}
        Assunto: {assunto}
        Mensagem:
        {mensagem}
        ========================================
        """
    
        # Grava no console sempre
        print(mensagem_simulada)
    
        # Mostra popup apenas se explicitamente solicitado
        if mostrar_popup:
            messagebox.showinfo("E-mail Simulado", mensagem_simulada)
    
        return True
        
    # ----------------------------------------------
    # MÃ©todos de RelatÃ³rios
    # ----------------------------------------------
    def gerar_relatorios(self):
        janela = tk.Toplevel(self.root)
        janela.title("RelatÃ³rios e EstatÃ­sticas")
        janela.geometry("900x600")

        # Notebook para abas
        notebook = ttk.Notebook(janela)
        
        # Aba de equipamentos
        frame_equip = ttk.Frame(notebook)
        self.criar_relatorio_equipamentos(frame_equip)
        notebook.add(frame_equip, text="Equipamentos")

        # Aba de reservas
        frame_reservas = ttk.Frame(notebook)
        self.criar_relatorio_reservas(frame_reservas)
        notebook.add(frame_reservas, text="Reservas")

        # Aba de manutenÃ§Ã£o
        frame_manutencao = ttk.Frame(notebook)
        self.criar_relatorio_manutencao(frame_manutencao)
        notebook.add(frame_manutencao, text="ManutenÃ§Ãµes")

        notebook.pack(expand=1, fill='both')

    def criar_relatorio_equipamentos(self, frame):
        # Dados para a treeview
        columns = ('equipamento', 'tipo', 'disponivel', 'reservas')
        tree = ttk.Treeview(frame, columns=columns, show='headings')
        
        # Configurar cabeÃ§alhos
        tree.heading('equipamento', text='Equipamento')
        tree.heading('tipo', text='Tipo')
        tree.heading('disponivel', text='DisponÃ­vel')
        tree.heading('reservas', text='Reservas')
        
        # Adicionar scrollbar
        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        vsb.pack(side='right', fill='y')
        tree.configure(yscrollcommand=vsb.set)
        
        # Popular dados
        for eq in self.equipamentos:
            num_reservas = sum(1 for r in self.reservas if r['equipamento_id'] == eq['id'])
            disponivel = 'Sim' if eq['disponivel'] else 'NÃ£o'
            tree.insert('', 'end', values=(
                eq['nome'],
                eq['tipo'],
                disponivel,
                num_reservas
            ))
        
        tree.pack(fill='both', expand=True)

    def criar_relatorio_reservas(self, frame):
        columns = ('usuario', 'equipamento', 'data', 'devolucao', 'status')
        tree = ttk.Treeview(frame, columns=columns, show='headings')
        
        tree.heading('usuario', text='UsuÃ¡rio')
        tree.heading('equipamento', text='Equipamento')
        tree.heading('data', text='Data EmprÃ©stimo')
        tree.heading('devolucao', text='Data DevoluÃ§Ã£o')
        tree.heading('status', text='Status')
        
        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        vsb.pack(side='right', fill='y')
        tree.configure(yscrollcommand=vsb.set)
        
        for r in self.reservas:
            equipamento = self.obter_nome_equipamento(r['equipamento_id'])
            tree.insert('', 'end', values=(
                r['usuario'],
                equipamento,
                r['data'],
                r['devolucao'],
                r['status'].capitalize()
            ))
        
        tree.pack(fill='both', expand=True)

    def criar_relatorio_manutencao(self, frame):
        columns = ('equipamento', 'data', 'problema', 'status')
        tree = ttk.Treeview(frame, columns=columns, show='headings')
        
        tree.heading('equipamento', text='Equipamento')
        tree.heading('data', text='Data Registro')
        tree.heading('problema', text='Problema')
        tree.heading('status', text='Status')
        
        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        vsb.pack(side='right', fill='y')
        tree.configure(yscrollcommand=vsb.set)
        
        for m in self.manutencoes:
            equipamento = self.obter_nome_equipamento(m['equipamento_id'])
            tree.insert('', 'end', values=(
                equipamento,
                m['data'],
                m['problema'][:50] + '...' if len(m['problema']) > 50 else m['problema'],
                m['status']
            ))
        
        tree.pack(fill='both', expand=True)

    # ----------------------------------------------
    # MÃ©todos de Cancelamento de Reserva
    # ----------------------------------------------
    def cancelar_reserva(self):
        janela = tk.Toplevel(self.root)
        janela.title("Cancelar Reserva")
        janela.geometry("600x400")

        # Obter reservas pendentes do usuÃ¡rio
        reservas_pendentes = [
            r for r in self.reservas 
            if r['status'] == 'reservado' 
            and r['usuario'] == self.usuario_atual['email']
        ]

        if not reservas_pendentes:
            tk.Label(janela, text="Nenhuma reserva para cancelar", fg="red").pack(pady=20)
            tk.Button(janela, text="Fechar", command=janela.destroy).pack()
            return

        # Listagem de reservas
        tk.Label(janela, text="Selecione a reserva a cancelar:", font=('Arial', 10)).pack(pady=10)
        
        self.lista_reservas = tk.Listbox(janela, width=80, height=10)
        for reserva in reservas_pendentes:
            equipamento = self.obter_nome_equipamento(reserva['equipamento_id'])
            texto = f"ID {reserva['id']} - {equipamento} | Reservado em: {reserva['data']} | DevoluÃ§Ã£o: {reserva['devolucao']}"
            self.lista_reservas.insert(tk.END, texto)
        self.lista_reservas.pack(pady=10)

        # BotÃµes
        btn_frame = tk.Frame(janela)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Cancelar Reserva", bg="#ff6666", fg="white",
                 command=lambda: self.processar_cancelamento(janela, reservas_pendentes)).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Voltar", command=janela.destroy).pack(side=tk.LEFT, padx=5)

    def processar_cancelamento(self, janela, reservas):
        selecao = self.lista_reservas.curselection()
        if not selecao:
            messagebox.showerror("Erro", "Nenhuma reserva selecionada!")
            return

        index = selecao[0]
        reserva = reservas[index]
        
        # Atualizar status
        equipamento = next(eq for eq in self.equipamentos if eq['id'] == reserva['equipamento_id'])
        equipamento['disponivel'] = True
        reserva['status'] = 'cancelada'

        # Salvar alteraÃ§Ãµes
        DataHandler.salvar_dados('equipamentos.json', self.equipamentos)
        DataHandler.salvar_dados('reservas.json', self.reservas)

        # Feedback e fechar janela
        messagebox.showinfo("Sucesso", f"Reserva ID {reserva['id']} cancelada com sucesso!")
        janela.destroy()

           # ----------------------------------------------
    # MÃ©todos de RenovaÃ§Ã£o de EmprÃ©stimo
    # ----------------------------------------------
    def renovar_emprestimo(self):
        janela = tk.Toplevel(self.root)
        janela.title("Renovar EmprÃ©stimo")
        janela.geometry("600x400")

        # Obter emprÃ©stimos ativos renovÃ¡veis
        emprestimos_ativos = [
            r for r in self.reservas 
            if r['status'] == 'emprestado'
            and r['usuario'] == self.usuario_atual['email']
        ]

        if not emprestimos_ativos:
            tk.Label(janela, text="Nenhum emprÃ©stimo disponÃ­vel para renovaÃ§Ã£o", fg="red").pack(pady=20)
            tk.Button(janela, text="Fechar", command=janela.destroy).pack()
            return

        tk.Label(janela, text="Selecione o emprÃ©stimo para renovar:").pack(pady=10)
        
        # Listar emprÃ©stimos formatados
        lista_emprestimos = [
            f"{self.obter_nome_equipamento(r['equipamento_id'])} | DevoluÃ§Ã£o: {r['devolucao']}"
            for r in emprestimos_ativos
        ]
        
        self.combo_emprestimos = ttk.Combobox(janela, values=lista_emprestimos, width=50)
        self.combo_emprestimos.pack(pady=5)

        tk.Label(janela, text="Nova Data de DevoluÃ§Ã£o:").pack(pady=5)
        self.nova_data = DateEntry(janela, date_pattern='dd/mm/yyyy')
        self.nova_data.pack(pady=5)

        tk.Button(janela, text="Renovar", 
                 command=lambda: self.processar_renovacao(janela, emprestimos_ativos),
                 bg="#99ff99").pack(pady=15)

    def processar_renovacao(self, janela, emprestimos):
        selecao = self.combo_emprestimos.current()
        if selecao == -1:
            messagebox.showerror("Erro", "Selecione um emprÃ©stimo!")
            return
            
        emprestimo = emprestimos[selecao]
        nova_data = self.nova_data.get_date()
        
        try:
            data_original = datetime.strptime(emprestimo['devolucao'], "%d/%m/%Y")
            if nova_data <= data_original:
                messagebox.showerror("Erro", "Nova data deve ser posterior Ã  data original!")
                return
                
            # Verificar disponibilidade
            equipamento = next(eq for eq in self.equipamentos if eq['id'] == emprestimo['equipamento_id'])
            if not equipamento['disponivel']:
                messagebox.showerror("Erro", "Equipamento nÃ£o estÃ¡ disponÃ­vel para renovaÃ§Ã£o!")
                return

            # Atualizar data
            emprestimo['devolucao'] = nova_data.strftime("%d/%m/%Y")
            DataHandler.salvar_dados('reservas.json', self.reservas)
            
            # Enviar confirmaÃ§Ã£o
            mensagem = f"""
            EmprÃ©stimo renovado:
            Equipamento: {equipamento['nome']}
            Nova Data DevoluÃ§Ã£o: {emprestimo['devolucao']}
            """
            self.enviar_email(
                self.usuario_atual['email'],
                "RenovaÃ§Ã£o de EmprÃ©stimo",
                mensagem,
                mostrar_popup=True  # Popup habilitado aqui
)
            
            messagebox.showinfo("Sucesso", "EmprÃ©stimo renovado com sucesso!")
            janela.destroy()
            
        except ValueError as e:
            messagebox.showerror("Erro", f"Data invÃ¡lida: {str(e)}")

  # ----------------------------------------------
    # ManutenÃ§Ã£o e Suporte
    # ----------------------------------------------
    def tela_manutencao_suporte(self):
        self.limpar_tela()
        tk.Label(self.root, text="ManutenÃ§Ã£o e Suporte TÃ©cnico", font=("Arial", 14)).pack(pady=10)

        opcoes = []
        if self.usuario_atual['perfil'] == "Administrador":
            opcoes.append(("Registrar ManutenÃ§Ã£o", self.registrar_manutencao))
            
        opcoes += [
            ("Canal de Suporte", self.canal_suporte),
            ("Voltar", self.tela_principal)
        ]

        for texto, comando in opcoes:
            ttk.Button(self.root, text=texto, command=comando).pack(pady=5)

    def registrar_manutencao(self):
        janela = tk.Toplevel(self.root)
        janela.title("Registro de ManutenÃ§Ã£o")
        
        # Listar equipamentos
        ttk.Label(janela, text="Selecione o equipamento:").pack(pady=5)
        equipamentos = [eq['nome'] for eq in self.equipamentos]
        self.combo_equip = ttk.Combobox(janela, values=equipamentos)
        self.combo_equip.pack(pady=5)

        # DescriÃ§Ã£o do problema
        ttk.Label(janela, text="DescriÃ§Ã£o do problema:").pack(pady=5)
        self.txt_problema = tk.Text(janela, height=5, width=40)
        self.txt_problema.pack(pady=5)

        ttk.Button(janela, text="Registrar", command=lambda: self.salvar_manutencao(janela)).pack(pady=10)

    def salvar_manutencao(self, janela):
        equip_nome = self.combo_equip.get()
        problema = self.txt_problema.get("1.0", tk.END).strip()
        
        if not equip_nome or not problema:
            messagebox.showerror("Erro", "Preencha todos os campos!")
            return
            
        equip = next((eq for eq in self.equipamentos if eq['nome'] == equip_nome), None)
        if not equip:
            messagebox.showerror("Erro", "Equipamento nÃ£o encontrado!")
            return

        nova_manutencao = {
            'id': len(self.manutencoes) + 1,
            'equipamento_id': equip['id'],
            'data': datetime.now().strftime("%d/%m/%Y %H:%M"),
            'problema': problema,
            'tecnico': self.usuario_atual['nome'],
            'status': 'Pendente'
        }
        
        self.manutencoes.append(nova_manutencao)
        DataHandler.salvar_dados('manutencoes.json', self.manutencoes)
        
        # Marcar equipamento como em manutenÃ§Ã£o
        equip['manutencao'] = True
        equip['disponivel'] = False
        DataHandler.salvar_dados('equipamentos.json', self.equipamentos)
        
        messagebox.showinfo("Sucesso", "ManutenÃ§Ã£o registrada com sucesso!")
        janela.destroy()

    def canal_suporte(self):
        janela = tk.Toplevel(self.root)
        janela.title("Suporte TÃ©cnico")
        
        ttk.Label(janela, text="Descreva seu problema:").pack(pady=5)
        self.txt_suporte = tk.Text(janela, height=10, width=50)
        self.txt_suporte.pack(pady=5)
        
        ttk.Button(janela, text="Enviar", command=lambda: self.enviar_suporte(janela)).pack(pady=10)

    def enviar_suporte(self, janela):
        problema = self.txt_suporte.get("1.0", tk.END).strip()
        if len(problema) < 10:
            messagebox.showerror("Erro", "DescriÃ§Ã£o muito curta!")
            return
            
        mensagem = f"""
        Novo chamado de suporte:
        UsuÃ¡rio: {self.usuario_atual['nome']}
        Email: {self.usuario_atual['email']}
        Problema:
        {problema}
        """
        
        self.enviar_email(
            "suporte@universidade.com",
            "Chamado de Suporte",
            mensagem,
            mostrar_popup=True  # Popup desabilitado
)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
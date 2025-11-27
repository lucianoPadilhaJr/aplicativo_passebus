import tkinter as tk
from tkinter import messagebox
import re
import bcrypt 
from database import get_db_connection 
from mysql.connector import Error


from interface_principal_frame import InterfacePrincipalFrame 

class CadastroFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#f5f5f5")

        self.fonte_entry = ("Arial", 11)

        tk.Label(self, text="Cadastro de Usuário", font=("Arial", 16, "bold"), bg="#f5f5f5").pack(pady=15)
        
        frame_principal = tk.Frame(self, bg="#f5f5f5")
        frame_principal.pack(expand=True, padx=40, pady=10)

        # Seus métodos criar_campo devem estar definidos abaixo (mantive a lógica de chamada)
        self.entry_nome = self.criar_campo(frame_principal, "Nome:")
        self.entry_sobrenome = self.criar_campo(frame_principal, "Sobrenome:")
        self.entry_email = self.criar_campo(frame_principal, "E-mail:")
        self.entry_cpf = self.criar_campo(frame_principal, "CPF (11 números):")

        self.criar_label_entry(frame_principal, "Senha (mínimo 8 caracteres):")
        
        frame_senha = tk.Frame(frame_principal, bg="#f5f5f5")
        frame_senha.pack(pady=(2, 10), fill="x")
        self.entry_senha = tk.Entry(frame_senha, width=45, show="*", font=self.fonte_entry)
        self.entry_senha.pack(side="left", fill="x", expand=True)
        
        self.var_mostrar_senha = tk.BooleanVar()
        check_senha = tk.Checkbutton(frame_principal, text="Mostrar senha", variable=self.var_mostrar_senha, 
                                     command=self.alternar_visualizacao_senha, bg="#f5f5f5")
        check_senha.pack(anchor="w")

        btn_cadastrar = tk.Button(
            self, text="Salvar Cadastro",
            bg="#28A745", fg="white",
            font=("Arial", 10, "bold"),
            command=self.cadastrar_usuario,
            cursor="hand2"
        )
        btn_cadastrar.pack(pady=15)

        # --- CORREÇÃO 2: O Botão Voltar ---
        # Antes estava: controller.mostrar_frame(controller.frames["InterfacePrincipalFrame"])
        # Isso causava o erro porque o dicionário usa Classes, não Strings.
        btn_voltar = tk.Button(
            self, text="Voltar",
            bg="#6c757d", fg="white",
            # Passamos a CLASSE diretamente. O controller sabe buscar a instância correta.
            command=lambda: controller.mostrar_frame(InterfacePrincipalFrame),
            cursor="hand2"
        )
        btn_voltar.pack(pady=5)

    def alternar_visualizacao_senha(self):
        if self.var_mostrar_senha.get():
            self.entry_senha.config(show="")
        else:
            self.entry_senha.config(show="*")

    def criar_campo(self, parent, label_text):
        """Utilitário para criar labels e entries"""
        self.criar_label_entry(parent, label_text)
        entry = tk.Entry(parent, width=45, font=self.fonte_entry)
        entry.pack(pady=(2, 10))
        return entry

    def criar_label_entry(self, parent, text):
        tk.Label(parent, text=text, bg="#f5f5f5", font=("Arial", 10)).pack(anchor="w")

    def cadastrar_usuario(self):
        nome = self.entry_nome.get()
        sobrenome = self.entry_sobrenome.get()
        email = self.entry_email.get()
        cpf = self.entry_cpf.get()
        senha = self.entry_senha.get()

        # Validações básicas
        if not (nome and sobrenome and email and cpf and senha):
            self.exibir_aviso("Todos os campos são obrigatórios!", "erro")
            return

        if not self.validar_email(email):
            self.exibir_aviso("E-mail inválido!", "erro")
            return

        if not self.validar_cpf(cpf):
            self.exibir_aviso("CPF inválido! Deve conter apenas 11 números.", "erro")
            return
            
        if len(senha) < 8:
            self.exibir_aviso("A senha deve ter pelo menos 8 caracteres.", "erro")
            return

        # Hash da senha
        salt = bcrypt.gensalt()
        hash_senha = bcrypt.hashpw(senha.encode('utf-8'), salt)

        # Conexão com banco
        conn = get_db_connection()
        if not conn:
            self.exibir_aviso("Erro de conexão com o banco.", "erro")
            return
        
        cursor = conn.cursor()
        try:
            # Verifica duplicidade
            sql_check = "SELECT 1 FROM tb_usuario WHERE nr_cpf = %s OR ds_email = %s"
            cursor.execute(sql_check, (cpf, email))
            if cursor.fetchone():
                self.exibir_aviso("CPF ou E-mail já cadastrado!", "erro")
                return

            sql_insert = """
            INSERT INTO tb_usuario_app (nm_nome, nm_sobrenome, ds_email, nr_cpf, ds_senha) 
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql_insert, (nome, sobrenome, email, cpf, hash_senha))
            conn.commit()

            messagebox.showinfo("Sucesso", "Cadastro realizado com sucesso! Faça o login.")
            
            # Limpa campos
            self.entry_nome.delete(0, 'end')
            self.entry_sobrenome.delete(0, 'end')
            self.entry_email.delete(0, 'end')
            self.entry_cpf.delete(0, 'end')
            self.entry_senha.delete(0, 'end')

            # Redireciona para Login
            # Importação local para evitar ciclo se login importar cadastro (boas práticas)
            from login_frame import LoginFrame 
            self.controller.mostrar_frame(LoginFrame)

        except Error as e:
            self.exibir_aviso(f"Erro ao cadastrar: {e}", "erro")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def exibir_aviso(self, mensagem, tipo):
        if tipo == "erro":
            messagebox.showerror("Erro", mensagem)
        else:
            messagebox.showinfo("Aviso", mensagem)

    def validar_email(self, email):
        padrao = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(padrao, email) is not None

    def validar_cpf(self, cpf):
        return cpf.isdigit() and len(cpf) == 11
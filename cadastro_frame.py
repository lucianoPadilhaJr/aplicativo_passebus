import tkinter as tk
from tkinter import messagebox
import re
import bcrypt 
from database import connect_app_db 
from mysql.connector import Error

class CadastroFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#f5f5f5")

        self.fonte_entry = ("Arial", 11)

        tk.Label(self, text="Cadastro de Usuário", font=("Arial", 16, "bold"), bg="#f5f5f5").pack(pady=15)
        
        frame_principal = tk.Frame(self, bg="#f5f5f5")
        frame_principal.pack(expand=True, padx=40, pady=10)

        self.entry_nome = self.criar_campo(frame_principal, "Nome:")
        self.entry_sobrenome = self.criar_campo(frame_principal, "Sobrenome:")
        self.entry_email = self.criar_campo(frame_principal, "E-mail:")
        self.entry_cpf = self.criar_campo(frame_principal, "CPF (11 números):")

        self.criar_label_entry(frame_principal, "Senha (mínimo 8 caracteres):")
        
        frame_senha = tk.Frame(frame_principal, bg="#f5f5f5")
        frame_senha.pack(pady=(2, 10), fill="x")
        self.entry_senha = tk.Entry(frame_senha, width=45, show="*", font=self.fonte_entry, relief="solid", bd=1)
        self.entry_senha.pack(fill="x", expand=True)
        
        self.var_mostrar_senha = tk.BooleanVar()
        self.chk_mostrar = tk.Checkbutton(
            frame_principal, text="Mostrar Senha", 
            variable=self.var_mostrar_senha, 
            onvalue=True, offvalue=False,
            bg="#f5f5f5", 
            command=self.toggle_senha
        )
        self.chk_mostrar.pack(anchor="w")

        self.lbl_aviso = tk.Label(frame_principal, text="", font=("Arial", 9), bg="#f5f5f5")
        self.lbl_aviso.pack(pady=(5,0))

        btn_cadastrar = tk.Button(
            frame_principal, text="Cadastrar", 
            bg="#007BFF", fg="white", 
            command=self.realizar_cadastro,
            cursor="hand2"
        )
        btn_cadastrar.pack(pady=10, fill="x")

        btn_voltar = tk.Button(
            frame_principal, text="Voltar", 
            bg="#6c757d", fg="white", 
            command=self.voltar,
            cursor="hand2"
        )
        btn_voltar.pack(pady=5, fill="x")

    def voltar(self):
        from interface_principal_frame import InterfacePrincipalFrame
        self.controller.mostrar_frame(InterfacePrincipalFrame)

    def toggle_senha(self):
        if self.var_mostrar_senha.get():
            self.entry_senha.config(show="")
        else:
            self.entry_senha.config(show="*")

    def criar_label_entry(self, master, texto):
        tk.Label(master, text=texto, font=("Arial", 10), bg="#f5f5f5").pack(anchor="w", pady=(8, 0))

    def criar_entry(self, master):
        entry = tk.Entry(master, width=45, font=self.fonte_entry, relief="solid", bd=1)
        return entry

    def criar_campo(self, master, texto):
        self.criar_label_entry(master, texto)
        entry = self.criar_entry(master)
        entry.pack(pady=(2, 8), fill="x")
        return entry

    def validar_senha(self, senha):
        return len(senha) >= 8 

    def exibir_aviso(self, mensagem, tipo="aviso"):
        cor = "red" if tipo in ("aviso", "erro") else "green"
        self.lbl_aviso.config(text=mensagem, fg=cor)

    def realizar_cadastro(self):
        nome = self.entry_nome.get().strip()
        sobrenome = self.entry_sobrenome.get().strip()
        email = self.entry_email.get().strip()
        cpf = self.entry_cpf.get().strip()
        senha = self.entry_senha.get().strip()

        if not all([nome, sobrenome, email, cpf, senha]):
            self.exibir_aviso("Todos os campos são obrigatórios!")
            return
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            self.exibir_aviso("E-mail inválido!")
            return
        if not (cpf.isdigit() and len(cpf) == 11):
            self.exibir_aviso("CPF inválido! Deve conter 11 números.")
            return
        if not self.validar_senha(senha):
            self.exibir_aviso("Senha muito curta!")
            return

        senha_bytes = senha.encode('utf-8')
        salt = bcrypt.gensalt()
        hash_senha = bcrypt.hashpw(senha_bytes, salt)

        conn = connect_app_db()
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

            # Inserção correta conforme SQL (nm_nome, nm_sobrenome)
            sql_insert = """
            INSERT INTO tb_usuario (nm_nome, nm_sobrenome, ds_email, nr_cpf, ds_senha) 
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql_insert, (nome, sobrenome, email, cpf, hash_senha))
            conn.commit()

            messagebox.showinfo("Sucesso", "Cadastro realizado com sucesso! Faça o login.")
            
            from login_frame import LoginFrame
            self.controller.mostrar_frame(LoginFrame)

        except Error as e:
            self.exibir_aviso(f"Erro no cadastro: {e}", "erro")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
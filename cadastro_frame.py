import tkinter as tk
from tkinter import messagebox
import re
import bcrypt 
from database import get_db_connection # Alterado
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
        self.entry_senha = tk.Entry(frame_senha, width=45, show="*", font=self.fonte_entry)
        self.entry_senha.pack(side="left", fill="x", expand=True)

        btn_cadastrar = tk.Button(
            self, text="Cadastrar",
            width=20, height=2,
            bg="#007BFF", fg="white",
            font=("Arial", 11, "bold"),
            command=self.realizar_cadastro,
            cursor="hand2"
        )
        btn_cadastrar.pack(pady=10)

        btn_voltar = tk.Button(
            self, text="Voltar",
            bg="#6c757d", fg="white",
            command=lambda: controller.mostrar_frame(controller.frames["InterfacePrincipalFrame"]),
            cursor="hand2"
        )
        btn_voltar.pack(pady=5)

    def criar_campo(self, parent, texto):
        self.criar_label_entry(parent, texto)
        entry = tk.Entry(parent, font=self.fonte_entry, width=45)
        entry.pack(pady=(0, 10))
        return entry

    def criar_label_entry(self, parent, texto):
        tk.Label(parent, text=texto, bg="#f5f5f5", anchor="w").pack(fill="x")

    def validar_email(self, email):
        padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(padrao, email)

    def validar_senha(self, senha):
        return len(senha) >= 8

    def exibir_aviso(self, mensagem, tipo="aviso"):
        if tipo == "erro":
            messagebox.showerror("Erro", mensagem)
        else:
            messagebox.showwarning("Atenção", mensagem)

    def realizar_cadastro(self):
        nome = self.entry_nome.get().strip()
        sobrenome = self.entry_sobrenome.get().strip()
        email = self.entry_email.get().strip()
        cpf = self.entry_cpf.get().strip()
        senha = self.entry_senha.get().strip()

        if not (nome and sobrenome and email and cpf and senha):
            self.exibir_aviso("Preencha todos os campos!")
            return

        if not cpf.isdigit() or len(cpf) != 11:
            self.exibir_aviso("CPF inválido! Digite apenas os 11 números.")
            return

        if not self.validar_email(email):
            self.exibir_aviso("E-mail inválido!")
            return
        
        if not self.validar_senha(senha):
            self.exibir_aviso("Senha muito curta!")
            return

        senha_bytes = senha.encode('utf-8')
        salt = bcrypt.gensalt()
        hash_senha = bcrypt.hashpw(senha_bytes, salt)

        # Conexão unificada
        conn = get_db_connection()
        if not conn:
            self.exibir_aviso("Erro de conexão com o banco.", "erro")
            return
        
        cursor = conn.cursor()
        try:
            # Verifica duplicidade na tabela do APP
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

            from login_frame import LoginFrame
            self.controller.mostrar_frame(LoginFrame)

        except Error as e:
            self.exibir_aviso(f"Erro no cadastro: {e}", "erro")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
import tkinter as tk
from tkinter import messagebox
import bcrypt 
from database import connect_app_db 
from mysql.connector import Error

class LoginFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#f5f5f5")

        tk.Label(self, text="Login PasseBus", font=("Arial", 16, "bold"), bg="#f5f5f5").pack(pady=20)
        
        frame_principal = tk.Frame(self, bg="#f5f5f5")
        frame_principal.pack(expand=True, padx=40, pady=10)

        tk.Label(frame_principal, text="E-mail ou CPF:", bg="#f5f5f5").pack(anchor="w")
        self.entry_usuario = tk.Entry(frame_principal, font=("Arial", 11), width=35)
        self.entry_usuario.pack(pady=(0,10), fill=tk.X)

        tk.Label(frame_principal, text="Senha:", bg="#f5f5f5").pack(anchor="w")
        
        frame_senha = tk.Frame(frame_principal, bg="#f5f5f5")
        frame_senha.pack(fill="x", pady=(0, 15))

        self.entry_senha = tk.Entry(frame_senha, show="*", font=("Arial", 11), width=35)
        self.entry_senha.pack(fill="x", expand=True)

        self.var_mostrar_senha = tk.BooleanVar()
        tk.Checkbutton(
            frame_principal, text="Mostrar Senha", 
            variable=self.var_mostrar_senha, 
            onvalue=True, offvalue=False,
            bg="#f5f5f5", 
            command=lambda: self.entry_senha.config(show="" if self.var_mostrar_senha.get() else "*")
        ).pack(anchor="w")

        self.lbl_aviso = tk.Label(frame_principal, text="", fg="red", bg="#f5f5f5")
        self.lbl_aviso.pack(pady=5)

        tk.Button(
            frame_principal, text="Entrar", 
            bg="#28A745", fg="white", font=("Arial", 11, "bold"),
            command=self.realizar_login,
            cursor="hand2"
        ).pack(pady=10, fill="x")

        tk.Button(
            frame_principal, text="Voltar", 
            bg="#6c757d", fg="white",
            command=self.voltar,
            cursor="hand2"
        ).pack(pady=5, fill="x")

    def voltar(self):
        from interface_principal_frame import InterfacePrincipalFrame
        self.controller.mostrar_frame(InterfacePrincipalFrame)

    def realizar_login(self):
        usuario = self.entry_usuario.get().strip()
        senha_digitada = self.entry_senha.get().strip()

        if not usuario or not senha_digitada:
            self.lbl_aviso.config(text="Preencha todos os campos!")
            return

        conn = connect_app_db()
        if not conn:
            self.lbl_aviso.config(text="Erro de conexão com o banco.")
            return

        cursor = conn.cursor(dictionary=True) 
        
        try:
            # Busca usuário pelo email ou CPF
            sql = "SELECT id_usuario, ds_senha FROM tb_usuario WHERE (ds_email=%s OR nr_cpf=%s)"
            cursor.execute(sql, (usuario, usuario))
            resultado = cursor.fetchone()

            if resultado:
                hash_salvo = resultado["ds_senha"].encode('utf-8') 
                
                if bcrypt.checkpw(senha_digitada.encode('utf-8'), hash_salvo):
                    id_usuario_logado = resultado["id_usuario"]
                    self.controller.id_usuario_logado = id_usuario_logado
                    
                    self.entry_usuario.delete(0, 'end')
                    self.entry_senha.delete(0, 'end')
                    self.lbl_aviso.config(text="")
                    
                    from tela_inicial_frame import TelaInicialFrame
                    self.controller.mostrar_frame(TelaInicialFrame)
                else:
                    self.lbl_aviso.config(text="E-mail/CPF ou senha incorretos!")
            else:
                self.lbl_aviso.config(text="E-mail/CPF ou senha incorretos!")

        except Error as e:
            self.lbl_aviso.config(text=f"Erro de login: {e}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
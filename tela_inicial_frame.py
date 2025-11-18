import tkinter as tk
from tkinter import messagebox
from database import connect_app_db
from mysql.connector import Error

class TelaInicialFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#f5f5f5")
        
        fonte_titulo = ("Arial", 16, "bold")
        fonte_botao = ("Arial", 11)

        self.lbl_boas_vindas = tk.Label(
            self, 
            text="Bem-vindo!", 
            font=fonte_titulo, 
            bg="#f5f5f5"
        )
        self.lbl_boas_vindas.pack(pady=30)

        frame_botoes = tk.Frame(self, bg="#f5f5f5")
        frame_botoes.pack(expand=True)

        btn_validar_cartao = tk.Button(
            frame_botoes, 
            text="Validar Cartão", 
            width=20, height=2,
            bg="#4CAF50", fg="white", 
            font=fonte_botao,
            command=self.ir_para_validar_cartao, 
            cursor="hand2"
        )
        btn_validar_cartao.pack(pady=10)

        btn_recarga_cartao = tk.Button(
            frame_botoes, 
            text="Recarregar Cartão", 
            width=20, height=2,
            bg="#FFC107", fg="black", 
            font=fonte_botao,
            command=self.recarga_cartao, 
            cursor="hand2"
        )
        btn_recarga_cartao.pack(pady=10)

        btn_sair = tk.Button(
            self, 
            text="Sair (Logout)",
            bg="#dc3545", fg="white",
            command=self.fazer_logout,
            cursor="hand2"
        )
        btn_sair.pack(pady=20, side="bottom")

    def ir_para_validar_cartao(self):
        from validar_cartao_frame import ValidarCartaoFrame
        self.controller.mostrar_frame(ValidarCartaoFrame)

    def recarga_cartao(self):
        messagebox.showinfo("Em Breve", "Função de recarga de cartão ainda não implementada.")

    def atualizar_dados_usuario(self):
        """Busca o nome do usuário no banco e atualiza o label."""
        id_usuario = self.controller.id_usuario_logado
        
        if not id_usuario:
            self.lbl_boas_vindas.config(text="Erro: Usuário não logado")
            return

        conn = connect_app_db()
        if not conn:
            self.lbl_boas_vindas.config(text="Erro de conexão")
            return
            
        cursor = conn.cursor()
        try:
            # Corrigido para nm_nome
            sql = "SELECT nm_nome FROM tb_usuario WHERE id_usuario = %s"
            cursor.execute(sql, (id_usuario,))
            resultado = cursor.fetchone()
            
            if resultado:
                nome_usuario = resultado[0]
                self.lbl_boas_vindas.config(text=f"Bem-vindo, {nome_usuario}!")
            else:
                self.lbl_boas_vindas.config(text="Usuário não encontrado.")
                
        except Error as e:
            self.lbl_boas_vindas.config(text="Erro ao buscar dados.")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def fazer_logout(self):
        if messagebox.askyesno("Sair", "Deseja realmente sair do aplicativo?"):
            self.controller.redefinir_para_login()
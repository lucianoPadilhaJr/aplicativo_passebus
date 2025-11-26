import tkinter as tk
from tkinter import messagebox
from database import get_db_connection # Alterado
from mysql.connector import Error

class TelaInicialFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#f5f5f5")
        
        fonte_titulo = ("Arial", 16, "bold")
        fonte_info = ("Arial", 12)
        fonte_botao = ("Arial", 11)

        self.lbl_boas_vindas = tk.Label(
            self, 
            text="Bem-vindo!", 
            font=fonte_titulo, 
            bg="#f5f5f5"
        )
        self.lbl_boas_vindas.pack(pady=(30, 10))

        # Painel de Status do Cartão
        self.lbl_info_cartao = tk.Label(
            self,
            text="Nenhum cartão vinculado.",
            font=fonte_info,
            bg="#e9ecef",
            fg="#333",
            padx=10, pady=10,
            relief="groove"
        )
        self.lbl_info_cartao.pack(pady=10, fill="x", padx=40)

        frame_botoes = tk.Frame(self, bg="#f5f5f5")
        frame_botoes.pack(expand=True)

        btn_validar_cartao = tk.Button(
            frame_botoes, 
            text="Validar/Sincronizar Cartão", 
            width=25, height=2,
            bg="#4CAF50", fg="white", 
            font=fonte_botao,
            command=self.ir_para_validar_cartao, 
            cursor="hand2"
        )
        btn_validar_cartao.pack(pady=10)

        btn_recarga_cartao = tk.Button(
            frame_botoes, 
            text="Recarregar Cartão", 
            width=25, height=2,
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
        """Busca o nome do usuário e dados do cartão no banco unificado."""
        id_usuario = self.controller.id_usuario_logado
        
        if not id_usuario:
            self.lbl_boas_vindas.config(text="Erro: Usuário não logado")
            return

        conn = get_db_connection() # Conexão única
        if not conn:
            self.lbl_boas_vindas.config(text="Erro de conexão")
            return
            
        cursor = conn.cursor(dictionary=True)
        try:
            # 1. Buscar Nome (Tabela do App)
            sql_user = "SELECT nm_nome FROM tb_usuario_app WHERE id_usuario = %s"
            cursor.execute(sql_user, (id_usuario,))
            user_data = cursor.fetchone()
            
            if user_data:
                self.lbl_boas_vindas.config(text=f"Bem-vindo, {user_data['nm_nome']}!")
            else:
                self.lbl_boas_vindas.config(text="Usuário não encontrado.")

            # 2. Buscar Cartão Vinculado (Tabela do App - dados locais/sincronizados)
            sql_card = """
                SELECT id_cartao_nmr_cartao, vlr_saldo, tipo_cartao 
                FROM tb_cartao_app 
                WHERE id_usuario = %s AND ds_status = 'desbloqueado'
                LIMIT 1
            """
            cursor.execute(sql_card, (id_usuario,))
            card_data = cursor.fetchone()

            if card_data:
                saldo_fmt = f"R$ {card_data['vlr_saldo']:.2f}".replace('.', ',')
                # Exibe tipo do cartão se disponível (vimos que adicionamos esse campo no passo anterior)
                tipo_str = f"\nTipo: {card_data.get('tipo_cartao', 'Comum')}"
                
                texto_cartao = (f"Cartão: {card_data['id_cartao_nmr_cartao']}"
                                f"{tipo_str}\n"
                                f"Saldo Atual: {saldo_fmt}")
                self.lbl_info_cartao.config(text=texto_cartao, fg="black", bg="#d4edda")
            else:
                self.lbl_info_cartao.config(text="Nenhum cartão ativo vinculado.", fg="#555", bg="#e9ecef")
                
        except Error as e:
            self.lbl_boas_vindas.config(text="Erro ao buscar dados.")
            print(e)
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def fazer_logout(self):
        if messagebox.askyesno("Sair", "Deseja realmente sair do aplicativo?"):
            self.controller.redefinir_para_login()
import tkinter as tk
from tkinter import messagebox
from database import connect_app_db, connect_sim_db
from mysql.connector import Error

class ValidarCartaoFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.id_usuario_logado_app = None
        self.configure(bg="#f5f5f5")

        tk.Label(self, text="Validação e Sincronização de Cartão", font=("Arial", 14, "bold"), bg="#f5f5f5").pack(pady=20)
        
        frame_meio = tk.Frame(self, bg="#f5f5f5")
        frame_meio.pack(pady=10, padx=40, fill="x")

        tk.Label(frame_meio, text="Número do Cartão:", font=("Arial", 12), bg="#f5f5f5").pack(pady=5)
        self.entry_numero = tk.Entry(frame_meio, font=("Arial", 12), width=30)
        self.entry_numero.pack(pady=6, fill="x")

        btn_validar = tk.Button(
            frame_meio, text="Validar e Sincronizar Cartão",
            font=("Arial", 12, "bold"), bg="#4CAF50", fg="white",
            command=self.validar_e_sincronizar,
            cursor="hand2"
        )
        btn_validar.pack(pady=15, fill="x")
        
        btn_voltar = tk.Button(
            frame_meio, text="Voltar ao Painel",
            font=("Arial", 10), bg="#6c757d", fg="white",
            command=self.voltar,
            cursor="hand2"
        )
        btn_voltar.pack(pady=5, fill="x")

    def voltar(self):
        from tela_inicial_frame import TelaInicialFrame
        self.controller.mostrar_frame(TelaInicialFrame)

    def definir_usuario_logado(self, id_usuario):
        self.id_usuario_logado_app = id_usuario

    def validar_e_sincronizar(self):
        numero_cartao = self.entry_numero.get().strip()
        if not (numero_cartao.isdigit() and len(numero_cartao) >= 5):
            messagebox.showerror("Erro", "Número do cartão inválido.")
            return

        if not self.id_usuario_logado_app:
            messagebox.showerror("Erro", "Usuário não logado. Reinicie o app.")
            return

        # ---------------------------------------------------------
        # PASSO 1: Buscar o CPF do usuário logado no APP
        # ---------------------------------------------------------
        cpf_usuario_app = None
        conn_app = connect_app_db()
        if not conn_app:
            messagebox.showerror("Erro", "Erro ao conectar ao banco do App.")
            return
        
        try:
            cursor_app = conn_app.cursor()
            cursor_app.execute("SELECT nr_cpf FROM tb_usuario WHERE id_usuario = %s", (self.id_usuario_logado_app,))
            resultado_app = cursor_app.fetchone()
            if resultado_app:
                cpf_usuario_app = resultado_app[0]
            else:
                messagebox.showerror("Erro", "Usuário logado não encontrado no banco.")
                return
        except Error as e:
            messagebox.showerror("Erro", f"Erro ao buscar CPF do usuário: {e}")
            return
        finally:
            cursor_app.close()
            conn_app.close()

        # ---------------------------------------------------------
        # PASSO 2: Buscar dados do cartão no banco SIMULADO e comparar CPFs
        # ---------------------------------------------------------
        conn_sim = connect_sim_db()
        if not conn_sim:
            messagebox.showerror("Erro", "Não foi possível conectar ao sistema de validação (SIM).")
            return
        
        cursor_sim = conn_sim.cursor(dictionary=True)
        try:
            # Fazemos um JOIN para pegar o CPF do dono do cartão na simulação
            sql_sim = """
                SELECT c.id_cartao_nmr_cartao, c.vlr_saldo, c.ds_status, u.nr_cpf 
                FROM cartao c
                INNER JOIN usuario u ON c.id_usuario = u.id_usuario
                WHERE c.id_cartao_nmr_cartao = %s
            """
            cursor_sim.execute(sql_sim, (numero_cartao,))
            cartao_sim = cursor_sim.fetchone()
            
            if not cartao_sim:
                messagebox.showerror("Inválido", "Cartão não encontrado no sistema da empresa.")
                return

            cpf_dono_cartao_sim = cartao_sim['nr_cpf']

            # ---------------------------------------------------------
            # PASSO 3: A Validação de Segurança
            # ---------------------------------------------------------
            # Comparamos o CPF logado (App) com o CPF do dono do cartão (Simulado)
            if cpf_usuario_app != cpf_dono_cartao_sim:
                messagebox.showerror(
                    "Acesso Negado", 
                    f"Este cartão pertence ao CPF: {cpf_dono_cartao_sim}.\n"
                    f"Você está logado com o CPF: {cpf_usuario_app}.\n\n"
                    "Não é possível validar um cartão que não lhe pertence."
                )
                return

            # Se os CPFs baterem, prossegue para sincronizar
            self.sincronizar_cartao_app(cartao_sim, self.id_usuario_logado_app)

        except Error as e:
            messagebox.showerror("Erro", f"Erro ao validar cartão no SIM: {e}")
        finally:
            if conn_sim.is_connected():
                cursor_sim.close()
                conn_sim.close()

    def sincronizar_cartao_app(self, cartao_sim_data, id_usuario_app):
        from tela_inicial_frame import TelaInicialFrame
        
        conn_app = connect_app_db()
        if not conn_app:
            messagebox.showerror("Erro", "Não foi possível conectar ao banco de dados do APP.")
            return
        
        cursor_app = conn_app.cursor()
        try:
            nr_cartao = cartao_sim_data['id_cartao_nmr_cartao']
            vlr_saldo = cartao_sim_data['vlr_saldo']
            ds_status = cartao_sim_data['ds_status']

            # Verifica se já existe na tabela tb_cartao do APP
            cursor_app.execute("SELECT id_cartao_nmr_cartao FROM tb_cartao WHERE id_cartao_nmr_cartao = %s", (nr_cartao,))
            cartao_app_existente = cursor_app.fetchone()

            if cartao_app_existente:
                # Atualiza
                sql_update = """
                UPDATE tb_cartao SET vlr_saldo = %s, id_usuario = %s, ds_status = %s 
                WHERE id_cartao_nmr_cartao = %s
                """
                cursor_app.execute(sql_update, (vlr_saldo, id_usuario_app, ds_status, nr_cartao))
            else:
                # Insere
                sql_insert = """
                INSERT INTO tb_cartao (id_cartao_nmr_cartao, vlr_saldo, id_usuario, ds_status)
                VALUES (%s, %s, %s, %s)
                """
                cursor_app.execute(sql_insert, (nr_cartao, vlr_saldo, id_usuario_app, ds_status))

            conn_app.commit()
            messagebox.showinfo("Sucesso", f"Cartão {nr_cartao} validado e sincronizado com sucesso!")
            
            self.entry_numero.delete(0, 'end')
            self.controller.mostrar_frame(TelaInicialFrame)

        except Error as e:
            messagebox.showerror("Erro", f"Erro ao salvar cartão no APP: {e}")
        finally:
            if conn_app.is_connected():
                cursor_app.close()
                conn_app.close()
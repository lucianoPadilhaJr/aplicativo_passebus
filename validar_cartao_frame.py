import tkinter as tk
from tkinter import messagebox
from database import get_db_connection
from mysql.connector import Error

class ValidarCartaoFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.id_usuario_logado_app = None
        self.configure(bg="#f5f5f5")

        tk.Label(
            self,
            text="Validação e Sincronização de Cartão",
            font=("Arial", 14, "bold"),
            bg="#f5f5f5"
        ).pack(pady=20)
        
        frame_meio = tk.Frame(self, bg="#f5f5f5")
        frame_meio.pack(pady=10, padx=40, fill="x")

        tk.Label(
            frame_meio, text="Número do Cartão:",
            font=("Arial", 12), bg="#f5f5f5"
        ).pack(pady=5)

        self.entry_numero = tk.Entry(frame_meio, font=("Arial", 12), width=30)
        self.entry_numero.pack(pady=6, fill="x")

        btn_validar = tk.Button(
            frame_meio, text="Validar e Sincronizar Cartão",
            font=("Arial", 12, "bold"), bg="#4CAF50", fg="white",
            command=self.validar_e_sincronizar, cursor="hand2"
        )
        btn_validar.pack(pady=15, fill="x")
        
        btn_voltar = tk.Button(
            frame_meio, text="Voltar ao Painel",
            font=("Arial", 10), bg="#6c757d", fg="white",
            command=self.voltar, cursor="hand2"
        )
        btn_voltar.pack(pady=5, fill="x")

    def voltar(self):
        from tela_inicial_frame import TelaInicialFrame
        self.controller.mostrar_frame(TelaInicialFrame)

    def definir_usuario_logado(self, id_usuario):
        """Define o usuário logado que veio do login."""
        self.id_usuario_logado_app = id_usuario

    def validar_e_sincronizar(self):
        numero_cartao = self.entry_numero.get().strip()

        if not (numero_cartao.isdigit() and len(numero_cartao) >= 5):
            messagebox.showerror("Erro", "Número do cartão inválido.")
            return

        if not self.id_usuario_logado_app:
            messagebox.showerror("Erro", "Usuário não logado. Reinicie o app.")
            return

        conn = get_db_connection()
        if not conn:
            messagebox.showerror("Erro", "Falha ao conectar no banco.")
            return

        try:
            cursor = conn.cursor(dictionary=True)

            # -------------------------------------------------------------
            # PASSO 1 → Buscar CPF do usuário logado (TABELA: tb_usuario_app)
            # -------------------------------------------------------------
            cursor.execute("""
                SELECT nr_cpf 
                FROM tb_usuario_app 
                WHERE id_usuario = %s
            """, (self.id_usuario_logado_app,))

            usuario_app = cursor.fetchone()

            if not usuario_app:
                messagebox.showerror("Erro", "Usuário logado não encontrado.")
                return

            cpf_usuario_app = usuario_app["nr_cpf"]

            # -------------------------------------------------------------
            # PASSO 2 → Buscar cartão na base da empresa
            # TABELAS corretas:
            #  - cartao_empresa
            #  - usuario_empresa
            #  - cartao_tipo_empresa
            # -------------------------------------------------------------
            sql_empresa = """
                SELECT 
                    c.id_cartao_nmr_cartao,
                    c.vlr_saldo,
                    c.id_usuario,
                    c.ds_status,
                    u.nr_cpf,
                    t.nome AS tipo_nome
                FROM cartao_empresa c
                INNER JOIN usuario_empresa u ON c.id_usuario = u.id_usuario
                INNER JOIN cartao_tipo_empresa t ON c.id_tipo = t.id_tipo
                WHERE c.id_cartao_nmr_cartao = %s
            """
            cursor.execute(sql_empresa, (numero_cartao,))
            cartao_dados = cursor.fetchone()

            if not cartao_dados:
                messagebox.showerror(
                    "Inválido",
                    "Cartão não encontrado na base da empresa."
                )
                return

            cpf_dono_cartao = cartao_dados["nr_cpf"]

            # -------------------------------------------------------------
            # PASSO 3 → Validação de segurança: CPF do app = CPF do cartão
            # -------------------------------------------------------------
            if cpf_usuario_app != cpf_dono_cartao:
                messagebox.showerror(
                    "Acesso Negado",
                    f"O cartão pertence ao CPF: {cpf_dono_cartao}.\n"
                    f"Seu CPF: {cpf_usuario_app}.\n"
                    "Só é permitido vincular cartões do mesmo titular."
                )
                return

            # -------------------------------------------------------------
            # PASSO 4 → Sincronizar com tb_cartao_app
            # -------------------------------------------------------------
            nr_cartao = cartao_dados["id_cartao_nmr_cartao"]
            vlr_saldo = cartao_dados["vlr_saldo"]
            ds_status = cartao_dados["ds_status"]
            tipo_cartao = cartao_dados["tipo_nome"]

            cursor.execute("""
                SELECT id_cartao_nmr_cartao 
                FROM tb_cartao_app 
                WHERE id_cartao_nmr_cartao = %s
            """, (nr_cartao,))

            existe = cursor.fetchone()

            if existe:
                cursor.execute("""
                    UPDATE tb_cartao_app
                    SET vlr_saldo=%s, id_usuario=%s, ds_status=%s, tipo_cartao=%s
                    WHERE id_cartao_nmr_cartao=%s
                """, (vlr_saldo, self.id_usuario_logado_app, ds_status, tipo_cartao, nr_cartao))
            else:
                cursor.execute("""
                    INSERT INTO tb_cartao_app
                    (id_cartao_nmr_cartao, vlr_saldo, id_usuario, ds_status, tipo_cartao)
                    VALUES (%s, %s, %s, %s, %s)
                """, (nr_cartao, vlr_saldo, self.id_usuario_logado_app, ds_status, tipo_cartao))

            conn.commit()

            messagebox.showinfo(
                "Sucesso",
                f"Cartão {nr_cartao} ({tipo_cartao}) sincronizado com sucesso!"
            )

            self.entry_numero.delete(0, "end")

            from tela_inicial_frame import TelaInicialFrame
            self.controller.mostrar_frame(TelaInicialFrame)

        except Error as e:
            messagebox.showerror("Erro", f"Erro no banco de dados: {e}")
        
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

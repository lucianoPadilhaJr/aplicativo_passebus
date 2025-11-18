# main.py
import tkinter as tk
from tkinter import font

# Importação das telas (Frames)
from interface_principal_frame import InterfacePrincipalFrame
from login_frame import LoginFrame
from cadastro_frame import CadastroFrame
from tela_inicial_frame import TelaInicialFrame
from validar_cartao_frame import ValidarCartaoFrame

# Utilitário para centralizar
from gui_utils import centralizar_janela

class AppPrincipal(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.title("PasseBus App")
        
        # Configuração da Janela
        self.largura_app = 450
        self.altura_app = 600
        self.geometry(f"{self.largura_app}x{self.altura_app}")
        
        # Tenta centralizar
        try:
            centralizar_janela(self, self.largura_app, self.altura_app)
        except Exception:
            pass # Se falhar, abre na posição padrão
            
        self.resizable(False, False) 
        
        # --- Dados Compartilhados (Sessão do Usuário) ---
        self.id_usuario_logado = None

        # --- Container Principal ---
        # É aqui que as telas são empilhadas
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # --- Dicionário para guardar as referências das telas ---
        self.frames = {}

        # Lista de todas as classes de tela
        telas_para_carregar = (
            InterfacePrincipalFrame, 
            LoginFrame, 
            CadastroFrame, 
            TelaInicialFrame, 
            ValidarCartaoFrame
        )

        # Cria todas as telas e as coloca no container
        for F in telas_para_carregar:
            frame = F(container, self)
            self.frames[F] = frame
            # sticky="nsew" faz o frame esticar para preencher o container
            frame.grid(row=0, column=0, sticky="nsew")

        # Mostra a primeira tela
        self.mostrar_frame(InterfacePrincipalFrame)

    def mostrar_frame(self, nome_frame_classe):
        """Traz o frame solicitado para a frente."""
        frame = self.frames[nome_frame_classe]
        
        # Lógica específica ao abrir certas telas
        if nome_frame_classe == TelaInicialFrame:
             # Se tiver método de atualizar, chama ele
             if hasattr(frame, 'atualizar_dados_usuario'):
                frame.atualizar_dados_usuario()
        
        if nome_frame_classe == ValidarCartaoFrame:
            if hasattr(frame, 'definir_usuario_logado'):
                frame.definir_usuario_logado(self.id_usuario_logado)

        frame.tkraise()
    
    def redefinir_para_login(self):
        """Função de Logout"""
        self.id_usuario_logado = None
        self.mostrar_frame(InterfacePrincipalFrame)

# --- ESTA PARTE É CRÍTICA PARA O APP ABRIR ---
if __name__ == "__main__":
    app = AppPrincipal()
    app.mainloop()
import tkinter as tk

class InterfacePrincipalFrame(tk.Frame):
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#f5f5f5")

        # Título
        tk.Label(self, text="Bem-vindo ao PasseBus", font=("Arial", 16, "bold"), bg="#f5f5f5").pack(pady=40)

        # Botões
        btn_cadastrar = tk.Button(
            self, text="Cadastrar",
            width=15, height=2,
            bg="#007BFF", fg="white",
            cursor="hand2",
            command=self.ir_para_cadastro
        )
        btn_cadastrar.pack(pady=10)

        btn_login = tk.Button(
            self, text="Login",
            width=15, height=2,
            bg="#28A745", fg="white",
            cursor="hand2",
            command=self.ir_para_login
        )
        btn_login.pack(pady=10)
    
    def ir_para_cadastro(self):
        from cadastro_frame import CadastroFrame
        self.controller.mostrar_frame(CadastroFrame)

    def ir_para_login(self):
        from login_frame import LoginFrame
        self.controller.mostrar_frame(LoginFrame)
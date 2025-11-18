# # gui_utils.py
from PIL import Image, ImageTk
from pathlib import Path
import os

def centralizar_janela(janela, largura, altura):
    """Centraliza uma janela (Tk ou Toplevel) na tela."""
    largura_tela = janela.winfo_screenwidth()
    altura_tela = janela.winfo_screenheight()
    pos_x = (largura_tela - largura) // 2
    pos_y = (altura_tela - altura) // 2
    janela.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")

def carregar_imagem_transparente(caminho, tamanho):
    """Carrega uma imagem com transparência (PNG) e a redimensiona."""
    try:
        # Garante que o caminho esteja correto, não importa de onde o script é chamado
        base_path = Path(__file__).parent
        caminho_completo = base_path / "assets" / "images" / caminho
        
        imagem = Image.open(caminho_completo)
        imagem = imagem.resize(tamanho, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(imagem)
    except Exception as e:
        print(f"Erro ao carregar imagem {caminho}: {e}")
        return None
import sys
import os
import customtkinter as ctk
from ui.app import NexusApp

def resource_path(relative_path):
    """ 
    Obtém o caminho absoluto para os recursos (como o ícone).
    Otimizado para a compilação nativa do Nuitka.
    """
    # No Nuitka, __file__ aponta corretamente para a pasta de extração em tempo de execução
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    # Inicializa o aplicativo principal que construímos em ui/app.py
    app = NexusApp()
    
    # Tratamento Profissional de Ícone
    icon_path = resource_path("icon.ico")
    if os.path.exists(icon_path):
        app.iconbitmap(icon_path)
    else:
        print(f"Aviso do Sistema: Arquivo de ícone não encontrado em {icon_path}")

    # Impede que o CustomTkinter redimensione elementos de forma esquisita no Windows
    ctk.set_widget_scaling(1.0)
    ctk.set_window_scaling(1.0)

    # Roda o loop da interface
    app.mainloop()
import customtkinter as ctk
from tkinter import filedialog
import os
from ui.help_window import HelpWindow 

# Configuração global de aparência (Minimalismo e Foco)
ctk.set_appearance_mode("Dark")  # Modo escuro para reduzir fadiga visual
ctk.set_default_color_theme("blue") 

class NexusApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("NexusRename - Gestão de Elite")
        self.geometry("900x650")
        self.minsize(800, 600)

        # 1. Criação do Header Superior
        self._build_header()

        # 2. Criação das Abas
        self._build_tabs()

    def _build_header(self):
        """Constrói a barra superior com título e botão de ajuda"""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 0)) # Margem apenas em cima e lados

        # Título decorativo à esquerda
        lbl_logo = ctk.CTkLabel(header_frame, text="NEXUS RENAME", font=("Segoe UI", 20, "bold"), text_color="#a0a0a0")
        lbl_logo.pack(side="left")

        # Botão de Ajuda à direita
        btn_help = ctk.CTkButton(
            header_frame, 
            text="? Ajuda", 
            width=80, 
            fg_color="#2b2b2b", 
            hover_color="#3d3d3d",
            command=self._open_help_window
        )
        btn_help.pack(side="right")

    def _open_help_window(self):
        """Garante que apenas uma janela de ajuda seja aberta por vez"""
        # Verifica se a janela já existe e está aberta
        if not hasattr(self, "help_window") or not self.help_window.winfo_exists():
            self.help_window = HelpWindow(self)
        else:
            self.help_window.focus()

    def _build_tabs(self):
        """Criação do sistema de Abas (Corrigido e separado)"""
        self.tabview = ctk.CTkTabview(self, corner_radius=10)
        self.tabview.pack(padx=20, pady=20, fill="both", expand=True)

        # Adicionando as duas únicas ferramentas
        self.tab_sync = self.tabview.add("Sincronizador (1:1)")
        self.tab_batch = self.tabview.add("Renomeação em Lote")

        self._build_sync_ui()
        self._build_batch_ui()

    def _build_sync_ui(self):
        """Interface da Aba 1: Sincronização Origem -> Destino"""
        # Título
        lbl_title = ctk.CTkLabel(self.tab_sync, text="Sincronizar Nomes entre Pastas", font=("Arial", 18, "bold"))
        lbl_title.pack(pady=(10, 20))

        # Inputs de Pasta
        self.path_origin = self._create_folder_input(self.tab_sync, "1. Pasta de Origem (Nomes Corretos):")
        self.path_dest = self._create_folder_input(self.tab_sync, "2. Pasta de Destino (Imagens Editadas):")

        # Botão de Ação Principal
        btn_start_sync = ctk.CTkButton(
            self.tab_sync, 
            text="Analisar e Sincronizar", 
            height=40,
            font=("Arial", 14, "bold"),
            command=self._run_sync_analysis
        )
        btn_start_sync.pack(pady=30)

    def _build_batch_ui(self):
        """Interface da Aba 2: Renomeação com Padrões"""
        lbl_title = ctk.CTkLabel(self.tab_batch, text="Renomeação Autônoma (Lote)", font=("Arial", 18, "bold"))
        lbl_title.pack(pady=(10, 20))

        # Input de Pasta Única
        self.path_batch = self._create_folder_input(self.tab_batch, "Pasta com as Imagens:")

        # Frame para os Padrões
        frame_pattern = ctk.CTkFrame(self.tab_batch, fg_color="transparent")
        frame_pattern.pack(fill="x", padx=40, pady=10)

        lbl_pattern = ctk.CTkLabel(frame_pattern, text="Padrão de Nome (Use ## para contagem, [DATA] para hoje):", anchor="w")
        lbl_pattern.pack(fill="x")
        
        self.entry_pattern = ctk.CTkEntry(frame_pattern, placeholder_text="Ex: Casamento_[DATA]_##")
        self.entry_pattern.pack(fill="x", pady=5)

        # Botão de Ação Principal
        btn_start_batch = ctk.CTkButton(
            self.tab_batch, 
            text="Aplicar Padrão", 
            height=40,
            fg_color="#A46B00", # Cor diferente para distinguir as ações
            hover_color="#825500",
            font=("Arial", 14, "bold"),
            command=self._run_batch_rename
        )
        btn_start_batch.pack(pady=30)

    def _create_folder_input(self, parent, label_text):
        """Componente reutilizável para seleção de pastas"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=40, pady=10)
        
        lbl = ctk.CTkLabel(frame, text=label_text, anchor="w")
        lbl.pack(fill="x")
        
        input_frame = ctk.CTkFrame(frame, fg_color="transparent")
        input_frame.pack(fill="x")
        
        entry = ctk.CTkEntry(input_frame)
        entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        btn = ctk.CTkButton(input_frame, text="Procurar...", width=80, command=lambda: self._browse_folder(entry))
        btn.pack(side="right")
        
        return entry

    def _browse_folder(self, entry_widget):
        folder = filedialog.askdirectory()
        if folder:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, folder)

    # --- Funções de Conexão com o Core ---
    def _run_sync_analysis(self):
        print("Iniciando análise de Sincronização...")

    def _run_batch_rename(self):
        print("Iniciando Renomeação em Lote...")

if __name__ == "__main__":
    app = NexusApp()
    app.mainloop()
import os
import customtkinter as ctk
from tkinter import filedialog, messagebox

# Importações dos Motores do Sistema
from ui.help_window import HelpWindow 
from ui.alignment_window import AlignmentWindow
from core.matcher import get_sequential_mapping
from core.renamer import execute_rename
from core.batch_generator import generate_batch_mapping
from utils.file_handler import get_valid_images
from utils.logger import create_rollback_log
from core.renamer import execute_rename, execute_rollback
from ui.preview_window import PreviewWindow
from ui.notifications import show_toast

# Configuração global de aparência (Minimalismo e Foco)
ctk.set_appearance_mode("Dark")
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
        """Constrói a barra superior com título e botão de ajuda/desfazer"""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 0))

        lbl_logo = ctk.CTkLabel(header_frame, text="NEXUS RENAME", font=("Segoe UI", 20, "bold"), text_color="#a0a0a0")
        lbl_logo.pack(side="left")

        # Botão de Ajuda (Já existia)
        btn_help = ctk.CTkButton(
            header_frame, text="? Ajuda", width=80, 
            fg_color="#2b2b2b", hover_color="#3d3d3d", command=self._open_help_window
        )
        btn_help.pack(side="right")

        # Botão de Desfazer (NOVO) - Cor vermelha para indicar alerta/emergência
        btn_undo = ctk.CTkButton(
            header_frame, text="↩️ Desfazer Ação", width=120, 
            fg_color="#8b0000", hover_color="#5a0000", command=self._run_rollback
        )
        btn_undo.pack(side="right", padx=(0, 10))

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

    # --- Funções de Conexão com o Core (Integração Final) ---
    def _run_sync_analysis(self):
        orig_folder = self.path_origin.get()
        dest_folder = self.path_dest.get()

        if not orig_folder or not dest_folder:
            show_toast(self, "Selecione as pastas primeiro!", "error")
            return

        try:
            # 1. Busca os arquivos
            orig_files = get_valid_images(orig_folder)
            dest_files = get_valid_images(dest_folder)
            
            # 2. Cria o mapeamento inicial (ZIP)
            # Garantimos que as listas tenham o mesmo tamanho para o preview
            max_len = max(len(orig_files), len(dest_files))
            while len(orig_files) < max_len: orig_files.append(None)
            while len(dest_files) < max_len: dest_files.append(None)
            
            initial_mapping = list(zip(orig_files, dest_files))
            
            # 3. Abre a TELA DE PREVIEW (Sua nova funcionalidade)
            PreviewWindow(self, initial_mapping, self._execute_and_log)
            
        except Exception as e:
            show_toast(self, f"Erro na análise: {str(e)}", "error")

    def _run_batch_rename(self):
        batch_folder = self.path_batch.get()
        pattern = self.entry_pattern.get()

        if not batch_folder or not pattern:
            messagebox.showwarning("Aviso", "Por favor, selecione a pasta e digite o padrão desejado.")
            return

        try:
            files = get_valid_images(batch_folder)
            if not files:
                messagebox.showinfo("Aviso", "Nenhuma imagem válida encontrada nesta pasta.")
                return
                
            mapping = generate_batch_mapping(files, pattern)
            self._execute_and_log(mapping)
            
        except Exception as e:
            messagebox.showerror("Erro Crítico", f"Falha ao gerar o lote: {str(e)}")

    def _execute_and_log(self, mapping):
        """Função unificada de Elite: Renomeia, gera log de segurança e mostra o relatório"""
        if not mapping:
            return
            
        # Executa fisicamente no sistema operacional
        results = execute_rename(mapping)
        
        # Filtra apenas os que não foram "Pulados" (None) para gerar o histórico de rollback
        successful_pairs = [(old, new) for old, new in mapping if old is not None and new is not None]
        log_file = create_rollback_log(successful_pairs)

        # Constrói o Relatório Final para o Usuário
        msg = (
            f"Operação Concluída com Sucesso!\n\n"
            f"✅ Renomeados: {results['success']}\n"
            f"⏭️ Pulados: {results['skipped']}\n"
            f"❌ Erros: {len(results['errors'])}"
        )
        
        if log_file:
            msg += f"\n\nLog de Segurança (Rollback) salvo em:\n{log_file}"
            
        if results['errors']:
            msg += f"\n\nPrimeiro erro registrado: {results['errors'][0]}"
            
        messagebox.showinfo("Relatório de Sincronização", msg)

    def _run_rollback(self):
        """Abre o seletor para escolher um log antigo e reverter as mudanças"""
        # Abre o explorador na pasta de logs do projeto
        log_dir = os.path.join(os.getcwd(), "logs")
        if not os.path.exists(log_dir):
            messagebox.showinfo("Aviso", "Nenhum histórico de renomeação encontrado.")
            return

        file_path = filedialog.askopenfilename(
            initialdir=log_dir,
            title="Selecione o arquivo de Backup (Log)",
            filetypes=(("Arquivos JSON", "*.json"), ("Todos os arquivos", "*.*"))
        )

        if not file_path:
            return # Usuário cancelou a seleção

        resposta = messagebox.askyesno("Confirmar Reversão", "Isso fará os arquivos voltarem aos nomes originais gravados neste log. Deseja continuar?")
        if resposta:
            results = execute_rollback(file_path)
            
            msg = f"Reversão Concluída!\n\n✅ Restaurados: {results['success']}\n❌ Erros: {len(results['errors'])}"
            if results['errors']:
                msg += f"\n\nPrimeiro erro: {results['errors'][0]}"
                messagebox.showwarning("Atenção", msg)
            else:
                messagebox.showinfo("Sucesso", msg)

if __name__ == "__main__":
    app = NexusApp()
    app.mainloop()
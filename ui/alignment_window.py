import customtkinter as ctk
from pathlib import Path

class AlignmentWindow(ctk.CTkToplevel):
    def __init__(self, master, origin_files: list[Path], dest_files: list[Path], on_confirm):
        super().__init__(master)
        self.title("NexusRename - Alinhamento Manual")
        self.geometry("800x600")
        self.attributes("-topmost", True) # Mantém a janela no topo
        
        self.origin_files = origin_files
        self.dest_items = list(dest_files) # Pode conter Path ou None
        self.on_confirm = on_confirm
        
        # Garante que a lista de destino tenha no mínimo o mesmo tamanho da origem
        while len(self.dest_items) < len(self.origin_files):
            self.dest_items.append(None)

        self.drag_start_index = None

        self._build_header()
        self._build_scrollable_frame()
        self._render_list()

    def _build_header(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=10)

        title = ctk.CTkLabel(header_frame, text="Alinhe os arquivos (Origem -> Destino)", font=("Arial", 16, "bold"))
        title.pack(side="left")

        # Seletor de Modo (Arrastar como Padrão)
        self.mode_var = ctk.StringVar(value="Arrastar e Soltar")
        self.mode_selector = ctk.CTkSegmentedButton(
            header_frame, 
            values=["Arrastar e Soltar", "Inserir Espaços"],
            variable=self.mode_var,
            command=self._on_mode_change
        )
        self.mode_selector.pack(side="right")

    def _build_scrollable_frame(self):
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Grid layout para alinhamento perfeito (2 colunas)
        self.scroll_frame.grid_columnconfigure(0, weight=1)
        self.scroll_frame.grid_columnconfigure(1, weight=1)

        # Rodapé com botão de confirmação
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=20, pady=10)
        
        btn_confirm = ctk.CTkButton(
            footer, 
            text="Confirmar Alinhamento", 
            fg_color="green", 
            hover_color="darkgreen",
            command=self._confirm_and_close
        )
        btn_confirm.pack(side="right")

    def _on_mode_change(self, value):
        self._render_list() # Redesenha a lista com as ferramentas do novo modo

    def _render_list(self):
        # Limpa o frame antes de redesenhar
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        mode = self.mode_var.get()

        for i in range(len(self.origin_files)):
            # Coluna Esquerda: Origem (Fixa)
            orig_name = self.origin_files[i].name if i < len(self.origin_files) else "---"
            orig_lbl = ctk.CTkLabel(self.scroll_frame, text=orig_name, anchor="w", fg_color="#2b2b2b", corner_radius=6)
            orig_lbl.grid(row=i, column=0, sticky="ew", padx=5, pady=5, ipady=5)

            # Coluna Direita: Destino (Interativa)
            dest_item = self.dest_items[i] if i < len(self.dest_items) else None
            dest_name = dest_item.name if dest_item else "[ ESPAÇO VAZIO / PULAR ]"
            dest_color = "#1f538d" if dest_item else "#8b0000" # Azul para arquivo, Vermelho escuro para vazio

            dest_frame = ctk.CTkFrame(self.scroll_frame, fg_color=dest_color, corner_radius=6)
            dest_frame.grid(row=i, column=1, sticky="ew", padx=5, pady=5)
            
            dest_lbl = ctk.CTkLabel(dest_frame, text=dest_name, anchor="w")
            dest_lbl.pack(side="left", padx=10, pady=5, fill="x", expand=True)

            # Comportamento: Inserir Espaços
            if mode == "Inserir Espaços":
                btn_space = ctk.CTkButton(dest_frame, text="+ Vazio", width=60, command=lambda idx=i: self._insert_space(idx))
                btn_space.pack(side="right", padx=5, pady=2)
                
                if dest_item is None:
                    btn_remove = ctk.CTkButton(dest_frame, text="Remover", width=60, fg_color="red", command=lambda idx=i: self._remove_space(idx))
                    btn_remove.pack(side="right", padx=5, pady=2)

            # Comportamento: Arrastar e Soltar (Simulado via eventos de mouse)
            elif mode == "Arrastar e Soltar":
                dest_lbl.bind("<Button-1>", lambda event, idx=i: self._drag_start(idx))
                dest_lbl.bind("<B1-Motion>", self._drag_motion)
                dest_lbl.bind("<ButtonRelease-1>", lambda event, idx=i: self._drag_drop(event, idx))
                dest_lbl.configure(cursor="hand2")

    def _insert_space(self, index):
        self.dest_items.insert(index, None)
        self._render_list()

    def _remove_space(self, index):
        if self.dest_items[index] is None:
            self.dest_items.pop(index)
            self._render_list()

    def _drag_start(self, index):
        self.drag_start_index = index

    def _drag_motion(self, event):
        # Feedback visual opcional poderia ir aqui, mas mantemos minimalista para performance
        pass

    def _drag_drop(self, event, drop_index):
        if self.drag_start_index is not None and self.drag_start_index != drop_index:
            # Move o item na lista virtual
            item = self.dest_items.pop(self.drag_start_index)
            self.dest_items.insert(drop_index, item)
            self._render_list()
        self.drag_start_index = None

    def _confirm_and_close(self):
        # Monta o mapping final exigido pelo renamer.py
        mapping = []
        for i in range(len(self.origin_files)):
            orig = self.origin_files[i]
            dest = self.dest_items[i] if i < len(self.dest_items) else None
            
            dest_str = str(dest) if dest else None
            # O novo nome será baseado na pasta do destino + nome da origem
            if dest:
                new_dest_str = str(dest.parent / orig.name)
            else:
                new_dest_str = None
                
            mapping.append((dest_str, new_dest_str))
            
        self.on_confirm(mapping)
        self.destroy()
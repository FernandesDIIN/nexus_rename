import customtkinter as ctk
from pathlib import Path

class AlignmentWindow(ctk.CTkToplevel):
    def __init__(self, master, origin_files: list[Path], dest_files: list[Path], on_confirm):
        super().__init__(master)
        self.title("NexusRename - Alinhamento Manual")
        self.geometry("800x600")
        self.attributes("-topmost", True)
        
        self.origin_files = origin_files
        self.dest_items = list(dest_files)
        self.on_confirm = on_confirm
        
        while len(self.dest_items) < len(self.origin_files):
            self.dest_items.append(None)

        self.selected_indices = set()
        self.checkboxes = []

        self._build_header()
        self._build_scrollable_frame()
        self._render_list()

    def _build_header(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=10)

        title = ctk.CTkLabel(header_frame, text="Alinhe os arquivos (Marque 2 para trocar)", font=("Arial", 16, "bold"))
        title.pack(side="left")

        self.btn_swap = ctk.CTkButton(
            header_frame, text="Trocar Selecionados", fg_color="#f59e0b", hover_color="#d97706",
            command=self._swap_selected, state="disabled"
        )
        self.btn_swap.pack(side="right", padx=10)

        btn_confirm = ctk.CTkButton(
            header_frame, text="Confirmar Alinhamento", fg_color="green", hover_color="darkgreen",
            command=self._confirm_and_close
        )
        btn_confirm.pack(side="right", padx=10)

    def _build_scrollable_frame(self):
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.scroll_frame.grid_columnconfigure(0, weight=1)
        self.scroll_frame.grid_columnconfigure(1, weight=1)

    def _render_list(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        self.checkboxes = []
        self.selected_indices = set()
        self.btn_swap.configure(state="disabled")

        for i in range(len(self.origin_files)):
            # Coluna Origem (fixa)
            orig_name = self.origin_files[i].name if i < len(self.origin_files) else "---"
            orig_lbl = ctk.CTkLabel(self.scroll_frame, text=orig_name, anchor="w", fg_color="#2b2b2b", corner_radius=6)
            orig_lbl.grid(row=i, column=0, sticky="ew", padx=5, pady=5, ipady=5)

            # Coluna Destino
            dest_item = self.dest_items[i] if i < len(self.dest_items) else None
            dest_name = dest_item.name if dest_item else "[ ESPAÇO VAZIO / PULAR ]"
            dest_color = "#1f538d" if dest_item else "#8b0000"

            dest_frame = ctk.CTkFrame(self.scroll_frame, fg_color=dest_color, corner_radius=6)
            dest_frame.grid(row=i, column=1, sticky="ew", padx=5, pady=5)
            
            dest_lbl = ctk.CTkLabel(dest_frame, text=dest_name, anchor="w")
            dest_lbl.pack(side="left", padx=10, pady=5, fill="x", expand=True)

            if dest_item is not None:
                # Checkbox de seleção
                var = ctk.BooleanVar(value=False)
                cb = ctk.CTkCheckBox(dest_frame, text="", variable=var, width=25,
                                     command=lambda idx=i, v=var: self._toggle_selection(idx, v))
                cb.pack(side="right", padx=5, pady=2)
                self.checkboxes.append((i, var))
            else:
                # Espaço vazio: botões de inserir / remover
                btn_space = ctk.CTkButton(dest_frame, text="+ Vazio", width=60,
                                          command=lambda idx=i: self._insert_space(idx))
                btn_space.pack(side="right", padx=5, pady=2)
                btn_remove = ctk.CTkButton(dest_frame, text="Remover", width=60, fg_color="red",
                                           command=lambda idx=i: self._remove_space(idx))
                btn_remove.pack(side="right", padx=5, pady=2)

    def _toggle_selection(self, index, var):
        if var.get():
            if len(self.selected_indices) >= 2:
                var.set(False)
                return
            self.selected_indices.add(index)
        else:
            self.selected_indices.discard(index)

        self.btn_swap.configure(state="normal" if len(self.selected_indices) == 2 else "disabled")

    def _swap_selected(self):
        if len(self.selected_indices) != 2:
            return
        idx1, idx2 = sorted(self.selected_indices)
        self.dest_items[idx1], self.dest_items[idx2] = self.dest_items[idx2], self.dest_items[idx1]
        self.selected_indices.clear()
        self._render_list()

    def _insert_space(self, index):
        self.dest_items.insert(index, None)
        self._render_list()

    def _remove_space(self, index):
        if self.dest_items[index] is None:
            self.dest_items.pop(index)
            self._render_list()

    def _confirm_and_close(self):
        mapping = []
        for i in range(len(self.origin_files)):
            orig = self.origin_files[i]
            dest = self.dest_items[i] if i < len(self.dest_items) else None
            dest_str = str(dest) if dest else None
            if dest:
                new_dest_str = str(dest.parent / orig.name)
            else:
                new_dest_str = None
            mapping.append((dest_str, new_dest_str))
        self.on_confirm(mapping)
        self.destroy()

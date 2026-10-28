import os
import queue
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import customtkinter as ctk
from PIL import Image, ImageOps
from tkinter import messagebox

from core.alignment import AlignmentModel


THUMBNAIL_SIZE = (160, 120)


def load_thumbnail(path: str | Path, size=THUMBNAIL_SIZE) -> Image.Image:
    """Decode an image efficiently outside Tk's main thread."""
    with Image.open(path) as image:
        # draft() lets JPEG decoders avoid materializing every full-resolution pixel.
        image.draft("RGB", size)
        image.thumbnail(size, Image.Resampling.LANCZOS, reducing_gap=3.0)
        image = ImageOps.exif_transpose(image)
        image.thumbnail(size, Image.Resampling.LANCZOS, reducing_gap=3.0)
        return image.convert("RGB").copy()


class PreviewWindow(ctk.CTkToplevel):
    """Responsive visual aligner with cached, asynchronous thumbnails."""

    def __init__(self, master, mapping_data, on_confirm):
        super().__init__(master)
        self.title("Revisão e Alinhamento Visual")
        self.geometry("980x650")
        self.minsize(800, 520)
        self.grab_set()

        self.model = AlignmentModel(mapping_data)
        self.on_confirm = on_confirm
        self.selected_indices: set[int] = set()
        self.destination_widgets = {}
        self.image_labels: dict[tuple[int, int], ctk.CTkLabel] = {}
        self.tk_images: dict[tuple[int, int], ctk.CTkImage] = {}
        self.thumbnail_cache: dict[str, Image.Image | None] = {}
        self.thumbnail_consumers: dict[str, set[tuple[int, int]]] = {}
        self.widget_paths: dict[tuple[int, int], str] = {}
        self.loading_paths: set[str] = set()
        self.thumbnail_results: queue.Queue = queue.Queue()
        self.executor = ThreadPoolExecutor(max_workers=min(8, (os.cpu_count() or 4)))
        self._closed = False

        self._setup_ui()
        self._render_rows()
        self._poll_thumbnail_results()
        self.protocol("WM_DELETE_WINDOW", self._close)
        self.bind("<Control-Return>", lambda _event: self._finalize())
        self.bind("<Control-z>", lambda _event: self._undo_swap())
        self.bind("<Escape>", lambda _event: self._close())

    def _setup_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(12, 4))

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(
            title_box,
            text="Alinhamento rápido",
            font=("Segoe UI", 17, "bold"),
            anchor="w",
        ).pack(fill="x")
        ctk.CTkLabel(
            title_box,
            text=f"{len(self.model)} pares • marque duas editadas para trocar • Ctrl+Z desfaz",
            text_color="#a0a0a0",
            anchor="w",
        ).pack(fill="x")

        self.btn_undo = ctk.CTkButton(
            header,
            text="Desfazer troca",
            width=110,
            state="disabled",
            fg_color="#444444",
            command=self._undo_swap,
        )
        self.btn_undo.pack(side="right", padx=5)
        self.btn_swap = ctk.CTkButton(
            header,
            text="Trocar selecionadas",
            width=135,
            state="disabled",
            fg_color="#f59e0b",
            hover_color="#d97706",
            command=self._swap_selected,
        )
        self.btn_swap.pack(side="right", padx=5)
        ctk.CTkButton(
            header,
            text="Confirmar",
            width=100,
            fg_color="#28a745",
            hover_color="#1e7e34",
            command=self._finalize,
        ).pack(side="right", padx=5)

        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.scroll_frame.grid_columnconfigure((0, 1), weight=1, uniform="images")
        self.scroll_frame.grid_columnconfigure(2, weight=0)

    def _render_rows(self):
        for index in range(len(self.model)):
            origin, destination = self.model.pair(index)
            self._create_image_card(index, 0, origin, "REFERÊNCIA (NOME)")
            self._create_destination_card(index, destination)
            self._create_result_info(index, origin)

    def _create_image_card(self, row, column, path, label_text):
        card = ctk.CTkFrame(
            self.scroll_frame,
            fg_color="#1a1a1a" if not path else "#2b2b2b",
            corner_radius=8,
        )
        card.grid(row=row, column=column, padx=8, pady=5, sticky="nsew")
        ctk.CTkLabel(
            card,
            text=label_text,
            font=("Segoe UI", 10, "bold"),
            text_color="#a0a0a0",
        ).pack(pady=(5, 0))
        image_label = ctk.CTkLabel(card, text="Carregando…" if path else "[ VAZIO ]", height=120)
        image_label.pack(pady=5, padx=10)
        name_label = ctk.CTkLabel(card, text=path.name if path else "---", font=("Consolas", 11))
        name_label.pack(pady=(0, 5))
        self.image_labels[(row, column)] = image_label
        self._set_thumbnail(row, column, path)
        return card, image_label, name_label

    def _create_destination_card(self, row, path):
        card, image_label, name_label = self._create_image_card(
            row, 1, path, "EDITADA (SELECIONAR)"
        )
        selection = ctk.BooleanVar(value=False)
        checkbox = ctk.CTkCheckBox(
            card,
            text="Selecionar",
            variable=selection,
            command=lambda idx=row, var=selection: self._toggle_selection(idx, var),
        )
        checkbox.pack(pady=(0, 5))
        if not path:
            checkbox.configure(state="disabled")
        self.destination_widgets[row] = {
            "card": card,
            "image": image_label,
            "name": name_label,
            "checkbox": checkbox,
            "variable": selection,
        }

    def _create_result_info(self, row, origin):
        frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        frame.grid(row=row, column=2, padx=8, pady=10)
        ctk.CTkLabel(
            frame,
            text="➔ NOVO NOME",
            font=("Segoe UI", 9, "bold"),
            text_color="#A46B00",
        ).pack()
        ctk.CTkLabel(
            frame,
            text=origin.name if origin else "N/A",
            font=("Segoe UI", 11, "bold"),
            wraplength=140,
        ).pack()

    def _set_thumbnail(self, row, column, path):
        key = (row, column)
        label = self.image_labels[key]
        previous_path = self.widget_paths.pop(key, None)
        if previous_path:
            self.thumbnail_consumers.get(previous_path, set()).discard(key)
        if not path:
            self._clear_thumbnail(key, label)
            label.configure(text="[ VAZIO / PULAR ]", text_color="#d66a6a")
            return
        cache_key = str(path)
        self.widget_paths[key] = cache_key
        self.thumbnail_consumers.setdefault(cache_key, set()).add(key)
        if cache_key in self.thumbnail_cache:
            image = self.thumbnail_cache[cache_key]
            if image is None:
                self._clear_thumbnail(key, label)
                label.configure(text="⚠ Não foi possível abrir", text_color="#d66a6a")
            else:
                tk_image = ctk.CTkImage(
                    light_image=image,
                    dark_image=image,
                    size=image.size,
                )
                # Keep the previous PhotoImage alive until Tk has attached the new one.
                label.configure(image=tk_image, text="")
                self.tk_images[key] = tk_image
            return
        self._clear_thumbnail(key, label)
        label.configure(text="Carregando…", text_color="#a0a0a0")
        if cache_key not in self.loading_paths:
            self.loading_paths.add(cache_key)
            future = self.executor.submit(load_thumbnail, path)
            future.add_done_callback(
                lambda task, item=cache_key: self.thumbnail_results.put((item, task))
            )

    def _clear_thumbnail(self, key, label):
        old_image = self.tk_images.get(key)
        label.configure(image=None)
        # CustomTkinter 5.2 keeps the previous native Tk image when assigned None.
        label._label.configure(image="")
        self.tk_images.pop(key, None)
        del old_image

    def _poll_thumbnail_results(self):
        if self._closed:
            return
        while True:
            try:
                cache_key, future = self.thumbnail_results.get_nowait()
            except queue.Empty:
                break
            self.loading_paths.discard(cache_key)
            try:
                self.thumbnail_cache[cache_key] = future.result()
            except Exception:
                self.thumbnail_cache[cache_key] = None
            for row, column in tuple(self.thumbnail_consumers.get(cache_key, ())):
                if self.widget_paths.get((row, column)) == cache_key:
                    self._set_thumbnail(row, column, Path(cache_key))
        self.after(30, self._poll_thumbnail_results)

    def _toggle_selection(self, index, variable):
        if variable.get():
            if len(self.selected_indices) >= 2:
                variable.set(False)
                return
            self.selected_indices.add(index)
        else:
            self.selected_indices.discard(index)
        self.btn_swap.configure(
            state="normal" if len(self.selected_indices) == 2 else "disabled"
        )

    def _refresh_destination(self, index):
        destination = self.model.destinations[index]
        widgets = self.destination_widgets[index]
        widgets["name"].configure(text=destination.name if destination else "---")
        widgets["variable"].set(False)
        widgets["checkbox"].configure(state="normal" if destination else "disabled")
        self._set_thumbnail(index, 1, destination)

    def _swap_selected(self):
        if len(self.selected_indices) != 2:
            return
        first, second = sorted(self.selected_indices)
        self.model.swap(first, second)
        self.selected_indices.clear()
        self._refresh_destination(first)
        self._refresh_destination(second)
        self.btn_swap.configure(state="disabled")
        self.btn_undo.configure(state="normal")

    def _undo_swap(self):
        changed = self.model.undo()
        if not changed:
            return
        for index in changed:
            self._refresh_destination(index)
        self.selected_indices.clear()
        self.btn_swap.configure(state="disabled")
        self.btn_undo.configure(state="normal" if self.model.can_undo else "disabled")

    def _finalize(self):
        final_mapping = self.model.final_mapping()
        if not final_mapping:
            messagebox.showwarning(
                "Nada para renomear",
                "Alinhe ao menos uma imagem editada antes de confirmar.",
                parent=self,
            )
            return
        self._close()
        self.on_confirm(final_mapping)

    def _close(self):
        if self._closed:
            return
        self._closed = True
        self.executor.shutdown(wait=False, cancel_futures=True)
        self.grab_release()
        self.destroy()


class BatchPreviewWindow(ctk.CTkToplevel):
    """Compact preview for batch renaming."""

    def __init__(self, master, mapping, on_confirm):
        super().__init__(master)
        self.title("Pré-visualização da Renomeação em Lote")
        self.geometry("680x500")
        self.grab_set()
        self.mapping = mapping
        self.on_confirm = on_confirm
        self._build_ui()
        self.bind("<Control-Return>", lambda _event: self._confirm())
        self.bind("<Escape>", lambda _event: self.destroy())

    def _build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(
            header,
            text=f"Confira {len(self.mapping)} novos nomes",
            font=("Segoe UI", 16, "bold"),
        ).pack(side="left")
        ctk.CTkButton(
            header,
            text="Aplicar",
            fg_color="#28a745",
            hover_color="#1e7e34",
            command=self._confirm,
        ).pack(side="right")
        ctk.CTkButton(
            header,
            text="Cancelar",
            fg_color="#8b0000",
            hover_color="#5a0000",
            command=self.destroy,
        ).pack(side="right", padx=5)

        table = ctk.CTkScrollableFrame(self)
        table.pack(fill="both", expand=True, padx=20, pady=10)
        table.grid_columnconfigure((0, 1), weight=1)
        for column, title in enumerate(("Nome atual", "Novo nome")):
            ctk.CTkLabel(
                table,
                text=title,
                font=("Segoe UI", 12, "bold"),
                fg_color="#2b2b2b",
                corner_radius=6,
                anchor="w",
                padx=10,
            ).grid(row=0, column=column, sticky="ew", pady=2)
        for row, (original, target) in enumerate(self.mapping, start=1):
            ctk.CTkLabel(table, text=os.path.basename(original), anchor="w", padx=10).grid(
                row=row, column=0, sticky="ew", pady=1
            )
            ctk.CTkLabel(table, text=os.path.basename(target), anchor="w", padx=10).grid(
                row=row, column=1, sticky="ew", pady=1
            )

    def _confirm(self):
        self.destroy()
        self.on_confirm(self.mapping)

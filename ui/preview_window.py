import customtkinter as ctk
from PIL import Image, ImageTk
import os

class PreviewWindow(ctk.CTkToplevel):
    def __init__(self, master, mapping_data, on_confirm):
        super().__init__(master)
        self.title("NexusRename - Revisão Visual de Elite")
        self.geometry("1100x800")
        self.grab_set()
        
        self.mapping = list(mapping_data)
        self.on_confirm = on_confirm
        self.temp_images = [] # Cache para evitar que o Garbage Collector apague as fotos

        self._setup_ui()
        self._render_preview()

    def _setup_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=15)
        
        lbl_info = ctk.CTkLabel(
            header, 
            text="Verificação de Identidade Visual", 
            font=("Segoe UI", 20, "bold")
        )
        lbl_info.pack(side="left")

        btn_run = ctk.CTkButton(
            header, 
            text="CONFIRMAR E RENOMEAR", 
            fg_color="#28a745", 
            hover_color="#1e7e34",
            font=("Segoe UI", 14, "bold"),
            command=self._finalize
        )
        btn_run.pack(side="right")

        # Container principal
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Colunas: [ Origem ] [ Destino ] [ Resultado Final ]
        self.scroll_frame.grid_columnconfigure((0, 1), weight=2)
        self.scroll_frame.grid_columnconfigure(2, weight=1)

    def _render_preview(self):
        # Limpa e reseta cache de imagens
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        self.temp_images = []

        for i, (orig_path, dest_path) in enumerate(self.mapping):
            # Coluna 0: Imagem de Origem (Referência de Nome)
            self._create_image_card(i, 0, orig_path, "REFERÊNCIA (NOME)")
            
            # Coluna 1: Imagem de Destino (Arquivo Editado)
            self._create_image_card(i, 1, dest_path, "EDITADA (DESTINO)")
            
            # Coluna 2: Seta e Nome Final
            self._create_result_info(i, 2, orig_path)

    def _create_image_card(self, row, col, path, label_text):
        card = ctk.CTkFrame(self.scroll_frame, fg_color="#2b2b2b", corner_radius=10)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Label de Título do Card
        ctk.CTkLabel(card, text=label_text, font=("Segoe UI", 10, "bold"), text_color="#a0a0a0").pack(pady=(5,0))

        # Motor de Renderização de Thumbnail
        img_label = ctk.CTkLabel(card, text="") # Container da imagem
        
        if path and os.path.exists(path):
            try:
                # Carrega a imagem e redimensiona para o thumbnail
                pil_img = Image.open(path)
                # Mantém a proporção (aspect ratio)
                pil_img.thumbnail((200, 150)) 
                
                # Converte para o formato do CustomTkinter
                ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=pil_img.size)
                
                img_label.configure(image=ctk_img)
                self.temp_images.append(ctk_img) # Mantém a referência viva
            except Exception as e:
                img_label.configure(text="⚠️ Erro ao carregar imagem")
        else:
            img_label.configure(text="[ VAZIO / PULADO ]", text_color="#8b0000")

        img_label.pack(pady=10, padx=10)
        
        # Nome do arquivo embaixo da foto
        file_name = os.path.basename(path) if path else "---"
        ctk.CTkLabel(card, text=file_name, font=("Consolas", 11), wraplength=180).pack(pady=(0, 10))

    def _create_result_info(self, row, col, orig_path):
        frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        frame.grid(row=row, column=col, sticky="center")
        
        new_name = os.path.basename(orig_path) if orig_path else "N/A"
        
        ctk.CTkLabel(frame, text="➔ NOVO NOME:", font=("Segoe UI", 10, "bold"), text_color="#A46B00").pack()
        ctk.CTkLabel(frame, text=new_name, font=("Segoe UI", 12, "bold"), wraplength=150).pack()

    def _finalize(self):
        final_mapping = []
        for orig, dest in self.mapping:
            if orig and dest:
                # O caminho final será na pasta de destino com o nome da origem
                dest_dir = os.path.dirname(dest)
                new_path = os.path.join(dest_dir, os.path.basename(orig))
                final_mapping.append((str(dest), str(new_path)))
        
        self.on_confirm(final_mapping)
        self.destroy()
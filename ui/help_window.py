import customtkinter as ctk

class HelpWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("NexusRename - Guia do Usuário")
        self.geometry("650x550")
        self.minsize(600, 500)
        
        # Faz a janela aparecer focada e bloqueia cliques na janela principal (Modal)
        self.grab_set()
        self.attributes("-topmost", True)

        self._build_content()

    def _build_content(self):
        # Área de Rolagem para o texto não ficar espremido
        scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Cabeçalho
        self._add_heading(scroll_frame, "📚 Como usar o NexusRename", 22)
        self._add_paragraph(scroll_frame, "O NexusRename é uma ferramenta de elite para gestão e sincronização de nomes de arquivos em lote. Abaixo, entenda como cada módulo funciona.")

        # Seção 1: Sincronizador Seguro
        self._add_heading(scroll_frame, "🔄 Sincronizador (1:1)", 18)
        sync_text = (
            "Uso ideal: Quando você exporta imagens de um editor, perde os nomes originais, e "
            "precisa devolver os nomes exatos para as imagens editadas.\n\n"
            "• Regra de Ouro: A ordem de leitura é alfabética na Origem e por Data de Criação no Destino.\n"
            "• Prevenção de Erros: Se houver quantidade diferente de imagens entre as pastas, o sistema "
            "abrirá a 'Janela de Alinhamento'.\n"
            "• Na Janela de Alinhamento: Você pode arrastar as imagens para casar com os nomes corretos, "
            "ou usar o botão '+ Vazio' para pular imagens que não foram editadas."
        )
        self._add_paragraph(scroll_frame, sync_text)

        # Seção 2: Renomeação em Lote
        self._add_heading(scroll_frame, "⚡ Renomeação Autônoma (Lote)", 18)
        batch_text = (
            "Uso ideal: Para padronizar uma pasta inteira com nomes sequenciais profissionais.\n\n"
            "Códigos Suportados no Padrão:\n"
            "• # : Numeração simples (1, 2, 3...)\n"
            "• ## : Numeração com zero à esquerda (01, 02... 10)\n"
            "• ### : Numeração em centenas (001, 002... 100)\n"
            "• [NOME] : Mantém o nome original da imagem.\n"
            "• [DATA] : Insere a data de hoje (Ex: 20260418)."
        )
        self._add_paragraph(scroll_frame, batch_text)
        
        # Exemplo de uso (Caixa de destaque)
        example_box = ctk.CTkTextbox(scroll_frame, height=60, fg_color="#2b2b2b", text_color="#A46B00")
        example_box.pack(fill="x", pady=(5, 15))
        example_box.insert("0.0", "Exemplo: Se você digitar '[DATA]_Projeto_##'\nO resultado será: '20260418_Projeto_01.jpg'")
        example_box.configure(state="disabled") # Bloqueia digitação, apenas leitura

        # Rodapé / Créditos Open Source
        self._add_heading(scroll_frame, "⚙️ Sobre o Projeto", 16)
        credits_text = (
            "Versão: 1.0.0\n"
            "Desenvolvido para a comunidade Open Source.\n"
            "Se encontrou um bug ou tem sugestões, visite o repositório no GitHub."
        )
        self._add_paragraph(scroll_frame, credits_text)

        # Botão Fechar
        btn_close = ctk.CTkButton(self, text="Entendi, Fechar", command=self.destroy, fg_color="#1f538d")
        btn_close.pack(pady=(0, 20))

    def _add_heading(self, parent, text, size):
        lbl = ctk.CTkLabel(parent, text=text, font=("Segoe UI", size, "bold"), anchor="w", justify="left")
        lbl.pack(fill="x", pady=(20, 5))

    def _add_paragraph(self, parent, text):
        lbl = ctk.CTkLabel(parent, text=text, font=("Segoe UI", 13), anchor="w", justify="left", wraplength=550)
        lbl.pack(fill="x", pady=(0, 10))
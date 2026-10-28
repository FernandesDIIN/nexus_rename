import os
import shutil
from datetime import datetime
from pathlib import Path
import customtkinter as ctk
from tkinter import filedialog, messagebox
from itertools import zip_longest

from ui.help_window import HelpWindow 
from ui.preview_window import PreviewWindow, BatchPreviewWindow
from core.renamer import execute_rename, execute_rollback
from core.batch_generator import generate_batch_mapping
from utils.file_handler import get_valid_images
from utils.logger import create_rollback_log
from ui.notifications import show_toast

# Configuração global de aparência
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue") 

class NexusApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("NexusRename")
        # 1. Ajuste de Tamanho (Mais compacto e direto)
        self.geometry("760x620")
        self.minsize(700, 560)

        self._build_header()
        self._build_tabs()

    def _build_header(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(15, 0))

        lbl_logo = ctk.CTkLabel(header_frame, text="NEXUS RENAME", font=("Segoe UI", 18, "bold"), text_color="#a0a0a0")
        lbl_logo.pack(side="left")

        btn_help = ctk.CTkButton(header_frame, text="? Ajuda", width=80, fg_color="#2b2b2b", hover_color="#3d3d3d", command=self._open_help_window)
        btn_help.pack(side="right")

        btn_undo = ctk.CTkButton(header_frame, text="↩ Desfazer última", width=125, fg_color="#8b0000", hover_color="#5a0000", command=self._run_rollback)
        btn_undo.pack(side="right", padx=(0, 10))

    def _open_help_window(self):
        if not hasattr(self, "help_window") or not self.help_window.winfo_exists():
            self.help_window = HelpWindow(self)
        else:
            self.help_window.focus()

    def _build_tabs(self):
        self.tabview = ctk.CTkTabview(self, corner_radius=10)
        self.tabview.pack(padx=20, pady=10, fill="both", expand=True)

        self.tab_sync = self.tabview.add("Sincronizador (1:1)")
        self.tab_batch = self.tabview.add("Lote")

        self._build_sync_ui()
        self._build_batch_ui()

    def _build_sync_ui(self):
        self.path_origin = self._create_folder_input(self.tab_sync, "1. Origem (Nomes Corretos):")
        self.path_dest = self._create_folder_input(self.tab_sync, "2. Destino (Imagens Editadas):")

        # 4. NOVA FUNÇÃO: Checkbox de Movimentação/Substituição
        self.checkbox_move = ctk.CTkCheckBox(
            self.tab_sync, 
            text="Substituir Originais (Apaga as imagens de Origem e move as Editadas para lá)",
            font=("Segoe UI", 12, "bold"),
            text_color="#A46B00"
        )
        self.checkbox_move.pack(pady=(10, 0))

        btn_start_sync = ctk.CTkButton(self.tab_sync, text="Analisar e Sincronizar", height=40, font=("Arial", 14, "bold"), command=self._run_sync_analysis)
        btn_start_sync.pack(pady=20)

    def _build_batch_ui(self):
        self.path_batch = self._create_folder_input(self.tab_batch, "Pasta com as Imagens:")
        
        frame_pattern = ctk.CTkFrame(self.tab_batch, fg_color="transparent")
        frame_pattern.pack(fill="x", padx=40, pady=10)

        lbl_pattern = ctk.CTkLabel(frame_pattern, text="Padrão de Nome (Use ## para contagem):", anchor="w")
        lbl_pattern.pack(fill="x")
        
        self.entry_pattern = ctk.CTkEntry(frame_pattern, placeholder_text="Ex: Projeto_##")
        self.entry_pattern.pack(fill="x", pady=5)

        options = ctk.CTkFrame(frame_pattern, fg_color="transparent")
        options.pack(fill="x", pady=(5, 0))
        ctk.CTkLabel(options, text="Início:").pack(side="left")
        self.entry_start = ctk.CTkEntry(options, width=65)
        self.entry_start.insert(0, "1")
        self.entry_start.pack(side="left", padx=(5, 15))
        ctk.CTkLabel(options, text="Incremento:").pack(side="left")
        self.entry_increment = ctk.CTkEntry(options, width=65)
        self.entry_increment.insert(0, "1")
        self.entry_increment.pack(side="left", padx=5)
        self.checkbox_recursive = ctk.CTkCheckBox(
            options,
            text="Incluir subpastas",
        )
        self.checkbox_recursive.pack(side="right")

        ctk.CTkLabel(
            frame_pattern,
            text="Tags: #  [NOME]  [DATA]  [PASTA]  [EXT]  [MODIFICADO]",
            anchor="w",
            text_color="#a0a0a0",
            font=("Segoe UI", 11),
        ).pack(fill="x", pady=(8, 0))

        btn_start_batch = ctk.CTkButton(self.tab_batch, text="Aplicar Padrão", height=40, fg_color="#A46B00", hover_color="#825500", font=("Arial", 14, "bold"), command=self._run_batch_rename)
        btn_start_batch.pack(pady=20)

    def _create_folder_input(self, parent, label_text):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=40, pady=5)
        ctk.CTkLabel(frame, text=label_text, anchor="w").pack(fill="x")
        
        input_frame = ctk.CTkFrame(frame, fg_color="transparent")
        input_frame.pack(fill="x")
        
        entry = ctk.CTkEntry(input_frame)
        entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(input_frame, text="Procurar...", width=80, command=lambda: self._browse_folder(entry)).pack(side="right")
        return entry

    def _browse_folder(self, entry_widget):
        folder = filedialog.askdirectory()
        if folder:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, folder)

    # --- Lógica de Execução ---
    def _run_sync_analysis(self):
        orig_folder = self.path_origin.get()
        dest_folder = self.path_dest.get()

        if not orig_folder or not dest_folder:
            messagebox.showwarning("Aviso", "Selecione as pastas!")
            return

        try:
            if os.path.abspath(orig_folder) == os.path.abspath(dest_folder):
                raise ValueError("Origem e destino precisam ser pastas diferentes.")
            orig_files = get_valid_images(orig_folder, order="name")
            dest_files = get_valid_images(dest_folder, order="modified")
            if not orig_files:
                raise ValueError("A pasta de origem não contém imagens válidas.")
            if not dest_files:
                raise ValueError("A pasta de destino não contém imagens válidas.")
            
            # 2. FIX: Usa zip_longest para garantir que TODAS as imagens apareçam no preview, preenchendo as faltantes com None
            initial_mapping = list(zip_longest(orig_files, dest_files, fillvalue=None))
            
            PreviewWindow(
                self,
                initial_mapping,
                lambda mapping: self._execute_and_log(mapping, move_to_origin=bool(self.checkbox_move.get())),
            )
        except Exception as e:
            messagebox.showerror("Erro", f"Falha na análise: {str(e)}")

    def _run_batch_rename(self):
        batch_folder = self.path_batch.get()
        pattern = self.entry_pattern.get()

        if not batch_folder or not pattern:
            messagebox.showwarning("Aviso", "Preencha os campos!")
            return

        try:
            try:
                start_index = int(self.entry_start.get())
                increment = int(self.entry_increment.get())
            except ValueError as exc:
                raise ValueError("Início e incremento precisam ser números inteiros.") from exc
            files = get_valid_images(
                batch_folder,
                recursive=bool(self.checkbox_recursive.get()),
            )
            mapping = generate_batch_mapping(
                files,
                pattern,
                start_index=start_index,
                increment=increment,
            )
            # Abre janela de preview antes de executar
            BatchPreviewWindow(self, mapping, self._execute_and_log)
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def _execute_and_log(self, mapping, move_to_origin=False):
        if not mapping:
            return
        
        if move_to_origin and not messagebox.askyesno(
            "Confirmar substituição",
            "As imagens originais serão substituídas pelas editadas.\n\n"
            "Uma cópia de segurança será criada para permitir desfazer. Continuar?",
        ):
            return

        results, real_pairs = execute_rename(mapping)

        # 4. Lógica da Nova Função: "Mover e Substituir"
        moved_count = 0
        deleted_count = 0
        should_move = move_to_origin and not results.get("errors")
        orig_folder = self.path_origin.get() if hasattr(self, "path_origin") else None
        operation_pairs = list(real_pairs)
        backup_dir = None

        if should_move and orig_folder:
            # Move os originais para uma cópia de segurança antes de substituí-los.
            try:
                orig_imgs = get_valid_images(orig_folder)
                stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                origin_path = Path(orig_folder)
                backup_dir = origin_path.parent / f".{origin_path.name}_nexus_backup_{stamp}"
                backup_dir.mkdir(parents=False, exist_ok=False)
                for img_path in orig_imgs:
                    try:
                        backup_path = backup_dir / img_path.name
                        shutil.move(str(img_path), str(backup_path))
                        operation_pairs.append((str(img_path), str(backup_path)))
                        deleted_count += 1
                    except Exception as e:
                        results['errors'].append(f"Erro ao remover original {img_path.name}: {e}")
            except Exception as e:
                results['errors'].append(f"Erro ao listar origem para limpeza: {e}")

            # Segundo: mover as imagens renomeadas para a origem (agora vazia)
            for old_dest, new_dest in real_pairs:
                if new_dest and os.path.exists(new_dest):
                    file_name = os.path.basename(new_dest)
                    target_path = os.path.join(orig_folder, file_name)
                    try:
                        # Sem risco de colisão, pois a origem foi limpa
                        shutil.move(new_dest, target_path)
                        operation_pairs.append((new_dest, target_path))
                        moved_count += 1
                    except Exception as e:
                        results['errors'].append(f"Erro ao mover {file_name}: {e}")

            if results["errors"]:
                # Reverte as movimentações já concluídas, incluindo a renomeação inicial.
                for original, current in reversed(operation_pairs):
                    original_path, current_path = Path(original), Path(current)
                    if current_path.exists() and not original_path.exists():
                        try:
                            original_path.parent.mkdir(parents=True, exist_ok=True)
                            shutil.move(str(current_path), str(original_path))
                        except OSError as exc:
                            results["errors"].append(f"Falha ao restaurar {original_path.name}: {exc}")
                real_pairs = []
                operation_pairs = []
                moved_count = 0
                deleted_count = 0

        try:
            log_path = create_rollback_log(operation_pairs)
        except OSError as exc:
            log_path = None
            results["errors"].append(f"Não foi possível criar o histórico para desfazer: {exc}")

        msg = f"✅ Operação Concluída!\n\nRenomeados: {results.get('success', 0)}"
        if should_move:
            msg += f"\n💾 Originais guardadas no backup: {deleted_count}"
            msg += f"\n🚚 Movidas p/ Origem: {moved_count}"
        if results.get('errors'):
            msg += f"\n❌ Erros: {len(results['errors'])}"
            msg += "\n\n" + "\n".join(results["errors"][:5])
        if backup_dir:
            msg += f"\n💾 Backup: {backup_dir}"
        if log_path:
            msg += "\n↩️ A ação pode ser desfeita pelo botão no topo."
            
        # O self.after garante que a notificação apareça DEPOIS que a janela de preview fechar
        self.after(500, lambda: messagebox.showinfo("Relatório Nexus", msg))
        # Toast rápido de conclusão
        self.after(600, lambda: show_toast(self, "Operação finalizada!", "success"))

    def _run_rollback(self):
        app_data = os.getenv("APPDATA")
        log_dir = os.path.join(app_data, "NexusRename", "logs") if app_data else str(Path.home() / ".nexusrename" / "logs")
        log_path = Path(log_dir)
        logs = sorted(log_path.glob("nexus_log_*.json"), key=lambda item: item.stat().st_mtime, reverse=True) if log_path.exists() else []
        if not logs:
            messagebox.showinfo("Desfazer", "Nenhuma ação registrada foi encontrada.")
            return
        file_path = str(logs[0])
        if messagebox.askyesno(
            "Confirmar",
            f"Desfazer a última ação registrada?\n\n{logs[0].name}",
        ):
            res = execute_rollback(file_path)
            msg = f"Reversão concluída.\nSucesso: {res['success']}"
            if res['errors']:
                msg += f"\nErros: {len(res['errors'])}"
            messagebox.showinfo("Reversão", msg)
            show_toast(self, "Reversão finalizada!", "info")

if __name__ == "__main__":
    app = NexusApp()
    app.mainloop()

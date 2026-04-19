import os
from pathlib import Path
import json

def execute_rename(aligned_mapping: list[tuple[str, str | None]]) -> dict:
    """
    Executa a renomeação física dos arquivos no sistema operacional.
    Aceita 'None' no caminho de destino para arquivos que foram pulados pelo usuário.
    
    Formato esperado: [(caminho_destino_atual, novo_caminho_destino), ...]
    Se o destino foi pulado na UI, o caminho_destino_atual será None.
    """
    results = {
        "success": 0,
        "skipped": 0,
        "errors": []
    }

    for current_dest, new_dest in aligned_mapping:
        # Se a UI enviou None, significa que o usuário marcou para pular esta imagem
        if current_dest is None:
            results["skipped"] += 1
            continue

        try:
            current_path = Path(current_dest)
            new_path = Path(new_dest)

            # Validação: Verifica se o arquivo de destino ainda existe antes de renomear
            if not current_path.exists():
                results["errors"].append(f"Arquivo não encontrado: {current_path.name}")
                continue

            # Prevenção de Colisão: Se já existir um arquivo com o novo nome
            if new_path.exists():
                # Adiciona um sufixo numérico para evitar sobrescrever a imagem
                base_name = new_path.stem
                extension = new_path.suffix
                counter = 1
                while new_path.exists():
                    new_path = new_path.with_name(f"{base_name}_{counter}{extension}")
                    counter += 1

            # Executa a renomeação no sistema operacional
            os.rename(current_path, new_path)
            results["success"] += 1

        except Exception as e:
            results["errors"].append(f"Erro ao renomear {current_path.name}: {str(e)}")

    return results

def execute_rollback(log_file_path: str) -> dict:
    """
    Lê o arquivo de log JSON e reverte os nomes dos arquivos para o estado original.
    """
    results = {
        "success": 0,
        "errors": []
    }

    try:
        with open(log_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        history = data.get("history", {})
        # O JSON salva como {"novo_caminho": "caminho_original"}
        
        for current_path_str, original_path_str in history.items():
            current_path = Path(current_path_str)
            original_path = Path(original_path_str)
            
            if current_path.exists():
                try:
                    os.rename(current_path, original_path)
                    results["success"] += 1
                except Exception as e:
                    results["errors"].append(f"Falha ao reverter {current_path.name}: {str(e)}")
            else:
                results["errors"].append(f"Arquivo alterado não encontrado: {current_path.name}")
                
    except Exception as e:
        results["errors"].append(f"Erro ao ler o arquivo de log: {str(e)}")
        
    return results
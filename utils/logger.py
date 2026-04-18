import json
from datetime import datetime
from pathlib import Path

def create_rollback_log(successful_renames: list[tuple[str, str]], log_folder: str = "logs"):
    """
    Gera um arquivo JSON estruturado após cada operação.
    Isso é vital para a Fase 3 (se decidirmos adicionar um botão de 'Desfazer' no futuro).
    """
    if not successful_renames:
        return None

    # Cria a pasta de logs na raiz do projeto se não existir
    log_dir = Path(log_folder)
    log_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"nexus_log_{timestamp}.json"
    
    # Formato ideal para reversão: "Caminho Atual (Novo)" : "Caminho Antigo (Original)"
    rollback_data = {
        "operation_date": timestamp,
        "total_files": len(successful_renames),
        "history": {}
    }

    for original_path, new_path in successful_renames:
        rollback_data["history"][new_path] = original_path
        
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(rollback_data, f, indent=4, ensure_ascii=False)
        
    return str(log_file)
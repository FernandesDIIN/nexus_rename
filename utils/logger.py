import json
import os
from datetime import datetime
from pathlib import Path

def create_rollback_log(successful_renames: list[tuple[str, str]], log_folder: str = None) -> str | None:
    """
    Gera um arquivo JSON estruturado após cada operação.
    O log é salvo em %APPDATA%/NexusRename/logs (acesso garantido).
    """
    if not successful_renames:
        return None

    # Caminho seguro: sempre na pasta de dados do usuário
    if log_folder is None:
        app_data = os.getenv("APPDATA")
        base_dir = (Path(app_data) / "NexusRename" if app_data else Path.home() / ".nexusrename") / "logs"
    else:
        base_dir = Path(log_folder)

    base_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    log_file = base_dir / f"nexus_log_{timestamp}.json"
    
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

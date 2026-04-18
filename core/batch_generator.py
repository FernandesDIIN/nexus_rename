import re
from pathlib import Path
from datetime import datetime

def generate_batch_mapping(files: list[Path], pattern: str, start_index: int = 1) -> list[tuple[str, str]]:
    """
    Gera o mapeamento de renomeação baseado em padrões de string digitados pelo usuário.
    Suporta wildcards como #, ##, [NOME] e [DATA].
    """
    mapping = []
    current_index = start_index
    today_str = datetime.now().strftime("%Y%m%d")

    for file_path in files:
        new_name = pattern

        # 1. Substituição de Tags Estáticas
        new_name = new_name.replace("[NOME]", file_path.stem)
        new_name = new_name.replace("[DATA]", today_str)

        # 2. Substituição Dinâmica de Numeração (Hashes)
        # O Regex busca blocos contínuos de '#', não importa se são 1, 2, 3 ou mais.
        match = re.search(r'(#+)', new_name)
        if match:
            hash_chars = match.group(1)
            padding = len(hash_chars)
            # Zfill adiciona os zeros à esquerda conforme a quantidade de '#'
            # Ex: padding 3 (###) com index 5 vira "005"
            num_str = str(current_index).zfill(padding)
            new_name = new_name.replace(hash_chars, num_str, 1)

        # 3. Montagem do Caminho Final
        # file_path.parent é a pasta original; file_path.suffix é a extensão (.jpg, .png)
        new_dest_path = file_path.parent / f"{new_name}{file_path.suffix}"
        
        mapping.append((str(file_path), str(new_dest_path)))
        
        current_index += 1

    return mapping
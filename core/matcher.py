import os
from pathlib import Path

def get_sequential_mapping(origin_folder: str, destination_folder: str) -> list[tuple[str, str]]:
    """
    Mapeia arquivos da origem para o destino baseando-se na ordem alfabética da origem
    e na ordem cronológica de salvamento no destino.
    """
    origin_path = Path(origin_folder)
    dest_path = Path(destination_folder)

    # Extensões válidas para evitar ler arquivos de sistema (ex: .DS_Store, thumbs.db)
    valid_extensions = {'.jpg', '.jpeg', '.png', '.webp'}

    # 1. Coletar e ordenar Origem (Alfabeticamente pelo nome/ID)
    origin_files = [f for f in origin_path.iterdir() if f.is_file() and f.suffix.lower() in valid_extensions]
    origin_files.sort(key=lambda x: x.name)

    # 2. Coletar e ordenar Destino (Cronologicamente pela data de modificação)
    dest_files = [f for f in dest_path.iterdir() if f.is_file() and f.suffix.lower() in valid_extensions]
    # os.path.getmtime retorna o timestamp da última modificação do arquivo
    dest_files.sort(key=lambda x: os.path.getmtime(x))

    # 3. Trava de Segurança Crítica (Antecipação de Erro)
    if len(origin_files) != len(dest_files):
        raise ValueError(
            f"FALHA DE SEGURANÇA: Quantidade incompatível. "
            f"Origem possui {len(origin_files)} imagens, Destino possui {len(dest_files)}. "
            f"A renomeação foi bloqueada para evitar o 'Efeito Dominó'."
        )

    # 4. Criar o mapeamento 1 para 1
    mapping = []
    for origin_file, dest_file in zip(origin_files, dest_files):
        # Queremos o caminho completo do destino, mas o novo nome será o nome exato da origem
        new_dest_path = dest_path / origin_file.name
        mapping.append((str(dest_file), str(new_dest_path)))

    return mapping
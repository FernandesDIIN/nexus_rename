from utils.file_handler import get_valid_images

def get_sequential_mapping(origin_folder: str, destination_folder: str) -> list[tuple[str, str]]:
    """
    Mapeia arquivos da origem para o destino baseando-se na ordem alfabética da origem
    e na ordem cronológica de salvamento no destino (desempate por nome).
    """
    origin_files = get_valid_images(origin_folder, order="name")
    dest_files = get_valid_images(destination_folder, order="modified")

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
        new_dest_path = dest_file.parent / origin_file.name
        mapping.append((str(dest_file), str(new_dest_path)))

    return mapping

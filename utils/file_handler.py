import re
from pathlib import Path

# Constante de segurança
VALID_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}

def _natural_key(path: Path):
    value = path.as_posix()
    return [int(part) if part.isdigit() else part.casefold() for part in re.split(r"(\d+)", value)]


def get_valid_images(
    folder_path: str,
    order: str = "name",
    recursive: bool = False,
) -> list[Path]:
    """
    Filtra diretórios, garantindo que o sistema tente processar apenas 
    arquivos de imagem válidos e que não estejam corrompidos.
    """
    path = Path(folder_path)
    
    if not path.exists() or not path.is_dir():
        raise ValueError(f"O diretório não existe ou é inválido: {folder_path}")
        
    valid_files = []
    
    candidates = path.rglob("*") if recursive else path.iterdir()
    for f in candidates:
        # Verifica se é arquivo, se a extensão é permitida
        if f.is_file() and f.suffix.lower() in VALID_EXTENSIONS:
            # Validação anti-corrupção: o arquivo tem pelo menos 1 byte?
            if f.stat().st_size > 0:
                valid_files.append(f)
                
    # Ordenação padrão para não depender da ordem aleatória do SO
    if order == "modified":
        valid_files.sort(key=lambda item: (item.stat().st_mtime_ns, _natural_key(item)))
    elif order == "name":
        valid_files.sort(key=_natural_key)
    else:
        raise ValueError(f"Ordenação inválida: {order}")
    
    return valid_files

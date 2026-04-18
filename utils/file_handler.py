import os
from pathlib import Path

# Constante de segurança
VALID_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}

def get_valid_images(folder_path: str) -> list[Path]:
    """
    Filtra diretórios, garantindo que o sistema tente processar apenas 
    arquivos de imagem válidos e que não estejam corrompidos.
    """
    path = Path(folder_path)
    
    if not path.exists() or not path.is_dir():
        raise ValueError(f"O diretório não existe ou é inválido: {folder_path}")
        
    valid_files = []
    
    for f in path.iterdir():
        # Verifica se é arquivo, se a extensão é permitida
        if f.is_file() and f.suffix.lower() in VALID_EXTENSIONS:
            # Validação anti-corrupção: o arquivo tem pelo menos 1 byte?
            if f.stat().st_size > 0:
                valid_files.append(f)
                
    # Ordenação padrão para não depender da ordem aleatória do SO
    valid_files.sort(key=lambda x: x.name)
    
    return valid_files
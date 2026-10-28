# NexusRename

NexusRename é um aplicativo desktop para sincronizar nomes entre imagens originais e editadas e para renomear imagens em lote. A interface é construída com CustomTkinter e funciona localmente, sem enviar arquivos para serviços externos.

## Funcionalidades

- Sincronização visual 1:1: originais em ordem natural e editadas por data de modificação.
- Alinhamento instantâneo: a troca atualiza apenas os dois itens envolvidos.
- Miniaturas paralelas, cache em memória, orientação EXIF correta e interface não bloqueante.
- Atalhos no alinhamento: `Ctrl+Z` desfaz a troca, `Ctrl+Enter` confirma e `Esc` fecha.
- Renomeação em lote com índice inicial, incremento e inclusão opcional de subpastas.
- Tags `#`, `[NOME]`, `[DATA]`, `[PASTA]`, `[EXT]` e `[MODIFICADO]`.
- Renomeação segura em duas fases, inclusive para trocas e ciclos de nomes.
- Detecção de colisões, arquivos ausentes, padrões inválidos e nomes reservados do Windows.
- Histórico em JSON e botão para desfazer diretamente a última ação.
- Substituição opcional dos originais com criação prévia de uma pasta de backup.

Formatos aceitos: JPG, JPEG, PNG e WebP.

## Executar o projeto

Requer Python 3.10 ou superior.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

Para executar os testes:

```powershell
python -m unittest discover -s tests -v
```

## Gerar o aplicativo para Windows

```powershell
python -m pip install nuitka
python -m nuitka --standalone --windows-console-mode=disable --windows-icon-from-ico=icon.ico --include-data-file=icon.ico=icon.ico --enable-plugin=tk-inter --output-filename=NexusRename.exe main.py
```

Depois, compile `NexusRename.iss` no Inno Setup. O script espera a saída standalone na pasta `main.dist`.

## Estrutura

- `core/`: geração de nomes e execução/rollback das operações.
- `ui/`: janelas e componentes da interface.
- `utils/`: descoberta de imagens e logs.
- `tests/`: testes automatizados do núcleo.

## Segurança dos arquivos

Revise sempre a pré-visualização. Em “Substituir Originais”, o NexusRename move os arquivos originais para uma pasta oculta de backup ao lado da pasta de origem antes de mover as versões editadas. Não remova esse backup enquanto ainda precisar desfazer a operação.

## Licença

Consulte a licença do repositório antes de redistribuir o aplicativo.

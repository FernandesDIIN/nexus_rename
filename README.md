# NexusRename
**NexusRename** é uma ferramenta de engenharia de software desenvolvida para automatizar e assegurar a gestão de arquivos em lote. Projetado com uma arquitetura limpa e interface minimalista, o sistema resolve o problema de perda de metadados durante fluxos de edição pesados (como remoção de objetos em imagens).

Desenvolvido e mantido por **[VENSEV]**.

## Funcionalidades Principais

* **Sincronização Segura (1:1):** Restaura os nomes originais de arquivos que foram processados em editores externos. Utiliza um algoritmo de mapeamento sequencial (Alfabético na Origem -> Cronológico no Destino).
* **Trava Anti-Dominó:** Prevenção algorítmica contra o "Efeito Dominó" na renomeação. Se houver discrepância no número de arquivos entre pastas, o sistema paralisa e exige intervenção.
* **Resolução Visual de Conflitos:** Interface Drag & Drop para alinhar arquivos faltantes ou ignorar itens durante a sincronização.
* **Renomeação Autônoma (Em Lote):** Motor de Regex que aceita padrões de string.
  * Suporte a chaves de indexação: `#`, `##`, `###`
  * Suporte a tags dinâmicas: `[NOME]`, `[DATA]`

## Arquitetura do Sistema

O projeto adota uma separação estrita de responsabilidades:
* `core/`: Regras de negócio, geradores de padrões e execução de comandos no Sistema Operacional (Sem interface gráfica).
* `ui/`: Componentes visuais utilizando CustomTkinter (Janelas, Abas, Inputs).
* `utils/`: Ferramentas auxiliares, validação de arquivos e geração de logs estruturados (JSON) para futura implementação de *rollback*.

## Guia de Instalação (Para Desenvolvedores)

Se você deseja clonar o repositório e rodar o projeto a partir do código-fonte:

### 1. Pré-requisitos
* Python 3.10 ou superior instalado na máquina.
* Git instalado.

### 2. Configuração do Ambiente
Abra o terminal e execute os seguintes comandos:

```bash
# Clone o repositório
git clone [LINK_DO_SEU_GITHUB_AQUI]/NexusRename.git

# Entre na pasta do projeto
cd NexusRename

# Instale as dependências visuais e de processamento
pip install customtkinter Pillow

3. Executando a Aplicação
Bash
python main.py
Distribuição (Gerando o Executável .exe)
Para criar um executável autônomo e distribuível para usuários finais sem a necessidade de instalar o Python:

Instale as ferramentas de compilação:

Bash
pip install pyinstaller
Gere o binário do aplicativo:
```
Bash
pyinstaller --noconsole --onefile --icon=icon.ico --add-data "icon.ico;." --collect-all customtkinter --name "NexusRename" main.py
(Opcional) Instalação Profissional: Utilize o arquivo nexus_build.iss incluído no repositório com o Inno Setup Compiler para gerar o instalador do Windows.
```

Sobre o Autor
[T.D.J Fernandes / VENSEV]
Engenharia de Software e Soluções em Automação.

GitHub: @FernandesDIIN

Contato: 

Website/Portfólio: 

Licença
Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.# nexus_rename
# nexus_rename

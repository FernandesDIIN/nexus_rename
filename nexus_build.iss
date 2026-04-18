; ------------------------------------------------------------------
; NEXUS RENAME - SCRIPT DE INSTALAÇÃO PROFISSIONAL
; Arquiteto: ASS. PROJETO
; ------------------------------------------------------------------

#define MyAppName "NexusRename"
#define MyAppVersion "1.0.2"
#define MyAppPublisher "VENSEV"
#define MyAppExeName "NexusRename.exe"

[Setup]
; Configurações Globais do Instalador
AppId={{8A7F4B2C-3D9E-41F2-A5B6-7C8D9E0F1A2B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes

; ------------------------------------------------------------------
; CONFIGURAÇÃO DE ÍCONE (INJEÇÃO VISUAL)
; ------------------------------------------------------------------
; Ícone do arquivo executável do instalador (setup.exe)
SetupIconFile=icon.ico
; Ícone que aparecerá no Painel de Controle (Adicionar/Remover Programas)
UninstallDisplayIcon={app}\{#MyAppExeName}

; Nome do arquivo final que será enviado aos clientes
OutputBaseFilename=Instalador_NexusRename_v1.0
; Compressão de Elite (Reduz drasticamente o tamanho do instalador)
Compression=lzma2/ultra64
SolidCompression=yes
; Interface Visual do Instalador (Moderna)
WizardStyle=modern
; Privilégios necessários para instalar na pasta Arquivos de Programas
PrivilegesRequired=admin

[Languages]
; Define o instalador para o idioma Português (Brasil)
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
; Opção para criar atalho na área de trabalho (desmarcada por padrão para ser minimalista)
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; O ALVO CRÍTICO: Pega o .exe gerado pelo PyInstaller na pasta dist
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; Nota: Não use "Flags: ignoreversion" em arquivos de sistema compartilhados, mas para o nosso .exe é seguro e recomendado.

[Icons]
; Cria os atalhos no Menu Iniciar e na Área de Trabalho
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; Oferece a opção de iniciar o aplicativo imediatamente após a instalação
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
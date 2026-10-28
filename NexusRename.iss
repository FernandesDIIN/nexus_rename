; ------------------------------------------------------------------
; NEXUS RENAME - SCRIPT DE INSTALAÇÃO PROFISSIONAL
; Arquiteto: ASS. PROJETO
; ------------------------------------------------------------------

#define MyAppName "NexusRename"
#define MyAppVersion "1.6.1"
#define MyAppPublisher "VENSEV"
#define MyAppExeName "NexusRename.exe"
#define MyAppSourceDir "main.dist"   ; Pasta gerada pelo Nuitka --standalone

[Setup]
; Configurações Globais do Instalador
AppId={{8A7F4B2C-3D9E-41F2-A5B6-7C8D9E0F1A2B}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes

; Ícone do instalador e do desinstalador
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

; Nome do arquivo final
OutputBaseFilename=Instalador_NexusRename_v1.6.0
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Copia o executável (ignora versão para não travar)
Source: "{#MyAppSourceDir}\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; Copia todo o restante da pasta standalone, preservando a estrutura de diretórios
Source: "{#MyAppSourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

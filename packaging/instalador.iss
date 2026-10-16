#ifndef AppVersion
  #define AppVersion "0.2.0"
#endif
[Setup]
AppId={{64851AEC-551F-4F1A-BD4A-559158E97550}
AppName=SASISOPA
AppVersion={#AppVersion}
AppPublisher=COG
DefaultDirName={localappdata}\Programs\SASISOPA
DefaultGroupName=SASISOPA
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
OutputDir=..\release
OutputBaseFilename=SASISOPA-Instalador-Windows
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\SASISOPA.exe
CloseApplications=yes
SetupLogging=yes
[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
[Tasks]
Name: "desktopicon"; Description: "Crear un acceso directo en el escritorio"; Flags: unchecked
[Files]
Source: "..\dist\SASISOPA\*"; DestDir: "{app}"; Excludes: "SASISOPA-Verificar.exe"; Flags: ignoreversion recursesubdirs createallsubdirs
[Icons]
Name: "{group}\SASISOPA"; Filename: "{app}\SASISOPA.exe"
Name: "{autodesktop}\SASISOPA"; Filename: "{app}\SASISOPA.exe"; Tasks: desktopicon
[Run]
Filename: "{app}\SASISOPA.exe"; Description: "Abrir SASISOPA"; Flags: nowait postinstall skipifsilent

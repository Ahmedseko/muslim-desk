; Muslim Desk — Inno Setup Installer Script
; Inno Setup 6.x

#define AppName      "Muslim Desk"
#define AppShort     "MuslimDesk"
#define AppVersion   "1.3.0"
#define AppPublisher "Ahmed Seko"
#define AppExeName   "MuslimDesk.exe"
#define AppURL       ""
#define DistDir      "..\dist\MuslimDesk"

[Setup]
; ── Identity
AppId={{7A3F2E91-4B8C-4D1F-9E2A-6C5B3D8F0A14}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} v{#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}

; ── Install location
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes

; ── Output
OutputDir=..\release
OutputBaseFilename=MuslimDesk-Setup-v{#AppVersion}
SetupIconFile=..\assets\icon.ico

; ── Compression
Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes

; ── Windows 10/11 x64 only
ArchitecturesInstallIn64BitMode=x64compatible
ArchitecturesAllowed=x64compatible
MinVersion=10.0.17763

; ── Appearance
WizardStyle=modern
WizardResizable=yes
WizardSizePercent=120

; ── Privileges
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; ── Misc
DisableWelcomePage=no
DisableDirPage=no
DisableReadyPage=no
UsePreviousAppDir=yes
UninstallDisplayName={#AppName}
UninstallDisplayIcon={app}\{#AppExeName}
CreateUninstallRegKey=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a Desktop shortcut";          GroupDescription: "Shortcuts:"; Flags: unchecked
Name: "startuprun";  Description: "Launch automatically at Windows Start"; GroupDescription: "Startup:";   Flags: unchecked

[Files]
Source: "{#DistDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#AppName}";           Filename: "{app}\{#AppExeName}"; Comment: "Muslim prayer time desktop app"
Name: "{group}\Uninstall {#AppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}";     Filename: "{app}\{#AppExeName}"; Tasks: desktopicon; Comment: "Muslim prayer time desktop app"

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; \
  ValueType: string; ValueName: "{#AppName}"; \
  ValueData: """{app}\{#AppExeName}"""; \
  Flags: uninsdeletevalue; Tasks: startuprun

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Launch {#AppName} now"; \
  Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "taskkill.exe"; Parameters: "/F /IM {#AppExeName}"; \
  Flags: runhidden; RunOnceId: "KillApp"

[UninstallDelete]

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
begin
  if CurStep = ssInstall then
    Exec('taskkill.exe', '/F /IM MuslimDesk.exe', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
end;

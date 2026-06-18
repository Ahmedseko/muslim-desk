; Muslim Desk — Inno Setup Installer Script
; Inno Setup 6.x

#define AppName      "Muslim Desk"
#define AppShort     "MuslimDesk"
#define AppVersion   "1.2.0"
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

; ── Compression (maksimum)
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
Name: "desktopicon";    Description: "Buat shortcut di Desktop";     GroupDescription: "Shortcut:"; Flags: unchecked
Name: "startuprun";     Description: "Jalankan otomatis saat Windows Start"; GroupDescription: "Startup:";  Flags: unchecked

[Files]
; Seluruh folder dist PyInstaller
Source: "{#DistDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Start Menu
Name: "{group}\{#AppName}";              Filename: "{app}\{#AppExeName}"; Comment: "Jadwal Sholat 5 Waktu"
Name: "{group}\Uninstall {#AppName}";    Filename: "{uninstallexe}"
; Desktop (opsional)
Name: "{autodesktop}\{#AppName}";        Filename: "{app}\{#AppExeName}"; Tasks: desktopicon; Comment: "Jadwal Sholat 5 Waktu"

[Registry]
; Auto-run saat startup (opsional, hanya jika task dipilih)
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; \
  ValueType: string; ValueName: "{#AppName}"; \
  ValueData: """{app}\{#AppExeName}"""; \
  Flags: uninsdeletevalue; Tasks: startuprun

[Run]
; Tawarkan menjalankan app setelah install selesai
Filename: "{app}\{#AppExeName}"; Description: "Jalankan {#AppName} sekarang"; \
  Flags: nowait postinstall skipifsilent

[UninstallRun]
; Tutup app sebelum uninstall
Filename: "taskkill.exe"; Parameters: "/F /IM {#AppExeName}"; \
  Flags: runhidden; RunOnceId: "KillApp"

[UninstallDelete]
; Bersihkan settings user (opsional — hapus baris ini jika ingin settings tetap ada)
; Type: filesandordirs; Name: "{userdocs}\.muslim_desk"

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
begin
  if CurStep = ssInstall then
    Exec('taskkill.exe', '/F /IM MuslimDesk.exe', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
end;

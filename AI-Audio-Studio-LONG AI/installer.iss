; =====================================================================
; Script Inno Setup: AI Audio Studio - LONG AI Edition
; Hotline / Zalo: 0566260837
; Đóng gói bộ cài đặt độc lập (.exe) không cần cài Python hay uv
; Ghi nhận nguồn gốc: Phạm Nguyễn Ngọc Bảo & Đặng Hữu Sơn
; =====================================================================

#define MyAppName "AI Audio Studio"
#define MyAppVersion "2.0.0"
#define MyAppPublisher "LONG AI (Hotline/Zalo: 0566260837)"
#define MyAppURL "https://zalo.me/0566260837"
#define MyAppExeName "AI-Audio-Studio.exe"

[Setup]
AppId={{E29F9A6C-32B8-4E45-927A-456789ABCDEF}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={userpf}\AI Audio Studio
DisableProgramGroupPage=yes
LicenseFile=LICENSE
OutputDir=dist-installer
OutputBaseFilename=AI-Audio-Studio-Setup-v2.0
SetupIconFile=apps\webapp\static\favicon.ico
UninstallDisplayIcon={app}\_internal\apps\webapp\static\favicon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
CloseApplications=force
RestartApplications=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Tạo biểu tượng ngoài màn hình chính (Desktop)"; GroupDescription: "Tùy chọn bổ sung:"
Name: "autostart"; Description: "Tự động khởi chạy cùng Windows khi mở máy"; GroupDescription: "Tùy chọn bổ sung:"; Flags: unchecked

[Files]
; Copy toàn bộ gói phần mềm độc lập từ dist\AI-Audio-Studio
Source: "dist\AI-Audio-Studio\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\_internal\apps\webapp\static\favicon.ico"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\_internal\apps\webapp\static\favicon.ico"; Tasks: desktopicon
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\_internal\apps\webapp\static\favicon.ico"; Tasks: autostart

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Khởi chạy {#MyAppName} ngay bây giờ"; Flags: nowait postinstall skipifsilent

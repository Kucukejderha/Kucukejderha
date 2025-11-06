; Inno Setup Script
; Bu betiği Inno Setup Compiler ile derleyerek setup.exe dosyasını oluşturun.

[Setup]
AppName=Sayim Veri Aktarim Servisi
AppVersion=3.0.0
; {cm:MyApp} sabit bir GUID'dir, her uygulama için farklı olmalıdır.
AppId={{F2A5B87C-6B3E-4B7C-8A5E-7D4E7C4B2A8C}}
DefaultDirName={autopf64}\SayimVeriAktarim
DefaultGroupName=Sayım Uygulaması
UninstallDisplayIcon={app}\settings_gui.exe
Compression=lzma
SolidCompression=yes
WizardStyle=modern
OutputBaseFilename=SayimUygulamasi_Kurulum_v3.0.0

[Languages]
Name: "turkish"; MessagesFile: "compiler:Languages\Turkish.isl"

[Files]
; PyInstaller ile oluşturulmuş olan .exe dosyaları ve diğer gerekli dosyalar.
; Bu dosyaların, bu betik dosyasıyla aynı klasördeki "dist" alt klasöründe olduğu varsayılmıştır.
Source: "dist\windows_service.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\settings_gui.exe"; DestDir: "{app}"; Flags: ignoreversion
; Ayar arayüzünün çalışması için config.ini dosyası gereklidir. Template'i kopyalayıp adını değiştiriyoruz.
Source: "config.ini.template"; DestDir: "{app}"; DestName: "config.ini"; Flags: ignoreversion

[Icons]
Name: "{group}\Sayım Uygulaması Ayarları"; Filename: "{app}\settings_gui.exe"
Name: "{group}\{cm:UninstallProgram,Sayim Veri Aktarim Servisi}"; Filename: "{uninstallexe}"

[Run]
; Kurulum bittikten sonra "Sayım Ayarları" programını çalıştırma seçeneği sunar.
Filename: "{app}\settings_gui.exe"; Description: "{cm:LaunchProgram,Sayım Uygulaması Ayarları}"; Flags: nowait postinstall skipifsilent

[InstallDelete]
; Kurulum sırasında eski log dosyasını temizle
Type: files; Name: "{app}\service.log"

[Code]
var
  ServiceInstalled: Boolean;

// Kurulum başladığında
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if (CurStep = ssInstall) then
  begin
    ServiceInstalled := False;
  end;
end;

// Kurulum tamamlandıktan sonra servisi kur ve başlat
procedure CurStepChanged_PostInstall(CurStep: TSetupStep);
begin
  if (CurStep = ssPostInstall) and not ServiceInstalled then
  begin
    // Servisi kur
    Log('Installing service...');
    if not Exec(ExpandConstant('{app}\windows_service.exe'), 'install', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
    begin
      MsgBox('Servis yüklenirken bir hata oluştu. Hata Kodu: ' + IntToStr(ResultCode), mbError, MB_OK);
    end
    else
    begin
      Log('Service installed.');
      ServiceInstalled := True;
      // Servisi başlat
      Log('Starting service...');
      if not Exec(ExpandConstant('{app}\windows_service.exe'), 'start', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
      begin
        MsgBox('Servis başlatılırken bir hata oluştu. Hata Kodu: ' + IntToStr(ResultCode), mbError, MB_OK);
      end
      else
        Log('Service started.');
    end;
  end;
end;

// Kaldırma işlemi başlamadan önce servisi durdur ve kaldır
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usUninstall then
  begin
    // Servisi durdur
    Log('Stopping service...');
    Exec(ExpandConstant('{app}\windows_service.exe'), 'stop', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    Log('Service stopped.');

    // Servisi kaldır
    Log('Removing service...');
    Exec(ExpandConstant('{app}\windows_service.exe'), 'remove', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    Log('Service removed.');
  end;
end;

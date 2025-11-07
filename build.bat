@echo off
setlocal

echo.
echo ==========================================================
echo Sayim Uygulamasi Derleme Betigi (Gelistirilmis Kontrol)
echo ==========================================================
echo.

rem --- Adim 0: Gereksinimleri Kontrol Etme ---
echo [0/6] Gereksinimler kontrol ediliyor...

rem Python kontrolu
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo HATA: Python komutu PATH'de bulunamadi.
    echo Lutfen Python 3'u https://www.python.org/downloads/ adresinden kurun.
    echo ONEMLI: KURULUM SIRASINDA "Add python.exe to PATH" SECENEGINI ISARETLEDIGINIZDEN EMIN OLUN.
    goto :error
)
echo  - Python bulundu.

rem Inno Setup kontrolu
where iscc >nul 2>nul
if %errorlevel% neq 0 (
    echo HATA: Inno Setup Compiler (iscc.exe) PATH'de bulunamadi.
    echo Lutfen Inno Setup'i https://jrsoftware.org/isinfo.php adresinden kurun.
    echo Kurulum sirasinda PATH'e eklenmesine izin verin.
    goto :error
)
echo  - Inno Setup Compiler bulundu.
echo Gereksinimler tamam.
echo.
echo Baslamak icin bir tusa basin...
pause > nul

rem --- Adim 1: Sanal Ortam Olusturma ---
echo.
echo [1/6] Sanal ortam olusturuluyor...
if not exist "venv\Scripts\activate.bat" (
    echo Sanal ortam mevcut degil, olusturuluyor...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo HATA: Sanal ortam olusturulamadi. Python kurulumunuzu kontrol edin.
        goto :error
    )
)
echo Sanal ortam hazir.

rem --- Adim 2: Sanal Ortami Aktiflestirme ve Bagimliliklari Yukleme ---
echo.
echo [2/6] Bagimliliklar yukleniyor (pyinstaller, pywin32, pyodbc, paramiko)...
call venv\Scripts\activate.bat
pip install pyinstaller pywin32 pyodbc paramiko
if %errorlevel% neq 0 (
    echo HATA: Gerekli kutuphaneler yuklenemedi. Internet baglantinizi ve Python/pip yapilandirmanizi kontrol edin.
    goto :error
)
echo Bagimliliklar yuklendi.

rem --- Adim 3: Ayar Arayuzunu Derleme (settings_gui.exe) ---
echo.
echo [3/6] Ayar arayuzu (settings_gui.exe) derleniyor...
pyinstaller --name settings_gui --onefile --windowed --icon=NONE settings_gui.py
if %errorlevel% neq 0 (
    echo HATA: Ayar arayuzu derlenirken bir hata olustu.
    goto :error
)
echo Ayar arayuzu derlendi.

rem --- Adim 4: Windows Servisini Derleme (windows_service.exe) ---
echo.
echo [4/6] Windows servisi (windows_service.exe) derleniyor...
pyinstaller --name windows_service --onefile --hidden-import=win32timezone --icon=NONE windows_service.py
if %errorlevel% neq 0 (
    echo HATA: Windows servisi derlenirken bir hata olustu.
    goto :error
)
echo Windows servisi derlendi.

rem --- Adim 5: Kurulum Dosyasini (setup.exe) Olusturma ---
echo.
echo [5/6] Kurulum dosyasi (setup.exe) Inno Setup ile olusturuluyor...
iscc setup.iss
if %errorlevel% neq 0 (
    echo HATA: Kurulum dosyasi olusturulurken bir hata olustu. Inno Setup kurulumunuzu kontrol edin.
    goto :error
)
echo Kurulum dosyasi derlendi.

rem --- Adim 6: Bitis ---
echo.
echo ==========================================================
echo DERLEME BASARIYLA TAMAMLANDI!
echo ==========================================================
echo.
echo "Output" klasoru altinda olusturulan "SayimUygulamasi_Kurulum_v3.0.3.exe"
echo dosyasini kullanarak uygulamayi kurabilirsiniz.
echo.
goto :end

:error
echo.
echo !!! ISLEM HATA NEDENIYLE DURDURULDU !!!
echo Lutfen yukaridaki hata mesajlarini inceleyip gerekli duzeltmeleri yapin.
echo.

:end
pause

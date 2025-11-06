@echo off
echo.
echo ==========================================================
echo Sayim Uygulamasi Derleme Betigi
echo ==========================================================
echo.
echo Bu betik, Sayim Uygulamasi bilesenlerini derleyip
echo kuruluma hazir hale getirecektir.
echo.
echo Gereksinimler:
echo 1. Python 3 (PATH'e eklenmis olmali)
echo 2. Inno Setup Compiler (iscc.exe PATH'e eklenmis olmali)
echo.
echo Baslamak icin bir tusa basin...
pause > nul

rem --- Adim 1: Sanal Ortam Olusturma ---
echo.
echo [1/5] Sanal ortam olusturuluyor...
if not exist "venv" (
    python -m venv venv
)
echo Sanal ortam hazir.

rem --- Adim 2: Sanal Ortami Aktiflestirme ve Bagimliliklari Yukleme ---
echo.
echo [2/5] Bagimliliklar yukleniyor (pyinstaller, pywin32, pyodbc, paramiko)...
call venv\Scripts\activate.bat
pip install pyinstaller pywin32 pyodbc paramiko
echo Bagimliliklar yuklendi.

rem --- Adim 3: Ayar Arayuzunu Derleme (settings_gui.exe) ---
echo.
echo [3/5] Ayar arayuzu (settings_gui.exe) derleniyor...
pyinstaller --name settings_gui --onefile --windowed --icon=NONE settings_gui.py
echo Ayar arayuzu derlendi.

rem --- Adim 4: Windows Servisini Derleme (windows_service.exe) ---
echo.
echo [4/5] Windows servisi (windows_service.exe) derleniyor...
pyinstaller --name windows_service --onefile --icon=NONE windows_service.py
echo Windows servisi derlendi.

rem --- Adim 5: Kurulum Dosyasini (setup.exe) Olusturma ---
echo.
echo [5/5] Kurulum dosyasi (setup.exe) Inno Setup ile olusturuluyor...
iscc setup.iss
echo Kurulum dosyasi derlendi.

echo.
echo ==========================================================
echo DERLEME TAMAMLANDI!
echo ==========================================================
echo.
echo "Output" klasoru altinda olusturulan "SayimUygulamasi_Kurulum_v3.0.0.exe"
echo dosyasini kullanarak uygulamayi kurabilirsiniz.
echo.
pause
exit

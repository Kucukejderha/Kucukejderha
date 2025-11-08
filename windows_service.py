# -*- coding: utf-8 -*-
import servicemanager
import socket
import sys
import win32timezone # This import is crucial for PyInstaller to find the hidden module
import win32event
import win32service
import win32serviceutil
import configparser
import os
import time
import logging
import pyodbc
import json
from ftplib import FTP

# --- Configuration ---
# Get the absolute path to the directory where this script is located.
# This is crucial for finding config.ini and log files when running as a service.
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_PATH, 'config.ini')
LOG_FILE = os.path.join(SCRIPT_PATH, 'service.log')

# --- Logging Setup ---
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def log_info(message):
    logging.info(message)

def log_error(message):
    logging.error(message)

# --- Core Data Export Logic ---
def run_data_export():
    """
    The main logic for fetching data from the database and uploading it via SFTP.
    This function is called periodically by the service.
    """
    log_info("Veri aktarım döngüsü başlatıldı.")

    if not os.path.exists(CONFIG_FILE):
        log_error(f"Yapılandırma dosyası bulunamadı: {CONFIG_FILE}")
        return

    try:
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)

        # Database connection details
        db_config = config['DATABASE']
        server, database, username, password = db_config['server'], db_config['database'], db_config['username'], db_config['password']

        # FTP connection details
        ftp_config = config['FTP']
        ftp_host, ftp_port, ftp_user, ftp_pass, ftp_remote_path = ftp_config['host'], int(ftp_config['port']), ftp_config['username'], ftp_config['password'], ftp_config['remote_path']

        local_json_path = os.path.join(SCRIPT_PATH, 'urunler.json')

        # --- 1. Fetch Data from Database ---
        log_info(f"Veritabanına bağlanılıyor: {server}...")
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};TrustServerCertificate=yes;'
        with pyodbc.connect(conn_str, timeout=10) as conn:
            log_info("Veritabanı bağlantısı başarılı.")
            cursor = conn.cursor()
            query = """
                SELECT s.STOK_KODU, s.STOK_ADI, s.OLCU_BR1, STRING_AGG(b.BARKOD, ',') AS Barkodlar
                FROM TBLSTSABIT s
                LEFT JOIN TBLSTOKBAR b ON s.STOK_KODU = b.STOK_KODU
                WHERE s.STOK_KODU IS NOT NULL AND b.BARKOD IS NOT NULL
                GROUP BY s.STOK_KODU, s.STOK_ADI, s.OLCU_BR1 ORDER BY s.STOK_KODU;
            """
            cursor.execute(query)
            columns = [column[0] for column in cursor.description]
            products = [dict(zip(columns, row)) for row in cursor.fetchall()]
            log_info(f"{len(products)} adet ürün veritabanından çekildi.")

        # --- 2. Create JSON File ---
        if not products:
            log_info("Veritabanından hiç ürün çekilemedi. Döngü tamamlandı.")
            return

        output_data = [{'stok_kodu': p['STOK_KODU'], 'stok_adi': p['STOK_ADI'], 'olcu_br1': p['OLCU_BR1'], 'barkod': p['Barkodlar']} for p in products]
        with open(local_json_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False)
        log_info(f"JSON dosyası oluşturuldu: {local_json_path}")

        # --- 3. Upload via FTP ---
        log_info(f"FTP sunucusuna bağlanılıyor: {ftp_host}...")
        with FTP() as ftp:
            ftp.connect(ftp_host, ftp_port, timeout=30)
            ftp.login(ftp_user, ftp_pass)
            log_info("FTP bağlantısı başarılı.")

            remote_file_path = f"{ftp_remote_path.rstrip('/')}/urunler.json"
            log_info(f"Dosya sunucuya yükleniyor: {remote_file_path}")

            with open(local_json_path, 'rb') as f:
                ftp.storbinary(f'STOR {remote_file_path}', f)

            log_info("Dosya başarıyla yüklendi.")
            ftp.quit()

    except Exception as e:
        log_error(f"Veri aktarım döngüsünde bir hata oluştu: {e}")

    log_info("Veri aktarım döngüsü tamamlandı.")


# --- Windows Service Class ---
class SayimDataService(win32serviceutil.ServiceFramework):
    _svc_name_ = "SayimDataExporterService"
    _svc_display_name_ = "Sayım Uygulaması Veri Aktarım Servisi"
    _svc_description_ = "Periyodik olarak MS SQL veritabanından ürün verilerini çeker ve web sunucusuna aktarır."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        self.is_running = True

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.is_running = False

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()

    def main(self):
        log_info("Servis başlatıldı.")

        # Read interval from config, default to 1 hour (3600 seconds)
        interval = 3600
        try:
            config = configparser.ConfigParser()
            if os.path.exists(CONFIG_FILE):
                config.read(CONFIG_FILE)
                interval = config.getint('SERVICE', 'interval_seconds', fallback=3600)
                log_info(f"Servis çalışma aralığı: {interval} saniye.")
        except Exception as e:
            log_error(f"Yapılandırma dosyasından 'interval_seconds' okunurken hata: {e}. Varsayılan (3600s) kullanılıyor.")

        while self.is_running:
            try:
                run_data_export()
            except Exception as e:
                log_error(f"Servis ana döngüsünde kritik hata: {e}")

            # Wait for the specified interval or until a stop signal is received
            rc = win32event.WaitForSingleObject(self.hWaitStop, interval * 1000)
            if rc == win32event.WAIT_OBJECT_0:
                # Stop signal received
                break

        log_info("Servis durduruldu.")


if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(SayimDataService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(SayimDataService)

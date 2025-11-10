# -*- coding: utf-8 -*-
import pyodbc
import json
import configparser
from ftplib import FTP
import os
import sys

def get_script_path():
    """Get the absolute path to the directory where this script is located."""
    return os.path.dirname(os.path.abspath(__file__))

def main():
    """
    Connects to the MS SQL database, fetches product data,
    creates a JSON file, and uploads it to a web server via FTP.
    """
    script_path = get_script_path()
    config_path = os.path.join(script_path, 'config.ini')

    print("--------------------------------------------------")
    print("Basit Veri Aktarim Betigi Baslatildi.")

    # --- 1. Read Configuration ---
    if not os.path.exists(config_path):
        print(f"HATA: Yapilandirma dosyasi bulunamadi: {config_path}")
        print("Lutfen 'config.ini.template' dosyasini 'config.ini' olarak kopyalayip icini doldurun.")
        sys.exit(1)

    config = configparser.ConfigParser()
    config.read(config_path)
    print("Yapilandirma dosyasi okundu.")

    try:
        db_config = config['DATABASE']
        ftp_config = config['FTP']
    except KeyError as e:
        print(f"HATA: Yapilandirma dosyasinda '{e}' bolumu eksik.")
        sys.exit(1)

    local_json_path = os.path.join(script_path, 'urunler.json')

    # --- 2. Connect to Database and Fetch Data ---
    products = []
    try:
        print(f"Veritabanina baglaniliyor: {db_config.get('server')}...")
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={db_config.get('server')};"
            f"DATABASE={db_config.get('database')};"
            f"UID={db_config.get('username')};"
            f"PWD={db_config.get('password')};"
            f"TrustServerCertificate=yes;"
        )
        with pyodbc.connect(conn_str, timeout=10) as conn:
            print("Veritabani baglantisi basarili.")
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
            print(f"Basariyla {len(products)} adet urun cekildi.")

    except Exception as e:
        print(f"VERITABANI HATASI: {e}")
        sys.exit(1)

    # --- 3. Create JSON File ---
    if not products:
        print("Uyari: Veritabanindan hic urun cekilemedi. Islem sonlandiriliyor.")
        sys.exit(0)

    try:
        output_data = [
            {'stok_kodu': p['STOK_KODU'], 'stok_adi': p['STOK_ADI'], 'olcu_br1': p['OLCU_BR1'], 'barkod': p['Barkodlar']}
            for p in products
        ]
        with open(local_json_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False)
        print(f"JSON dosyasi olusturuldu: {local_json_path}")

    except Exception as e:
        print(f"JSON dosyasi yazilirken bir hata olustu: {e}")
        sys.exit(1)

    # --- 4. Upload via FTP ---
    try:
        print(f"FTP sunucusuna baglaniliyor: {ftp_config.get('host')}...")
        with FTP() as ftp:
            ftp.connect(ftp_config.get('host'), int(ftp_config.get('port', 21)), timeout=30)
            ftp.login(ftp_config.get('username'), ftp_config.get('password'))
            print("FTP baglantisi basarili.")

            remote_path = ftp_config.get('remote_path')
            remote_file_path = f"{remote_path.rstrip('/')}/urunler.json"
            print(f"Dosya sunucuya yukleniyor: {remote_file_path}")

            with open(local_json_path, 'rb') as f:
                ftp.storbinary(f'STOR {remote_file_path}', f)

            print("Dosya basariyla yuklendi.")
            ftp.quit()

    except Exception as e:
        print(f"FTP YUKLEME HATASI: {e}")
        sys.exit(1)

    print("Veri aktarimi basariyla tamamlandi.")
    print("--------------------------------------------------")

if __name__ == '__main__':
    main()

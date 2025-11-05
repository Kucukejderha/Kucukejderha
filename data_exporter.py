# -*- coding: utf-8 -*-
import pyodbc
import json
import configparser
import paramiko
import os
import sys

def get_script_path():
    """Get the absolute path to the directory where this script is located."""
    return os.path.dirname(os.path.abspath(__file__))

def main():
    """
    Connects to the MS SQL database, fetches product data,
    creates a JSON file, and uploads it to a web server via SFTP.
    """
    script_path = get_script_path()
    config_path = os.path.join(script_path, 'config.ini')

    print("--------------------------------------------------")
    print("Veri Aktarım Betiği Başlatıldı.")

    # --- 1. Read Configuration ---
    if not os.path.exists(config_path):
        print(f"HATA: Yapılandırma dosyası bulunamadı: {config_path}")
        sys.exit(1)

    config = configparser.ConfigParser()
    config.read(config_path)

    print("Yapılandırma dosyası okundu.")

    # Database connection details
    db_config = config['DATABASE']
    server = db_config.get('server')
    database = db_config.get('database')
    username = db_config.get('username')
    password = db_config.get('password')
    driver = db_config.get('driver', '{ODBC Driver 17 for SQL Server}') # Default driver

    # SFTP connection details
    sftp_config = config['SFTP']
    sftp_host = sftp_config.get('host')
    sftp_port = sftp_config.getint('port', 22)
    sftp_user = sftp_config.get('username')
    sftp_pass = sftp_config.get('password')
    sftp_remote_path = sftp_config.get('remote_path')

    local_json_path = os.path.join(script_path, 'urunler.json')

    # --- 2. Connect to Database and Fetch Data ---
    products = []
    try:
        conn_str = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'
        print(f"Veritabanına bağlanılıyor: {server}...")
        with pyodbc.connect(conn_str, timeout=10) as conn:
            print("Veritabanı bağlantısı başarılı.")
            cursor = conn.cursor()

            # This query joins the product info table with the barcode table.
            # It groups by the product and aggregates all barcodes into a single comma-separated string.
            # STRING_AGG is available on SQL Server 2017 and later.
            # For older versions, a different approach (like FOR XML PATH) would be needed.
            query = """
                SELECT
                    s.STOK_KODU,
                    s.STOK_ADI,
                    s.OLCU_BR1,
                    STRING_AGG(b.BARKOD, ',') AS Barkodlar
                FROM
                    TBLSTSABIT s
                LEFT JOIN
                    TBLSTOKBAR b ON s.STOK_KODU = b.STOK_KODU
                WHERE
                    s.STOK_KODU IS NOT NULL AND b.BARKOD IS NOT NULL
                GROUP BY
                    s.STOK_KODU, s.STOK_ADI, s.OLCU_BR1
                ORDER BY
                    s.STOK_KODU;
            """

            print("Veri sorgusu çalıştırılıyor...")
            cursor.execute(query)

            # Fetch data and convert to a list of dictionaries
            columns = [column[0] for column in cursor.description]
            for row in cursor.fetchall():
                products.append(dict(zip(columns, row)))

            print(f"Başarıyla {len(products)} adet ürün çekildi.")

    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        print(f"VERİTABANI HATASI: {sqlstate}")
        print(ex)
        sys.exit(1)
    except Exception as e:
        print(f"Beklenmedik bir veritabanı hatası oluştu: {e}")
        sys.exit(1)

    # --- 3. Create JSON File ---
    if not products:
        print("Uyarı: Veritabanından hiç ürün çekilemedi. İşlem sonlandırılıyor.")
        sys.exit(0)

    try:
        # Remap keys to match the web application's expectations
        output_data = [
            {
                'stok_kodu': p['STOK_KODU'],
                'stok_adi': p['STOK_ADI'],
                'olcu_br1': p['OLCU_BR1'],
                'barkod': p['Barkodlar']
            }
            for p in products
        ]

        print(f"JSON dosyası oluşturuluyor: {local_json_path}")
        with open(local_json_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=4)
        print("JSON dosyası başarıyla oluşturuldu.")

    except Exception as e:
        print(f"JSON dosyası yazılırken bir hata oluştu: {e}")
        sys.exit(1)

    # --- 4. Upload via SFTP ---
    try:
        print(f"SFTP sunucusuna bağlanılıyor: {sftp_host}...")
        with paramiko.Transport((sftp_host, sftp_port)) as transport:
            transport.connect(username=sftp_user, password=sftp_pass)
            with paramiko.SFTPClient.from_transport(transport) as sftp:
                remote_file_path = f"{sftp_remote_path.rstrip('/')}/urunler.json"
                print(f"Dosya sunucuya yükleniyor: {remote_file_path}")
                sftp.put(local_json_path, remote_file_path)
                print("Dosya başarıyla yüklendi.")

    except Exception as e:
        print(f"SFTP YÜKLEME HATASI: Dosya yüklenirken bir hata oluştu.")
        print(e)
        sys.exit(1)

    print("Veri aktarımı başarıyla tamamlandı.")
    print("--------------------------------------------------")


if __name__ == '__main__':
    main()

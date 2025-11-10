# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox, Frame, Label, Entry, Button, LabelFrame, StringVar, Text, Scrollbar, END
import configparser
import os
import datetime
import json
import pyodbc
from ftplib import FTP

# --- Constants ---
CONFIG_FILE = 'config.ini'
LOG_FILE = 'log.txt'
JSON_FILE = 'urunler.json'

# --- Main Application Class ---
class ManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sayım Uygulaması - Veri Aktarım Yöneticisi")
        self.root.geometry("700x650")
        self.config = configparser.ConfigParser()
        self.script_path = os.path.dirname(os.path.abspath(__file__))

        # --- UI Setup (omitted for brevity, same as before) ---
        top_frame = Frame(root); top_frame.pack(padx=10, pady=5, fill="x")
        middle_frame = Frame(root); middle_frame.pack(padx=10, pady=5, fill="x")
        log_frame = LabelFrame(root, text="İşlem Kayıtları (Log)", padx=10, pady=10); log_frame.pack(padx=10, pady=10, fill="both", expand=True)
        db_frame = LabelFrame(top_frame, text="Veritabanı Ayarları (MS SQL)", padx=10, pady=10); db_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ewns")
        ftp_frame = LabelFrame(top_frame, text="Web Sunucusu Ayarları (FTP)", padx=10, pady=10); ftp_frame.grid(row=0, column=1, padx=5, pady=5, sticky="ewns")
        top_frame.grid_columnconfigure(0, weight=1); top_frame.grid_columnconfigure(1, weight=1)

        self.db_vars = {'server': StringVar(), 'database': StringVar(), 'username': StringVar(), 'password': StringVar()}
        self._create_entry(db_frame, "Sunucu Adresi:", self.db_vars['server']); self._create_entry(db_frame, "Veritabanı Adı:", self.db_vars['database']); self._create_entry(db_frame, "Kullanıcı Adı:", self.db_vars['username']); self._create_entry(db_frame, "Şifre:", self.db_vars['password'], show="*")

        self.ftp_vars = {'host': StringVar(), 'port': StringVar(value="21"), 'username': StringVar(), 'password': StringVar(), 'remote_path': StringVar()}
        self._create_entry(ftp_frame, "Sunucu Adresi (Host):", self.ftp_vars['host']); self._create_entry(ftp_frame, "Port:", self.ftp_vars['port']); self._create_entry(ftp_frame, "Kullanıcı Adı:", self.ftp_vars['username']); self._create_entry(ftp_frame, "Şifre:", self.ftp_vars['password'], show="*"); self._create_entry(ftp_frame, "Uzak Dosya Yolu:", self.ftp_vars['remote_path'])

        Button(middle_frame, text="Ayarları Kaydet", command=self.save_config, bg="#007bff", fg="white", font=('Helvetica', 10, 'bold')).pack(side="left", expand=True, fill="x", padx=5, pady=5)
        Button(middle_frame, text="1. Veriyi Çek ve JSON Oluştur", command=self.export_data_to_json, font=('Helvetica', 10, 'bold')).pack(side="left", expand=True, fill="x", padx=5, pady=5)
        Button(middle_frame, text="2. JSON'u FTP'ye Yükle", command=self.upload_json_to_ftp, font=('Helvetica', 10, 'bold')).pack(side="left", expand=True, fill="x", padx=5, pady=5)

        self.log_text = Text(log_frame, wrap="word", height=15, state="normal", bg="#f0f0f0"); scrollbar = Scrollbar(log_frame, command=self.log_text.yview); self.log_text.config(yscrollcommand=scrollbar.set); self.log_text.pack(side="left", fill="both", expand=True); scrollbar.pack(side="right", fill="y")

        self.load_config()
        self.log("Uygulama başlatıldı.")

    def _create_entry(self, parent, text, var, show=None):
        frame = Frame(parent); frame.pack(fill="x", pady=2, anchor="w"); Label(frame, text=text, width=15, anchor="w").pack(side="left"); Entry(frame, textvariable=var, show=show).pack(side="left", expand=True, fill="x")

    def log(self, message, is_error=False):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {'HATA: ' if is_error else ''}{message}\n"
        self.log_text.config(state="normal"); self.log_text.insert(END, log_entry); self.log_text.see(END); self.log_text.config(state="disabled")
        log_file_path = os.path.join(self.script_path, LOG_FILE)
        with open(log_file_path, "a", encoding="utf-8") as f: f.write(log_entry)

    def load_config(self):
        config_path = os.path.join(self.script_path, CONFIG_FILE)
        if not os.path.exists(config_path): self.log("Yapılandırma dosyası bulunamadı.", is_error=True); return
        try:
            self.config.read(config_path)
            if 'DATABASE' in self.config:
                for key, var in self.db_vars.items(): var.set(self.config['DATABASE'].get(key, ''))
            if 'FTP' in self.config:
                for key, var in self.ftp_vars.items(): var.set(self.config['FTP'].get(key, ''))
            self.log("Mevcut ayarlar yüklendi.")
        except Exception as e: self.log(f"Yapılandırma dosyası okunurken hata: {e}", is_error=True)

    def save_config(self):
        self.log("Ayarlar kaydediliyor..."); self.config['DATABASE'] = {key: var.get() for key, var in self.db_vars.items()}; self.config['FTP'] = {key: var.get() for key, var in self.ftp_vars.items()}
        config_path = os.path.join(self.script_path, CONFIG_FILE)
        try:
            with open(config_path, 'w') as configfile: self.config.write(configfile)
            self.log("Ayarlar başarıyla kaydedildi!"); messagebox.showinfo("Başarılı", "Ayarlar kaydedildi.")
        except Exception as e: self.log(f"Ayarlar kaydedilemedi: {e}", is_error=True); messagebox.showerror("Hata", f"Ayarlar kaydedilemedi:\n{e}")

    def export_data_to_json(self):
        self.log("Veri çekme ve JSON oluşturma işlemi başlatıldı.")
        try:
            db = self.db_vars
            conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={db['server'].get()};DATABASE={db['database'].get()};UID={db['username'].get()};PWD={db['password'].get()};TrustServerCertificate=yes;"

            self.log(f"Veritabanına bağlanılıyor: {db['server'].get()}...")
            with pyodbc.connect(conn_str, timeout=10) as conn:
                self.log("Veritabanı bağlantısı başarılı.")
                cursor = conn.cursor()
                query = """
                    SELECT s.STOK_KODU, s.STOK_ADI, s.OLCU_BR1, STRING_AGG(b.BARKOD, ',') AS Barkodlar
                    FROM TBLSTSABIT s LEFT JOIN TBLSTOKBAR b ON s.STOK_KODU = b.STOK_KODU
                    WHERE s.STOK_KODU IS NOT NULL AND b.BARKOD IS NOT NULL
                    GROUP BY s.STOK_KODU, s.STOK_ADI, s.OLCU_BR1 ORDER BY s.STOK_KODU;
                """
                cursor.execute(query)
                columns = [column[0] for column in cursor.description]
                products = [dict(zip(columns, row)) for row in cursor.fetchall()]
                self.log(f"{len(products)} adet ürün başarıyla çekildi.")

            output_data = [{'stok_kodu': p['STOK_KODU'], 'stok_adi': p['STOK_ADI'], 'olcu_br1': p['OLCU_BR1'], 'barkod': p['Barkodlar']} for p in products]
            json_path = os.path.join(self.script_path, JSON_FILE)
            with open(json_path, 'w', encoding='utf-8') as f: json.dump(output_data, f, ensure_ascii=False)

            self.log(f"'{JSON_FILE}' dosyası başarıyla oluşturuldu.")
            messagebox.showinfo("Başarılı", f"{len(products)} ürün '{JSON_FILE}' dosyasına yazıldı.")
        except Exception as e:
            self.log(f"Veri çekme işlemi sırasında hata: {e}", is_error=True); messagebox.showerror("Hata", f"Veri çekme işlemi başarısız:\n{e}")

    def upload_json_to_ftp(self):
        self.log("FTP yükleme işlemi başlatıldı.")
        json_path = os.path.join(self.script_path, JSON_FILE)
        if not os.path.exists(json_path):
            self.log(f"'{JSON_FILE}' bulunamadı. Lütfen önce veri çekme işlemini yapın.", is_error=True)
            messagebox.showwarning("Uyarı", f"'{JSON_FILE}' bulunamadı.\nLütfen önce 'Veriyi Çek' butonuna tıklayın.")
            return

        try:
            ftp_cfg = self.ftp_vars
            host, port, user, passwd, remote_path = ftp_cfg['host'].get(), int(ftp_cfg['port'].get()), ftp_cfg['username'].get(), ftp_cfg['password'].get(), ftp_cfg['remote_path'].get()

            self.log(f"FTP sunucusuna bağlanılıyor: {host}...")
            with FTP() as ftp:
                ftp.connect(host, port, timeout=30)
                ftp.login(user, passwd)
                self.log("FTP bağlantısı başarılı.")

                remote_file = f"{remote_path.rstrip('/')}/{JSON_FILE}"
                self.log(f"Dosya '{remote_file}' konumuna yükleniyor...")
                with open(json_path, 'rb') as f:
                    ftp.storbinary(f'STOR {remote_file}', f)

                self.log("Dosya başarıyla yüklendi.")
                messagebox.showinfo("Başarılı", f"'{JSON_FILE}' dosyası sunucuya başarıyla yüklendi.")
                ftp.quit()
        except Exception as e:
            self.log(f"FTP yükleme sırasında hata: {e}", is_error=True)
            messagebox.showerror("Hata", f"FTP yüklemesi başarısız:\n{e}")

if __name__ == '__main__':
    root = tk.Tk()
    app = ManagerApp(root)
    root.mainloop()

# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox, Frame, Label, Entry, Button, LabelFrame, StringVar
import configparser
import os
import pyodbc
from ftplib import FTP, error_perm

# --- Configuration File Handling ---
CONFIG_FILE = 'config.ini'

def get_script_path():
    """Get the absolute path to the directory where this script is located."""
    return os.path.dirname(os.path.abspath(__file__))

# --- Main Application Class ---
class SettingsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sayım Uygulaması Ayarları")
        self.root.geometry("550x500")
        self.config = configparser.ConfigParser()

        # --- Create UI Frames ---
        db_frame = LabelFrame(root, text="Veritabanı Ayarları (MS SQL)", padx=10, pady=10)
        db_frame.pack(padx=10, pady=10, fill="x")

        ftp_frame = LabelFrame(root, text="Web Sunucusu Ayarları (FTP)", padx=10, pady=10)
        ftp_frame.pack(padx=10, pady=10, fill="x")

        action_frame = Frame(root, padx=10, pady=10)
        action_frame.pack(fill="x")

        # --- Database Section Widgets ---
        self.db_vars = {
            'server': StringVar(), 'database': StringVar(),
            'username': StringVar(), 'password': StringVar()
        }
        self._create_entry(db_frame, "Sunucu Adresi:", self.db_vars['server'])
        self._create_entry(db_frame, "Veritabanı Adı:", self.db_vars['database'])
        self._create_entry(db_frame, "Kullanıcı Adı:", self.db_vars['username'])
        self._create_entry(db_frame, "Şifre:", self.db_vars['password'], show="*")
        Button(db_frame, text="Veritabanı Bağlantısını Sına", command=self._test_db_connection).pack(pady=5)

        # --- FTP Section Widgets ---
        self.ftp_vars = {
            'host': StringVar(), 'port': StringVar(value="21"),
            'username': StringVar(), 'password': StringVar(),
            'remote_path': StringVar()
        }
        self._create_entry(ftp_frame, "Sunucu Adresi (Host):", self.ftp_vars['host'])
        self._create_entry(ftp_frame, "Port:", self.ftp_vars['port'])
        self._create_entry(ftp_frame, "Kullanıcı Adı:", self.ftp_vars['username'])
        self._create_entry(ftp_frame, "Şifre:", self.ftp_vars['password'], show="*")
        self._create_entry(ftp_frame, "Uzak Dosya Yolu:", self.ftp_vars['remote_path'])
        Button(ftp_frame, text="FTP Bağlantısını Sına", command=self._test_ftp_connection).pack(pady=5)

        # --- Action Buttons ---
        Button(action_frame, text="Ayarları Kaydet", command=self._save_config, bg="#28a745", fg="white", font=('Helvetica', 10, 'bold')).pack(side="left", expand=True, fill="x", padx=5)
        Button(action_frame, text="Kapat", command=root.quit, bg="#6c757d", fg="white").pack(side="left", expand=True, fill="x", padx=5)

        # --- Status Bar ---
        self.status_var = StringVar()
        Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor="w").pack(side="bottom", fill="x")

        # --- Load initial config ---
        self._load_config()

    def _create_entry(self, parent, text, var, show=None):
        """Helper to create a labeled entry."""
        frame = Frame(parent)
        frame.pack(fill="x", pady=2)
        Label(frame, text=text, width=15, anchor="w").pack(side="left")
        Entry(frame, textvariable=var, show=show).pack(side="right", expand=True, fill="x")

    def _load_config(self):
        """Loads settings from config.ini if it exists."""
        config_path = os.path.join(get_script_path(), CONFIG_FILE)
        if not os.path.exists(config_path):
            self.status_var.set("Yapılandırma dosyası bulunamadı. Lütfen ayarları girip kaydedin.")
            return

        self.config.read(config_path)
        if 'DATABASE' in self.config:
            for key, var in self.db_vars.items():
                var.set(self.config['DATABASE'].get(key, ''))
        if 'FTP' in self.config:
            for key, var in self.ftp_vars.items():
                var.set(self.config['FTP'].get(key, ''))
        self.status_var.set("Mevcut ayarlar yüklendi.")

    def _save_config(self):
        """Saves current settings to config.ini."""
        self.config['DATABASE'] = {key: var.get() for key, var in self.db_vars.items()}
        self.config['FTP'] = {key: var.get() for key, var in self.ftp_vars.items()}

        config_path = os.path.join(get_script_path(), CONFIG_FILE)
        try:
            with open(config_path, 'w') as configfile:
                self.config.write(configfile)
            self.status_var.set("Ayarlar başarıyla kaydedildi!")
            messagebox.showinfo("Başarılı", "Ayarlar başarıyla kaydedildi.")
        except Exception as e:
            self.status_var.set(f"HATA: Ayarlar kaydedilemedi: {e}")
            messagebox.showerror("Hata", f"Ayarlar kaydedilirken bir hata oluştu:\n{e}")

    def _test_db_connection(self):
        """Tests the MS SQL database connection with the provided credentials."""
        self.status_var.set("Veritabanı bağlantısı test ediliyor...")
        try:
            conn_str = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={self.db_vars['server'].get()};"
                f"DATABASE={self.db_vars['database'].get()};"
                f"UID={self.db_vars['username'].get()};"
                f"PWD={self.db_vars['password'].get()};"
                f"TrustServerCertificate=yes;" # Added for flexibility
                f"Connection Timeout=5;"
            )
            with pyodbc.connect(conn_str, timeout=5) as conn:
                if conn:
                    self.status_var.set("Veritabanı bağlantısı BAŞARILI!")
                    messagebox.showinfo("Başarılı", "Veritabanı bağlantısı başarıyla sağlandı.")
        except Exception as e:
            self.status_var.set(f"HATA: Veritabanı bağlantısı başarısız.")
            messagebox.showerror("Bağlantı Hatası", f"Veritabanına bağlanılamadı:\n{e}")

    def _test_ftp_connection(self):
        """Tests the FTP connection with the provided credentials."""
        self.status_var.set("FTP bağlantısı test ediliyor...")
        try:
            host = self.ftp_vars['host'].get()
            port = int(self.ftp_vars['port'].get())
            user = self.ftp_vars['username'].get()
            passwd = self.ftp_vars['password'].get()

            with FTP() as ftp:
                ftp.connect(host, port, timeout=10)
                ftp.login(user, passwd)
                self.status_var.set("FTP bağlantısı BAŞARILI!")
                messagebox.showinfo("Başarılı", f"FTP sunucusuna başarıyla bağlanıldı.\nSunucu Mesajı: {ftp.getwelcome()}")
                ftp.quit()
        except Exception as e:
            self.status_var.set(f"HATA: FTP bağlantısı başarısız.")
            messagebox.showerror("Bağlantı Hatası", f"FTP sunucusuna bağlanılamadı:\n{e}")


if __name__ == '__main__':
    root = tk.Tk()
    app = SettingsApp(root)
    root.mainloop()

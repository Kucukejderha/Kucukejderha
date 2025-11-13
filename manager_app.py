import tkinter as tk
from tkinter import font
import socket
import http.server
import socketserver
import threading
import sys
import os

# --- Ayarlar ---
PORT = 8000

# --- Ana Uygulama ---
class App:
    def __init__(self, root):
        self.root = root
        self.setup_ui()
        self.start_server_and_find_ip()

    def setup_ui(self):
        self.root.title("Barkodlu Sayım Sunucusu")
        self.root.geometry("600x250")
        self.root.configure(bg="#f0f0f0")

        # Fontlar
        title_font = font.Font(family="Helvetica", size=16, weight="bold")
        url_font = font.Font(family="Courier", size=14)
        info_font = font.Font(family="Helvetica", size=11)

        # Başlık
        title_label = tk.Label(self.root, text="Sayım Programı Başlatıldı", font=title_font, bg="#f0f0f0", fg="#333")
        title_label.pack(pady=(20, 10))

        # Talimat
        info_text = "Lütfen telefonunuzun kamerasını açın ve aşağıdaki adresi tarayıcınıza yazın:"
        info_label = tk.Label(self.root, text=info_text, font=info_font, bg="#f0f0f0", wraplength=550)
        info_label.pack(pady=5)

        # IP Adresi ve URL'yi gösterecek alan
        self.url_label = tk.Label(self.root, text="IP adresi aranıyor...", font=url_font, bg="#ffffff", fg="#007bff", relief="solid", padx=10, pady=10)
        self.url_label.pack(pady=15, fill="x", padx=20)

        # Durum
        self.status_label = tk.Label(self.root, text="Sunucu başlatılıyor...", font=info_font, bg="#f0f0f0", fg="gray")
        self.status_label.pack(side="bottom", pady=10)

    def get_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # Herhangi bir adrese bağlanmaya çalışarak yerel IP'yi bulur (gerçek bir bağlantı kurmaz)
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1' # Bulunamazsa
        finally:
            s.close()
        return IP

    def start_server_and_find_ip(self):
        # Sunucuyu bir thread'de başlat
        handler = http.server.SimpleHTTPRequestHandler

        # PyInstaller'ın oluşturduğu geçici dizinde çalışıyorsa, yolu ayarla
        if getattr(sys, 'frozen', False):
            os.chdir(sys._MEIPASS)

        self.httpd = socketserver.TCPServer(("", PORT), handler)
        server_thread = threading.Thread(target=self.httpd.serve_forever)
        server_thread.daemon = True
        server_thread.start()

        # IP adresini bul ve arayüzü güncelle
        ip_address = self.get_local_ip()
        full_url = f"http://{ip_address}:{PORT}/sayim.html"
        self.url_label.config(text=full_url)
        self.status_label.config(text=f"Sunucu {PORT} portunda çalışıyor. Programı kapattığınızda sunucu duracaktır.")

    def on_closing(self):
        print("Sunucu durduruluyor...")
        self.httpd.shutdown()
        self.root.destroy()

# --- Programı Başlat ---
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

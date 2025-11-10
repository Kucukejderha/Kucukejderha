# Barkod ile Sayım Uygulaması - Veri Aktarım Yöneticisi

Bu proje iki ana bölümden oluşur:
1.  **Veri Aktarım Yöneticisi (`manager_app.py`):** Ürün verilerini MS SQL veritabanından çeken, `urunler.json` dosyasını oluşturan ve bu dosyayı FTP ile web sunucusuna yükleyen, kullanıcı arayüzüne sahip bir masaüstü uygulamasıdır.
2.  **Web Uygulaması (`sayim.html`, `sayim.js`):** `urunler.json` dosyasını okuyarak mobil cihazlarda barkod ile sayım yapılmasını sağlayan web arayüzüdür.

---

## Veri Aktarım Yöneticisi'nin Kurulumu ve Kullanımı

Bu bölüm, sunucu tarafında çalışacak olan yönetici programının nasıl kurulacağını ve kullanılacağını açıklar.

### Adım 1: Gereksinimleri Yükleme

Yönetici programını çalıştıracağınız Windows bilgisayarında aşağıdakilerin kurulu olması gerekmektedir:

1.  **Python 3:** [python.org](https://www.python.org/) adresinden indirin. Kurulum sırasında **"Add Python to PATH"** seçeneğini mutlaka işaretleyin.
2.  **Gerekli Python Kütüphaneleri:** `pyodbc` ve `pyinstaller`.
3.  **MS SQL ODBC Sürücüsü:** Gerekliyse [Microsoft'un sitesinden](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server) indirilebilir.

Python kurulduktan sonra, bir Komut İstemi (cmd) veya PowerShell penceresi açıp aşağıdaki komutları çalıştırarak gerekli kütüphaneleri yükleyin:
```sh
pip install pyodbc
pip install pyinstaller
```

### Adım 2: Programı Çalıştırılabilir `.exe` Dosyasına Dönüştürme

1.  Proje dosyalarını (`manager_app.py` vb.) sunucunuzda kalıcı bir klasöre koyun (örn: `C:\SayimYonetici\`).
2.  Bir Komut İstemi veya PowerShell penceresi açın ve bu klasöre gidin: `cd C:\SayimYonetici\`
3.  Aşağıdaki `pyinstaller` komutunu çalıştırarak programı tek bir `.exe` dosyasına dönüştürün:
    ```sh
    pyinstaller --name SayimYonetici --onefile --windowed manager_app.py
    ```
4.  İşlem tamamlandığında, `C:\SayimYonetici\dist\` klasörü içinde **`SayimYonetici.exe`** adında tek bir dosya oluşacaktır. Artık bu dosyayı kullanacaksınız. Diğer `.py` dosyalarına ihtiyacınız kalmamıştır.

### Adım 3: Programı Kullanma

1.  `SayimYonetici.exe` programını çalıştırın.
2.  Açılan arayüzde, **"Veritabanı Ayarları"** ve **"Web Sunucusu Ayarları (FTP)"** bölümlerini kendi sunucu bilgilerinize göre doldurun.
3.  **"Ayarları Kaydet"** butonuna tıklayın. Ayarlarınız, programın yanındaki `config.ini` dosyasına kaydedilecektir.
4.  Veri aktarımını yapmak istediğinizde:
    *   Önce **"1. Veriyi Çek ve JSON Oluştur"** butonuna tıklayın. İşlem bittiğinde `urunler.json` dosyası programın yanında oluşacaktır.
    *   Ardından **"2. JSON'u FTP'ye Yükle"** butonuna tıklayarak bu dosyayı web sunucunuza gönderin.
5.  Tüm işlemlerin sonuçlarını ve olası hataları, arayüzün altındaki **"İşlem Kayıtları (Log)"** bölümünden veya programın yanındaki `log.txt` dosyasından takip edebilirsiniz.

Bu program, veri güncellemelerini sizin kontrolünüzde, istediğiniz zaman yapmanızı sağlar. Otomasyona ihtiyaç duyulmamıştır.

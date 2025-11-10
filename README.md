# Barkod ile Sayım Uygulaması - Veri Aktarım Betiği

Bu döküman, "Barkod ile Sayım" web uygulamasının ihtiyaç duyduğu ürün verilerini MS SQL veritabanından otomatik olarak çeken ve web sunucusuna aktaran basit Python betiğinin kurulumunu ve kullanımını açıklar.

Bu yöntem, karmaşık Windows servisi kurulumu yerine, standart **Windows Görev Zamanlayıcı** kullanarak otomasyon sağlar.

---

## Kurulum ve Kullanım

### Adım 1: Gereksinimleri Yükleme

Betiğin çalışacağı Windows sunucusunda aşağıdakilerin kurulu olması gerekmektedir:

1.  **Python 3:** [python.org](https://www.python.org/) adresinden indirin. Kurulum sırasında **"Add Python to PATH"** seçeneğini mutlaka işaretleyin.
2.  **Gerekli Python Kütüphaneleri:** `pyodbc`. (FTP kütüphanesi Python'da standart olarak gelir.)
3.  **MS SQL ODBC Sürücüsü:** Betiğin veritabanına bağlanabilmesi için gereklidir. Genellikle SQL Server ile birlikte gelir, ancak eksikse [Microsoft'un sitesinden](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server) indirilebilir.

Python kurulduktan sonra, bir Komut İstemi (cmd) veya PowerShell penceresi açıp aşağıdaki komutu çalıştırarak `pyodbc` kütüphanesini yükleyin:
```sh
pip install pyodbc
```

### Adım 2: Dosyaları Yerleştirme ve Yapılandırma

1.  `data_exporter.py` ve `config.ini.template` dosyalarını, sunucunuzda kalıcı bir klasöre koyun (örn: `C:\SayimBetik\`).
2.  `config.ini.template` dosyasının adını `config.ini` olarak değiştirin.
3.  `config.ini` dosyasını bir metin düzenleyici (Notepad) ile açın ve **kendi bilgilerinize göre** doldurun:
    *   `[DATABASE]` bölümüne MS SQL veritabanı bağlantı bilgilerinizi girin.
    *   `[FTP]` bölümüne web sunucunuzun FTP bilgilerini ve `urunler.json` dosyasının yükleneceği yolu (`remote_path`) girin.
4.  Dosyayı kaydedin.

### Adım 3: Manuel Test

Her şeyin doğru çalıştığından emin olmak için betiği önce bir kez elle çalıştırın:
1.  Bir Komut İstemi veya PowerShell penceresi açın.
2.  Betiğin bulunduğu klasöre gidin: `cd C:\SayimBetik\`
3.  Betiği çalıştırın: `python data_exporter.py`
4.  Ekranda "Veri aktarimi basariyla tamamlandi." mesajını görmelisiniz. Web sunucunuzdaki ilgili klasörü kontrol ederek `urunler.json` dosyasının yüklendiğini doğrulayın.

### Adım 4: Otomatik Görev Olarak Zamanlama (Windows Görev Zamanlayıcı)

Bu betiğin belirli aralıklarla (örneğin her saat başı) otomatik çalışmasını sağlamak için:

1.  Başlat menüsüne **"Görev Zamanlayıcı"** (Task Scheduler) yazıp uygulamayı açın.
2.  Sağdaki "Eylemler" menüsünden **"Temel Görev Oluştur..."** seçeneğine tıklayın.
3.  **Ad:** "Sayim Veri Aktarimi", **Açıklama:** "Sayım uygulaması için veritabanından JSON oluşturup sunucuya aktarır." yazıp "İleri" deyin.
4.  **Tetikleyici:** Görevin ne sıklıkla çalışacağını seçin ("Günlük", "Saatlik" vb.). "İleri" deyin.
5.  **Zamanlama:** Başlangıç tarihini ve saatini ayarlayın. "İleri" deyin.
6.  **Eylem:** **"Program başlat"** seçeneğini seçip "İleri" deyin.
7.  Açılan pencerede:
    *   **Program/betik:** `python.exe` yazın. (PATH'e doğru eklendiyse bu yeterlidir).
    *   **Bağımsız değişken ekle (isteğe bağlı):** `data_exporter.py` dosyanızın tam yolunu yazın. Örneğin: `C:\SayimBetik\data_exporter.py`
    *   **Başlat (isteğe bağlı):** Betiğin bulunduğu klasörün yolunu yazın. Örneğin: `C:\SayimBetik\`
8.  "Son" butonuna tıklayarak görevi oluşturun.

Artık bu betik, belirlediğiniz aralıklarla otomatik olarak çalışacak ve ürün listenizi güncel tutacaktır. Bu yöntem, Windows servisine göre çok daha basit ve yönetimi kolaydır.

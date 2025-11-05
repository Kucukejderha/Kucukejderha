# Barkod ile Sayım Uygulaması - Sunucu Kurulum ve Kullanım Talimatları

Bu döküman, Barkod ile Sayım uygulamasının veritabanı ile entegre bir şekilde çalışması için gereken sunucu tarafı kurulumunu ve kullanımını adım adım açıklamaktadır.

---

### 1. Sisteme Genel Bakış

Bu sistem iki ana bölümden oluşur:

1.  **Veri Aktarım Betiği (`data_exporter.py`):**
    *   Bu Python betiği, MS SQL veritabanınızın kurulu olduğu sunucuda çalışır.
    *   Veritabanınıza bağlanır, ürün ve barkod bilgilerini çeker.
    *   Bu bilgileri `urunler.json` adında tek bir dosyada birleştirir.
    *   Son olarak, bu `urunler.json` dosyasını web sitenizin bulunduğu sunucuya (hosting) SFTP/FTP ile yükler.

2.  **Web Uygulaması (`sayim.html` ve `sayim.js`):**
    *   Bu iki dosya, web sitenizin sunucusunda bulunur (`rotaniz.com/sayim/` gibi).
    *   Kullanıcı uygulamayı açtığında, sunucuya yüklenmiş olan `urunler.json` dosyasını okuyarak ürün listesini alır ve sayım işlemine hazır hale gelir.

Bu yapı sayesinde, ürün listenizdeki herhangi bir değişiklik (yeni ürün, yeni barkod vb.) otomatik olarak web uygulamasına yansır.

---

### 2. Sunucu Gereksinimleri

Veritabanı sunucunuzda (veya betiği çalıştıracağınız herhangi bir Windows sunucuda) aşağıdakilerin kurulu olması gerekmektedir:

*   **Python 3:** Eğer kurulu değilse, [python.org](https://www.python.org/downloads/) adresinden indirebilirsiniz. Kurulum sırasında "Add Python to PATH" seçeneğini işaretlemeyi unutmayın.
*   **Gerekli Python Kütüphaneleri:** `pyodbc` ve `paramiko`.
*   **MS SQL ODBC Sürücüsü:** Betiğin veritabanına bağlanabilmesi için gereklidir. Genellikle SQL Server ile birlikte gelir, ancak eksikse [Microsoft'un sitesinden](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server) indirilebilir.

---

### 3. Kurulum Adımları

**Adım 1: Dosyaları Yerleştirme**

*   **Web Sunucusu İçin:** `sayim.html` ve `sayim.js` dosyalarını, web sitenizin sunucusunda uygulamanın çalışmasını istediğiniz klasöre yükleyin (örneğin, `public_html/sayim/`).
*   **Veritabanı Sunucusu İçin:** `data_exporter.py` ve `config.ini.template` dosyalarını, veritabanı sunucunuzda bu betiğin çalışacağı bir klasöre koyun (örneğin, `C:\SayimBetik\`).

**Adım 2: Python Kütüphanelerini Yükleme**

1.  Veritabanı sunucunuzda Komut İstemi'ni (Command Prompt veya cmd) **yönetici olarak** çalıştırın.
2.  Aşağıdaki komutları sırasıyla yazıp Enter'a basın:
    ```sh
    pip install pyodbc
    pip install paramiko
    ```

**Adım 3: Yapılandırma Dosyasını Doldurma**

1.  Veritabanı sunucusundaki `C:\SayimBetik\` klasörüne gidin.
2.  `config.ini.template` dosyasının adını `config.ini` olarak değiştirin.
3.  `config.ini` dosyasını bir metin düzenleyici (Notepad gibi) ile açın ve **kendi bilgilerinize göre** doldurun:
    *   `[DATABASE]` bölümüne MS SQL veritabanı bağlantı bilgilerinizi girin.
    *   `[SFTP]` bölümüne web sunucunuzun FTP/SFTP bilgilerini ve `urunler.json` dosyasının yükleneceği yolu (`remote_path`) girin.
4.  Dosyayı UTF-8 formatında kaydedin.

---

### 4. Betiği Çalıştırma ve Otomatikleştirme

**Adım 1: Manuel Test**

Her şeyin doğru çalıştığından emin olmak için betiği önce bir kez elle çalıştırın:
1.  Komut İstemi'ni açın.
2.  Betiğin bulunduğu klasöre gidin: `cd C:\SayimBetik\`
3.  Betiği çalıştırın: `python data_exporter.py`
4.  Ekranda "Veri aktarımı başarıyla tamamlandı." mesajını görmelisiniz. Ayrıca web sunucunuzdaki `sayim` klasörünü kontrol ederek `urunler.json` dosyasının oraya yüklendiğini doğrulayın.

**Adım 2: Otomatik Görev Olarak Zamanlama (Windows Görev Zamanlayıcı)**

Bu betiğin belirli aralıklarla (örneğin her saat başı) otomatik çalışmasını sağlamak, verilerinizin hep güncel kalması için kritiktir.

1.  Başlat menüsüne "Görev Zamanlayıcı" (Task Scheduler) yazıp uygulamayı açın.
2.  Sağdaki "Eylemler" menüsünden "Temel Görev Oluştur..." seçeneğine tıklayın.
3.  **Ad:** "Sayim Veri Aktarimi", **Açıklama:** "Sayım uygulaması için veritabanından JSON oluşturup sunucuya aktarır." yazıp "İleri" deyin.
4.  **Tetikleyici:** Görevin ne sıklıkla çalışacağını seçin ("Günlük", "Saatlik" vb.). "İleri" deyin.
5.  **Zamanlama:** Başlangıç tarihini ve saatini ayarlayın. "İleri" deyin.
6.  **Eylem:** "Program başlat" seçeneğini seçip "İleri" deyin.
7.  **Program/betik:** `python.exe` dosyasının tam yolunu yazın. (Emin değilseniz, Komut İstemi'ne `where python` yazarak bulabilirsiniz). Genellikle `C:\Python39\python.exe` gibi bir yoldur.
8.  **Bağımsız değişken ekle (isteğe bağlı):** `data_exporter.py` dosyanızın tam yolunu yazın. Örneğin: `C:\SayimBetik\data_exporter.py`
9.  **Başlat (isteğe bağlı):** Betiğin bulunduğu klasörün yolunu yazın. Örneğin: `C:\SayimBetik\`
10. "Son" butonuna tıklayarak görevi oluşturun.

Artık bu betik, belirlediğiniz aralıklarla otomatik olarak çalışacak ve ürün listenizi güncel tutacaktır.

---

### 5. Web Uygulamasının Kullanımı

1.  Telefonunuzun veya bilgisayarınızın tarayıcısından uygulamanızın adresine gidin (örn: `https://rotaniz.com/sayim/sayim.html`).
2.  Uygulama açıldığında, ürün listesi otomatik olarak yüklenecektir.
3.  Kamera görüntüsü ekrana geldiğinde barkod okutmaya başlayabilirsiniz.

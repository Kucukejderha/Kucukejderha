# Barkod ile Sayım Uygulaması - Veri Aktarım Servisi

Bu paket, "Barkod ile Sayım" web uygulamasının ihtiyaç duyduğu ürün verilerini MS SQL veritabanından otomatik olarak çeken ve web sunucusuna aktaran Windows hizmetini içerir.

Bu proje, son kullanıcıların kolayca kurup yönetebilmesi için bir kurulum sihirbazı (`setup.exe`) ve bir ayar arayüzü ile birlikte gelir.

---

## Son Kullanıcılar İçin Kurulum ve Kullanım

Bu bölüm, uygulamayı veritabanı sunucusuna kuracak ve ayarlarını yapacak kişiler içindir.

### Adım 1: Kurulum

1.  Size teslim edilen `SayimUygulamasi_Kurulum_vX.X.X.exe` dosyasını veritabanı sunucunuza kopyalayın.
2.  Kurulum dosyasına çift tıklayın ve kurulum sihirbazındaki adımları takip edin ("İleri" -> "Kur" -> "Son").
3.  Kurulum tamamlandığında, "Sayım Uygulaması Ayarları" programı otomatik olarak başlayacaktır.

### Adım 2: Ayarları Yapılandırma

![Ayar Arayüzü](https://i.imgur.com/your-image-url.png) <!-- Bu URL daha sonra gerçek bir ekran görüntüsü ile değiştirilebilir -->

Açılan "Sayım Uygulaması Ayarları" penceresinde:

1.  **Veritabanı Ayarları (MS SQL):**
    *   **Sunucu Adresi:** MS SQL sunucunuzun IP adresini veya ağ adını girin.
    *   **Veritabanı Adı:** Ürün tablolarının bulunduğu veritabanının adını girin.
    *   **Kullanıcı Adı ve Şifre:** Veritabanına bağlanma yetkisi olan bir kullanıcının bilgilerini girin.
    *   **"Veritabanı Bağlantısını Sına"** butonuna tıklayarak bilgilerin doğru olduğundan emin olun. Başarılı bir "Bağlantı Başarılı" mesajı almalısınız.

2.  **Web Sunucusu Ayarları (SFTP/FTP):**
    *   **Sunucu Adresi (Host):** Web sitenizin barındığı sunucunun FTP/SFTP adresini girin (örn: `rotaniz.com`).
    *   **Port:** Genellikle `22`'dir, farklıysa düzeltin.
    *   **Kullanıcı Adı ve Şifre:** Web sunucusuna dosya yükleme yetkisi olan FTP/SFTP kullanıcınızın bilgilerini girin.
    *   **Uzak Dosya Yolu:** `urunler.json` dosyasının web sunucusunda tam olarak nereye yükleneceğini belirtin (örn: `/public_html/sayim`).
    *   **"SFTP Bağlantısını Sına"** butonuna tıklayarak bu bilgilerin de doğruluğunu kontrol edin.

3.  **Ayarları Kaydet:**
    *   Tüm testler başarılı olduktan sonra, **"Ayarları Kaydet"** butonuna tıklayın.

### Adım 3: Kontrol

Her şey doğru yapıldıysa, "Sayim Veri Aktarim Servisi" adlı Windows hizmeti artık arka planda çalışmaya başlamıştır. Belirlenen aralıklarla (varsayılan olarak saatte bir) veritabanınızı kontrol edecek ve güncel ürün listesini web sunucunuza yükleyecektir.

*   Servisin durumunu kontrol etmek için Windows'ta "Hizmetler" (Services) uygulamasını açıp listede bulabilirsiniz.
*   Servisin işlem kayıtlarını (`service.log`) ve ayar dosyasını (`config.ini`) programın kurulduğu dizinde bulabilirsiniz (genellikle `C:\Program Files (x86)\SayimVeriAktarim`).

---

## Geliştiriciler İçin Derleme Süreci

Bu bölüm, proje dosyalarından yeniden bir `setup.exe` oluşturmak isteyen geliştiriciler içindir. `build.bat` betiği, platform uyumluluk sorunları nedeniyle kullanımdan kaldırılmıştır. Lütfen aşağıdaki manuel adımları takip edin.

### Gereksinimler

1.  **Python 3:** [python.org](https://www.python.org/) (Kurulumda **"Add python.exe to PATH"** seçeneğini işaretlediğinizden emin olun).
2.  **Inno Setup:** [jrsoftware.org](https://jrsoftware.org/isinfo.php) (Standart ayarlarla kurmanız yeterlidir).

### Derleme Adımları

Aşağıdaki komutlar, **proje klasörünün içinde açılmış bir PowerShell penceresinde** sırasıyla çalıştırılmalıdır.

**Adım 0: PowerShell'i Açın**
Proje klasörünün adres çubuğuna `powershell` yazıp Enter'a basarak bir PowerShell penceresi açın.

**Adım 1: Sanal Ortamı Oluşturun**
```powershell
python -m venv venv
```

**Adım 2: Sanal Ortamı Aktifleştirin**
```powershell
.\venv\Scripts\Activate.ps1
```

**Adım 3: Gerekli Kütüphaneleri Yükleyin**
```powershell
pip install pyinstaller pywin32 pyodbc paramiko
```

**Adım 4: Ayar Programını Derleyin (`settings_gui.exe`)**
```powershell
pyinstaller --name settings_gui --onefile --windowed --icon=NONE settings_gui.py
```

**Adım 5: Servis Programını Derleyin (`windows_service.exe`)**
```powershell
pyinstaller --name windows_service --onefile --icon=NONE windows_service.py
```

**Adım 6: Kurulum Dosyasını Oluşturun (`setup.exe`)**
```powershell
& "C:\Program Files (x86)\Inno Setup 6\iscc.exe" setup.iss
```

Bu adımlar tamamlandığında, `Output` klasörünün içinde son kullanıcıya dağıtılabilecek olan `SayimUygulamasi_Kurulum_vX.X.X.exe` dosyası hazır olacaktır.

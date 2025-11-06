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

Bu bölüm, proje dosyalarından yeniden bir `setup.exe` oluşturmak isteyen geliştiriciler içindir.

### Gereksinimler

1.  **Python 3:** [python.org](https://www.python.org/) (Kurulumda "Add Python to PATH" seçeneğini işaretleyin).
2.  **Inno Setup:** [jrsoftware.org](https://jrsoftware.org/isinfo.php) (Kurulumda PATH'e ekleme seçeneğini işaretleyin).

### Derleme Adımları

Projenin ana dizininde bulunan `build.bat` komut dosyasını çalıştırmanız yeterlidir.

```bash
build.bat
```

Bu betik aşağıdaki işlemleri otomatik olarak yapar:
1.  Bir Python sanal ortamı oluşturur.
2.  Gerekli tüm Python kütüphanelerini (`pyinstaller`, `pywin32`, `pyodbc`, `paramiko`) kurar.
3.  `settings_gui.py` ve `windows_service.py` betiklerini, `dist` klasörü altında bağımsız `.exe` dosyalarına derler.
4.  `setup.iss` Inno Setup betiğini kullanarak bu `.exe` dosyalarını ve `config.ini` şablonunu tek bir kurulum dosyasına (`Output` klasörü altında `SayimUygulamasi_Kurulum_vX.X.X.exe`) paketler.

Derleme tamamlandığında, son kullanıcıya dağıtılabilecek olan `setup.exe` dosyası hazır olacaktır.

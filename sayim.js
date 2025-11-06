document.addEventListener('DOMContentLoaded', () => {
    // HTML Elementleri
    const scannerSection = document.getElementById('scanner-section');
    const videoElement = document.getElementById('video');
    const productNameElement = document.getElementById('product-name');
    const productUnitElement = document.getElementById('product-unit');
    const previousCountElement = document.getElementById('previous-count');
    const previousCountContainer = previousCountElement.parentElement;
    const resultsTableBody = document.querySelector("#results-table tbody");
    const exportCsvButton = document.getElementById('export-csv');

    // Veri Depolama
    let productDataByBarcode = new Map();
    let countedItems = new Map(); // Key: stok_kodu, Value: { name, unit, quantity }

    // Barkod Okuyucu
    const codeReader = new ZXing.BrowserMultiFormatReader();
    let isScanning = true;

    // --- 1. Uygulamayı Başlat ---
    // Sayfa yüklendiğinde ürün verilerini sunucudan çek
    initApp();

    async function initApp() {
        try {
            console.log("Ürün verileri sunucudan çekiliyor...");
            // urunler.json dosyasını, sayim.html ile aynı dizinden çekmeye çalışır.
            const response = await fetch('urunler.json');
            if (!response.ok) {
                throw new Error(`Veri dosyası yüklenemedi. Sunucu yanıtı: ${response.statusText}`);
            }
            const data = await response.json();

            processProductData(data);

            scannerSection.classList.remove('hidden'); // Tarayıcıyı göster
            console.log('Ürün listesi başarıyla yüklendi. Kamera başlatılıyor...');
            startScanner(); // Veriler hazır, tarayıcıyı başlat

        } catch (error) {
            console.error("Uygulama başlatılırken hata oluştu:", error);
            alert(`HATA: Ürün listesi sunucudan alınamadı.\n\nDetay: ${error.message}\n\nLütfen 'urunler.json' dosyasının doğru konumda ve geçerli olduğundan emin olun.`);
            // Hata durumunda tarayıcı bölümünü gizli tut
            scannerSection.style.display = 'none';
        }
    }

    // --- 2. Ürün Verisini İşleme ---
    function processProductData(data) {
        productDataByBarcode.clear();
        countedItems.clear();
        data.forEach(row => {
            const sku = row.stok_kodu;
            const name = row.stok_adi;
            const unit = row.olcu_br1;
            // Barkod alanı artık virgülle ayrılmış bir string
            const barcodeString = String(row.barkod || '').trim();

            if (!sku || !name || !unit || !barcodeString) return;

            const productInfo = { sku, name, unit };

            const barcodes = barcodeString.split(',').map(b => b.trim());
            barcodes.forEach(b => {
                if (b) productDataByBarcode.set(b, productInfo);
            });
        });
        console.log(`${productDataByBarcode.size} barkod başarıyla işlendi.`);
    }

    // --- 3. Barkod Okuyucuyu Başlatma ---
    function startScanner() {
        codeReader.getVideoInputDevices()
            .then(videoInputDevices => {
                if (videoInputDevices.length > 0) {
                    const rearCamera = videoInputDevices.find(d => d.label.toLowerCase().includes('back')) || videoInputDevices[videoInputDevices.length - 1];
                    codeReader.decodeFromVideoDevice(rearCamera.deviceId, videoElement, (result, err) => {
                        if (result && isScanning) {
                            isScanning = false;
                            handleBarcode(result.text);
                        }
                        if (err && !(err instanceof ZXing.NotFoundException)) console.error("Tarama Hatası:", err);
                    });
                } else alert("Kamera bulunamadı.");
            })
            .catch(err => {
                console.error("Kamera erişim hatası:", err);
                alert("Kamera izni reddedildi veya bir hata oluştu. Sayfayı yenileyip tekrar deneyin.");
            });
    }

    // --- 4. Stok Sayım Mantığı ---
    function handleBarcode(barcode) {
        const product = productDataByBarcode.get(barcode);
        if (product) {
            productNameElement.textContent = product.name;
            productUnitElement.textContent = product.unit;

            let currentQuantity = countedItems.has(product.sku) ? countedItems.get(product.sku).quantity : 0;
            if (currentQuantity > 0) {
                previousCountElement.textContent = currentQuantity;
                previousCountContainer.classList.remove('hidden');
            }

            const amountStr = prompt(`Ürün: ${product.name}\nMevcut Miktar: ${currentQuantity} ${product.unit}\n\nEklenecek Miktarı Girin:`);

            if (amountStr) {
                const amount = parseFloat(amountStr.replace(',', '.'));
                if (!isNaN(amount) && amount > 0) {
                    countedItems.set(product.sku, { name: product.name, unit: product.unit, quantity: currentQuantity + amount });
                    updateResultsTable();
                } else alert("Lütfen geçerli bir sayı girin.");
            }
            previousCountContainer.classList.add('hidden');
        } else {
            alert('Bu barkod ürün listenizde bulunamadı.');
        }
        setTimeout(() => { isScanning = true; }, 1000);
    }

    // --- 5. Sonuç Tablosunu Güncelleme ---
    function updateResultsTable() {
        resultsTableBody.innerHTML = '';
        countedItems.forEach((item, sku) => {
            const row = resultsTableBody.insertRow();
            row.innerHTML = `<td>${sku}</td><td>${item.name}</td><td>${item.quantity}</td><td>${item.unit}</td>`;
        });
    }

    // --- 6. CSV Dışa Aktarma ---
    exportCsvButton.addEventListener('click', () => {
        if (countedItems.size === 0) {
            alert("Dışa aktarılacak sayım sonucu bulunmuyor.");
            return;
        }

        let csvContent = "data:text/csv;charset=utf-8,stok_kodu,stok_adi,miktar,olcu_br1\n";
        countedItems.forEach((item, sku) => {
            // CSV'de virgül sorunu olmaması için alanları tırnak içine al
            const row = [`"${sku}"`, `"${item.name}"`, item.quantity, `"${item.unit}"`].join(",");
            csvContent += row + "\n";
        });

        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", `sayim_sonuclari_${new Date().toISOString().slice(0,10)}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    });
});

document.addEventListener('DOMContentLoaded', () => {
    // HTML Elementleri
    const scannerSection = document.getElementById('scanner-section');
    const videoElement = document.getElementById('video');
    const productNameElement = document.getElementById('product-name');
    const productUnitElement = document.getElementById('product-unit');
    const previousCountElement = document.getElementById('previous-count');
    const previousCountContainer = previousCountElement.parentElement;
    const userFeedbackElement = document.getElementById('user-feedback');
    const resultsTableBody = document.querySelector("#results-table tbody");
    const exportCsvButton = document.getElementById('export-csv');

    // Veri Depolama
    let productDataByBarcode = new Map();
    let countedItems = new Map();

    // Barkod Okuyucu
    const hints = new Map();
    const formats = [
        ZXing.BarcodeFormat.EAN_13,
        ZXing.BarcodeFormat.EAN_8,
        ZXing.BarcodeFormat.UPC_A,
        ZXing.BarcodeFormat.UPC_E
    ];
    hints.set(ZXing.DecodeHintType.POSSIBLE_FORMATS, formats);
    const codeReader = new ZXing.BrowserMultiFormatReader(hints);

    let isScanning = true;
    let feedbackTimeout;

    // --- 1. Uygulamayı Başlat ---
    initApp();

    async function initApp() {
        try {
            const response = await fetch('urunler.json?v=' + Date.now()); // Cache-busting
            if (!response.ok) throw new Error(`Sunucu yanıtı: ${response.statusText}`);
            const data = await response.json();
            processProductData(data);
            showFeedback('Ürün listesi yüklendi. Kamera başlatılıyor...', 'success');
            startScanner();
        } catch (error) {
            showFeedback(`HATA: Ürün listesi alınamadı. ${error.message}`, 'error');
            scannerSection.style.display = 'none';
        }
    }

    // --- 2. Ürün Verisini İşleme ---
    function processProductData(data) {
        productDataByBarcode.clear();
        countedItems.clear();
        data.forEach(row => {
            if (!row.stok_kodu || !row.stok_adi || !row.olcu_br1 || !row.barkod) return;
            const productInfo = { sku: row.stok_kodu, name: row.stok_adi, unit: row.olcu_br1 };
            const barcodes = String(row.barkod).split(',').map(b => b.trim());
            barcodes.forEach(b => { if (b) productDataByBarcode.set(b, productInfo); });
        });
    }

    // --- 3. Kullanıcı Geri Bildirimi ---
    function showFeedback(message, type = 'error') {
        clearTimeout(feedbackTimeout);
        userFeedbackElement.textContent = message;
        userFeedbackElement.style.color = type === 'error' ? 'var(--danger-color)' : 'var(--success-color)';
        userFeedbackElement.style.display = 'block';

        feedbackTimeout = setTimeout(() => {
            userFeedbackElement.style.display = 'none';
        }, 3000); // Mesaj 3 saniye sonra kaybolur
    }

    // --- 4. Barkod Okuyucuyu Başlatma ---
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
                } else showFeedback("Kamera bulunamadı.", 'error');
            })
            .catch(err => showFeedback("Kamera izni reddedildi veya hata oluştu.", 'error'));
    }

    // --- 5. Stok Sayım Mantığı ---
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
                } else {
                    showFeedback("Geçersiz miktar girdiniz!", 'error');
                }
            }
            previousCountContainer.classList.add('hidden');
        } else {
            showFeedback(`Barkod bulunamadı: ${barcode}`, 'error');
        }
        setTimeout(() => { isScanning = true; }, 1500); // Kullanıcının geri bildirimi görmesi için bekleme süresi
    }

    // --- 6. Sonuç Tablosunu Güncelleme ---
    function updateResultsTable() {
        resultsTableBody.innerHTML = '';
        countedItems.forEach((item, sku) => {
            const row = resultsTableBody.insertRow();
            row.innerHTML = `<td>${sku}</td><td>${item.name}</td><td>${item.quantity}</td><td>${item.unit}</td>`;
        });
    }

    // --- 7. CSV Dışa Aktarma ---
    exportCsvButton.addEventListener('click', () => {
        if (countedItems.size === 0) {
            messagebox.showwarning("Uyarı", "Dışa aktarılacak sayım sonucu bulunmuyor.");
            return;
        }
        let csvContent = "data:text/csv;charset=utf-8,stok_kodu,stok_adi,miktar,olcu_br1\n";
        countedItems.forEach((item, sku) => {
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

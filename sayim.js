document.addEventListener('DOMContentLoaded', () => {
    // HTML Elementleri
    const fileInput = document.getElementById('file-input');
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

    // 1. Dosya Yükleme Mantığı
    fileInput.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = (e) => {
            const data = new Uint8Array(e.target.result);
            const workbook = XLSX.read(data, { type: 'array' });
            const firstSheetName = workbook.SheetNames[0];
            const worksheet = workbook.Sheets[firstSheetName];
            const json = XLSX.utils.sheet_to_json(worksheet);

            processProductData(json);
            scannerSection.classList.remove('hidden');
            alert('Ürün listesi başarıyla yüklendi. Kamera başlatılıyor...');
            startScanner();
        };
        reader.readAsArrayBuffer(file);
    });

    // 2. Excel Verisini İşleme
    function processProductData(data) {
        productDataByBarcode.clear();
        countedItems.clear();
        data.forEach(row => {
            const sku = row.stok_kodu;
            const name = row.stok_adi;
            const unit = row.olcu_br1;
            const barcode = String(row.barkod).trim();
            if (!sku || !name || !unit || !barcode) return;

            const productInfo = { sku, name, unit };
            const barcodes = barcode.split(',').map(b => b.trim());
            barcodes.forEach(b => {
                if (b) productDataByBarcode.set(b, productInfo);
            });
        });
    }

    // 3. Barkod Okuyucuyu Başlatma
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
            .catch(err => console.error("Kamera erişim hatası:", err));
    }

    // 4. Stok Sayım Mantığı
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

    // 5. Sonuç Tablosunu Güncelleme
    function updateResultsTable() {
        resultsTableBody.innerHTML = '';
        countedItems.forEach((item, sku) => {
            const row = resultsTableBody.insertRow();
            row.innerHTML = `<td>${sku}</td><td>${item.name}</td><td>${item.quantity}</td><td>${item.unit}</td>`;
        });
    }

    // 6. CSV Dışa Aktarma
    exportCsvButton.addEventListener('click', () => {
        if (countedItems.size === 0) {
            alert("Dışa aktarılacak sayım sonucu bulunmuyor.");
            return;
        }

        let csvContent = "data:text/csv;charset=utf-8,stok_kodu,stok_adi,miktar,olcu_br1\n";
        countedItems.forEach((item, sku) => {
            const row = [sku, item.name, item.quantity, item.unit].join(",");
            csvContent += row + "\n";
        });

        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", "sayim_sonuclari.csv");
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    });
});

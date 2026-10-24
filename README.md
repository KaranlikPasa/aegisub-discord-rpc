# 🎬 Aegisub Discord Rich Presence

Aegisub'da altyazı çevirirken veya düzenlerken Discord profilinizde şık ve detaylı bir **Rich Presence (Oynuyor / Çeviriyor)** aktivitesi gösteren modern Windows uygulaması.

![Aegisub RPC Preview](assets/aegisub_icon_128.png)

---

## ✨ Özellikler

* **🚀 Tam Otomatik Algılama:** Yalnızca gerçek `aegisub.exe` sürecini takip eder. Aegisub açıldığında aktivite otomatik başlar, Aegisub kapandığında Discord aktivitesi anında silinir.
* **🧹 Akıllı Dosya Adı Sadeleştirme:** Release gruplarını, CRC kodlarını ve çözünürlük etiketlerini otomatik temizler:
  * `[SubsPlease] Magical Explorer - 05 (1080p) [BE62F093].tr.ass` ➔ **`Magical Explorer - 05`**
* **🎯 Çeviri / Düzenleme Durumları:**
  * `Altyazı Çeviriyor` (Varsayılan)
  * `Bölüm Çeviriyor`
  * `Zamanlama (Timing) Yapıyor`
  * `Typesetting (Dizgi) Yapıyor`
  * `Karaoke / FX Yapıyor`
  * `Altyazı Kontrolü (QC) Yapıyor`
  * `Özel Metin...` (Serbest açıklama)
* **⏱️ Canlı Süre Sayacı:** Çeviri oturumunuz boyunca geçen süreyi Discord profilinizde canlı olarak gösterir.
* **🔒 Gizlilik / Spoiler Koruması:** İsterseniz dosya adını tek tıkla gizleyebilir veya sabit bir proje adı yazabilirsiniz.
* **📦 Sistem Tepsisi (System Tray):** Kapatıldığında saatin yanına küçülür, arka planda sıfır yük ile sessizce çalışır.
* **🛑 Aegisub ile Otomatik Kapanma:** Aegisub kapatıldığında uygulamanın da arka plandan otomatik kapanmasını sağlar, sistemde asılı kalmaz.
* **⚡ Windows ile Başlatma:** Bilgisayar her açıldığında arka planda başlaması için tek tıkla ayarlanabilir.

---

## 📥 Kurulum ve Çalıştırma

### Yöntem 1: Hazır Exe ile (Önerilen)
1. [Releases](../../releases) sayfasından son sürümü (`AegisubDiscordRPC.zip`) indirin.
2. Klasöre çıkartıp `AegisubDiscordRPC.exe` dosyasını çalıştırın.

### Yöntem 2: Python ile
Gereksinimler: Python 3.10+

```bash
# Bağımlılıkları yükleyin
pip install -r requirements.txt

# Uygulamayı başlatın
python main.py
```

---

## 📝 Sürüm Geçmişi (Changelog)

### v1.0.2
* **Fix (Süreç Tespiti):** Genel pencere başlıkları yerine doğrudan `aegisub.exe` süreci kontrol edilerek başka pencerelerin (tarayıcı, IDE veya uygulamanın kendi penceresi) yanlışlıkla Aegisub sanılması engellendi.
* **Fix (Discord Temizleme):** Aegisub kapandığı anda Discord profilindeki durumun anında silinmesi sağlandı.
* **Özellik:** *Aegisub kapatıldığında bu uygulamayı da otomatik kapat* seçeneği eklendi.

### v1.0.1
* **Fix (Kapanma Kilitlenmesi):** Sistem tepsisindeki *"Tamamen Kapat"* butonuna basıldığında `pystray` menü iş parçacığının kilitlenmesi (deadlock) giderildi, temiz `os._exit(0)` ile sonlandırma sağlandı.
* **Özellik:** Uygulama penceresine kırmızı renkli *"Uygulamayı Tamamen Kapat (Çıkış)"* butonu eklendi.

### v1.0.0
* İlk kararlı sürüm.
* CustomTkinter tabanlı modern karanlık tema arayüzü.
* Aegisub doğrulanmış Discord App ID (592657785368477728) entegrasyonu.
* Akıllı etiket temizleme ve süre sayacı.
* Sistem tepsisi entegrasyonu.

---

## 📄 Lisans
MIT License

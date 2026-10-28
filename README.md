# 🎬 Aegisub Discord Rich Presence

[![Arch Linux](https://img.shields.io/badge/Arch%20Linux-AUR%20%7C%20PKGBUILD-1793d1?style=for-the-badge&logo=arch-linux&logoColor=white)](https://github.com/KaranlikPasa/aegisub-discord-rpc)
[![Platform](https://img.shields.io/badge/Platform-Arch%20Linux%20%7C%20Windows-blue?style=for-the-badge)](https://github.com/KaranlikPasa/aegisub-discord-rpc)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

Aegisub'da altyazı çevirirken veya düzenlerken Discord profilinizde şık ve detaylı bir **Rich Presence (Oynuyor / Çeviriyor)** aktivitesi gösteren modern masaüstü uygulaması. **Arch Linux** ve **Windows** üzerinde tam uyumlu çalışır.

![Aegisub RPC Preview](assets/aegisub_icon_128.png)

---

## ✨ Özellikler

* **🚀 Tam Otomatik Algılama:** Yalnızca gerçek `aegisub` sürecini takip eder. Aegisub açıldığında aktivite otomatik başlar, kapandığında Discord aktivitesi anında silinir.
* **🐧 Tam Arch Linux & Linux Desteği:**
  * X11 (`xdotool`, `wmctrl`) ve Wayland uyumlu pencere / açık dosya algılama.
  * PKGBUILD, `makepkg -si`, `install.sh` tek komutla kurulum, `.desktop` menü kısayolu.
  * `~/.config/autostart` üzerinden sistem başlangıcında otomatik başlama.
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
* **⚡ Sistemle Otomatik Başlatma:** Bilgisayar her açıldığında arka planda başlaması için tek tıkla ayarlanabilir.

---

## 📥 Kurulum ve Çalıştırma

### 🐧 1. Arch Linux Kurulumu

#### Yöntem A: PKGBUILD ile Kurulum
```bash
git clone https://github.com/KaranlikPasa/aegisub-discord-rpc.git
cd aegisub-discord-rpc
makepkg -si
```

#### Yöntem B: Tek Tıkla Kurulum Betiği (`install.sh`)
```bash
git clone https://github.com/KaranlikPasa/aegisub-discord-rpc.git
cd aegisub-discord-rpc
chmod +x install.sh
sudo ./install.sh
```

Kurulumdan sonra uygulama menünüzden **Aegisub Discord RPC**'yi seçebilir veya terminalde doğrudan çalıştırabilirsiniz:
```bash
aegisub-discord-rpc
```

---

### 🪟 2. Windows Kurulumu

#### Hazır .exe İle:
1. [Releases](../../releases) sayfasından son sürümü (`AegisubDiscordRPC.zip`) indirin.
2. Klasöre çıkartıp `AegisubDiscordRPC.exe` dosyasını çalıştırın.

#### Python İle:
```cmd
pip install -r requirements.txt
python main.py
```

---

## 📝 Sürüm Geçmişi (Changelog)

### v1.0.3
* **Arch Linux & Linux Desteği:** `ctypes.windll` bağımlılığı kaldırıldı, `xdotool`, `wmctrl` ve açık altyazı dosyası tespiti ile X11/Wayland tam uyumlu hale getirildi.
* **Arch Linux Paketleme:** `PKGBUILD`, `install.sh`, `.desktop` entegrasyonu ve `~/.config/autostart` desteği eklendi.

### v1.0.2
* **Fix (Süreç Tespiti):** Genel pencere başlıkları yerine doğrudan `aegisub` süreci kontrol edilerek başka pencerelerin yanlışlıkla Aegisub sanılması engellendi.
* **Fix (Discord Temizleme):** Aegisub kapandığı anda Discord profilindeki durumun anında silinmesi sağlandı.
* **Özellik:** *Aegisub kapatıldığında bu uygulamayı da otomatik kapat* seçeneği eklendi.

---

## 📄 Lisans
MIT License

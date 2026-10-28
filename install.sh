#!/usr/bin/env bash
# ==============================================================================
# Aegisub Discord RPC - Arch Linux & Linux Kurulum Betiği
# ==============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}======================================================${NC}"
echo -e "${CYAN}   🎙️ Aegisub Discord RPC - Linux Kurulum Sihirbazı  ${NC}"
echo -e "${CYAN}======================================================${NC}"

if [ "$EUID" -ne 0 ]; then
  echo -e "${YELLOW}[Bilgi] Sistem geneline (/opt/aegisub-discord-rpc) kurulum için root yetkisi gereklidir.${NC}"
  echo -e "Yönetici şifreniz istenebilir..."
  exec sudo "$0" "$@"
fi

INSTALL_DIR="/opt/aegisub-discord-rpc"
BIN_LINK="/usr/bin/aegisub-discord-rpc"
DESKTOP_DIR="/usr/share/applications"
ICONS_BASE="/usr/share/icons/hicolor"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo -e "\n${BLUE}1/4: Sistem Bağımlılıkları Kontrol Ediliyor...${NC}"

if command -v pacman >/dev/null 2>&1; then
    echo -e "${GREEN}Arch Linux tespit edildi. pacman ile bağımlılıklar kuruluyor...${NC}"
    pacman -S --noconfirm --needed python python-pillow python-psutil tk xdotool
elif command -v apt-get >/dev/null 2>&1; then
    echo -e "${GREEN}Debian/Ubuntu tespit edildi. apt ile bağımlılıklar kuruluyor...${NC}"
    apt-get update && apt-get install -y python3 python3-pil python3-psutil python3-tk xdotool
elif command -v dnf >/dev/null 2>&1; then
    echo -e "${GREEN}Fedora tespit edildi. dnf ile bağımlılıklar kuruluyor...${NC}"
    dnf install -y python3 python3-pillow python3-psutil python3-tkinter xdotool
fi

# Pip bağımlılıkları (customtkinter, pypresence, pystray)
echo -e "${BLUE}Python kütüphaneleri kontrol ediliyor (customtkinter, pypresence, pystray)...${NC}"
pip install --break-system-packages -r "$SCRIPT_DIR/requirements.txt" 2>/dev/null || \
pip install -r "$SCRIPT_DIR/requirements.txt" 2>/dev/null || true

echo -e "\n${BLUE}2/4: Uygulama Dosyaları $INSTALL_DIR Dizinine Kopyalanıyor...${NC}"
mkdir -p "$INSTALL_DIR"
cp -r "$SCRIPT_DIR/assets" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/config.py" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/detector.py" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/discord_rpc.py" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/gui.py" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/main.py" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/aegisub-discord-rpc" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/run.sh" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/aegisub-discord-rpc.desktop" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/requirements.txt" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/README.md" "$INSTALL_DIR/" 2>/dev/null || true

chmod -R 755 "$INSTALL_DIR"
chmod +x "$INSTALL_DIR/aegisub-discord-rpc"
chmod +x "$INSTALL_DIR/run.sh"

echo -e "\n${BLUE}3/4: Sistem Başlatıcısı ve Masaüstü Kısayolu Oluşturuluyor...${NC}"
ln -sf "$INSTALL_DIR/aegisub-discord-rpc" "$BIN_LINK"

mkdir -p "$DESKTOP_DIR"
cp "$INSTALL_DIR/aegisub-discord-rpc.desktop" "$DESKTOP_DIR/aegisub-discord-rpc.desktop"
chmod 644 "$DESKTOP_DIR/aegisub-discord-rpc.desktop"

echo -e "\n${BLUE}4/4: Simgeler ve Önbellek Güncelleniyor...${NC}"
if [ -f "$INSTALL_DIR/assets/aegisub_icon_128.png" ]; then
    mkdir -p "$ICONS_BASE/128x128/apps"
    cp "$INSTALL_DIR/assets/aegisub_icon_128.png" "$ICONS_BASE/128x128/apps/aegisub-discord-rpc.png"
    mkdir -p /usr/share/pixmaps
    cp "$INSTALL_DIR/assets/aegisub_icon_128.png" /usr/share/pixmaps/aegisub-discord-rpc.png
fi

if command -v gtk-update-icon-cache >/dev/null 2>&1; then
  gtk-update-icon-cache -f -t "$ICONS_BASE" 2>/dev/null || true
fi
if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
fi

echo -e "\n${GREEN}======================================================${NC}"
echo -e "${GREEN}   ✅ Aegisub Discord RPC Başarıyla Kuruldu!${NC}"
echo -e "${GREEN}======================================================${NC}"
echo -e "Uygulamayı çalıştırmak için:"
echo -e "  - Uygulama menünüzden ${CYAN}Aegisub Discord RPC${NC} seçin"
echo -e "  - Veya terminalde doğrudan ${CYAN}aegisub-discord-rpc${NC} komutunu verin."
echo -e ""
echo -e "Kaldırmak isterseniz: ${YELLOW}sudo rm -rf /opt/aegisub-discord-rpc /usr/bin/aegisub-discord-rpc /usr/share/applications/aegisub-discord-rpc.desktop${NC}\n"

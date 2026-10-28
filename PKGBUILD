# Maintainer: KaranlikPasa <https://github.com/KaranlikPasa>
pkgname=aegisub-discord-rpc
pkgver=1.0.3
pkgrel=1
pkgdesc="Discord Rich Presence activity for Aegisub subtitle editor"
arch=('any')
url="https://github.com/KaranlikPasa/aegisub-discord-rpc"
license=('MIT')
depends=('python' 'python-pillow' 'python-psutil' 'tk')
optdepends=(
    'xdotool: X11 pencere başlığı algılama'
    'wmctrl: Alternatif X11 pencere yöneticisi entegrasyonu'
    'python-customtkinter: Modern CTk grafik arayüzü'
    'python-pypresence: Discord IPC bağlantısı'
    'python-pystray: Sistem tepsisi simgesi'
)
provides=('aegisub-discord-rpc')
conflicts=('aegisub-discord-rpc')

package() {
    install -d "${pkgdir}/opt/aegisub-discord-rpc"
    cp -r "${srcdir}/.."/{assets,config.py,detector.py,discord_rpc.py,gui.py,main.py,aegisub-discord-rpc,run.sh,aegisub-discord-rpc.desktop,requirements.txt,README.md,LICENSE} "${pkgdir}/opt/aegisub-discord-rpc/" 2>/dev/null || \
    cp -r "${startdir}"/{assets,config.py,detector.py,discord_rpc.py,gui.py,main.py,aegisub-discord-rpc,run.sh,aegisub-discord-rpc.desktop,requirements.txt,README.md,LICENSE} "${pkgdir}/opt/aegisub-discord-rpc/"
    
    chmod -R 755 "${pkgdir}/opt/aegisub-discord-rpc"
    chmod +x "${pkgdir}/opt/aegisub-discord-rpc/aegisub-discord-rpc"
    chmod +x "${pkgdir}/opt/aegisub-discord-rpc/run.sh"

    # Wrapper executable
    install -d "${pkgdir}/usr/bin"
    ln -sf /opt/aegisub-discord-rpc/aegisub-discord-rpc "${pkgdir}/usr/bin/aegisub-discord-rpc"

    # Desktop entry
    install -Dm644 "${pkgdir}/opt/aegisub-discord-rpc/aegisub-discord-rpc.desktop" "${pkgdir}/usr/share/applications/aegisub-discord-rpc.desktop"

    # Icons
    if [ -f "${pkgdir}/opt/aegisub-discord-rpc/assets/aegisub_icon_128.png" ]; then
        install -Dm644 "${pkgdir}/opt/aegisub-discord-rpc/assets/aegisub_icon_128.png" \
            "${pkgdir}/usr/share/icons/hicolor/128x128/apps/aegisub-discord-rpc.png"
        install -Dm644 "${pkgdir}/opt/aegisub-discord-rpc/assets/aegisub_icon_128.png" \
            "${pkgdir}/usr/share/pixmaps/aegisub-discord-rpc.png"
    fi
}

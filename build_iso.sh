#!/bin/bash
# Script para crear una Debian Live ISO personalizada (Compatible con Ventoy)
set -e # Detener el script si hay cualquier error

echo "Iniciando compilación de MBR-GPT Live OS..."

# Instalar prerrequisitos si es necesario (para GH Actions)
if ! command -v lb &> /dev/null; then
    sudo apt-get update && sudo apt-get install -y live-build debootstrap
fi

# Crear carpeta de trabajo
WORKSPACE="/tmp/mbr-gpt-live"
sudo rm -rf "$WORKSPACE"
mkdir -p "$WORKSPACE"
cd "$WORKSPACE"

echo "Configurando entorno Live..."
# Configurar live-build (arquitectura amd64)
lb config -a amd64 \
    --distribution bookworm \
    --binary-images iso-hybrid \
    --archive-areas "main contrib non-free non-free-firmware" \
    --iso-application "MBR-GPT Converter" \
    --iso-volume "MBR-GPT-LIVE" \
    --bootappend-live "boot=live components locales=es_ES.UTF-8 keyboard-layouts=es quiet splash"

# Instalar paquetes requeridos
mkdir -p config/package-lists/
cat <<EOF > config/package-lists/my-packages.list.chroot
lxde-core
xserver-xorg
xinit
python3
python3-tk
gdisk
util-linux
parted
sfdisk
sudo
EOF

# Copiar el script de la app al entorno Live ISO
mkdir -p config/includes.chroot/opt/mbr-gpt/
cp "/home/runner/work/MBR-GPT-PRO/MBR-GPT-PRO/app.py" config/includes.chroot/opt/mbr-gpt/ 2>/dev/null || cp "/Users/danielgil/Documents/MBR-GPT/app.py" config/includes.chroot/opt/mbr-gpt/
cp "/home/runner/work/MBR-GPT-PRO/MBR-GPT-PRO/disk_operations.py" config/includes.chroot/opt/mbr-gpt/ 2>/dev/null || cp "/Users/danielgil/Documents/MBR-GPT/disk_operations.py" config/includes.chroot/opt/mbr-gpt/

# Crear script de autoarranque
mkdir -p config/includes.chroot/etc/xdg/lxsession/LXDE/
cat <<EOF > config/includes.chroot/etc/xdg/lxsession/LXDE/autostart
@lxpanel --profile LXDE
@pcmanfm --desktop --profile LXDE
@xset s off
@sudo python3 /opt/mbr-gpt/app.py
EOF

# Permisos sudo
mkdir -p config/includes.chroot/etc/sudoers.d/
echo "live ALL=(ALL) NOPASSWD: ALL" > config/includes.chroot/etc/sudoers.d/live
chmod 0440 config/includes.chroot/etc/sudoers.d/live

echo "Construyendo la ISO... Esto tardará unos minutos."
sudo lb build

# Mover la ISO al directorio de salida
if [ -f live-image-amd64.hybrid.iso ]; then
    cp live-image-amd64.hybrid.iso /home/runner/work/MBR-GPT-PRO/MBR-GPT-PRO/mbr_gpt_converter.iso 2>/dev/null || cp live-image-amd64.hybrid.iso /Users/danielgil/Documents/MBR-GPT/mbr_gpt_converter.iso
    echo "¡ÉXITO: ISO generada!"
else
    echo "ERROR: No se encontró la ISO tras la compilación."
    exit 1
fi


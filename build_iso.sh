#!/bin/bash
# Script para crear una Debian Live ISO personalizada (Compatible con Ventoy)

echo "Iniciando compilación de MBR-GPT Live OS..."
echo "Asegúrate de ejecutar esto como root en una distribución basada en Debian/Ubuntu."

# Instalamos prerrequisitos de live-build
apt-get update
apt-get install -y live-build debootstrap

# Crear carpeta de trabajo
WORKSPACE="/tmp/mbr-gpt-live"
rm -rf "$WORKSPACE"
mkdir -p "$WORKSPACE"
cd "$WORKSPACE"

# Configurar live-build (arquitectura amd64)
lb config -a amd64 \
    --distribution bookworm \
    --binary-images iso-hybrid \
    --archive-areas "main contrib non-free non-free-firmware" \
    --iso-application "MBR-GPT Converter Live" \
    --iso-volume "MBR-GPT-LIVE" \
    --bootappend-live "boot=live components locales=es_ES.UTF-8 keyboard-layouts=es quiet splash"

# Instalar paquetes requeridos (Entorno gráfico ligero y herramientas)
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
cp "$(dirname "$0")/app.py" config/includes.chroot/opt/mbr-gpt/
cp "$(dirname "$0")/disk_operations.py" config/includes.chroot/opt/mbr-gpt/

# Crear script de autoarranque para la GUI
mkdir -p config/includes.chroot/etc/xdg/lxsession/LXDE/
cat <<EOF > config/includes.chroot/etc/xdg/lxsession/LXDE/autostart
@lxpanel --profile LXDE
@pcmanfm --desktop --profile LXDE
@xset s off
@xset -dpms
@xset s noblank
@sudo python3 /opt/mbr-gpt/app.py
EOF

# Asegurar que el usuario live tenga sudo sin contraseña
mkdir -p config/includes.chroot/etc/sudoers.d/
echo "live ALL=(ALL) NOPASSWD: ALL" > config/includes.chroot/etc/sudoers.d/live
chmod 0440 config/includes.chroot/etc/sudoers.d/live

# Limpiar cache y construir
lb clean
echo "Construyendo la ISO... esto tomará tiempo."
lb build

# Acabar y copiar la ISO al directorio original
if [ -f live-image-amd64.hybrid.iso ]; then
    cp live-image-amd64.hybrid.iso "$(dirname "$0")/mbr_gpt_converter.iso"
    echo "¡ISO creada con éxito en la carpeta original del proyecto!"
else
    echo "Fallo en la creación de la ISO."
fi

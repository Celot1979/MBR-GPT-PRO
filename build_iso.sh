#!/bin/bash
set -e # Detener el script ante cualquier error

echo "--- INICIANDO CONSTRUCCIÓN PROFESIONAL DE MBR-GPT LIVE ---"

# 1. Limpieza de seguridad
rm -rf build_space
mkdir -p build_space
cd build_space

# 2. Configuración de la ISO (Debian Bookworm con interfaz LXDE)
lb config \
    --distribution bookworm \
    --binary-images iso-hybrid \
    --architectures amd64 \
    --archive-areas "main contrib non-free non-free-firmware" \
    --iso-application "MBR-GPT-Pro" \
    --iso-volume "MBR-GPT-LIVE" \
    --bootappend-live "boot=live components locales=es_ES.UTF-8 keyboard-layouts=es"

# 3. Lista de paquetes a incluir
mkdir -p config/package-lists/
cat <<EOF > config/package-lists/desktop.list.chroot
lxde-core
xserver-xorg
xinit
python3
python3-tk
gdisk
util-linux
parted
sudo
EOF

# 4. Inyectar nuestra aplicación en la ISO
# La carpeta config/includes.chroot copia archivos directamente al sistema de la ISO
APP_DIR="config/includes.chroot/opt/mbr-gpt"
mkdir -p "$APP_DIR"
cp ../app.py "$APP_DIR/"
cp ../disk_operations.py "$APP_DIR/"

# 5. Configurar el Auto-Arranque (Que se abra la app al encender)
AUTOSTART_DIR="config/includes.chroot/etc/xdg/lxsession/LXDE"
mkdir -p "$AUTOSTART_DIR"
cat <<EOF > "$AUTOSTART_DIR/autostart"
@lxpanel --profile LXDE
@pcmanfm --desktop --profile LXDE
@xset s off
@sudo /usr/bin/python3 /opt/mbr-gpt/app.py
EOF

# 6. Permisos de administrador automáticos para el usuario Live
SUDO_DIR="config/includes.chroot/etc/sudoers.d"
mkdir -p "$SUDO_DIR"
echo "live ALL=(ALL) NOPASSWD: ALL" > "$SUDO_DIR/live"
chmod 0440 "$SUDO_DIR/live"

# 7. EJECUCIÓN DE LA COMPILACIÓN
echo "Compilando... Este proceso dura unos minutos ya que descarga el sistema base Debian."
lb build

# 8. Mover el resultado a la raíz para que GitHub lo vea
if [ -f live-image-amd64.hybrid.iso ]; then
    mv live-image-amd64.hybrid.iso ../mbr_gpt_converter.iso
    echo "--- ¡ÉXITO! ISO GENERADA CORRECTAMENTE ---"
else
    echo "ERROR: La ISO no se generó. Revisa los logs de lb build arriba."
    exit 1
fi

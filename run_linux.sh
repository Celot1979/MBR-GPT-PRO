#!/bin/bash
# Script de un solo clic para lanzar el programa en cualquier LINUX
# (Ubuntu, Debian, Fedora, Arch, etc.)

echo "Lanzando MBR-GPT Pro para Linux..."

# Comprobar si tenemos Python 3 y Tkinter
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 no está instalado."
    exit 1
fi

# Instalar dependencias necesarias si faltan (requiere root)
sudo apt-get update && sudo apt-get install -y python3-tk gdisk util-linux parted 2>/dev/null

# Ejecutar la aplicación como superusuario (necesario para manejar discos)
sudo python3 app.py

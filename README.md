# 🛠️ MBR-GPT Pro: Conversor Universal de Particiones

![Estado del Proyecto](https://img.shields.io/badge/Status-Estable-green)
![OS](https://img.shields.io/badge/SO-Windows%20%7C%20Linux%20%7C%20Live%20ISO-blue)

**MBR-GPT Pro** es una herramienta técnica diseñada para la gestión segura y conversión de tablas de particiones entre formatos **MBR (Legacy)** y **GPT (UEFI)**. Creado para técnicos y estudiantes, permite trabajar desde sistemas operativos en ejecución o mediante una **ISO de Rescate Universal** compatible con Ventoy.

---

## 🚀 ¿Cómo usarlo en Ventoy? (Guía Rápida)

Si quieres usar esta herramienta en cualquier PC (incluso si no arranca), sigue estos pasos:

1.  **Descarga la ISO:** 
    *   Ve a la pestaña [Actions](https://github.com/Celot1979/MBR-GPT-PRO/actions) de este repositorio.
    *   Haz clic en la última construcción exitosa ✅.
    *   Descarga el archivo en la sección **Artifacts** y descomprime el `.zip`.
2.  **Copia a Ventoy:**
    *   Arrastra el archivo `mbr_gpt_converter.iso` a tu pendrive Ventoy.
3.  **Arranca el PC:**
    *   Inicia el ordenador desde el USB.
    *   Selecciona `MBR-GPT-Pro` y pulsa Enter.
    *   **¡Listo!** El programa se abrirá automáticamente en segundos.

> [!TIP]
> **INSERTA AQUÍ TU FOTO:** *Muestra una captura de pantalla del menú de Ventoy con la ISO seleccionada o la interfaz del programa abierta en el PC.*

---

## 🧬 ¿Cómo se construyó este proyecto?

Este proyecto nació de la necesidad de tener una herramienta multiplataforma que no dependiera de costosas licencias de software propietario.

### Stack Tecnológico:
*   **Lenguaje:** [Python 3](https://www.python.org/) para la lógica y la interfaz.
*   **Interfaz Gráfica (GUI):** `Tkinter` con un diseño moderno y centrado de ventana.
*   **Motor de Discos (Backend):** 
    *   En **Windows**: PowerShell nativo + `mbr2gpt.exe`.
    *   En **Linux**: `gdisk`, `sgdisk` y `lsblk`.
*   **Infraestructura Live:** [Debian Bookworm](https://www.debian.org/) como base para la ISO ligera.
*   **Automatización (CI/CD):** [GitHub Actions](https://github.com/features/actions) para fabricar la ISO en un contenedor Docker de Debian Privilegiado.

---

## 🛡️ ¿Es seguro? (Preguntas Frecuentes)

**¿Perderé mis datos al convertir?**
El programa utiliza métodos **no destructivos**. En la conversión de MBR a GPT, los datos se preservan al 100%. Para GPT a MBR, siempre que el disco tenga **4 particiones o menos**, la estructura se respeta. 
*Nota: Siempre recomendamos backup para datos críticos.*

**¿Funciona en discos de sistema?**
Sí, especialmente desde la **ISO de Ventoy**, ya que el disco de Windows no está "en uso" y el programa tiene acceso total al hardware.

---

## 👨‍🎓 Para Compañeros de Clase (Desarrollo)

Si quieres modificar o mejorar este programa:

```bash
# Clonar el repo
git clone https://github.com/Celot1979/MBR-GPT-PRO.git

# Ejecutar en Linux
chmod +x run_linux.sh
./run_linux.sh

# Ejecutar en Windows
python app.py
```

> [!IMPORTANT]
> **INSERTA AQUÍ TU FOTO:** *Una captura de la interfaz de usuario mostrando la detección de los discos de tu PC.*

---

## ✍️ Autor
*   **Daniel Gil** - [Celot1979](https://github.com/Celot1979)

Si este proyecto te ha servido en tus prácticas, ¡no olvides darle una ⭐ en GitHub!

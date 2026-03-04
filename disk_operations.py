import subprocess
import json
import os
import platform

def get_disks_info():
    """
    Obtiene la lista de discos del sistema de forma multiplataforma.
    Detecta si es Windows o Linux y usa las herramientas correspondientes.
    """
    system = platform.system()
    disks = []

    if system == "Windows":
        try:
            # Usar PowerShell para obtener información de discos en formato JSON
            ps_cmd = 'Get-Disk | Select-Object Number, FriendlyName, Size, PartitionStyle | ConvertTo-Json'
            result = subprocess.run(['powershell', '-Command', ps_cmd], capture_output=True, text=True, check=True)
            
            # Si hay un solo disco, PowerShell no devuelve una lista, sino un objeto directo
            raw_data = json.loads(result.stdout)
            data = raw_data if isinstance(raw_data, list) else [raw_data]

            for d in data:
                # El tamaño viene en bytes, lo pasamos a GB
                size_gb = float(d.get('Size', 0)) / (1024**3)
                ptstyle = str(d.get('PartitionStyle', 'Unknown')).upper()
                name = rf"\\.\PhysicalDrive{d.get('Number')}"
                
                disks.append({
                    'name': name,
                    'friendly_name': d.get('FriendlyName', 'Unknown'),
                    'size_gb': f"{size_gb:.2f} GB",
                    'pttype': ptstyle
                })
        except Exception as e:
            print(f"Error en Windows: {e}")
            return []

    else: # Asumimos entorno Linux (como el de la ISO)
        try:
            result = subprocess.run(['lsblk', '-J', '-b', '-o', 'NAME,SIZE,TYPE,PTTYPE,MODEL'], 
                                    capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            for dev in data.get('blockdevices', []):
                if dev.get('type') == 'disk':
                    name = dev.get('name')
                    size = dev.get('size', 0) / (1024**3)
                    pttype = dev.get('pttype')
                    if not pttype:
                        pttype = "None"
                    
                    disks.append({
                        'name': f"/dev/{name}",
                        'friendly_name': dev.get('model', 'Disco Genérico'),
                        'size_gb': f"{size:.2f} GB",
                        'pttype': str(pttype).upper()
                    })
        except Exception:
            return []

    return disks

def get_partitions_count(disk_path):
    """Obtiene el número de particiones de un disco."""
    system = platform.system()
    if system == "Windows":
        try:
            # Obtener número de particiones vía PowerShell
            disk_num = disk_path.split('PhysicalDrive')[-1]
            ps_cmd = f'Get-Partition -DiskNumber {disk_num} | Measure-Object | Select-Object -ExpandProperty Count'
            result = subprocess.run(['powershell', '-Command', ps_cmd], capture_output=True, text=True)
            return int(result.stdout.strip())
        except:
            return 0
    else:
        try:
            result = subprocess.run(['lsblk', '-J', disk_path], capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            dev = data.get('blockdevices', [])[0]
            children = dev.get('children', [])
            return len(children)
        except Exception:
            return 0

def backup_mbr(disk_path):
    """Respalda la tabla MBR antes de convertir a GPT."""
    if platform.system() == "Windows":
        # En Windows, MBR2GPT maneja el proceso de forma integrada y segura
        return True, "Gestionado por MBR2GPT"
        
    backup_file = f"/tmp/backup_mbr_{os.path.basename(disk_path)}.txt"
    try:
        with open(backup_file, 'w') as f:
            subprocess.run(['sfdisk', '-d', disk_path], stdout=f, check=True)
        return True, backup_file
    except Exception as e:
        return False, str(e)

def convert_mbr_to_gpt(disk_path):
    """Convierte el disco MBR a GPT."""
    system = platform.system()
    
    if system == "Windows":
        try:
            # En Windows usamos mbr2gpt.exe que es oficial y no destructivo
            # /allowFullOS permite usarlo desde el sistema en ejecución, aunque se recomienda PE
            disk_num = disk_path.split('PhysicalDrive')[-1]
            cmd = f"mbr2gpt /convert /disk:{disk_num} /allowFullOS"
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                return True, "Conversión Windows realizada con éxito mediante MBR2GPT."
            else:
                return False, f"Error de MBR2GPT: {result.stdout}\n{result.stderr}"
        except Exception as e:
            return False, str(e)
            
    else: # Linux
        status, backup_file = backup_mbr(disk_path)
        if not status:
            return False, f"Error al crear copia de seguridad: {backup_file}"
        try:
            subprocess.run(['sgdisk', '-g', disk_path], capture_output=True, text=True, check=True)
            subprocess.run(['partprobe', disk_path], capture_output=True)
            return True, "Conversión (sgdisk) completada con éxito. Backup: " + backup_file
        except subprocess.CalledProcessError as e:
            return False, f"Error en la conversión: {e.stderr}"

def convert_gpt_to_mbr(disk_path):
    """Convierte el disco GPT a MBR."""
    system = platform.system()
    
    # Validar número de particiones (MBR soporta máx 4)
    part_count = get_partitions_count(disk_path)
    if part_count > 4:
        return False, f"Error: {part_count} particiones detectadas. MBR solo permite 4 primarias."

    if system == "Windows":
        return False, "Windows no soporta conversión GPT -> MBR de forma no destructiva nativamente."
    
    else: # Linux
        try:
            # Modo experto gdisk r -> g -> w -> Y
            commands = "r\ng\nw\nY\n"
            process = subprocess.run(['gdisk', disk_path], input=commands, capture_output=True, text=True)
            if process.returncode != 0:
                return False, f"Error gdisk: {process.stderr}"
            subprocess.run(['partprobe', disk_path], capture_output=True)
            return True, "Conversión completada."
        except Exception as e:
            return False, str(e)


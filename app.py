import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import disk_operations
import threading
import platform
import sys

class AppUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MBR-GPT Pro - Conversor de Particiones")
        self.geometry("850x600")
        self.center_window()
        
        # Estilo Moderno
        self.style = ttk.Style()
        self.style.theme_use('clam') # Usamos un tema base más limpio que el default
        
        # Colores
        self.bg_color = "#f0f0f0"
        self.configure(bg=self.bg_color, padx=20, pady=20)

        # Header
        header_frame = tk.Frame(self, bg=self.bg_color)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        lbl_titulo = tk.Label(header_frame, text="MBR ↔ GPT Converter", 
                              font=("Segoe UI" if platform.system()=="Windows" else "Arial", 20, "bold"), 
                              bg=self.bg_color, fg="#333")
        lbl_titulo.pack(side=tk.LEFT)
        
        self.lbl_os = tk.Label(header_frame, text=f"Sistema: {platform.system()} ({platform.machine()})", 
                               font=("Arial", 10, "italic"), bg=self.bg_color, fg="#666")
        self.lbl_os.pack(side=tk.RIGHT, pady=10)

        # Barra de herramientas
        btn_frame = tk.Frame(self, bg=self.bg_color)
        btn_frame.pack(fill=tk.X, pady=5)
        
        self.btn_refresh = ttk.Button(btn_frame, text="🔄 Refrescar Discos", command=self.load_disks)
        self.btn_refresh.pack(side=tk.LEFT)
        
        # Tabla de Discos (Mejorada)
        columns = ("Disco", "Modelo/Nombre", "Tamaño", "Tabla")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=10)
        self.tree.heading("Disco", text="Identificador")
        self.tree.heading("Modelo/Nombre", text="Modelo / Nombre Amigable")
        self.tree.heading("Tamaño", text="Capacidad")
        self.tree.heading("Tabla", text="Estilo Actual")
        
        self.tree.column("Disco", width=120)
        self.tree.column("Modelo/Nombre", width=350)
        self.tree.column("Tamaño", width=100)
        self.tree.column("Tabla", width=100)
        
        self.tree.pack(fill=tk.BOTH, expand=True, pady=10)

        # Botones de Acción (Estilo Premium)
        action_frame = tk.Frame(self, bg=self.bg_color)
        action_frame.pack(fill=tk.X, pady=10)
        
        self.btn_to_gpt = tk.Button(action_frame, text="CONVERTIR A GPT (UEFI)", 
                                   bg="#2ecc71", fg="white", font=("Arial", 11, "bold"), 
                                   relief=tk.FLAT, height=2, command=self.start_to_gpt)
        self.btn_to_gpt.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)
        
        self.btn_to_mbr = tk.Button(action_frame, text="CONVERTIR A MBR (Legacy)", 
                                   bg="#3498db", fg="white", font=("Arial", 11, "bold"), 
                                   relief=tk.FLAT, height=2, command=self.start_to_mbr)
        self.btn_to_mbr.pack(side=tk.RIGHT, padx=10, expand=True, fill=tk.X)

        # Área de Log con scroll automático
        lbl_log = tk.Label(self, text="Registro de Operaciones:", bg=self.bg_color, font=("Arial", 9, "bold"))
        lbl_log.pack(anchor=tk.W)
        
        self.log_area = scrolledtext.ScrolledText(self, height=8, font=("Consolas" if platform.system()=="Windows" else "Courier", 10), 
                                                bg="#2c3e50", fg="#ecf0f1", padx=10, pady=10)
        self.log_area.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        self.load_disks()

    def log(self, message):
        self.log_area.insert(tk.END, f"> {message}\n")
        self.log_area.see(tk.END)

    def load_disks(self):
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.log("Buscando dispositivos de almacenamiento...")
        disks = disk_operations.get_disks_info()
        
        if not disks:
            self.log("CRÍTICO: No se detectan discos o faltan privilegios de administrador.")
            messagebox.showerror("Error", "No se detectaron discos. Asegúrate de ejecutar como Administrador/Root.")
            return

        for d in disks:
            self.tree.insert("", tk.END, values=(d['name'], d['friendly_name'], d['size_gb'], d['pttype']))
            self.log(f"Detectado: {d['friendly_name']} ({d['size_gb']}) -> {d['pttype']}")
            
    def get_selected_disk(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Atención", "Seleccione un disco de la lista para continuar.")
            return None
        return self.tree.item(selected[0])['values']

    def start_to_gpt(self):
        disk_data = self.get_selected_disk()
        if not disk_data: return
        disk_path, friendly, _, pttype = disk_data
        
        if pttype == "GPT":
            messagebox.showinfo("INFO", "El disco ya se encuentra en formato GPT.")
            return

        confirm = messagebox.askyesno("Confirmar Conversión", 
            f"¿Desea convertir '{friendly}' a GPT?\n\n"
            "Esta operación modificará la estructura del disco. Aunque se intenta preservar los datos, "
            "se recomienda tener una copia de seguridad.")
        
        if not confirm: return

        self.set_ui_state(tk.DISABLED)
        self.log(f"Iniciando proceso: MBR -> GPT en {disk_path}...")
        
        def tarea():
            success, msg = disk_operations.convert_mbr_to_gpt(str(disk_path))
            self.after(0, lambda: self.finalizar_tarea(success, msg))
            
        threading.Thread(target=tarea, daemon=True).start()

    def start_to_mbr(self):
        disk_data = self.get_selected_disk()
        if not disk_data: return
        disk_path, friendly, _, pttype = disk_data
        
        if pttype in ["MBR", "DOS"]:
            messagebox.showinfo("INFO", "El disco ya se encuentra en formato MBR.")
            return

        confirm = messagebox.askyesno("RIESGO - GPT a MBR", 
            f"¿Convertir '{friendly}' a MBR?\n\n"
            "ADVERTENCIA: Esta operación solo es exitosa si el disco tiene 4 o menos particiones. "
            "¿Desea continuar bajo su responsabilidad?")
        
        if not confirm: return

        self.set_ui_state(tk.DISABLED)
        self.log(f"Iniciando proceso: GPT -> MBR en {disk_path}...")
        
        def tarea():
            success, msg = disk_operations.convert_gpt_to_mbr(str(disk_path))
            self.after(0, lambda: self.finalizar_tarea(success, msg))
            
        threading.Thread(target=tarea, daemon=True).start()

    def set_ui_state(self, state):
        self.btn_to_gpt.config(state=state)
        self.btn_to_mbr.config(state=state)
        self.btn_refresh.config(state=state)

    def finalizar_tarea(self, success, msg):
        self.log(msg)
        if success:
            messagebox.showinfo("ÉXITO", "La operación se completó correctamente.")
        else:
            messagebox.showerror("ERROR", msg)
        self.set_ui_state(tk.NORMAL)
        self.load_disks()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

if __name__ == "__main__":
    app = AppUI()
    app.mainloop()


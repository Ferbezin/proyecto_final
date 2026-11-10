import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from backend.reportes import (
    obtener_top_productos_vendidos, 
    obtener_resumen_ventas_por_cliente, 
    obtener_inventario_completo, 
    exportar_reporte_a_csv
)

class ReportesWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("E-Market Express - Panel Gerencial (Gráficos)")
        
        # PANTALLA COMPLETA: Maximizamos la ventana y permitimos que se expanda
        self.root.state('zoomed')
        self.root.configure(bg="#f8f9fa")

        # --- Encabezado ---
        header_frame = tk.Frame(self.root, bg="#f8f9fa")
        header_frame.pack(fill="x", pady=(15, 5), padx=20)
        
        tk.Label(
            header_frame, 
            text="Tableros de Control - Tiempo Real", 
            font=("Segoe UI", 16, "bold"), 
            bg="#f8f9fa", 
            fg="#212529"
        ).pack(side="left")

        # Botón de actualización
        tk.Button(
            header_frame, 
            text="🔄 Actualizar", 
            bg="#212529", 
            fg="white", 
            font=("Segoe UI", 10, "bold"), 
            relief="flat", 
            padx=15, 
            pady=3,
            cursor="hand2", 
            command=self.dibujar_graficas
        ).pack(side="right")

        # NUEVO: Menú desplegable para el filtro de tiempo
        self.combo_filtro = ttk.Combobox(
            header_frame, 
            values=["Histórico Completo", "Hoy", "Últimos 5 min"],
            state="readonly",
            font=("Segoe UI", 10),
            width=18
        )
        self.combo_filtro.set("Histórico Completo") # Valor por defecto
        self.combo_filtro.pack(side="right", padx=(0, 15))
        
        tk.Label(header_frame, text="Filtrar ventas por:", bg="#f8f9fa", font=("Segoe UI", 10, "bold")).pack(side="right", padx=5)

        # --- Contenedor de las Gráficas ---
        self.graficas_frame = tk.Frame(self.root, bg="white", bd=1, relief="solid")
        self.graficas_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))

        plt.style.use('ggplot')
        
        # ALTA DEFINICIÓN: Aumentamos figsize a (12, 6) y dpi a 130 para evitar el pixelado en pantalla completa
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(12, 6), dpi=130)
        self.fig.patch.set_facecolor('#ffffff')

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graficas_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        self.dibujar_graficas()

    def dibujar_graficas(self):
        self.ax1.clear()
        self.ax2.clear()

        # Leemos qué filtro seleccionó el gerente
        filtro_seleccionado = self.combo_filtro.get()

        # Enviamos ese filtro al backend
        top_productos = obtener_top_productos_vendidos(5, filtro=filtro_seleccionado)
        inventario = obtener_inventario_completo() 

        # --- Gráfica 1: Top Ventas ---
        if top_productos:
            nombres = [p['nombre'][:12] + '..' if len(p['nombre'])>12 else p['nombre'] for p in top_productos]
            cantidades = [p['total_vendido'] for p in top_productos]
            
            barras1 = self.ax1.bar(nombres, cantidades, color='#3b82f6', edgecolor='none')
            self.ax1.set_title(f'Top Más Comprados ({filtro_seleccionado})', fontsize=12, fontweight='bold', pad=15)
            self.ax1.set_ylabel('Unidades Vendidas')
            self.ax1.tick_params(axis='x', rotation=15)
            self.ax1.bar_label(barras1, padding=3, fontweight='bold', color='#1e293b')
        else:
            self.ax1.text(0.5, 0.5, f'Sin ventas en:\n{filtro_seleccionado}', ha='center', va='center', fontsize=11, color='gray')
            self.ax1.set_title('Top Productos Más Comprados', fontsize=12, fontweight='bold')

        # --- Gráfica 2: Stock Disponible ---
        if inventario:
            nombres_inv = [p['nombre'][:15] for p in inventario]
            cantidades_inv = [p['cantidad_disponible'] for p in inventario]
            
            barras2 = self.ax2.barh(nombres_inv, cantidades_inv, color='#10b981', edgecolor='none')
            self.ax2.set_title('Stock Disponible (Catálogo Completo)', fontsize=12, fontweight='bold', pad=15)
            self.ax2.set_xlabel('Unidades en Bodega')
            
            max_val = max(cantidades_inv) if cantidades_inv else 10
            self.ax2.set_xlim(0, max_val + (max_val * 0.2)) 
            self.ax2.bar_label(barras2, padding=5, fontweight='bold', color='#1e293b')
        else:
            self.ax2.text(0.5, 0.5, 'No hay productos registrados', ha='center', va='center', fontsize=11, color='gray')
            self.ax2.set_title('Stock Disponible', fontsize=12, fontweight='bold')

        self.fig.tight_layout()
        self.canvas.draw()
import customtkinter as ctk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from backend.reportes import (
    obtener_top_productos_vendidos, 
    obtener_resumen_ventas_por_cliente, 
    obtener_inventario_completo
)

class ReportesWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("E-Market Express — Reportes & Estadísticas")
        
        # PANTALLA COMPLETA GARANTIZADA
        self.root.configure(fg_color="#070a12")
        self.root.after(50, lambda: self.root.state('zoomed'))

        # Contenedor Principal
        main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=25, pady=20)

        # ==========================================
        # HEADER SUPERIOR (BARRA DE HERRAMIENTAS)
        # ==========================================
        header = ctk.CTkFrame(main_container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            header,
            text="📊 Tableros de Control & Analítica",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color="#ffffff"
        ).pack(side="left")

        # Grupo de controles superiores
        ctrl_frame = ctk.CTkFrame(header, fg_color="transparent")
        ctrl_frame.pack(side="right")

        ctk.CTkLabel(
            ctrl_frame, 
            text="Filtrar por:", 
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), 
            text_color="#94a3b8"
        ).pack(side="left", padx=(0, 8))

        self.combo_filtro = ctk.CTkOptionMenu(
            ctrl_frame,
            values=["Histórico Completo", "Hoy", "Últimos 5 min"],
            height=36,
            width=170,
            corner_radius=8,
            fg_color="#1e293b",
            button_color="#334155",
            button_hover_color="#475569",
            text_color="#ffffff",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            command=lambda val: self.dibujar_graficas()
        )
        self.combo_filtro.set("Histórico Completo")
        self.combo_filtro.pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            ctrl_frame,
            text="🔄 Actualizar",
            height=36,
            corner_radius=8,
            fg_color="#0284c7",
            hover_color="#0369a1",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            command=self.dibujar_graficas
        ).pack(side="left", padx=(0, 10))

        # BOTÓN DE RETORNO AL DASHBOARD
        ctk.CTkButton(
            ctrl_frame,
            text="← Volver al Dashboard",
            height=36,
            corner_radius=8,
            fg_color="#334155",
            hover_color="#475569",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            command=self.volver_al_dashboard
        ).pack(side="left")

        # ==========================================
        # CONTENEDOR DE GRÁFICAS INTEGRADO
        # ==========================================
        self.graficas_frame = ctk.CTkFrame(
            main_container, 
            fg_color="#0f172a", 
            corner_radius=16, 
            border_width=1, 
            border_color="#1e293b"
        )
        self.graficas_frame.pack(fill="both", expand=True)

        # Configuración del tema visual de Matplotlib a Dark Mode
        plt.style.use('dark_background')
        
        # 3 Gráficas en distribución horizontal (1 fila, 3 columnas)
        self.fig, (self.ax1, self.ax2, self.ax3) = plt.subplots(1, 3, figsize=(14, 5), dpi=110)
        self.fig.patch.set_facecolor('#0f172a')

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graficas_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=15)

        self.dibujar_graficas()

    def volver_al_dashboard(self):
        """Cierra la ventana de reportes y vuelve limpiamente al Dashboard."""
        self.root.destroy()

    def dibujar_graficas(self):
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()

        # Colores del fondo de las parcelas
        for ax in (self.ax1, self.ax2, self.ax3):
            ax.set_facecolor('#1e293b')

        filtro_seleccionado = self.combo_filtro.get()

        # Cargar datos desde Backend
        top_productos = obtener_top_productos_vendidos(5, filtro=filtro_seleccionado)
        inventario = obtener_inventario_completo()

        # ------------------------------------------
        # GRÁFICA 1: TOP MÁS VENDIDOS (Barras Verticales)
        # ------------------------------------------
        if top_productos:
            nombres = [p['nombre'][:10] + '..' if len(p['nombre']) > 10 else p['nombre'] for p in top_productos]
            cantidades = [p['total_vendido'] for p in top_productos]
            
            barras1 = self.ax1.bar(nombres, cantidades, color='#38bdf8', edgecolor='none', width=0.55)
            self.ax1.set_title(f'Top Más Comprados\n({filtro_seleccionado})', fontsize=10, fontweight='bold', pad=12, color='#ffffff')
            self.ax1.set_ylabel('Unidades Vendidas', fontsize=9, color='#94a3b8')
            self.ax1.tick_params(axis='x', rotation=20, labelsize=8, colors='#cbd5e1')
            self.ax1.tick_params(axis='y', labelsize=8, colors='#cbd5e1')
            self.ax1.bar_label(barras1, padding=3, fontweight='bold', color='#ffffff', fontsize=8)
        else:
            self.ax1.text(0.5, 0.5, f'Sin ventas en:\n{filtro_seleccionado}', ha='center', va='center', fontsize=10, color='#94a3b8')
            self.ax1.set_title('Top Productos Vendidos', fontsize=10, fontweight='bold', color='#ffffff')

        # ------------------------------------------
        # GRÁFICA 2: STOCK BODEGA (Barras Horizontales)
        # ------------------------------------------
        if inventario:
            # Mostramos los primeros 6 artículos
            inv_sub = inventario[:6]
            nombres_inv = [p['nombre'][:12] + '..' if len(p['nombre']) > 12 else p['nombre'] for p in inv_sub]
            cantidades_inv = [p['cantidad_disponible'] for p in inv_sub]
            
            barras2 = self.ax2.barh(nombres_inv, cantidades_inv, color='#34d399', edgecolor='none', height=0.55)
            self.ax2.set_title('Stock Disponible\n(Nivel en Bodega)', fontsize=10, fontweight='bold', pad=12, color='#ffffff')
            self.ax2.set_xlabel('Unidades Disponibles', fontsize=9, color='#94a3b8')
            self.ax2.tick_params(axis='x', labelsize=8, colors='#cbd5e1')
            self.ax2.tick_params(axis='y', labelsize=8, colors='#cbd5e1')
            
            max_val = max(cantidades_inv) if cantidades_inv else 10
            self.ax2.set_xlim(0, max_val + (max_val * 0.25)) 
            self.ax2.bar_label(barras2, padding=4, fontweight='bold', color='#ffffff', fontsize=8)
        else:
            self.ax2.text(0.5, 0.5, 'No hay productos', ha='center', va='center', fontsize=10, color='#94a3b8')
            self.ax2.set_title('Stock Disponible', fontsize=10, fontweight='bold', color='#ffffff')

        # ------------------------------------------
        # GRÁFICA 3: DISTRIBUCIÓN POR CATEGORÍAS (Donut Chart)
        # ------------------------------------------
        if inventario:
            cat_counts = {}
            for p in inventario:
                cat = p.get('categoria') or 'General'
                cat_counts[cat] = cat_counts.get(cat, 0) + p['cantidad_disponible']

            labels = list(cat_counts.keys())
            values = list(cat_counts.values())
            colores_pie = ['#818cf8', '#f43f5e', '#fbbf24', '#34d399', '#38bdf8', '#a855f7']

            wedges, texts, autotexts = self.ax3.pie(
                values, 
                labels=labels, 
                autopct='%1.0f%%',
                startangle=140,
                colors=colores_pie[:len(labels)],
                textprops=dict(color="#ffffff", fontsize=8),
                wedgeprops=dict(width=0.4, edgecolor='#0f172a') # Efecto Donut
            )
            for at in autotexts:
                at.set_color('#ffffff')
                at.set_weight('bold')
                
            self.ax3.set_title('Distribución de Inventario\n(Por Categoría)', fontsize=10, fontweight='bold', pad=12, color='#ffffff')
        else:
            self.ax3.text(0.5, 0.5, 'Sin categorías', ha='center', va='center', fontsize=10, color='#94a3b8')
            self.ax3.set_title('Distribución Categorías', fontsize=10, fontweight='bold', color='#ffffff')

        self.fig.tight_layout()
        self.canvas.draw()
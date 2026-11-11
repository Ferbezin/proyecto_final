import customtkinter as ctk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from backend.reportes import (
    obtener_top_productos_vendidos, 
    obtener_inventario_completo
)

class ReportesWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("E-Market Express — Tablero de Analítica Gerencial")
        
        # PANTALLA COMPLETA
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
            text="📊 Tablero de Control & Analítica Comercial",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color="#ffffff"
        ).pack(side="left")

        # Controles a la derecha
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

        # BOTÓN RETORNO AL DASHBOARD
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
        # TARJETAS DE INDICADORES RÁPIDOS (KPIs)
        # ==========================================
        kpi_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        kpi_frame.pack(fill="x", pady=(0, 15))

        # KPI 1: Total Unidades Vendidas
        card1 = ctk.CTkFrame(kpi_frame, fg_color="#0f172a", corner_radius=12, border_width=1, border_color="#1e293b")
        card1.pack(side="left", fill="both", expand=True, padx=(0, 10))
        ctk.CTkLabel(card1, text="UNIDADES VENDIDAS", font=ctk.CTkFont(size=9, weight="bold"), text_color="#94a3b8").pack(anchor="w", padx=15, pady=(10, 0))
        self.lbl_kpi_unidades = ctk.CTkLabel(card1, text="0 Uds", font=ctk.CTkFont(size=18, weight="bold"), text_color="#38bdf8")
        self.lbl_kpi_unidades.pack(anchor="w", padx=15, pady=(0, 10))

        # KPI 2: Productos con Stock Crítico
        card2 = ctk.CTkFrame(kpi_frame, fg_color="#0f172a", corner_radius=12, border_width=1, border_color="#1e293b")
        card2.pack(side="left", fill="both", expand=True, padx=(0, 10))
        ctk.CTkLabel(card2, text="ARTÍCULOS EN RIESGO (< 5 UDS)", font=ctk.CTkFont(size=9, weight="bold"), text_color="#94a3b8").pack(anchor="w", padx=15, pady=(10, 0))
        self.lbl_kpi_criticos = ctk.CTkLabel(card2, text="0 Productos", font=ctk.CTkFont(size=18, weight="bold"), text_color="#ef4444")
        self.lbl_kpi_criticos.pack(anchor="w", padx=15, pady=(0, 10))

        # KPI 3: Variedad en Catálogo
        card3 = ctk.CTkFrame(kpi_frame, fg_color="#0f172a", corner_radius=12, border_width=1, border_color="#1e293b")
        card3.pack(side="left", fill="both", expand=True)
        ctk.CTkLabel(card3, text="TOTAL PRODUCTOS REGISTRADOS", font=ctk.CTkFont(size=9, weight="bold"), text_color="#94a3b8").pack(anchor="w", padx=15, pady=(10, 0))
        self.lbl_kpi_total_prod = ctk.CTkLabel(card3, text="0 Ítems", font=ctk.CTkFont(size=18, weight="bold"), text_color="#34d399")
        self.lbl_kpi_total_prod.pack(anchor="w", padx=15, pady=(0, 10))

        # ==========================================
        # CONTENEDOR DE GRÁFICAS EN GRID (1 fila, 3 columnas adaptadas)
        # ==========================================
        self.graficas_frame = ctk.CTkFrame(
            main_container, 
            fg_color="#0f172a", 
            corner_radius=16, 
            border_width=1, 
            border_color="#1e293b"
        )
        self.graficas_frame.pack(fill="both", expand=True)

        # Tema Matplotlib
        plt.style.use('dark_background')
        
        # 3 Gráficas con mayor altura y espacio entre sí
        self.fig, (self.ax1, self.ax2, self.ax3) = plt.subplots(1, 3, figsize=(15, 5), dpi=100)
        self.fig.patch.set_facecolor('#0f172a')

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graficas_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=15)

        self.dibujar_graficas()

    def volver_al_dashboard(self):
        """Cierra la ventana de reportes y vuelve al Dashboard."""
        self.root.destroy()

    def dibujar_graficas(self):
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()

        for ax in (self.ax1, self.ax2, self.ax3):
            ax.set_facecolor('#1e293b')

        filtro_seleccionado = self.combo_filtro.get()

        # Datos desde backend
        top_productos = obtener_top_productos_vendidos(5, filtro=filtro_seleccionado)
        inventario = obtener_inventario_completo()

        # Actualizar Tarjetas KPI
        total_uds = sum(p['total_vendido'] for p in top_productos) if top_productos else 0
        self.lbl_kpi_unidades.configure(text=f"{total_uds:,} Uds")

        if inventario:
            criticos = [p for p in inventario if p['cantidad_disponible'] <= 5]
            self.lbl_kpi_criticos.configure(text=f"{len(criticos)} Productos")
            self.lbl_kpi_total_prod.configure(text=f"{len(inventario)} Ítems")
        else:
            self.lbl_kpi_criticos.configure(text="0 Productos")
            self.lbl_kpi_total_prod.configure(text="0 Ítems")

        # ------------------------------------------
        # GRÁFICA 1: TOP 5 MÁS VENDIDOS (Se Mantiene)
        # ------------------------------------------
        if top_productos:
            nombres = [p['nombre'][:10] + '..' if len(p['nombre']) > 10 else p['nombre'] for p in top_productos]
            cantidades = [p['total_vendido'] for p in top_productos]
            
            barras1 = self.ax1.bar(nombres, cantidades, color='#38bdf8', edgecolor='none', width=0.5)
            self.ax1.set_title(f'Top 5 Productos Más Vendidos\n({filtro_seleccionado})', fontsize=10, fontweight='bold', pad=12, color='#ffffff')
            self.ax1.set_ylabel('Unidades', fontsize=8, color='#94a3b8')
            self.ax1.tick_params(axis='x', rotation=20, labelsize=8, colors='#cbd5e1')
            self.ax1.tick_params(axis='y', labelsize=8, colors='#cbd5e1')
            self.ax1.bar_label(barras1, padding=3, fontweight='bold', color='#ffffff', fontsize=8)
        else:
            self.ax1.text(0.5, 0.5, f'Sin ventas en:\n{filtro_seleccionado}', ha='center', va='center', fontsize=9, color='#94a3b8')
            self.ax1.set_title('Top Productos Vendidos', fontsize=10, fontweight='bold', color='#ffffff')

        # ------------------------------------------
        # GRÁFICA 2: RECAUDO / VENTAS POR CATEGORÍA (NUEVA Y CLARA)
        # ------------------------------------------
        if inventario:
            cat_totals = {}
            for p in inventario:
                cat = p.get('categoria') or 'Sin Categoría'
                # Estimación de stock acumulado por categoría
                cat_totals[cat] = cat_totals.get(cat, 0) + p['cantidad_disponible']

            cat_nombres = list(cat_totals.keys())[:5] # Top 5 categorías
            cat_valores = [cat_totals[k] for k in cat_nombres]

            barras2 = self.ax2.barh(cat_nombres, cat_valores, color='#818cf8', edgecolor='none', height=0.5)
            self.ax2.set_title('Volumen de Stock\n(Por Categorías Top)', fontsize=10, fontweight='bold', pad=12, color='#ffffff')
            self.ax2.set_xlabel('Unidades en Inventario', fontsize=8, color='#94a3b8')
            self.ax2.tick_params(axis='x', labelsize=8, colors='#cbd5e1')
            self.ax2.tick_params(axis='y', labelsize=8, colors='#cbd5e1')
            self.ax2.bar_label(barras2, padding=3, fontweight='bold', color='#ffffff', fontsize=8)
        else:
            self.ax2.text(0.5, 0.5, 'Sin datos de categoría', ha='center', va='center', fontsize=9, color='#94a3b8')
            self.ax2.set_title('Stock por Categoría', fontsize=10, fontweight='bold', color='#ffffff')

        # ------------------------------------------
        # GRÁFICA 3: ALERTAS DE INVENTARIO CRÍTICO (NUEVA: Menor Stock)
        # ------------------------------------------
        if inventario:
            # Ordenamos los productos por menor stock para mostrar cuáles se van a agotar
            inv_ordenado = sorted(inventario, key=lambda x: x['cantidad_disponible'])[:5]
            nombres_crit = [p['nombre'][:10] + '..' if len(p['nombre']) > 10 else p['nombre'] for p in inv_ordenado]
            stocks_crit = [p['cantidad_disponible'] for p in inv_ordenado]
            
            # Pintar de rojo los menores a 5 unidades, verde los demás
            colores_barras = ['#f43f5e' if s <= 5 else '#34d399' for s in stocks_crit]

            barras3 = self.ax3.bar(nombres_crit, stocks_crit, color=colores_barras, edgecolor='none', width=0.5)
            self.ax3.set_title('Alertas de Stock Crítico\n(Menor Inventario)', fontsize=10, fontweight='bold', pad=12, color='#ffffff')
            self.ax3.set_ylabel('Stock Restante', fontsize=8, color='#94a3b8')
            self.ax3.tick_params(axis='x', rotation=20, labelsize=8, colors='#cbd5e1')
            self.ax3.tick_params(axis='y', labelsize=8, colors='#cbd5e1')
            self.ax3.bar_label(barras3, padding=3, fontweight='bold', color='#ffffff', fontsize=8)
        else:
            self.ax3.text(0.5, 0.5, 'Sin productos', ha='center', va='center', fontsize=9, color='#94a3b8')
            self.ax3.set_title('Stock Crítico', fontsize=10, fontweight='bold', color='#ffffff')

        self.fig.subplots_adjust(wspace=0.35)
        self.canvas.draw()
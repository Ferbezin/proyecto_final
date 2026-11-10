import tkinter as tk
from tkinter import ttk, messagebox
from backend.transacciones import listar_productos, generar_comprobante_pdf, registrar_carrito_completo
from frontend.crud_window import CRUDWindow
from frontend.reportes_window import ReportesWindow

class DashboardWindow:
    def __init__(self, root, usuario_actual):
        self.root = root
        self.usuario_actual = usuario_actual
        self.root.title(f"E-Market Express - Dashboard ({self.usuario_actual['rol']})")
        
        # PANTALLA COMPLETA: Maximizamos la ventana
        self.root.state('zoomed')
        self.root.configure(bg="#f8f9fa")

        # Variables para el pedido temporal
        self.carrito = []
        self.total_pedido = 0.0

        # --- CABECERA MODAL ---
        frame_header = tk.Frame(self.root, bg="#ffffff", pady=15, padx=20)
        frame_header.pack(fill="x")
        
        tk.Label(
            frame_header, 
            text=f"Hola, {self.usuario_actual['nombre']} ({self.usuario_actual['rol']})", 
            font=("Segoe UI", 12, "bold"), 
            bg="#ffffff", 
            fg="#212529"
        ).pack(side="left")
        
        # Botón de Cerrar Sesión moderno
        tk.Button(
            frame_header, 
            text="Cerrar Sesión", 
            command=self.cerrar_sesion, 
            bg="#dc3545", 
            fg="white", 
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=10,
            pady=5,
            cursor="hand2"
        ).pack(side="right", padx=5)

       # Si es Administrador, agregamos los botones de gestión
        if self.usuario_actual['rol'] == 'Administrador':
            # 1. Botón original para el CRUD (Gestión de Catálogo)
            tk.Button(
                frame_header,
                text="⚙ Panel Gerencial",
                command=self.abrir_panel_admin,
                bg="#ffc107",
                fg="#212529",
                font=("Segoe UI", 9, "bold"),
                relief="flat",
                padx=10,
                pady=5,
                cursor="hand2"
            ).pack(side="right", padx=5)

            # 2. NUEVO Botón para los Reportes y Gráficas
            tk.Button(
                frame_header,
                text="📊 Reportes",
                command=self.abrir_panel_reportes,
                bg="#0dcaf0",
                fg="black",
                font=("Segoe UI", 9, "bold"),
                relief="flat",
                padx=10,
                pady=5,
                cursor="hand2"
            ).pack(side="right", padx=5)

        # Contenedor principal con padding
        main_container = tk.Frame(self.root, bg="#f8f9fa", padx=20, pady=10)
        main_container.pack(fill="both", expand=True)

        # --- SECCIÓN 1: CATÁLOGO DE PRODUCTOS ---
        frame_catalogo = tk.LabelFrame(
            main_container, 
            text=" Catálogo de Productos ", 
            font=("Segoe UI", 10, "bold"),
            bg="#f8f9fa", 
            fg="#495057",
            padx=15, 
            pady=15
        )
        frame_catalogo.pack(fill="both", expand=True, pady=(0, 15))

        # Estilo moderno para el Treeview (Tabla)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=25, background="#ffffff", fieldbackground="#ffffff")
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#e9ecef", foreground="#212529")

        columnas = ("ID", "Nombre", "Precio", "Stock")
        self.tabla_productos = ttk.Treeview(frame_catalogo, columns=columnas, show="headings", height=5)
        
        self.tabla_productos.heading("ID", text="ID")
        self.tabla_productos.heading("Nombre", text="Producto")
        self.tabla_productos.heading("Precio", text="Precio Unitario")
        self.tabla_productos.heading("Stock", text="Stock")
        
        self.tabla_productos.column("ID", width=50, anchor="center")
        self.tabla_productos.column("Nombre", width=320, anchor="w")
        self.tabla_productos.column("Precio", width=130, anchor="e")
        self.tabla_productos.column("Stock", width=90, anchor="center")
        
        self.tabla_productos.pack(fill="both", expand=True, pady=(0, 10))

        # Cargar datos de PostgreSQL
        self.cargar_catalogo()

        # Controles de cantidad
        frame_controles = tk.Frame(frame_catalogo, bg="#f8f9fa")
        frame_controles.pack(fill="x", pady=5)
        
        tk.Label(frame_controles, text="Cantidad:", font=("Segoe UI", 9, "bold"), bg="#f8f9fa", fg="#495057").pack(side="left", padx=(0, 5))
        
        self.txt_cantidad = tk.Entry(frame_controles, font=("Segoe UI", 10), width=8, relief="solid", bd=1)
        self.txt_cantidad.insert(0, "1")
        self.txt_cantidad.pack(side="left", padx=5)
        
        tk.Button(
            frame_controles, 
            text="+ Agregar al Pedido", 
            bg="#28a745", 
            fg="white", 
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2",
            command=self.agregar_al_pedido
        ).pack(side="left", padx=15)

        # --- SECCIÓN 2: RESUMEN Y CONFIRMACIÓN ---
        frame_resumen = tk.LabelFrame(
            main_container, 
            text=" Detalle del Pedido Actual ", 
            font=("Segoe UI", 10, "bold"),
            bg="#f8f9fa", 
            fg="#495057",
            padx=15, 
            pady=15
        )
        frame_resumen.pack(fill="both", expand=True)

        self.lbl_detalle = tk.Label(
            frame_resumen, 
            text="No hay productos agregados.", 
            justify="left", 
            font=("Segoe UI", 10), 
            bg="#f8f9fa",
            fg="#212529"
        )
        self.lbl_detalle.pack(anchor="w", pady=(0, 10))

        tk.Button(
            frame_resumen, 
            text="✔ Confirmar Pedido y Generar Comprobante", 
            bg="#1a73e8", 
            fg="white", 
            font=("Segoe UI", 10, "bold"), 
            relief="flat",
            padx=15,
            pady=8,
            cursor="hand2",
            command=self.confirmar_compra
        ).pack(anchor="e")

    def cargar_catalogo(self):
        for item in self.tabla_productos.get_children():
            self.tabla_productos.delete(item)
            
        productos = listar_productos()
        if productos:
            for p in productos:
                self.tabla_productos.insert("", "end", values=(
                    p['codigo_producto'],
                    p['nombre'],
                    f"${p['precio_lista']:,.2f}",
                    p['cantidad_disponible']
                ))

    def agregar_al_pedido(self):
        seleccion = self.tabla_productos.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Selecciona un producto del catálogo.")
            return

        item = self.tabla_productos.item(seleccion[0])
        valores = item['values']
        
        id_prod = int(valores[0])
        nombre_prod = valores[1]
        
        # Extraer precio (limpiando $ y comas si los hay por el formato de la tabla)
        precio_str = str(valores[2]).replace('$', '').replace(',', '').strip()
        precio_prod = float(precio_str)
        stock = int(valores[3])

        try:
            cantidad = int(self.txt_cantidad.get())
            if cantidad <= 0: 
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Ingresa una cantidad válida mayor a 0.")
            return

        if cantidad > stock:
            messagebox.showwarning("Stock", f"Solo hay {stock} disponibles de este producto.")
            return

        # --- NUEVA LÓGICA: Verificar si el producto ya está en el carrito ---
        for articulo in self.carrito:
            if articulo['id'] == id_prod:
                # Verificamos que la suma total no supere el stock de la bodega
                if articulo['cantidad'] + cantidad > stock:
                    messagebox.showwarning("Stock Insuficiente", f"No puedes agregar más. El stock máximo es {stock}.")
                    return
                
                # Actualizamos cantidades y subtotales
                articulo['cantidad'] += cantidad
                articulo['subtotal'] = articulo['cantidad'] * articulo['precio']
                self.total_pedido += (cantidad * articulo['precio'])
                self.actualizar_texto_resumen()
                
                self.txt_cantidad.delete(0, tk.END)
                self.txt_cantidad.insert(0, "1")
                return # Terminamos la función aquí para no crear duplicados

        # Si el producto no estaba en el carrito, lo agregamos normalmente
        subtotal = precio_prod * cantidad
        self.carrito.append({
            'id': id_prod,
            'nombre': nombre_prod,
            'precio': precio_prod,
            'cantidad': cantidad,
            'subtotal': subtotal
        })
        
        self.total_pedido += subtotal
        self.actualizar_texto_resumen()
        
        # Limpiar el campo de cantidad
        self.txt_cantidad.delete(0, tk.END)
        self.txt_cantidad.insert(0, "1")

    def actualizar_texto_resumen(self):
        texto = ""
        for item in self.carrito:
            texto += f"• [{item['cantidad']}x] {item['nombre']} — Subtotal: ${item['subtotal']:,.2f}\n"
        texto += f"\nTOTAL A PAGAR: ${self.total_pedido:,.2f}"
        self.lbl_detalle.config(text=texto)

    def confirmar_compra(self):
        if not self.carrito:
            messagebox.showwarning("Vacío", "Agrega al menos un producto al pedido.")
            return
            
        # 1. Enviamos todo el carrito de un solo golpe usando la NUEVA función
        exito, resultado = registrar_carrito_completo(
            cc_usuario=self.usuario_actual['cc'],
            carrito=self.carrito,
            total_pedido=self.total_pedido,
            metodo_pago="PSE"
        )

        if exito:
            id_pedido_final = resultado
            messagebox.showinfo("Éxito", f"¡Pedido #{id_pedido_final} registrado exitosamente en la base de datos!")
            
            # 2. Generamos UN SOLO PDF con el ID real de la compra
            ex_pdf, msj_pdf = generar_comprobante_pdf(
                id_pedido=id_pedido_final,
                nombre_cliente=self.usuario_actual['nombre'],
                lista_carrito=self.carrito,
                total_general=self.total_pedido,
                metodo_pago="PSE",
                ruta_salida=f"comprobante_{id_pedido_final}.pdf"
            )
            
            if ex_pdf:
                messagebox.showinfo("PDF Creado", msj_pdf)
            
            # 3. Limpiamos la pantalla para la siguiente venta
            self.carrito.clear()
            self.total_pedido = 0.0
            self.actualizar_texto_resumen()
            self.cargar_catalogo()
        else:
            messagebox.showerror("Error de Transacción", f"No se pudo registrar la compra:\n{resultado}")

    def abrir_panel_admin(self):
        ventana_crud = tk.Toplevel(self.root)
        app_crud = CRUDWindow(ventana_crud)
        
        # Espera a que se cierre la ventana del CRUD
        self.root.wait_window(ventana_crud)
        
        # Solo actualiza el catálogo si la ventana principal no ha sido destruida
        if self.root.winfo_exists():
            self.cargar_catalogo()
    def cerrar_sesion(self):
        self.root.destroy()
    def abrir_panel_reportes(self):
        ventana_reportes = tk.Toplevel(self.root)
        app_reportes = ReportesWindow(ventana_reportes)
        ventana_reportes.grab_set() # Evita clics fuera de la ventana de reportes
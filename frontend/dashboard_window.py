import tkinter as tk
from tkinter import ttk, messagebox
from backend.transacciones import listar_productos, registrar_pedido, generar_comprobante_pdf
from frontend.crud_window import CRUDWindow
from frontend.reportes_window import ReportesWindow

class DashboardWindow:
    def __init__(self, root, usuario_actual):
        self.root = root
        self.usuario_actual = usuario_actual
        self.root.title(f"E-Market Express - Dashboard ({self.usuario_actual['rol']})")
        self.root.geometry("800x620")
        self.root.resizable(False, False)
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
            messagebox.showwarning("Atención", "Selecciona un producto de la tabla.")
            return
            
        valores = self.tabla_productos.item(seleccion[0])['values']
        id_prod = valores[0]
        nombre = valores[1]
        
        precio = float(str(valores[2]).replace("$", "").replace(",", ""))
        stock_disp = int(valores[3])
        
        try:
            cant = int(self.txt_cantidad.get())
            if cant <= 0: raise ValueError
        except:
            messagebox.showerror("Error", "Ingresa una cantidad válida mayor a 0.")
            return

        if cant > stock_disp:
            messagebox.showerror("Stock Insuficiente", f"Solo hay {stock_disp} unidades disponibles.")
            return

        subtotal = cant * precio
        self.carrito.append({
            "id": id_prod, "nombre": nombre, "cantidad": cant, "subtotal": subtotal
        })
        self.total_pedido += subtotal
        
        self.actualizar_texto_resumen()

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
            
        id_pedido_final = None
        errores = False

        # Recorremos todo el carrito para registrar cada producto
        for item in self.carrito:
            exito, resultado = registrar_pedido(
                cc_usuario=self.usuario_actual['cc'],
                codigo_producto=item['id'],
                cantidad=item['cantidad'],
                metodo_pago="PSE"
            )
            
            if exito:
                # Guardamos el primer ID generado para usarlo en el nombre del PDF
                if not id_pedido_final:
                    id_pedido_final = resultado
            else:
                errores = True
                messagebox.showerror("Error de Transacción", f"No se pudo registrar {item['nombre']}: {resultado}")
                break

        # Si el bucle termina sin errores, generamos el PDF y limpiamos
        if not errores and id_pedido_final:
            messagebox.showinfo("Éxito", f"¡Pedido #{id_pedido_final} registrado exitosamente en PostgreSQL!")
            
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
            
            self.carrito.clear()
            self.total_pedido = 0.0
            self.actualizar_texto_resumen()
            self.cargar_catalogo()

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
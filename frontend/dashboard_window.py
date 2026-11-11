import customtkinter as ctk
from tkinter import messagebox
from backend.transacciones import (
    listar_productos_con_categoria, 
    generar_comprobante_pdf, 
    registrar_carrito_completo
)
from frontend.crud_window import CRUDWindow
from frontend.reportes_window import ReportesWindow

class DashboardWindow:
    def __init__(self, root, usuario_actual):
        self.root = root
        self.usuario_actual = usuario_actual
        self.root.title("E-Market Express — Enterprise Dashboard")
        
        self.root.configure(fg_color="#070a12")
        self.root.after(50, lambda: self.root.state('zoomed'))

        self.carrito = []
        self.total_pedido = 0.0
        self.todos_los_productos = []
        self.producto_seleccionado = None

        header = ctk.CTkFrame(self.root, fg_color="#0f172a", height=70, corner_radius=0, border_width=1, border_color="#1e293b")
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        brand_frame = ctk.CTkFrame(header, fg_color="transparent")
        brand_frame.pack(side="left", padx=25)

        ctk.CTkLabel(
            brand_frame, 
            text="E-MARKET", 
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color="#ffffff"
        ).pack(side="left")

        ctk.CTkLabel(
            brand_frame, 
            text="EXPRESS", 
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color="#38bdf8"
        ).pack(side="left", padx=(4, 15))

        es_admin = self.usuario_actual['rol'] == 'Administrador'
        color_rol = "#312e81" if es_admin else "#065f46"
        text_rol = "#818cf8" if es_admin else "#34d399"
        
        ctk.CTkLabel(
            brand_frame,
            text=f"● {self.usuario_actual['nombre']} | {self.usuario_actual['rol'].upper()}",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            fg_color=color_rol,
            text_color=text_rol,
            corner_radius=10,
            padx=14,
            pady=5
        ).pack(side="left")

        btn_container = ctk.CTkFrame(header, fg_color="transparent")
        btn_container.pack(side="right", padx=25)

        if es_admin:
            ctk.CTkButton(
                btn_container,
                text="⚙ Panel Gerencial",
                fg_color="#d97706",
                hover_color="#b45309",
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                height=38,
                corner_radius=10,
                command=self.abrir_panel_admin
            ).pack(side="left", padx=5)

            ctk.CTkButton(
                btn_container,
                text="📊 Reportes",
                fg_color="#0284c7",
                hover_color="#0369a1",
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                height=38,
                corner_radius=10,
                command=self.abrir_panel_reportes
            ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_container,
            text="Cerrar Sesión",
            fg_color="#ef4444",
            hover_color="#dc2626",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            height=38,
            corner_radius=10,
            command=self.cerrar_sesion
        ).pack(side="left", padx=(10, 0))

        main_body = ctk.CTkFrame(self.root, fg_color="transparent")
        main_body.pack(fill="both", expand=True, padx=25, pady=20)

      
        col_left = ctk.CTkFrame(main_body, fg_color="#0f172a", corner_radius=16, border_width=1, border_color="#1e293b")
        col_left.pack(side="left", fill="both", expand=True, padx=(0, 15))

        top_left_bar = ctk.CTkFrame(col_left, fg_color="transparent")
        top_left_bar.pack(fill="x", padx=20, pady=(18, 12))

        ctk.CTkLabel(
            top_left_bar,
            text="Catálogo de Productos",
            font=ctk.CTkFont(family="Segoe UI", size=17, weight="bold"),
            text_color="#ffffff"
        ).pack(side="left")

        frame_filtros = ctk.CTkFrame(col_left, fg_color="#1e293b", corner_radius=12)
        frame_filtros.pack(fill="x", padx=20, pady=(0, 15))

        self.txt_buscar = ctk.CTkEntry(
            frame_filtros,
            placeholder_text="🔍 Buscar por nombre...",
            height=40,
            corner_radius=10,
            fg_color="#070a12",
            border_color="#334155",
            text_color="#ffffff"
        )
        self.txt_buscar.pack(side="left", fill="x", expand=True, padx=10, pady=8)
        self.txt_buscar.bind("<KeyRelease>", lambda e: self.filtrar_productos())

        self.combo_categoria = ctk.CTkOptionMenu(
            frame_filtros,
            values=["Todas las Categorías"],
            height=40,
            width=200,
            corner_radius=10,
            fg_color="#4f46e5",
            button_color="#4338ca",
            button_hover_color="#3730a3",
            dropdown_fg_color="#0f172a",
            dropdown_hover_color="#1e293b",
            dropdown_text_color="#ffffff",
            text_color="#ffffff",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            command=lambda val: self.filtrar_productos()
        )
        self.combo_categoria.pack(side="right", padx=10, pady=8)

        # GRID SCROLLEABLE DE TARJETAS
        self.grid_productos = ctk.CTkScrollableFrame(col_left, fg_color="#070a12", corner_radius=12)
        self.grid_productos.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        # BARRA INFERIOR: SELECCIÓN & CONTADOR
        frame_accion = ctk.CTkFrame(col_left, fg_color="#1e293b", corner_radius=12, height=60)
        frame_accion.pack(fill="x", padx=20, pady=(0, 15))

        self.lbl_prod_seleccionado = ctk.CTkLabel(
            frame_accion, 
            text="Selecciona un producto del catálogo...", 
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), 
            text_color="#94a3b8"
        )
        self.lbl_prod_seleccionado.pack(side="left", padx=15)

        frame_cant = ctk.CTkFrame(frame_accion, fg_color="transparent")
        frame_cant.pack(side="right", padx=15)

        ctk.CTkButton(
            frame_cant, text="-", width=32, height=32, corner_radius=8, 
            fg_color="#334155", hover_color="#475569", 
            font=ctk.CTkFont(size=14, weight="bold"), command=self.decrementar_cant
        ).pack(side="left", padx=2)

        self.txt_cantidad = ctk.CTkEntry(
            frame_cant, width=50, height=32, justify="center", corner_radius=8, 
            fg_color="#070a12", border_color="#334155", text_color="#ffffff"
        )
        self.txt_cantidad.insert(0, "1")
        self.txt_cantidad.pack(side="left", padx=2)

        ctk.CTkButton(
            frame_cant, text="+", width=32, height=32, corner_radius=8, 
            fg_color="#334155", hover_color="#475569", 
            font=ctk.CTkFont(size=14, weight="bold"), command=self.incrementar_cant
        ).pack(side="left", padx=(2, 12))

        ctk.CTkButton(
            frame_cant,
            text="+ Agregar al Pedido",
            height=38,
            corner_radius=10,
            fg_color="#10b981",
            hover_color="#059669",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            command=self.agregar_al_pedido
        ).pack(side="left")

      
        col_right = ctk.CTkFrame(main_body, fg_color="#0f172a", corner_radius=16, width=400, border_width=1, border_color="#1e293b")
        col_right.pack(side="right", fill="both")
        col_right.pack_propagate(False)

        top_resumen = ctk.CTkFrame(col_right, fg_color="transparent")
        top_resumen.pack(fill="x", padx=20, pady=(18, 12))

        ctk.CTkLabel(
            top_resumen,
            text="Resumen del Pedido",
            font=ctk.CTkFont(family="Segoe UI", size=17, weight="bold"),
            text_color="#ffffff"
        ).pack(side="left")

        # Botón para Vaciar Todo el Carrito
        ctk.CTkButton(
            top_resumen,
            text="Vaciar",
            width=60,
            height=26,
            corner_radius=6,
            fg_color="#334155",
            hover_color="#ef4444",
            text_color="#94a3b8",
            font=ctk.CTkFont(size=10, weight="bold"),
            command=self.vaciar_carrito
        ).pack(side="right")

        self.scroll_resumen = ctk.CTkScrollableFrame(col_right, fg_color="#1e293b", corner_radius=12)
        self.scroll_resumen.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        self.lbl_vacio = ctk.CTkLabel(
            self.scroll_resumen, 
            text="🛒 Tu carrito está vacío.\nHaz clic en un producto para agregarlo.", 
            font=ctk.CTkFont(family="Segoe UI", size=11), 
            text_color="#94a3b8"
        )
        self.lbl_vacio.pack(pady=40)

        frame_total = ctk.CTkFrame(col_right, fg_color="transparent")
        frame_total.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkLabel(
            frame_total, 
            text="TOTAL A PAGAR:", 
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), 
            text_color="#94a3b8"
        ).pack(anchor="w")

        self.lbl_total_valor = ctk.CTkLabel(
            frame_total, 
            text="$0.00", 
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"), 
            text_color="#38bdf8"
        )
        self.lbl_total_valor.pack(anchor="w", pady=(0, 15))

        ctk.CTkButton(
            frame_total,
            text="✔ Confirmar Compra y Facturar",
            height=45,
            corner_radius=12,
            fg_color="#4f46e5",
            hover_color="#4338ca",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            command=self.confirmar_compra
        ).pack(fill="x")

        # Cargar catálogo de PostgreSQL
        self.cargar_catalogo()

        # Botón de Actualizar / Refrescar Catálogo
        self.btn_actualizar = ctk.CTkButton(
            header,
            text="🔄 Actualizar",
            width=110,
            fg_color="#2b3137",
            hover_color="#3e444b",
            command=self.recargar_catalogo_manual
        )
        self.btn_actualizar.pack(side="right", padx=10)

    # --- CONTADORES INFERIORES (- / +) ---
    def incrementar_cant(self):
        try:
            val = int(self.txt_cantidad.get())
            self.txt_cantidad.delete(0, 'end')
            self.txt_cantidad.insert(0, str(val + 1))
        except ValueError:
            self.txt_cantidad.delete(0, 'end')
            self.txt_cantidad.insert(0, "1")

    def decrementar_cant(self):
        try:
            val = int(self.txt_cantidad.get())
            if val > 1:
                self.txt_cantidad.delete(0, 'end')
                self.txt_cantidad.insert(0, str(val - 1))
        except ValueError:
            self.txt_cantidad.delete(0, 'end')
            self.txt_cantidad.insert(0, "1")

    # --- LÓGICA DE DATOS ---
    def cargar_catalogo(self):
        self.todos_los_productos = listar_productos_con_categoria()
        
        categorias_set = set()
        for p in self.todos_los_productos:
            cat = str(p.get('categoria') or 'Sin Categoría').strip()
            if cat:
                categorias_set.add(cat)

        categorias_lista = ["Todas las Categorías"] + sorted(list(categorias_set))
        self.combo_categoria.configure(values=categorias_lista)
        self.combo_categoria.set("Todas las Categorías")
        self.filtrar_productos()

    def filtrar_productos(self):
        for child in self.grid_productos.winfo_children():
            child.destroy()

        busqueda = self.txt_buscar.get().strip().lower()
        cat_seleccionada = self.combo_categoria.get()

        productos_filtrados = []
        for p in self.todos_los_productos:
            nombre = str(p['nombre']).lower()
            categoria = str(p.get('categoria') or 'Sin Categoría')

            coincide_nombre = busqueda in nombre
            coincide_cat = (cat_seleccionada == "Todas las Categorías") or (categoria == cat_seleccionada)

            if coincide_nombre and coincide_cat:
                productos_filtrados.append(p)

        if not productos_filtrados:
            ctk.CTkLabel(
                self.grid_productos, 
                text="No se encontraron productos con los filtros aplicados.", 
                text_color="#94a3b8", 
                font=ctk.CTkFont(size=12)
            ).pack(pady=30)
            return

        for p in productos_filtrados:
            self._crear_tarjeta_producto(p)

    def _crear_tarjeta_producto(self, producto):
        card = ctk.CTkFrame(
            self.grid_productos, 
            fg_color="#0f172a", 
            corner_radius=12, 
            border_width=1, 
            border_color="#1e293b"
        )
        card.pack(fill="x", pady=6, padx=4)

        header_card = ctk.CTkFrame(card, fg_color="transparent")
        header_card.pack(fill="x", padx=15, pady=(12, 4))

        ctk.CTkLabel(
            header_card, 
            text=producto['nombre'], 
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), 
            text_color="#ffffff"
        ).pack(side="left")

        ctk.CTkLabel(
            header_card, 
            text=producto['categoria'].upper(), 
            font=ctk.CTkFont(family="Segoe UI", size=8, weight="bold"), 
            fg_color="#1e293b", 
            text_color="#38bdf8", 
            corner_radius=6, 
            padx=8, 
            pady=2
        ).pack(side="right")

        footer_card = ctk.CTkFrame(card, fg_color="transparent")
        footer_card.pack(fill="x", padx=15, pady=(0, 12))

        precio_fmt = f"${float(producto['precio_lista']):,.2f}"
        ctk.CTkLabel(
            footer_card, 
            text=precio_fmt, 
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"), 
            text_color="#34d399"
        ).pack(side="left")

        stock_txt = f"Stock: {producto['cantidad_disponible']}"
        ctk.CTkLabel(
            footer_card, 
            text=stock_txt, 
            font=ctk.CTkFont(family="Segoe UI", size=10), 
            text_color="#94a3b8"
        ).pack(side="left", padx=15)

        btn_seleccionar = ctk.CTkButton(
            footer_card, 
            text="Seleccionar", 
            width=90, 
            height=28, 
            corner_radius=8, 
            fg_color="#312e81", 
            hover_color="#4338ca", 
            font=ctk.CTkFont(size=10, weight="bold"),
            command=lambda p=producto: self.seleccionar_producto(p)
        )
        btn_seleccionar.pack(side="right")

    def seleccionar_producto(self, producto):
        self.producto_seleccionado = producto
        self.lbl_prod_seleccionado.configure(
            text=f"✔ {producto['nombre']} (${float(producto['precio_lista']):,.2f})", 
            text_color="#38bdf8"
        )

    def agregar_al_pedido(self):
        if not self.producto_seleccionado:
            messagebox.showwarning("Advertencia", "Haz clic en 'Seleccionar' en alguno de los productos del catálogo.")
            return

        p = self.producto_seleccionado
        id_prod = int(p['codigo_producto'])
        nombre_prod = p['nombre']
        precio_prod = float(p['precio_lista'])
        stock = int(p['cantidad_disponible'])

        try:
            cantidad = int(self.txt_cantidad.get())
            if cantidad <= 0: raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Ingresa una cantidad válida mayor a 0.")
            return

        if cantidad > stock:
            messagebox.showwarning("Stock Insuficiente", f"Solo hay {stock} unidades disponibles.")
            return

        for articulo in self.carrito:
            if articulo['id'] == id_prod:
                if articulo['cantidad'] + cantidad > stock:
                    messagebox.showwarning("Stock Límite", f"Superas el stock disponible ({stock}).")
                    return
                articulo['cantidad'] += cantidad
                articulo['subtotal'] = articulo['cantidad'] * articulo['precio']
                self.actualizar_vista_carrito()
                return

        subtotal = precio_prod * cantidad
        self.carrito.append({
            'id': id_prod,
            'nombre': nombre_prod,
            'precio': precio_prod,
            'cantidad': cantidad,
            'stock_max': stock,
            'subtotal': subtotal
        })
        
        self.txt_cantidad.delete(0, 'end')
        self.txt_cantidad.insert(0, "1")
        self.actualizar_vista_carrito()

    # --- NUEVAS FUNCIONES DE GESTIÓN INTERACTIVA DEL CARRITO ---
    def cambiar_cantidad_item(self, id_prod, cambio):
        """Aumenta o reduce 1 unidad directamente desde el ticket del carrito."""
        for item in self.carrito:
            if item['id'] == id_prod:
                nueva_cant = item['cantidad'] + cambio
                
                # Si llega a 0, eliminar ítem
                if nueva_cant <= 0:
                    self.eliminar_item_carrito(id_prod)
                    return

                # Validar stock máximo
                if nueva_cant > item['stock_max']:
                    messagebox.showwarning("Stock Máximo", f"Solo hay {item['stock_max']} unidades disponibles.")
                    return

                item['cantidad'] = nueva_cant
                item['subtotal'] = item['cantidad'] * item['precio']
                self.actualizar_vista_carrito()
                return

    def eliminar_item_carrito(self, id_prod):
        """Remueve completamente un producto del carrito."""
        self.carrito = [item for item in self.carrito if item['id'] != id_prod]
        self.actualizar_vista_carrito()

    def vaciar_carrito(self):
        """Limpia todo el carrito de compras."""
        if self.carrito:
            self.carrito.clear()
            self.actualizar_vista_carrito()

    # --- VISTA DEL RECIBO DEL CARRITO ---
    def actualizar_vista_carrito(self):
        for widget in self.scroll_resumen.winfo_children():
            widget.destroy()

        if not self.carrito:
            self.lbl_vacio = ctk.CTkLabel(
                self.scroll_resumen, 
                text="🛒 Tu carrito está vacío.\nHaz clic en un producto para agregarlo.", 
                font=ctk.CTkFont(family="Segoe UI", size=11), 
                text_color="#94a3b8"
            )
            self.lbl_vacio.pack(pady=40)
            self.lbl_total_valor.configure(text="$0.00")
            self.total_pedido = 0.0
            return

        self.total_pedido = 0.0
        for item in self.carrito:
            self.total_pedido += item['subtotal']

            card_item = ctk.CTkFrame(self.scroll_resumen, fg_color="#0f172a", corner_radius=10, border_width=1, border_color="#1e293b")
            card_item.pack(fill="x", pady=4, padx=2)

            # Nombre y Botón Eliminar [X]
            top_card = ctk.CTkFrame(card_item, fg_color="transparent")
            top_card.pack(fill="x", padx=10, pady=(6, 2))

            ctk.CTkLabel(
                top_card, 
                text=item['nombre'], 
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), 
                text_color="#ffffff"
            ).pack(side="left")

            btn_del = ctk.CTkButton(
                top_card, 
                text="✕", 
                width=22, 
                height=22, 
                corner_radius=6, 
                fg_color="#334155", 
                hover_color="#ef4444", 
                text_color="#ffffff", 
                font=ctk.CTkFont(size=10, weight="bold"),
                command=lambda id_p=item['id']: self.eliminar_item_carrito(id_p)
            )
            btn_del.pack(side="right")

            # Fila Inferior: Contadores [-] [+] y Subtotal
            bottom_card = ctk.CTkFrame(card_item, fg_color="transparent")
            bottom_card.pack(fill="x", padx=10, pady=(0, 6))

            # Contadores de unidad en el ticket
            cnt_frame = ctk.CTkFrame(bottom_card, fg_color="transparent")
            cnt_frame.pack(side="left")

            ctk.CTkButton(
                cnt_frame, text="-", width=22, height=22, corner_radius=5, 
                fg_color="#1e293b", hover_color="#334155", font=ctk.CTkFont(size=12, weight="bold"),
                command=lambda id_p=item['id']: self.cambiar_cantidad_item(id_p, -1)
            ).pack(side="left", padx=1)

            ctk.CTkLabel(
                cnt_frame, text=str(item['cantidad']), width=28, 
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color="#38bdf8"
            ).pack(side="left", padx=2)

            ctk.CTkButton(
                cnt_frame, text="+", width=22, height=22, corner_radius=5, 
                fg_color="#1e293b", hover_color="#334155", font=ctk.CTkFont(size=12, weight="bold"),
                command=lambda id_p=item['id']: self.cambiar_cantidad_item(id_p, 1)
            ).pack(side="left", padx=1)

            # Subtotal
            sub_txt = f"${item['subtotal']:,.2f}"
            ctk.CTkLabel(
                bottom_card, 
                text=sub_txt, 
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), 
                text_color="#34d399"
            ).pack(side="right")

        self.lbl_total_valor.configure(text=f"${self.total_pedido:,.2f}")

    def confirmar_compra(self):
        if not self.carrito:
            messagebox.showwarning("Carrito Vacío", "Agrega al menos un producto antes de confirmar.")
            return
            
        exito, resultado = registrar_carrito_completo(
            cc_usuario=self.usuario_actual['cc'],
            carrito=self.carrito,
            total_pedido=self.total_pedido,
            metodo_pago="PSE"
        )

        if exito:
            id_pedido_final = resultado
            messagebox.showinfo("¡Compra Exitosa!", f"Pedido #{id_pedido_final} registrado correctamente.")
            
            correo_cliente = self.usuario_actual.get('correo') or self.usuario_actual.get('email')
            
            ex_pdf, msj_pdf = generar_comprobante_pdf(
                id_pedido=id_pedido_final,
                nombre_cliente=self.usuario_actual['nombre'],
                lista_carrito=self.carrito,
                total_general=self.total_pedido,
                metodo_pago="PSE",
                ruta_salida=f"comprobante_{id_pedido_final}.pdf",
                correo_cliente=correo_cliente
            )
            
            if ex_pdf:
                messagebox.showinfo("Comprobante Enviado", msj_pdf)
            
            self.carrito.clear()
            self.actualizar_vista_carrito()
            self.cargar_catalogo()
        else:
            messagebox.showerror("Error de Transacción", f"No se pudo completar la compra:\n{resultado}")

    def abrir_panel_admin(self):
        ventana_crud = ctk.CTkToplevel(self.root)
        ventana_crud.title("Panel Gerencial - CRUD")
        ventana_crud.geometry("900x600")
        ventana_crud.lift()
        ventana_crud.focus_force()
        app_crud = CRUDWindow(ventana_crud)
        
        # --- NUEVAS LÍNEAS PARA LA SINCRONIZACIÓN AUTOMÁTICA ---
        self.root.wait_window(ventana_crud)
        self.cargar_catalogo()

    def abrir_panel_reportes(self):
        ventana_reportes = ctk.CTkToplevel(self.root)
        ventana_reportes.title("Reportes & Estadísticas")
        ventana_reportes.geometry("900x600")
        ventana_reportes.lift()
        ventana_reportes.focus_force()
        app_reportes = ReportesWindow(ventana_reportes)

    def cerrar_sesion(self):
        self.root.destroy()
        from frontend.login_window import LoginWindow
        nueva_raiz = ctk.CTk()
        app_login = LoginWindow(nueva_raiz)
        nueva_raiz.mainloop()

    def recargar_catalogo_manual(self):
        """Recarga de forma manual el catálogo y las categorías desde la BD."""
        try:
            self.cargar_catalogo()
            messagebox.showinfo("Actualizado", "Catálogo recargado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo recargar: {e}")
        
        
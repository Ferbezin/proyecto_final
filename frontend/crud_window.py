import customtkinter as ctk
from tkinter import ttk, messagebox
from backend.transacciones import (
    listar_productos_con_categoria, 
    eliminar_articulo,
    obtener_categorias_db,
    crear_articulo_con_cat,
    actualizar_articulo_con_cat
)

class CRUDWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("E-Market Express — Panel Gerencial (CRUD)")
        
        # PANTALLA COMPLETA NATIVA
        self.root.configure(fg_color="#070a12")
        self.root.after(50, lambda: self.root.state('zoomed'))

        self.id_seleccionado = None
        self.categorias_map = {} # {"NombreCat": id_cat}

        # Contenedor Principal
        main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=25, pady=20)

        # ==========================================
        # ENCABEZADO CON BOTÓN DE RETORNO
        # ==========================================
        header_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            header_frame,
            text="⚙ Panel Gerencial — Administración de Inventario",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color="#ffffff"
        ).pack(side="left")

        # BOTÓN DE RETORNO AL DASHBOARD
        ctk.CTkButton(
            header_frame,
            text="← Volver al Dashboard",
            height=36,
            corner_radius=10,
            fg_color="#334155",
            hover_color="#475569",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            command=self.volver_al_dashboard
        ).pack(side="right")

        body_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        body_frame.pack(fill="both", expand=True)

        left_frame = ctk.CTkFrame(body_frame, fg_color="#0f172a", corner_radius=15, border_width=1, border_color="#1e293b")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 15))

        ctk.CTkLabel(
            left_frame,
            text="Catálogo Registrado en PostgreSQL",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color="#38bdf8"
        ).pack(anchor="w", padx=20, pady=(15, 10))

        # Tabla 
        table_wrapper = ctk.CTkFrame(left_frame, fg_color="#1e293b", corner_radius=10, border_width=1, border_color="#334155")
        table_wrapper.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview", 
            font=("Segoe UI", 10), 
            rowheight=30, 
            background="#1e293b", 
            fieldbackground="#1e293b", 
            foreground="#ffffff",
            borderwidth=0
        )
        style.configure(
            "Treeview.Heading", 
            font=("Segoe UI", 10, "bold"), 
            background="#0f172a", 
            foreground="#38bdf8",
            relief="flat"
        )
        style.map("Treeview", background=[("selected", "#4f46e5")], foreground=[("selected", "#ffffff")])

        columnas = ("ID", "Nombre", "Categoría", "Precio", "Stock")
        self.tabla = ttk.Treeview(table_wrapper, columns=columnas, show="headings", selectmode="browse")
        
        self.tabla.heading("ID", text="ID")
        self.tabla.heading("Nombre", text="Nombre del Producto")
        self.tabla.heading("Categoría", text="Categoría")
        self.tabla.heading("Precio", text="Precio Unitario")
        self.tabla.heading("Stock", text="Stock")
        
        self.tabla.column("ID", width=50, anchor="center")
        self.tabla.column("Nombre", width=220, anchor="w")
        self.tabla.column("Categoría", width=130, anchor="center")
        self.tabla.column("Precio", width=100, anchor="e")
        self.tabla.column("Stock", width=70, anchor="center")
        
        self.tabla.pack(fill="both", expand=True, padx=2, pady=2)
        self.tabla.bind("<<TreeviewSelect>>", self.cargar_datos_seleccionados)

        # --- SECCIÓN DERECHA: FORMULARIO CRUD ---
        right_frame = ctk.CTkFrame(body_frame, fg_color="#0f172a", corner_radius=15, width=380, border_width=1, border_color="#1e293b")
        right_frame.pack(side="right", fill="both")
        right_frame.pack_propagate(False)

        ctk.CTkLabel(
            right_frame,
            text="Detalles del Artículo",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color="#ffffff"
        ).pack(anchor="w", padx=20, pady=(15, 15))

        form = ctk.CTkFrame(right_frame, fg_color="transparent")
        form.pack(fill="x", padx=20)

        # CAMPO: NOMBRE
        ctk.CTkLabel(form, text="NOMBRE DEL PRODUCTO", font=ctk.CTkFont(size=9, weight="bold"), text_color="#cbd5e1").pack(anchor="w", pady=(0, 2))
        self.txt_nombre = ctk.CTkEntry(form, height=38, corner_radius=8, fg_color="#1e293b", border_color="#334155", text_color="#ffffff")
        self.txt_nombre.pack(fill="x", pady=(0, 12))

        # CAMPO: CATEGORÍA (OPTION MENU)
        ctk.CTkLabel(form, text="CATEGORÍA", font=ctk.CTkFont(size=9, weight="bold"), text_color="#cbd5e1").pack(anchor="w", pady=(0, 2))
        self.combo_categoria = ctk.CTkOptionMenu(
            form, 
            values=["Cargando..."], 
            height=38, 
            corner_radius=8, 
            fg_color="#1e293b", 
            button_color="#334155", 
            button_hover_color="#475569", 
            text_color="#ffffff"
        )
        self.combo_categoria.pack(fill="x", pady=(0, 12))

        # CAMPO: PRECIO
        ctk.CTkLabel(form, text="PRECIO UNITARIO ($)", font=ctk.CTkFont(size=9, weight="bold"), text_color="#cbd5e1").pack(anchor="w", pady=(0, 2))
        self.txt_precio = ctk.CTkEntry(form, height=38, corner_radius=8, fg_color="#1e293b", border_color="#334155", text_color="#ffffff")
        self.txt_precio.pack(fill="x", pady=(0, 12))

        # CAMPO: STOCK
        ctk.CTkLabel(form, text="STOCK DISPONIBLE", font=ctk.CTkFont(size=9, weight="bold"), text_color="#cbd5e1").pack(anchor="w", pady=(0, 20))
        self.txt_stock = ctk.CTkEntry(form, height=38, corner_radius=8, fg_color="#1e293b", border_color="#334155", text_color="#ffffff")
        self.txt_stock.pack(fill="x", pady=(0, 20))

        # BOTONES DE ACCIÓN CRUD
        btn_grid = ctk.CTkFrame(right_frame, fg_color="transparent")
        btn_grid.pack(fill="x", padx=20, side="bottom", pady=20)

        ctk.CTkButton(
            btn_grid, text="➕ Crear", height=38, corner_radius=8, 
            fg_color="#10b981", hover_color="#059669", font=ctk.CTkFont(size=11, weight="bold"),
            command=self.crear
        ).pack(fill="x", pady=(0, 8))

        ctk.CTkButton(
            btn_grid, text="✏️ Actualizar", height=38, corner_radius=8, 
            fg_color="#d97706", hover_color="#b45309", font=ctk.CTkFont(size=11, weight="bold"),
            command=self.actualizar
        ).pack(fill="x", pady=(0, 8))

        ctk.CTkButton(
            btn_grid, text="🗑 Eliminar", height=38, corner_radius=8, 
            fg_color="#ef4444", hover_color="#dc2626", font=ctk.CTkFont(size=11, weight="bold"),
            command=self.eliminar
        ).pack(fill="x", pady=(0, 8))

        ctk.CTkButton(
            btn_grid, text="🧹 Limpiar Campos", height=34, corner_radius=8, 
            fg_color="#334155", hover_color="#475569", text_color="#cbd5e1", font=ctk.CTkFont(size=10, weight="bold"),
            command=self.limpiar_campos
        ).pack(fill="x")

        # Cargar datos iniciales
        self.cargar_categorias_combo()
        self.cargar_tabla()

    def volver_al_dashboard(self):
        """Cierra la ventana del CRUD y regresa limpiamente al Dashboard."""
        self.root.destroy()

    def cargar_categorias_combo(self):
        cats = obtener_categorias_db()
        if cats:
            self.categorias_map = {c['nombre']: c['id_categoria'] for c in cats}
            nombres = list(self.categorias_map.keys())
            self.combo_categoria.configure(values=nombres)
            self.combo_categoria.set(nombres[0])
        else:
            self.combo_categoria.configure(values=["Sin Categorías"])

    def cargar_tabla(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
            
        productos = listar_productos_con_categoria()
        if productos:
            for p in productos:
                self.tabla.insert("", "end", values=(
                    p['codigo_producto'],
                    p['nombre'],
                    p['categoria'],
                    f"${float(p['precio_lista']):,.2f}",
                    p['cantidad_disponible']
                ))

    def cargar_datos_seleccionados(self, event):
        seleccion = self.tabla.selection()
        if seleccion:
            valores = self.tabla.item(seleccion[0])['values']
            self.id_seleccionado = valores[0]
            
            self.txt_nombre.delete(0, 'end')
            self.txt_nombre.insert(0, valores[1])
            
            cat_nombre = str(valores[2])
            if cat_nombre in self.categorias_map:
                self.combo_categoria.set(cat_nombre)
            
            precio_limpio = str(valores[3]).replace("$", "").replace(",", "").strip()
            self.txt_precio.delete(0, 'end')
            self.txt_precio.insert(0, precio_limpio)
            
            self.txt_stock.delete(0, 'end')
            self.txt_stock.insert(0, valores[4])

    def limpiar_campos(self):
        self.id_seleccionado = None
        self.txt_nombre.delete(0, 'end')
        self.txt_precio.delete(0, 'end')
        self.txt_stock.delete(0, 'end')

    def crear(self):
        nombre = self.txt_nombre.get().strip()
        cat_nombre = self.combo_categoria.get()
        id_cat = self.categorias_map.get(cat_nombre)

        try:
            precio = float(self.txt_precio.get())
            stock = int(self.txt_stock.get())
        except ValueError:
            messagebox.showerror("Error", "El precio y el stock deben ser numéricos.")
            return

        if not nombre or not id_cat:
            messagebox.showwarning("Atención", "El nombre y la categoría son obligatorios.")
            return

        exito, msg = crear_articulo_con_cat(nombre, precio, stock, id_cat)
        if exito:
            messagebox.showinfo("Éxito", msg)
            self.cargar_tabla()
            self.limpiar_campos()
        else:
            messagebox.showerror("Error", msg)

    def actualizar(self):
        if not self.id_seleccionado:
            messagebox.showwarning("Atención", "Selecciona un producto de la tabla para actualizar.")
            return

        nombre = self.txt_nombre.get().strip()
        cat_nombre = self.combo_categoria.get()
        id_cat = self.categorias_map.get(cat_nombre)

        try:
            precio = float(self.txt_precio.get())
            stock = int(self.txt_stock.get())
        except ValueError:
            messagebox.showerror("Error", "El precio y el stock deben ser numéricos.")
            return

        exito, msg = actualizar_articulo_con_cat(self.id_seleccionado, nombre, precio, stock, id_cat)
        if exito:
            messagebox.showinfo("Éxito", msg)
            self.cargar_tabla()
            self.limpiar_campos()
        else:
            messagebox.showerror("Error", msg)

    def eliminar(self):
        if not self.id_seleccionado:
            messagebox.showwarning("Atención", "Selecciona un producto de la tabla para eliminar.")
            return

        if messagebox.askyesno("Confirmar", "¿Estás seguro de eliminar este artículo?"):
            exito, msg = eliminar_articulo(self.id_seleccionado)
            if exito:
                messagebox.showinfo("Éxito", msg)
                self.cargar_tabla()
                self.limpiar_campos()
            else:
                messagebox.showerror("Error", msg)
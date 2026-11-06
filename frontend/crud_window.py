import tkinter as tk
from tkinter import ttk, messagebox
from backend.transacciones import listar_productos, crear_articulo, actualizar_articulo, eliminar_articulo

class CRUDWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("E-Market Express - Gestión de Catálogo (CRUD)")
        self.root.geometry("750x550")
        self.root.resizable(False, False)
        self.root.configure(bg="#f8f9fa")

        main_frame = tk.Frame(self.root, bg="#f8f9fa", padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)

        tk.Label(
            main_frame, 
            text="Administración de Artículos", 
            font=("Segoe UI", 16, "bold"), 
            bg="#f8f9fa", 
            fg="#212529"
        ).pack(anchor="w", pady=(0, 15))

        # --- TABLA DE PRODUCTOS ---
        columnas = ("ID", "Nombre", "Precio", "Stock")
        self.tabla = ttk.Treeview(main_frame, columns=columnas, show="headings", height=8)
        
        self.tabla.heading("ID", text="ID")
        self.tabla.heading("Nombre", text="Nombre del Producto")
        self.tabla.heading("Precio", text="Precio Unitario")
        self.tabla.heading("Stock", text="Stock Disponible")
        
        self.tabla.column("ID", width=50, anchor="center")
        self.tabla.column("Nombre", width=300, anchor="w")
        self.tabla.column("Precio", width=130, anchor="e")
        self.tabla.column("Stock", width=100, anchor="center")
        
        self.tabla.pack(fill="x", pady=(0, 15))
        self.tabla.bind("<<TreeviewSelect>>", self.cargar_datos_seleccionados)

        self.cargar_tabla()

        # --- FORMULARIO DE ENTRADA ---
        form_frame = tk.LabelFrame(
            main_frame, 
            text=" Detalle del Artículo ", 
            font=("Segoe UI", 10, "bold"), 
            bg="#f8f9fa", 
            fg="#495057",
            padx=15, 
            pady=15
        )
        form_frame.pack(fill="both", expand=True)

        tk.Label(form_frame, text="Nombre:", font=("Segoe UI", 9, "bold"), bg="#f8f9fa").grid(row=0, column=0, sticky="w", pady=5)
        self.txt_nombre = tk.Entry(form_frame, font=("Segoe UI", 10), width=30, relief="solid", bd=1)
        self.txt_nombre.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        tk.Label(form_frame, text="Precio ($):", font=("Segoe UI", 9, "bold"), bg="#f8f9fa").grid(row=1, column=0, sticky="w", pady=5)
        self.txt_precio = tk.Entry(form_frame, font=("Segoe UI", 10), width=15, relief="solid", bd=1)
        self.txt_precio.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        tk.Label(form_frame, text="Stock:", font=("Segoe UI", 9, "bold"), bg="#f8f9fa").grid(row=2, column=0, sticky="w", pady=5)
        self.txt_stock = tk.Entry(form_frame, font=("Segoe UI", 10), width=15, relief="solid", bd=1)
        self.txt_stock.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        # Botones de Acción CRUD
        btn_frame = tk.Frame(form_frame, bg="#f8f9fa")
        btn_frame.grid(row=3, column=0, columnspan=2, pady=15)

        tk.Button(
            btn_frame, text="➕ Crear Nuevo", bg="#28a745", fg="white", font=("Segoe UI", 9, "bold"),
            relief="flat", padx=10, pady=6, cursor="hand2", command=self.crear
        ).pack(side="left", padx=5)

        tk.Button(
            btn_frame, text="✏️ Actualizar", bg="#ffc107", fg="#212529", font=("Segoe UI", 9, "bold"),
            relief="flat", padx=10, pady=6, cursor="hand2", command=self.actualizar
        ).pack(side="left", padx=5)

        tk.Button(
            btn_frame, text="🗑 Eliminar", bg="#dc3545", fg="white", font=("Segoe UI", 9, "bold"),
            relief="flat", padx=10, pady=6, cursor="hand2", command=self.eliminar
        ).pack(side="left", padx=5)

        tk.Button(
            btn_frame, text="🧹 Limpiar Campos", bg="#6c757d", fg="white", font=("Segoe UI", 9, "bold"),
            relief="flat", padx=10, pady=6, cursor="hand2", command=self.limpiar_campos
        ).pack(side="left", padx=5)

        self.id_seleccionado = None

    def cargar_tabla(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        productos = listar_productos()
        if productos:
            for p in productos:
                self.tabla.insert("", "end", values=(
                    p['codigo_producto'],
                    p['nombre'],
                    f"${p['precio_lista']:,.2f}",
                    p['cantidad_disponible']
                ))

    def cargar_datos_seleccionados(self, event):
        seleccion = self.tabla.selection()
        if seleccion:
            valores = self.tabla.item(seleccion[0])['values']
            self.id_seleccionado = valores[0]
            self.txt_nombre.delete(0, tk.END)
            self.txt_nombre.insert(0, valores[1])
            
            precio_limpio = str(valores[2]).replace("$", "").replace(",", "")
            self.txt_precio.delete(0, tk.END)
            self.txt_precio.insert(0, precio_limpio)
            
            self.txt_stock.delete(0, tk.END)
            self.txt_stock.insert(0, valores[3])

    def limpiar_campos(self):
        self.id_seleccionado = None
        self.txt_nombre.delete(0, tk.END)
        self.txt_precio.delete(0, tk.END)
        self.txt_stock.delete(0, tk.END)
        self.txt_stock.insert(0, "0")

    def crear(self):
        nombre = self.txt_nombre.get().strip()
        try:
            precio = float(self.txt_precio.get())
            stock = int(self.txt_stock.get())
        except ValueError:
            messagebox.showerror("Error", "El precio y el stock deben ser numéricos.")
            return

        if not nombre:
            messagebox.showwarning("Atención", "El nombre del producto es obligatorio.")
            return

        exito, msg = crear_articulo(nombre, precio, stock)
        if exito:
            messagebox.showinfo("Éxito", msg)
            self.cargar_tabla()
            self.limpiar_codes = self.limpiar_campos()
        else:
            messagebox.showerror("Error", msg)

    def actualizar(self):
        if not self.id_seleccionado:
            messagebox.showwarning("Atención", "Selecciona un producto de la tabla para actualizar.")
            return

        nombre = self.txt_nombre.get().strip()
        try:
            precio = float(self.txt_precio.get())
            stock = int(self.txt_stock.get())
        except ValueError:
            messagebox.showerror("Error", "El precio y el stock deben ser numéricos.")
            return

        exito, msg = actualizar_articulo(self.id_seleccionado, nombre, precio, stock)
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
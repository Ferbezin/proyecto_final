import tkinter as tk
from tkinter import ttk, messagebox
from backend.auth import autenticar_usuario
from backend.transacciones import listar_productos, registrar_pedido

class DemoAvanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Backend con Carrito")
        self.root.geometry("750x680")

        # Variables de estado local
        self.carrito = [] # Lista de items: [{'id': 1, 'nombre': '...', 'cantidad': 2, 'precio_unit': 100, 'subtotal': 200}]
        self.total_acumulado = 0.0

        # --- SECCIÓN 1: LOGIN (backend.auth) ---
        frame_login = tk.LabelFrame(self.root, text=" 1. Autenticación (backend.auth) ", padx=10, pady=10)
        frame_login.pack(fill="x", padx=15, pady=5)

        tk.Label(frame_login, text="Cédula / CC:").grid(row=0, column=0, sticky="w", pady=5)
        self.txt_cc = tk.Entry(frame_login, width=15)
        self.txt_cc.insert(0, "11223344")
        self.txt_cc.grid(row=0, column=1, pady=5)

        tk.Label(frame_login, text="Contraseña:").grid(row=0, column=2, sticky="w", pady=5, padx=(10, 0))
        self.txt_pass = tk.Entry(frame_login, width=15, show="*")
        self.txt_pass.insert(0, "clave123")
        self.txt_pass.grid(row=0, column=3, pady=5)

        btn_login = tk.Button(frame_login, text="Iniciar Sesión", bg="#2196F3", fg="white", command=self.probar_login)
        btn_login.grid(row=0, column=4, padx=10, pady=5)

        # --- SECCIÓN 2: CATÁLOGO EN TIEMPO REAL (PostgreSQL) ---
        frame_cat = tk.LabelFrame(self.root, text=" 2. Catálogo de Productos Disponible ", padx=10, pady=5)
        frame_cat.pack(fill="both", expand=True, padx=15, pady=5)

        self.tabla_cat = ttk.Treeview(frame_cat, columns=("ID", "Nombre", "Precio", "Stock"), show="headings", height=4)
        self.tabla_cat.heading("ID", text="ID")
        self.tabla_cat.heading("Nombre", text="Producto")
        self.tabla_cat.heading("Precio", text="Precio Unitario")
        self.tabla_cat.heading("Stock", text="Stock")

        self.tabla_cat.column("ID", width=50, anchor="center")
        self.tabla_cat.column("Nombre", width=250)
        self.tabla_cat.column("Precio", width=100, anchor="e")
        self.tabla_cat.column("Stock", width=80, anchor="center")
        self.tabla_cat.pack(fill="both", expand=True)

        # Controles para añadir al carrito
        frame_add = tk.Frame(frame_cat)
        frame_add.pack(fill="x", pady=5)

        tk.Label(frame_add, text="ID Producto seleccionado:").pack(side="left", padx=5)
        self.txt_prod_id = tk.Entry(frame_add, width=8)
        self.txt_prod_id.insert(0, "1")
        self.txt_prod_id.pack(side="left", padx=5)

        tk.Label(frame_add, text="Cantidad:").pack(side="left", padx=5)
        self.txt_cant = tk.Entry(frame_add, width=8)
        self.txt_cant.insert(0, "1")
        self.txt_cant.pack(side="left", padx=5)

        btn_add = tk.Button(frame_add, text="+ Agregar al Carrito", bg="#FF9800", fg="white", command=self.agregar_al_carrito)
        btn_add.pack(side="left", padx=15)

        # --- SECCIÓN 3: CARRITO Y CONFIRMACIÓN ---
        frame_car = tk.LabelFrame(self.root, text=" 3. Pedido Actual (En Proceso) ", padx=10, pady=5)
        frame_car.pack(fill="both", expand=True, padx=15, pady=5)

        self.tabla_car = ttk.Treeview(frame_car, columns=("ID", "Nombre", "Cantidad", "Subtotal"), show="headings", height=4)
        self.tabla_car.heading("ID", text="ID")
        self.tabla_car.heading("Nombre", text="Producto")
        self.tabla_car.heading("Cantidad", text="Cantidad")
        self.tabla_car.heading("Subtotal", text="Subtotal")

        self.tabla_car.column("ID", width=50, anchor="center")
        self.tabla_car.column("Nombre", width=250)
        self.tabla_car.column("Cantidad", width=80, anchor="center")
        self.tabla_car.column("Subtotal", width=120, anchor="e")
        self.tabla_car.pack(fill="both", expand=True)

        # Pie de carrito: Total y Botón de confirmación
        frame_total = tk.Frame(frame_car)
        frame_total.pack(fill="x", pady=5)

        self.lbl_total = tk.Label(frame_total, text="Total del Pedido: $0.00", font=("Arial", 12, "bold"), fg="#D32F2F")
        self.lbl_total.pack(side="left", padx=10)

        btn_confirmar = tk.Button(frame_total, text="✔ Confirmar y Registrar Pedido", bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), command=self.confirmar_pedido)
        btn_confirmar.pack(side="right", padx=10)

        # Cargar catálogo inicial
        self.cargar_catalogo()

    def cargar_catalogo(self):
        for fila in self.tabla_cat.get_children():
            self.tabla_cat.delete(fila)
        
        self.productos_db = listar_productos()
        if self.productos_db:
            for p in self.productos_db:
                self.tabla_cat.insert("", "end", values=(
                    p['codigo_producto'],
                    p['nombre'],
                    f"${p['precio_lista']:,.2f}",
                    p['cantidad_disponible']
                ))

    def probar_login(self):
        cc = self.txt_cc.get().strip()
        clave = self.txt_pass.get().strip()

        if not cc or not clave:
            messagebox.showwarning("Atención", "Ingresa CC y contraseña.")
            return

        exito, res = autenticar_usuario(int(cc), clave)
        if exito:
            messagebox.showinfo("Éxito Auth", f"¡Bienvenido! Autenticado como {res['rol']}")
        else:
            messagebox.showerror("Error Auth", f"Credenciales inválidas: {res}")

    def agregar_al_carrito(self):
        prod_id = self.txt_prod_id.get().strip()
        cant = self.txt_cant.get().strip()

        if not prod_id or not cant:
            messagebox.showwarning("Atención", "Ingresa ID y cantidad.")
            return

        # Buscar el producto en el catálogo cargado de PostgreSQL
        prod_id = int(prod_id)
        cant = int(cant)
        producto_encontrado = None

        if self.productos_db:
            for p in self.productos_db:
                if p['codigo_producto'] == prod_id:
                    producto_encontrado = p
                    break

        if not producto_encontrado:
            messagebox.showerror("Error", f"Producto con ID #{prod_id} no existe en el catálogo.")
            return

        if cant > producto_encontrado['cantidad_disponible']:
            messagebox.showwarning("Stock Insuficiente", f"Solo hay {producto_encontrado['cantidad_disponible']} unidades disponibles.")
            return

        # Calcular valor y agregar
        precio_unit = float(producto_encontrado['precio_lista'])
        subtotal = precio_unit * cant

        self.carrito.append({
            'id': prod_id,
            'nombre': producto_encontrado['nombre'],
            'cantidad': cant,
            'subtotal': subtotal
        })

        self.actualizar_vista_carrito()

    def actualizar_vista_carrito(self):
        # Limpiar lista visual del carrito
        for fila in self.tabla_car.get_children():
            self.tabla_car.delete(fila)

        self.total_acumulado = 0.0

        for item in self.carrito:
            self.tabla_car.insert("", "end", values=(
                item['id'],
                item['nombre'],
                item['cantidad'],
                f"${item['subtotal']:,.2f}"
            ))
            self.total_acumulado += item['subtotal']

        # Actualizar la etiqueta del valor total del pedido
        self.lbl_total.config(text=f"Total del Pedido: ${self.total_acumulado:,.2f}")

    def confirmar_pedido(self):
        cc = self.txt_cc.get().strip()

        if not self.carrito:
            messagebox.showwarning("Carrito Vacío", "No has agregado ningún producto al pedido.")
            return

        if not cc:
            messagebox.showwarning("Atención", "Ingresa la Cédula/CC del usuario.")
            return

        pedidos_exitosos = 0
        errores = []

        # Procesar los elementos del carrito llamando al backend
        for item in self.carrito:
            exito, res = registrar_pedido(
                cc_usuario=int(cc),
                codigo_producto=item['id'],
                cantidad=item['cantidad'],
                metodo_pago='PSE'
            )

            if exito:
                pedidos_exitosos += 1
            else:
                errores.append(f"Prod #{item['id']}: {res}")

        if pedidos_exitosos > 0:
            messagebox.showinfo("Pedido Confirmado", f"¡Se procesaron {pedidos_exitosos} ítem(s) correctamente en PostgreSQL!\nTotal Pagado: ${self.total_acumulado:,.2f}")
            
            # Limpiar carrito y refrescar inventario real
            self.carrito.clear()
            self.actualizar_vista_carrito()
            self.cargar_catalogo()
        else:
            messagebox.showerror("Error al procesar", f"No se pudo completar la transacción:\n" + "\n".join(errores))

if __name__ == "__main__":
    root = tk.Tk()
    app = DemoAvanceApp(root)
    root.mainloop()
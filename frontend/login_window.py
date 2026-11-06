import tkinter as tk
from tkinter import messagebox
from backend.auth import autenticar_usuario
from frontend.dashboard_window import DashboardWindow

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("E-Market Express - Iniciar Sesión")
        self.root.geometry("400x380")
        self.root.resizable(False, False)
        self.root.configure(bg="#f8f9fa")

        # Contenedor principal con padding y fondo moderno
        main_frame = tk.Frame(self.root, bg="#f8f9fa", padx=30, pady=30)
        main_frame.pack(fill="both", expand=True)

        # Título principal moderno
        tk.Label(
            main_frame, 
            text="E-Market Express", 
            font=("Segoe UI", 18, "bold"), 
            bg="#f8f9fa", 
            fg="#1a73e8"
        ).pack(anchor="w", pady=(0, 5))

        tk.Label(
            main_frame, 
            text="Inicia sesión para continuar", 
            font=("Segoe UI", 10), 
            bg="#f8f9fa", 
            fg="#6c757d"
        ).pack(anchor="w", pady=(0, 20))

        # Campo para el correo
        tk.Label(
            main_frame, 
            text="Correo electrónico", 
            font=("Segoe UI", 9, "bold"), 
            bg="#f8f9fa", 
            fg="#495057"
        ).pack(anchor="w", pady=(0, 5))
        
        self.txt_correo = tk.Entry(
            main_frame, 
            font=("Segoe UI", 11), 
            relief="solid", 
            bd=1
        )
        self.txt_correo.pack(fill="x", ipady=6, pady=(0, 15))

        # Campo para la contraseña
        tk.Label(
            main_frame, 
            text="Contraseña", 
            font=("Segoe UI", 9, "bold"), 
            bg="#f8f9fa", 
            fg="#495057"
        ).pack(anchor="w", pady=(0, 5))
        
        self.txt_clave = tk.Entry(
            main_frame, 
            font=("Segoe UI", 11), 
            show="*", 
            relief="solid", 
            bd=1
        )
        self.txt_clave.pack(fill="x", ipady=6, pady=(0, 25))

        # Botón de ingreso moderno tipo "flat"
        self.btn_ingresar = tk.Button(
            main_frame, 
            text="Ingresar", 
            bg="#1a73e8", 
            fg="white", 
            font=("Segoe UI", 10, "bold"), 
            relief="flat", 
            cursor="hand2",
            command=self.validar_login
        )
        self.btn_ingresar.pack(fill="x", ipady=8)

    def validar_login(self):
        correo = self.txt_correo.get().strip()
        clave = self.txt_clave.get().strip()

        if not correo or not clave:
            messagebox.showwarning("Campos vacíos", "Por favor, ingresa tu correo y contraseña.")
            return

        usuario = autenticar_usuario(correo, clave)

        if usuario:
            messagebox.showinfo("Acceso Concedido", f"¡Bienvenido {usuario['nombre']}!\nRol: {usuario['rol']}")
            self.root.destroy()
            
            nueva_raiz = tk.Tk()
            app_dashboard = DashboardWindow(nueva_raiz, usuario)
            nueva_raiz.mainloop()
        else:
            messagebox.showerror("Error de Autenticación", "El correo o la contraseña son incorrectos. Verifica e intenta de nuevo.")
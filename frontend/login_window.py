import customtkinter as ctk
from tkinter import messagebox
from backend.auth import autenticar_usuario
from frontend.dashboard_window import DashboardWindow
from frontend.register_window import RegisterWindow

# Configuración del tema global de la app
ctk.set_appearance_mode("Dark")  # Opciones: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # Opciones: "blue", "green", "dark-blue"

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("E-Market Express — Access Portal")
        
        # PANTALLA COMPLETA NATIVA
        self.root.state('zoomed')
        self.root.configure(fg_color="#0b0f19")

        # Contenedor Principal Centrado
        main_wrapper = ctk.CTkFrame(self.root, fg_color="transparent")
        main_wrapper.pack(expand=True)

        # TARJETA PRINCIPAL CON BORDES REDONDEADOS Y SOMBRA VISUAL
        card = ctk.CTkFrame(
            main_wrapper, 
            corner_radius=20, 
            fg_color="#131b2e", 
            border_width=1, 
            border_color="#1e293b"
        )
        card.pack(padx=20, pady=20)

        # ==========================================
        # PANEL IZQUIERDO: HERO INSTITUCIONAL
        # ==========================================
        panel_left = ctk.CTkFrame(
            card, 
            corner_radius=20, 
            fg_color="#1e1b4b", 
            width=320, 
            height=460
        )
        panel_left.pack_propagate(False)
        panel_left.pack(side="left", fill="both", padx=(5, 0), pady=5)

        # Badge superior
        badge = ctk.CTkLabel(
            panel_left,
            text="SYSTEM ENTERPRISE",
            font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
            fg_color="#312e81",
            text_color="#818cf8",
            corner_radius=8,
            padx=10,
            pady=4
        )
        badge.pack(anchor="w", padx=30, pady=(40, 25))

        # Título principal
        ctk.CTkLabel(
            panel_left,
            text="E-Market",
            font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"),
            text_color="#ffffff"
        ).pack(anchor="w", padx=30)

        ctk.CTkLabel(
            panel_left,
            text="Express",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color="#818cf8"
        ).pack(anchor="w", padx=30, pady=(0, 20))

        # Descripción
        desc_text = (
            "Gestión inteligente de inventarios,\n"
            "control de ventas en tiempo real y\n"
            "facturación automatizada vía Gmail."
        )
        ctk.CTkLabel(
            panel_left,
            text=desc_text,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            justify="left",
            text_color="#a5b4fc"
        ).pack(anchor="w", padx=30)

        # Footer
        ctk.CTkLabel(
            panel_left,
            text="v2.4 Build 2026 • Security Protected",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color="#6366f1"
        ).pack(side="bottom", anchor="w", padx=30, pady=25)


        # ==========================================
        # PANEL DERECHO: FORMULARIO MODERNO
        # ==========================================
        panel_right = ctk.CTkFrame(card, fg_color="transparent", width=400, height=460)
        panel_right.pack_propagate(False)
        panel_right.pack(side="right", fill="both", expand=True, padx=35, pady=35)

        ctk.CTkLabel(
            panel_right,
            text="Iniciar Sesión",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color="#ffffff"
        ).pack(anchor="w", pady=(0, 2))

        ctk.CTkLabel(
            panel_right,
            text="Ingresa tus credenciales para continuar",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#94a3b8"
        ).pack(anchor="w", pady=(0, 25))

        # CAMPO: CORREO
        ctk.CTkLabel(
            panel_right,
            text="CORREO ELECTRÓNICO",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color="#cbd5e1"
        ).pack(anchor="w", pady=(0, 5))

        self.txt_correo = ctk.CTkEntry(
            panel_right,
            placeholder_text="ejemplo@correo.com",
            height=42,
            corner_radius=10,
            fg_color="#1e293b",
            border_color="#334155",
            text_color="#ffffff",
            placeholder_text_color="#64748b"
        )
        self.txt_correo.pack(fill="x", pady=(0, 15))

        # CAMPO: CONTRASEÑA
        ctk.CTkLabel(
            panel_right,
            text="CONTRASEÑA",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color="#cbd5e1"
        ).pack(anchor="w", pady=(0, 5))

        self.txt_clave = ctk.CTkEntry(
            panel_right,
            placeholder_text="••••••••",
            show="*",
            height=42,
            corner_radius=10,
            fg_color="#1e293b",
            border_color="#334155",
            text_color="#ffffff",
            placeholder_text_color="#64748b"
        )
        self.txt_clave.pack(fill="x", pady=(0, 25))

        # BOTÓN PRINCIPAL: INGRESAR
        self.btn_ingresar = ctk.CTkButton(
            panel_right,
            text="Acceder al Sistema",
            height=45,
            corner_radius=10,
            fg_color="#4f46e5",
            hover_color="#4338ca",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            command=self.validar_login
        )
        self.btn_ingresar.pack(fill="x", pady=(0, 12))

        # BOTÓN SECUNDARIO: CREAR CUENTA
        self.btn_crear = ctk.CTkButton(
            panel_right,
            text="Crear una cuenta nueva",
            height=38,
            corner_radius=10,
            fg_color="#1e293b",
            hover_color="#334155",
            text_color="#94a3b8",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            command=self.abrir_registro
        )
        self.btn_crear.pack(fill="x")

    def validar_login(self):
        correo = self.txt_correo.get().strip()
        clave = self.txt_clave.get().strip()

        if not correo or not clave:
            messagebox.showwarning("Campos Incompletos", "Por favor ingresa tu correo y contraseña.")
            return

        usuario = autenticar_usuario(correo, clave)

        if usuario:
            messagebox.showinfo("Acceso Concedido", f"¡Bienvenido {usuario['nombre']}!\nRol asignado: {usuario['rol']}")
            self.root.destroy()
            
            # Nota: Al migrar Dashboard a CustomTkinter usaremos ctk.CTk()
            nueva_raiz = ctk.CTk()
            app_dashboard = DashboardWindow(nueva_raiz, usuario)
            nueva_raiz.mainloop()
        else:
            messagebox.showerror("Error de Autenticación", "El correo o la contraseña son incorrectos. Intenta de nuevo.")

    def abrir_registro(self):
        RegisterWindow(self.root)
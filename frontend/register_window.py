import customtkinter as ctk
from tkinter import messagebox
import psycopg2

def registrar_cliente_db(cc, nombre, correo, telefono, clave):
    """
    Inserta un nuevo usuario en la base de datos PostgreSQL.
    """
    try:
        conexion = psycopg2.connect(
            dbname="proyecto_final",
            user="postgres",
            password="1234",  # Tu contraseña de PostgreSQL
            host="localhost",
            port="5432"
        )
        conexion.autocommit = True
        cursor = conexion.cursor()
        
        query = """
            INSERT INTO usuario (cc, nombre, correo, telefono, clave) 
            VALUES (%s, %s, %s, %s, %s);
        """
        cursor.execute(query, (int(cc), str(nombre), str(correo), str(telefono), str(clave)))
        cursor.close()
        conexion.close()
        return True, "Registro exitoso."
    except Exception as e:
        return False, str(e)


class RegisterWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("E-Market Express — Crear Cuenta")
        self.geometry("480x640")
        self.resizable(False, False)
        self.configure(fg_color="#0b0f19")
        
        # Mantener la ventana al frente
        self.grab_set()

        # Contenedor Tarjeta con bordes suaves
        card = ctk.CTkFrame(
            self, 
            corner_radius=20, 
            fg_color="#131b2e", 
            border_width=1, 
            border_color="#1e293b"
        )
        card.pack(fill="both", expand=True, padx=20, pady=20)

        # Encabezado
        ctk.CTkLabel(
            card,
            text="Crear nueva cuenta",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color="#ffffff"
        ).pack(anchor="w", padx=30, pady=(25, 2))

        ctk.CTkLabel(
            card,
            text="Ingresa tus datos para registrarte como cliente",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#94a3b8"
        ).pack(anchor="w", padx=30, pady=(0, 20))

        # --- CAMPOS DE FORMULARIO ESTILIZADOS ---
        scroll_frame = ctk.CTkFrame(card, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=30)

        self.txt_cc = self._crear_campo(scroll_frame, "CÉDULA / DOCUMENTO (CC)", "Ej: 10203040")
        self.txt_nombre = self._crear_campo(scroll_frame, "NOMBRE COMPLETO", "Ej: Ana Gómez")
        self.txt_correo = self._crear_campo(scroll_frame, "CORREO ELECTRÓNICO", "ejemplo@correo.com")
        self.txt_telefono = self._crear_campo(scroll_frame, "TELÉFONO / CELULAR", "Ej: 3001234567")
        self.txt_clave = self._crear_campo(scroll_frame, "CONTRASEÑA", "••••••••", es_clave=True)

        # BOTÓN DE REGISTRO
        btn_registrar = ctk.CTkButton(
            card,
            text="Completar Registro",
            height=45,
            corner_radius=10,
            fg_color="#4f46e5",
            hover_color="#4338ca",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            command=self.procesar_registro
        )
        btn_registrar.pack(fill="x", padx=30, pady=(15, 25))

    def _crear_campo(self, parent, label_text, placeholder, es_clave=False):
        ctk.CTkLabel(
            parent,
            text=label_text,
            font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
            text_color="#cbd5e1"
        ).pack(anchor="w", pady=(0, 3))

        entry = ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            show="*" if es_clave else "",
            height=38,
            corner_radius=8,
            fg_color="#1e293b",
            border_color="#334155",
            text_color="#ffffff",
            placeholder_text_color="#64748b"
        )
        entry.pack(fill="x", pady=(0, 10))
        return entry

    def procesar_registro(self):
        cc = self.txt_cc.get().strip()
        nombre = self.txt_nombre.get().strip()
        correo = self.txt_correo.get().strip()
        telefono = self.txt_telefono.get().strip()
        clave = self.txt_clave.get().strip()

        if not all([cc, nombre, correo, telefono, clave]):
            messagebox.showwarning("Campos Incompletos", "Por favor completa todos los campos del formulario.")
            return

        exito, msg = registrar_cliente_db(cc, nombre, correo, telefono, clave)
        if exito:
            messagebox.showinfo("¡Registro Exitoso!", "Tu cuenta ha sido creada correctamente. Ya puedes iniciar sesión.")
            self.destroy()
        else:
            messagebox.showerror("Error al Registrar", f"No se pudo crear la cuenta:\n{msg}")
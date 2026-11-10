# -*- coding: utf-8 -*-
import customtkinter as ctk
from frontend.login_window import LoginWindow

if __name__ == "__main__":
    # Usamos ctk.CTk() en lugar de tk.Tk() para activar el motor gráfico moderno
    root = ctk.CTk()
    
    # Inyectamos la ventana de Login
    app = LoginWindow(root)
    
    # Mantenemos la aplicación corriendo
    root.mainloop()
import tkinter as tk
from frontend.login_window import LoginWindow

if __name__ == "__main__":
    # Creamos la ventana principal vacía
    root = tk.Tk()
    
    # Le inyectamos el diseño que acabamos de hacer
    app = LoginWindow(root)
    
    # Mantenemos la ventana abierta
    root.mainloop()
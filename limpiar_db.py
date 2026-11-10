from backend.conexion import conectar_bd

def reiniciar_sistema_completo():
    conexion = conectar_bd()
    
    if not conexion:
        print("Error: No se pudo conectar a la base de datos.")
        return

    try:
        cursor = conexion.cursor()
        
        # 1. Borra todas las ventas, vacía los filtros de tiempo y reinicia los IDs de comprobantes a 1
        cursor.execute("TRUNCATE TABLE pedido RESTART IDENTITY CASCADE;")
        
        # 2. Restaura el stock de todos los artículos en el catálogo a 50 unidades
        cursor.execute("UPDATE articulo SET cantidad_disponible = 50;")
        
        conexion.commit()
        
        print("Sistema reseteado con éxito.")
        print("Comprobantes, histórico general, ventas de hoy y 5 min están en CERO.")
        print("El stock de todos los artículos ha vuelto a 50 unidades.")
        
    except Exception as e:
        print(f"Error al limpiar: {e}")
        conexion.rollback()
    finally:
        if cursor: 
            cursor.close()
        if conexion: 
            conexion.close()

if __name__ == "__main__":
    reiniciar_sistema_completo()
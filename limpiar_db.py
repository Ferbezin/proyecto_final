import os
from backend.conexion import conectar_bd

def reiniciar_sistema_completo():
    conexion = conectar_bd()
    
    if not conexion:
        print("Error: No se pudo conectar a la base de datos.")
        return

    try:
        cursor = conexion.cursor()
        
        # 1. Borrar toda la estructura vieja para evitar choques con el código nuevo
        print("Eliminando estructura antigua de la base de datos...")
        cursor.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
        
        # 2. Leer el archivo SQL actualizado de tus compañeros
        ruta_sql = 'base de datos_emarket/proyecto_final.sql'
        
        if os.path.exists(ruta_sql):
            with open(ruta_sql, 'r', encoding='utf-8') as archivo_sql:
                script = archivo_sql.read()
            
            # 3. Ejecutar el script para crear las tablas nuevas e insertar los productos
            print("Inyectando nueva estructura y datos desde proyecto_final.sql...")
            cursor.execute(script)
            conexion.commit()
            
            print("¡Base de datos actualizada y reconstruida con éxito!")
        else:
            print(f"Error: No se encontró el archivo {ruta_sql} en la carpeta actual.")
            
    except Exception as e:
        print(f"Error al limpiar y actualizar la base de datos: {e}")
        conexion.rollback()
    finally:
        if 'cursor' in locals() and cursor: 
            cursor.close()
        if conexion: 
            conexion.close()

if __name__ == "__main__":
    reiniciar_sistema_completo()
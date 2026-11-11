import psycopg2

# Configuración de conexión a PostgreSQL
DB_CONFIG = {
    "dbname": "proyecto_final",
    "user": "postgres",
    "password": "1234",  
    "host": "localhost",
    "port": "5432",
    "options": "-c lc_messages=C"  # <-- ESTA LÍNEA ES LA CLAVE
}

def conectar_bd():
    try:
        conexion = psycopg2.connect(**DB_CONFIG)
        conexion.set_client_encoding('LATIN1')
        return conexion
    except Exception as e:
        print(f"Error al conectar a la BD: {e}")
        return None

def ejecutar_consulta(query, params=None, fetch=False):
    conexion = None
    cursor = None
    try:
        conexion = conectar_bd()
        if not conexion:
            return None
        cursor = conexion.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        resultado = None
        if fetch:
            columnas = [desc[0] for desc in cursor.description]
            filas = cursor.fetchall()
            resultado = []
            for fila in filas:
                fila_limpia = []
                for val in fila:
                    if isinstance(val, bytes):
                        # Ajustado a latin1 para coincidir con la codificación de la BD
                        val = val.decode('latin1', errors='ignore')
                    fila_limpia.append(val)
                resultado.append(dict(zip(columnas, fila_limpia)))
        
        conexion.commit()
        return resultado
    except Exception as e:
        # Aquí es donde se imprimirá el error real en español
        print(f"Error en consulta: {e}")
        return None
    finally:
        if cursor: cursor.close()
        if conexion: conexion.close()

def ejecutar_procedimiento(nombre_sp, params=None):
    conexion = None
    cursor = None
    try:
        conexion = conectar_bd()
        if not conexion:
            return False, "No se pudo conectar a la base de datos."
        cursor = conexion.cursor()
        
        # Solución para PostgreSQL moderno: Forzar el uso de CALL
        if params:
            placeholders = ", ".join(["%s"] * len(params))
            query = f"CALL {nombre_sp}({placeholders});"
            cursor.execute(query, params)
        else:
            query = f"CALL {nombre_sp}();"
            cursor.execute(query)
            
        try:
            resultado = cursor.fetchone()
        except:
            resultado = None
            
        conexion.commit()
        return True, resultado
    except Exception as e:
        if conexion: conexion.rollback()
        return False, str(e)
    finally:
        if cursor: cursor.close()
        if conexion: conexion.close()
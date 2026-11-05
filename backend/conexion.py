import psycopg2
from psycopg2 import Error, extras

CONFIG_DB = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "12345",
    "database": "proyecto_final"
}

def obtener_conexion():
    try:
        conexion = psycopg2.connect(**CONFIG_DB)
        conexion.set_client_encoding('UTF8')
        return conexion
    except Error as e:
        print(f"Error de conexion a la base de datos: {e}")
        return None

def ejecutar_consulta(query, params=None, fetch=False, commit=False):
    conexion = obtener_conexion()
    if not conexion:
        return (False, "Sin conexion a la base de datos.") if commit else []

    try:
        with conexion.cursor(cursor_factory=extras.RealDictCursor) as cursor:
            cursor.execute(query, params or ())
            
            if commit:
                conexion.commit()
                return True, cursor.rowcount
            
            if fetch:
                return cursor.fetchall()
                
    except Error as e:
        if commit:
            conexion.rollback()
        print(f"Error en la consulta SQL: {e}")
        return (False, str(e)) if commit else []
    finally:
        conexion.close()

def ejecutar_procedimiento(nombre_sp, params=None):
    conexion = obtener_conexion()
    if not conexion:
        return False, "Sin conexion a la base de datos."

    try:
        with conexion.cursor() as cursor:
            placeholders = ", ".join(["%s"] * len(params)) if params else ""
            sql = f"CALL {nombre_sp}({placeholders});"
            
            cursor.execute(sql, params or ())
            
            res = None
            if cursor.description:
                res = cursor.fetchone()
                
            conexion.commit()
            return True, res
    except Error as e:
        conexion.rollback()
        print(f"Error al ejecutar el procedimiento {nombre_sp}: {e}")
        return False, str(e)
    finally:
        conexion.close()

if __name__ == "__main__":
    conn = obtener_conexion()
    if conn:
        print("Conexion exitosa a la base de datos 'proyecto_final'.")
        conn.close()
    else:
        print("Error: No se logro conectar a PostgreSQL.")
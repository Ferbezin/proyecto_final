from backend.conexion import ejecutar_consulta

import csv

#De aqui en adelante seran las funciones que mas o menos tenga que usar el de la interfaz para ver como muestra las consultas mas apropiadas
#Estos son fundamentalmente los SELECTS que vaya a usar.

def obtener_top_productos_vendidos(limite=5, filtro="Histórico Completo"):
    # 1. Consulta base uniendo la tabla 'pedido'
    query = """
        SELECT p.codigo_producto, a.nombre, SUM(p.cantidad_vendida) as total_vendido
        FROM pedido_articulo p
        JOIN articulo a ON p.codigo_producto = a.codigo_producto
        JOIN pedido ped ON p.id_pedido = ped.id_pedido
    """
    
    # 2. Aplicar el filtro de tiempo si es necesario
    if filtro == "Últimos 5 min":
        query += " WHERE ped.f_transaccion >= NOW() - INTERVAL '5 minutes'"
    elif filtro == "Hoy":
        query += " WHERE DATE(ped.f_transaccion) = CURRENT_DATE"
        
    # 3. Agrupar y ordenar
    query += """
        GROUP BY p.codigo_producto, a.nombre
        ORDER BY total_vendido DESC
        LIMIT %s;
    """
    
    return ejecutar_consulta(query, params=(limite,), fetch=True)

def obtener_resumen_ventas_por_cliente():
    query = """
        SELECT u.cc, u.nombre, COUNT(p.id_pedido) AS total_pedidos
        FROM usuario u
        LEFT JOIN pedido p ON u.cc = p.cc_usuario
        GROUP BY u.cc, u.nombre
        ORDER BY total_pedidos DESC;
    """
    return ejecutar_consulta(query, fetch=True)

def obtener_inventario_critico(umbral_minimo=10):
    query = """
        SELECT codigo_producto, nombre, cantidad_disponible
        FROM articulo
        WHERE cantidad_disponible <= %s
        ORDER BY cantidad_disponible ASC;
    """
    return ejecutar_consulta(query, params=(umbral_minimo,), fetch=True)

def obtener_inventario_completo():
    query = """
        SELECT codigo_producto, nombre, cantidad_disponible
        FROM articulo
        ORDER BY cantidad_disponible ASC;
    """
    return ejecutar_consulta(query, fetch=True)

#IMPORTANTE: Hay que hacer un botón o algo para la funcion de aqui abajo, la cual, crea un csv con los datos
#de cualquiera de las 3 consultas anteriores, si lo ve pertinente, puede hacer mas consultas utiles.

def exportar_reporte_a_csv(datos, nombre_archivo="reporte.csv"):
    if not datos:
        return False, "No hay datos para exportar."
    
    try:
        columnas = datos[0].keys()
        with open(nombre_archivo, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=columnas)
            writer.writeheader()
            writer.writerows(datos)
        return True, f"Reporte exportado exitosamente como '{nombre_archivo}'."
    except Exception as e:
        return False, f"Error al exportar reporte: {e}"

if __name__ == "__main__":
    print("Probando reporte: Top productos vendidos")
    print(obtener_top_productos_vendidos())
    
    print("\nProbando reporte: Resumen de ventas por cliente")
    print(obtener_resumen_ventas_por_cliente())
    
    print("\nProbando reporte: Inventario critico")
    print(obtener_inventario_critico())
    #Esto se puede quitar es solo para ver si funciona sin interfaz grafica
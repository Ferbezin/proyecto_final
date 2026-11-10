from backend.conexion import ejecutar_procedimiento, ejecutar_consulta
from fpdf import FPDF
import os
import psycopg2

def listar_productos():
    query = """
        SELECT codigo_producto, nombre, precio_lista, cantidad_disponible
        FROM articulo
        ORDER BY codigo_producto ASC;
    """
    return ejecutar_consulta(query, fetch=True)

def registrar_pedido(cc_usuario, codigo_producto, cantidad, metodo_pago):
    params = (cc_usuario, codigo_producto, cantidad, metodo_pago, None)
    exito, res = ejecutar_procedimiento("sp_registrar_pedido_completo", params)
    
    if exito:
        id_pedido = res[0] if res else None
        return True, id_pedido
    else:
        return False, res

def transferir_inventario(codigo_producto, id_bodega_origen, id_bodega_destino, cantidad):
    params = (codigo_producto, id_bodega_origen, id_bodega_destino, cantidad)
    exito, res = ejecutar_procedimiento("sp_atualizar_inventario_bodega", params)
    
    if exito:
        return True, "Transferencia de inventario realizada correctamente."
    else:
        return False, res


# --- FUNCIONES DEL MÓDULO CRUD DE ARTÍCULOS ---

def crear_articulo(nombre, precio, stock):
    try:
        conexion = psycopg2.connect(
            dbname="proyecto_final",
            user="postgres",
            password="1234",  # Tu contraseña actual
            host="localhost",
            port="5432"
        )
        conexion.autocommit = True
        cursor = conexion.cursor()
        query = "INSERT INTO articulo (nombre, precio_lista, cantidad_disponible) VALUES (%s, %s, %s);"
        cursor.execute(query, (str(nombre), float(precio), int(stock)))
        cursor.close()
        conexion.close()
        return True, "Artículo creado exitosamente."
    except Exception as e:
        return False, str(e)

def actualizar_articulo(codigo_producto, nombre, precio, stock):
    try:
        conexion = psycopg2.connect(
            dbname="proyecto_final",
            user="postgres",
            password="1234",  # Tu contraseña actual
            host="localhost",
            port="5432"
        )
        conexion.autocommit = True
        cursor = conexion.cursor()
        query = "UPDATE articulo SET nombre = %s, precio_lista = %s, cantidad_disponible = %s WHERE codigo_producto = %s;"
        cursor.execute(query, (str(nombre), float(precio), int(stock), int(codigo_producto)))
        cursor.close()
        conexion.close()
        return True, "Artículo actualizado exitosamente."
    except Exception as e:
        return False, str(e)

def eliminar_articulo(codigo_producto):
    try:
        conexion = psycopg2.connect(
            dbname="proyecto_final",
            user="postgres",
            password="1234",  # Tu contraseña actual
            host="localhost",
            port="5432"
        )
        conexion.autocommit = True
        cursor = conexion.cursor()
        query = "DELETE FROM articulo WHERE codigo_producto = %s;"
        cursor.execute(query, (int(codigo_producto),))
        cursor.close()
        conexion.close()
        return True, "Artículo eliminado exitosamente."
    except Exception as e:
        return False, str(e)


# --- GENERACIÓN DE COMPROBANTE PDF ---

def generar_comprobante_pdf(id_pedido, nombre_cliente, lista_carrito, total_general, metodo_pago, ruta_salida):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        
        pdf.cell(0, 10, "COMPROBANTE DE COMPRA", 0, 1, "C")
        pdf.ln(10)
        
        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 6, f"ID Pedido: #{id_pedido}", 0, 1)
        pdf.cell(0, 6, f"Cliente: {nombre_cliente}", 0, 1)
        pdf.cell(0, 6, f"Metodo de Pago: {metodo_pago}", 0, 1)
        pdf.ln(10)
        
        pdf.set_font("Arial", "B", 10)
        pdf.cell(90, 8, "Producto", 1, 0, "C")
        pdf.cell(40, 8, "Cantidad", 1, 0, "C")
        pdf.cell(50, 8, "Subtotal", 1, 1, "C")
        
        pdf.set_font("Arial", "", 10)
        for item in lista_carrito:
            pdf.cell(90, 8, str(item['nombre']), 1, 0, "L")
            pdf.cell(40, 8, str(item['cantidad']), 1, 0, "C")
            pdf.cell(50, 8, f"${item['subtotal']:,.2f}", 1, 1, "R")
            
        pdf.set_font("Arial", "B", 10)
        pdf.cell(130, 8, "TOTAL GENERAL:", 1, 0, "R")
        pdf.cell(50, 8, f"${total_general:,.2f}", 1, 1, "R")
        
        pdf.ln(15)
        pdf.set_font("Arial", "I", 9)
        pdf.cell(0, 6, "Gracias por su compra en nuestra plataforma.", 0, 1, "C")
        
        pdf.output(ruta_salida)
        return True, f"Comprobante guardado como {ruta_salida}"
    except Exception as e:
        return False, str(e)

# --- NUEVA FUNCIÓN PARA SOLUCIONAR LOS SALTOS DE NÚMEROS ---
def registrar_carrito_completo(cc_usuario, carrito, total_pedido, metodo_pago="PSE"):
    # Importamos tu conexión real
    from backend.conexion import conectar_bd 
    
    conexion = conectar_bd()
    if not conexion:
        return False, "No se pudo conectar a la base de datos."
        
    try:
        cursor = conexion.cursor()
        
        # 1. Crear UN SOLO encabezado de pedido para todo el carrito
        cursor.execute("""
            INSERT INTO pedido (cc_usuario, total, estado_id) 
            VALUES (%s, %s, (SELECT MIN(estado_id) FROM estado_envio)) 
            RETURNING id_pedido;
        """, (cc_usuario, total_pedido))
        
        id_pedido = cursor.fetchone()[0]
        
        # 2. Guardar todos los productos bajo ESE MISMO id_pedido
        for item in carrito:
            # Buscamos el precio actual del producto en la base de datos
            cursor.execute("SELECT precio_lista FROM articulo WHERE codigo_producto = %s", (item['id'],))
            precio_real = cursor.fetchone()[0]
            
            # Guardamos el detalle de la venta sin crear un nuevo ID de pedido
            cursor.execute("""
                INSERT INTO pedido_articulo (id_pedido, codigo_producto, cantidad_vendida, precio_facturado)
                VALUES (%s, %s, %s, %s);
            """, (id_pedido, item['id'], item['cantidad'], precio_real))
            
            # Descontamos el stock
            cursor.execute("""
                UPDATE articulo 
                SET cantidad_disponible = cantidad_disponible - %s
                WHERE codigo_producto = %s;
            """, (item['cantidad'], item['id']))
        
       # 3. Registrar el pago de la factura
        cursor.execute("""
            INSERT INTO factura_pago (id_pedido, metodo_pago, valor_pagado)
            VALUES (%s, %s, %s);
        """, (id_pedido, metodo_pago, total_pedido))
        
        # Guardamos todo de un solo golpe
        conexion.commit() 
        return True, id_pedido
        
    except Exception as e:
        conexion.rollback() 
        return False, str(e)
    finally:
        if cursor: cursor.close()
        if conexion: conexion.close()

    
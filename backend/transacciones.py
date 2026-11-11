# -*- coding: utf-8 -*-
from backend.conexion import ejecutar_procedimiento, ejecutar_consulta
from backend.email_service import enviar_comprobante_email
from fpdf import FPDF
import os
import psycopg2
import psycopg2
from psycopg2.extras import RealDictCursor

def listar_productos():
    query = """
        SELECT codigo_producto, nombre, precio_lista, cantidad_disponible
        FROM articulo
        ORDER BY codigo_producto ASC;
    """
    return ejecutar_consulta(query, fetch=True)

import psycopg2
from psycopg2.extras import RealDictCursor

def listar_productos_con_categoria():
    """
    Obtiene la lista de artículos resolviendo problemas de codificación de tildes/caracteres especiales.
    """
    try:
        conexion = psycopg2.connect(
            dbname="proyecto_final",
            user="postgres",
            password="1234",
            host="localhost",
            port="5432",
            options="-c client_encoding=UTF8"
        )
        conexion.set_client_encoding('UTF8')
        cursor = conexion.cursor(cursor_factory=RealDictCursor)
        
        query = """
            SELECT 
                a.codigo_producto,
                a.nombre,
                a.precio_lista,
                a.cantidad_disponible,
                COALESCE(c.nombre, 'Sin Categoría') AS categoria
            FROM articulo a
            LEFT JOIN categoria c ON a.id_categoria = c.id_categoria
            ORDER BY a.codigo_producto ASC;
        """
        cursor.execute(query)
        productos = cursor.fetchall()
        
        # Limpieza activa de codificación para tildes y ñ
        productos_limpios = []
        for p in productos:
            nombre = p['nombre']
            categoria = p['categoria']
            
            if isinstance(nombre, bytes):
                nombre = nombre.decode('utf-8', errors='ignore')
            if isinstance(categoria, bytes):
                categoria = categoria.decode('utf-8', errors='ignore')
                
            p['nombre'] = str(nombre)
            p['categoria'] = str(categoria)
            productos_limpios.append(p)

        cursor.close()
        conexion.close()
        return productos_limpios
    except Exception as e:
        print(f"Error al listar productos con categoría: {e}")
        return []

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

def obtener_categorias_db():
    """Obtiene el listado de categorías disponibles."""
    try:
        conexion = psycopg2.connect(
            dbname="proyecto_final", user="postgres", password="1234", host="localhost", port="5432"
        )
        cursor = conexion.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT id_categoria, nombre FROM categoria ORDER BY nombre ASC;")
        cats = cursor.fetchall()
        cursor.close()
        conexion.close()
        return cats
    except Exception as e:
        print(f"Error al obtener categorias: {e}")
        return []

def crear_articulo_con_cat(nombre, precio, stock, id_categoria):
    """Crea un artículo asignándole su categoría."""
    try:
        conexion = psycopg2.connect(
            dbname="proyecto_final", user="postgres", password="1234", host="localhost", port="5432"
        )
        conexion.autocommit = True
        cursor = conexion.cursor()
        query = """
            INSERT INTO articulo (nombre, precio_lista, cantidad_disponible, id_categoria)
            VALUES (%s, %s, %s, %s);
        """
        cursor.execute(query, (nombre, precio, stock, id_categoria))
        cursor.close()
        conexion.close()
        return True, "Artículo creado exitosamente."
    except Exception as e:
        return False, str(e)

def actualizar_articulo_con_cat(codigo_producto, nombre, precio, stock, id_categoria):
    """Actualiza los datos de un artículo existente."""
    try:
        conexion = psycopg2.connect(
            dbname="proyecto_final", user="postgres", password="1234", host="localhost", port="5432"
        )
        conexion.autocommit = True
        cursor = conexion.cursor()
        query = """
            UPDATE articulo 
            SET nombre = %s, precio_lista = %s, cantidad_disponible = %s, id_categoria = %s
            WHERE codigo_producto = %s;
        """
        cursor.execute(query, (nombre, precio, stock, id_categoria, codigo_producto))
        cursor.close()
        conexion.close()
        return True, "Artículo actualizado correctamente."
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


# --- GENERACIÓN Y ENVÍO DE COMPROBANTE PDF ---

def generar_comprobante_pdf(id_pedido, nombre_cliente, lista_carrito, total_general, metodo_pago, ruta_salida, correo_cliente=None):
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
        
        # 1. Guardar el PDF en disco
        pdf.output(ruta_salida)
        msg_resultado = f"Comprobante guardado en {ruta_salida}"

        # 2. Si se proporciona correo, enviarlo en automático
        if correo_cliente:
            exito_mail, msg_mail = enviar_comprobante_email(correo_cliente, nombre_cliente, ruta_salida)
            if exito_mail:
                msg_resultado += " y enviado por correo electrónico."
            else:
                msg_resultado += f", pero falló el envío del correo: {msg_mail}"

        return True, msg_resultado
    except Exception as e:
        return False, str(e)


# --- FUNCIÓN DE REGISTRO COMPLETO DEL CARRITO ---

def registrar_carrito_completo(cc_usuario, carrito, total_pedido, metodo_pago="PSE"):
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
            cursor.execute("SELECT precio_lista FROM articulo WHERE codigo_producto = %s", (item['id'],))
            precio_real = cursor.fetchone()[0]
            
            cursor.execute("""
                INSERT INTO pedido_articulo (id_pedido, codigo_producto, cantidad_vendida, precio_facturado)
                VALUES (%s, %s, %s, %s);
            """, (id_pedido, item['id'], item['cantidad'], precio_real))
            
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
        
        conexion.commit() 
        return True, id_pedido
        
    except Exception as e:
        conexion.rollback() 
        return False, str(e)
    finally:
        if cursor: cursor.close()
        if conexion: conexion.close()
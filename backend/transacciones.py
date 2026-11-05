from backend.conexion import ejecutar_procedimiento, ejecutar_consulta
from fpdf import FPDF #Hay que descargar esta libreria desde la terminal de visual si algo, solo hacer un "pip install fpdf2"
import os

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
    #Yap, el solamente hace el pedido que se tenga que registrar, ya el como lo registra hace parte del que desarrolle la parte grafica

def transferir_inventario(codigo_producto, id_bodega_origen, id_bodega_destino, cantidad):
    params = (codigo_producto, id_bodega_origen, id_bodega_destino, cantidad)
    exito, res = ejecutar_procedimiento("sp_actualizar_inventario_bodega", params)
    
    if exito:
        return True, "Transferencia de inventario realizada correctamente."
    else:
        return False, res

    #La funcion se llama transferir_inventario pero realmente solo actualiza el inventario de una unica bodega

    #Decidí hacer esta funcion de abajo que hace un comprobante de pago

def generar_comprobante_pdf(id_pedido, nombre_cliente, producto, cantidad, total, metodo_pago, ruta_salida="comprobante.pdf"):
    """
    Genera un archivo PDF profesional con el comprobante de compra.
    """
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        
        # Encabezado
        pdf.cell(0, 10, "COMPROBANTE DE COMPRA", ln=True, align="C")
        pdf.ln(5)
        
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 8, f"ID Pedido: #{id_pedido}", ln=True)
        pdf.cell(0, 8, f"Cliente: {nombre_cliente}", ln=True)
        pdf.cell(0, 8, f"Metodo de Pago: {metodo_pago}", ln=True)
        pdf.ln(5)
        
        # Linea divisoria
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
        
        # Detalle del producto
        pdf.set_font("Arial", "B", 12)
        pdf.cell(100, 8, "Producto", border=1)
        pdf.cell(40, 8, "Cantidad", border=1, align="C")
        pdf.cell(50, 8, "Total", border=1, align="C")
        pdf.ln()
        
        pdf.set_font("Arial", "", 12)
        pdf.cell(100, 8, str(producto), border=1)
        pdf.cell(40, 8, str(cantidad), border=1, align="C")
        pdf.cell(50, 8, f"${total:,.2f}", border=1, align="C")
        pdf.ln(15)
        
        # Pie de pagina
        pdf.set_font("Arial", "I", 10)
        pdf.cell(0, 10, "Gracias por su compra en nuestra plataforma.", ln=True, align="C")
        
        # Guardar archivo
        pdf.output(ruta_salida)
        return True, f"Comprobante guardado exitosamente en '{ruta_salida}'."
    
    except Exception as e:
        return False, f"Error al generar el PDF: {e}"

if __name__ == "__main__":
    print("Probando listado de productos:")
    productos = listar_productos()
    print(productos)
    
    print("\nProbando registro de pedido:")
    exito_ped, res_ped = registrar_pedido(
        cc_usuario=11223344, 
        codigo_producto=1, 
        cantidad=1, 
        metodo_pago='PSE'
    )
    if exito_ped:
        print(f"Pedido registrado exitosamente. ID Pedido: {res_ped}")
    else:
        print(f"Error al registrar pedido: {res_ped}")

    #Esto tambien se puede quitar solo es una prueba para ver si funciona sin interfaz grafica.
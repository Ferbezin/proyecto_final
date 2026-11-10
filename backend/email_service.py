import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os

GMAIL_USER = "ca.va.barbosa@unillanos.edu.co"  #correo emisor
GMAIL_PASS = "uriq uqsj qauf sani"        

def enviar_comprobante_email(destinatario_email, nombre_cliente, ruta_pdf):
    """
    Envía el comprobante PDF generado al correo del cliente.
    """
    if not destinatario_email or not os.path.exists(ruta_pdf):
        print(f"Error: Destinatario no válido o archivo {ruta_pdf} no encontrado.")
        return False, "Archivo de comprobante o correo de destino no encontrado."

    try:
        # Estructura del correo
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = destinatario_email
        msg['Subject'] = "E-Market Express - Comprobante de Compra"

        cuerpo = f"""Hola {nombre_cliente},

¡Muchas gracias por tu compra en E-Market Express!

Adjunto a este correo encontrarás el comprobante PDF correspondiente a tu orden.

Saludos cordiales,
El equipo de E-Market Express.
"""
        msg.attach(MIMEText(cuerpo, 'plain'))

        # Adjuntar PDF
        with open(ruta_pdf, "rb") as archivo:
            adjunto = MIMEApplication(archivo.read(), _subtype="pdf")
            adjunto.add_header('Content-Disposition', 'attachment', filename=os.path.basename(ruta_pdf))
            msg.attach(adjunto)

        # Conexión al servidor SMTP de Gmail
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASS)
        server.send_message(msg)
        server.quit()

        print(f"Correo enviado exitosamente a {destinatario_email}")
        return True, "Correo enviado exitosamente."

    except Exception as e:
        print(f"Error al enviar el correo: {e}")
        return False, str(e)
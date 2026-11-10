import hashlib
from backend.conexion import ejecutar_consulta

def _hash_clave(clave):
    return hashlib.sha256(clave.encode('utf-8')).hexdigest()
#Convierte la contraseñaen un hash 

def autenticar_usuario(correo, clave):
    correo_clean = correo.strip()
    clave_input = clave.strip()
    clave_hashed = _hash_clave(clave_input)
    
    query = """
        SELECT cc, nombre, correo, telefono, clave 
        FROM usuario 
        WHERE correo = %s;
    """
    
    resultado = ejecutar_consulta(query, params=(correo_clean,), fetch=True)
    if not resultado:
        return None
    
    usuario = resultado[0]
    
    if usuario['clave'] == clave_hashed or usuario['clave'] == clave_input:
        del usuario['clave']
        
        if usuario['cc'] in [11223344, 1081]:
            usuario['rol'] = 'Administrador'
        else:
            usuario['rol'] = 'Cliente'
            
        return usuario
    
    return None

def registrar_nuevo_usuario(cc, nombre, correo, telefono, clave):
    clave_hashed = _hash_clave(clave.strip())
    query = """
        INSERT INTO usuario (cc, nombre, correo, telefono, clave)
        VALUES (%s, %s, %s, %s, %s);
    """
    params = (cc, nombre, correo.strip(), telefono.strip(), clave_hashed)
    
    exito, res = ejecutar_consulta(query, params=params, commit=True)
    
    if exito:
        return True, f"Usuario {nombre} registrado con exito."
    else:
        if "duplicate key value" in res.lower() or "unique constraint" in res.lower():
            return False, "Error: Ya existe un usuario registrado con esa cedula o correo."
        return False, f"Error al registrar el usuario: {res}"

if __name__ == "__main__":
    print("Probando validacion de Login con Hash...")
    
    user = autenticar_usuario("juan.perez@email.com", "pass123")
    if user:
        print(f"Login Exitoso: Bienvenido {user['nombre']} | Rol: {user['rol']}")
    else:
        print("Fallo de autenticacion en Prueba 1")
        
    user_fail = autenticar_usuario("juan.perez@email.com", "clave_erronea")
    if not user_fail:
        print("Prueba de contraseña incorrecta superada.")
    else:
        print("Error: Valido una contraseña incorrecta.")
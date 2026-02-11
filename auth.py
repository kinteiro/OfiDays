import streamlit as st

def cargar_usuarios():
    """Carga los usuarios desde st.secrets"""
    try:
        usuarios = st.secrets.get('users', {})
        return [
            {'usuario': usuario, 'nombre_completo': nombre_completo}
            for usuario, nombre_completo in usuarios.items()
        ]
    except Exception as e:
        print(f"Error al cargar usuarios: {e}")
        return []

def verificar_credenciales(usuario, password):
    """Verifica si las credenciales son correctas"""
    password_correcta = st.secrets['PASSWORD']

    if password != password_correcta:
        return False, None

    usuarios = cargar_usuarios()
    usuario_encontrado = next((u for u in usuarios if u['usuario'].lower() == usuario.lower()), None)

    if usuario_encontrado:
        return True, usuario_encontrado

    return False, None

def obtener_todos_usuarios():
    """Obtiene lista de todos los usuarios activos"""
    return cargar_usuarios()

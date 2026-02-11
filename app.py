import streamlit as st
from datetime import timedelta
import auth
import data_manager as dm

# Configuración de la página
st.set_page_config(
    page_title="Votación Oficina",
    page_icon="🏢",
    layout="wide"
)

# Inicializar session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'usuario' not in st.session_state:
    st.session_state.usuario = None

def login_page():
    """Página de inicio de sesión"""
    st.title("🏢 Sistema de Votación de Oficina")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.subheader("Iniciar Sesión")

        usuario = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")

        if st.button("Entrar", use_container_width=True):
            if usuario and password:
                valido, datos_usuario = auth.verificar_credenciales(usuario, password)

                if valido:
                    st.session_state.logged_in = True
                    st.session_state.usuario = datos_usuario
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")
            else:
                st.warning("Por favor ingresa usuario y contraseña")

def mostrar_tabla_semana(lunes, votos_semana, tipo_semana, es_editable=False):
    """Muestra la tabla de una semana con los votos"""

    st.markdown(f"### {'📅 Semana Actual' if tipo_semana == 'current' else '📋 Próxima Semana (Planificación)'}")
    st.markdown(f"**{dm.formatear_semana(lunes)}**")

    # Crear columnas para cada día
    cols = st.columns(5)

    for idx, dia in enumerate(dm.DIAS_SEMANA):
        with cols[idx]:
            fecha = dm.obtener_fecha_semana(lunes, dia)

            # Mostrar fecha y día
            st.markdown(f"**{dia}**")
            st.caption(fecha.strftime('%d/%m'))

            # Mostrar usuarios que van ese día
            usuarios_dia = votos_semana.get(dia, [])

            if usuarios_dia:
                for usr in usuarios_dia:
                    st.info(f"👤 {usr}")
            else:
                st.write("_Nadie aún_")

            st.markdown(f"**Total: {len(usuarios_dia)}**")

def pagina_votacion_usuario():
    """Página de votación para usuario individual"""
    st.title(f"Hola, {st.session_state.usuario['nombre_completo']} 👋")

    # Verificar y reiniciar si es necesario
    if dm.verificar_y_reiniciar_si_necesario():
        st.success("✅ Nueva semana iniciada - Los datos se han actualizado")

    # Obtener las dos semanas
    lunes_actual = dm.obtener_lunes_de_semana()
    lunes_siguiente = lunes_actual + timedelta(days=7)

    # Obtener votos
    votos_current = dm.obtener_votos_semana(lunes_actual, 'current')
    votos_next = dm.obtener_votos_semana(lunes_actual, 'next')

    # Tabs para las dos semanas
    tab1, tab2 = st.tabs(["📅 Semana Actual", "📋 Próxima Semana"])

    with tab1:
        st.markdown("### Semana Actual (Solo visualización)")
        st.markdown(f"**{dm.formatear_semana(lunes_actual)}**")

        cols = st.columns(5)
        for idx, dia in enumerate(dm.DIAS_SEMANA):
            with cols[idx]:
                fecha = dm.obtener_fecha_semana(lunes_actual, dia)
                st.markdown(f"**{dia}**")
                st.caption(fecha.strftime('%d/%m'))

                usuarios_dia = votos_current.get(dia, [])

                if usuarios_dia:
                    for usr in usuarios_dia:
                        if usr == st.session_state.usuario['usuario']:
                            st.success(f"✓ {usr}")
                        else:
                            st.info(f"👤 {usr}")
                else:
                    st.write("_Nadie_")

                st.markdown(f"**Total: {len(usuarios_dia)}**")

    with tab2:
        st.markdown("### Próxima Semana - Planifica tus días")
        st.markdown(f"**{dm.formatear_semana(lunes_siguiente)}**")

        st.markdown("---")
        st.subheader("Selecciona los días que quieres ir a la oficina:")

        # Obtener los días actuales del usuario
        dias_usuario_actual = [dia for dia, usuarios in votos_next.items()
                               if st.session_state.usuario['usuario'] in usuarios]

        # Multiselect para elegir días
        dias_seleccionados = st.multiselect(
            "Tus días:",
            options=dm.DIAS_SEMANA,
            default=dias_usuario_actual,
            key="dias_selector"
        )

        if st.button("💾 Guardar mi planificación", use_container_width=True):
            usuario = st.session_state.usuario['usuario']

            # Eliminar todos los votos anteriores del usuario para la próxima semana
            for dia in dm.DIAS_SEMANA:
                dm.eliminar_voto(lunes_actual, usuario, dia, 'next')

            # Agregar los nuevos votos
            for dia in dias_seleccionados:
                dm.agregar_voto(lunes_actual, usuario, dia, 'next')

            st.success("✅ Planificación guardada correctamente")
            st.rerun()

        st.markdown("---")
        st.markdown("### Vista general de la próxima semana:")

        # Recargar votos después de guardar
        votos_next = dm.obtener_votos_semana(lunes_actual, 'next')

        cols = st.columns(5)
        for idx, dia in enumerate(dm.DIAS_SEMANA):
            with cols[idx]:
                fecha = dm.obtener_fecha_semana(lunes_siguiente, dia)
                st.markdown(f"**{dia}**")
                st.caption(fecha.strftime('%d/%m'))

                usuarios_dia = votos_next.get(dia, [])

                if usuarios_dia:
                    for usr in usuarios_dia:
                        if usr == st.session_state.usuario['usuario']:
                            st.success(f"✓ {usr}")
                        else:
                            st.info(f"👤 {usr}")
                else:
                    st.write("_Nadie_")

                st.markdown(f"**Total: {len(usuarios_dia)}**")

def main():
    """Función principal"""

    if not st.session_state.logged_in:
        login_page()
    else:
        # Botón de cerrar sesión en la sidebar
        with st.sidebar:
            st.markdown(f"### Usuario: {st.session_state.usuario['nombre_completo']}")
            if st.button("🚪 Cerrar Sesión"):
                st.session_state.logged_in = False
                st.session_state.usuario = None
                st.rerun()

            st.markdown("---")
            # st.markdown("### 📊 Usuarios Activos")

            # todos_usuarios = auth.obtener_todos_usuarios()
            # for usr in todos_usuarios:
            #     st.write(f"• {usr['nombre_completo']}")

        # Página principal
        pagina_votacion_usuario()

if __name__ == "__main__":
    main()

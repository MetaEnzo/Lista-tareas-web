import streamlit as st
from datetime import datetime, date
import calendar
from supabase import create_client, Client

# Configuración de página
st.set_page_config(
    page_title="Lista de Tareas - Multi Usuario",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuración Supabase
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")

# Inicializar cliente Supabase
@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase: Client = init_supabase()

# Categorías disponibles
CATEGORIAS = {
    "🏢 Trabajo": {"color": "#3498db", "emoji": "🏢"},
    "🏠 Personal": {"color": "#2ecc71", "emoji": "🏠"},
    "💪 Gym/Salud": {"color": "#f39c12", "emoji": "💪"},
    "📚 Estudio": {"color": "#9b59b6", "emoji": "📚"},
    "🛒 Compras": {"color": "#e91e63", "emoji": "🛒"},
    "⚡ Otro": {"color": "#95a5a6", "emoji": "⚡"}
}

# CSS personalizado
st.markdown("""
<style>
    .login-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .user-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 10px 20px;
        border-radius: 30px;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 10px;
    }
    
    .categoria-badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        display: inline-block;
        margin: 2px;
    }
</style>
""", unsafe_allow_html=True)

# Funciones de autenticación
def registrar_usuario(email, password, nombre):
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "nombre": nombre
                }
            }
        })
        
        if response.user:
            # Crear perfil
            supabase.table('profiles').insert({
                "id": response.user.id,
                "email": email,
                "nombre": nombre
            }).execute()
            return True, "✅ Registro exitoso! Ahora puedes iniciar sesión"
        return False, "Error en el registro"
    except Exception as e:
        error_msg = str(e)
        if "already registered" in error_msg:
            return False, "Este email ya está registrado"
        return False, f"Error: {error_msg}"

def iniciar_sesion(email, password):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if response.user:
            st.session_state['logged_in'] = True
            st.session_state['user_id'] = response.user.id
            st.session_state['user_email'] = email
            
            # Obtener nombre del perfil
            profile = supabase.table('profiles').select("nombre").eq('id', response.user.id).execute()
            if profile.data:
                st.session_state['user_nombre'] = profile.data[0]['nombre']
            else:
                st.session_state['user_nombre'] = email.split('@')[0]
            
            return True
        return False
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return False

def cerrar_sesion():
    supabase.auth.sign_out()
    for key in ['logged_in', 'user_id', 'user_email', 'user_nombre']:
        if key in st.session_state:
            del st.session_state[key]

# CRUD de tareas
def obtener_tareas():
    try:
        response = supabase.table('tareas')\
            .select("*")\
            .eq('user_id', st.session_state['user_id'])\
            .order('fecha', desc=False)\
            .execute()
        return response.data
    except:
        return []

def agregar_tarea(texto, categoria, fecha, urgente):
    try:
        response = supabase.table('tareas').insert({
            'user_id': st.session_state['user_id'],
            'texto': texto,
            'categoria': categoria,
            'fecha': fecha.isoformat() if fecha else None,
            'urgente': urgente,
            'completada': False
        }).execute()
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False

def actualizar_tarea(tarea_id, updates):
    try:
        response = supabase.table('tareas')\
            .update(updates)\
            .eq('id', tarea_id)\
            .eq('user_id', st.session_state['user_id'])\
            .execute()
        return True
    except:
        return False

def eliminar_tarea(tarea_id):
    try:
        response = supabase.table('tareas')\
            .delete()\
            .eq('id', tarea_id)\
            .eq('user_id', st.session_state['user_id'])\
            .execute()
        return True
    except:
        return False

# PÁGINA DE LOGIN/REGISTRO
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    # Header con gradiente
    st.markdown('<div class="login-header"><h1>🔐 Sistema de Tareas</h1><p>Con base de datos PostgreSQL</p></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab1, tab2 = st.tabs(["🔑 Iniciar Sesión", "📝 Crear Cuenta"])
        
        with tab1:
            with st.form("login_form"):
                st.subheader("Bienvenido de vuelta")
                email = st.text_input("📧 Email", placeholder="tu@email.com")
                password = st.text_input("🔒 Contraseña", type="password")
                
                submit = st.form_submit_button("Iniciar Sesión", type="primary", use_container_width=True)
                
                if submit:
                    if email and password:
                        if iniciar_sesion(email, password):
                            st.success("✅ ¡Bienvenido!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("❌ Email o contraseña incorrectos")
                    else:
                        st.warning("Por favor completa todos los campos")
        
        with tab2:
            with st.form("register_form"):
                st.subheader("Crea tu cuenta gratis")
                nombre = st.text_input("👤 Tu nombre", placeholder="Juan Pérez")
                email = st.text_input("📧 Email", placeholder="tu@email.com")
                password = st.text_input("🔒 Contraseña", type="password", help="Mínimo 6 caracteres")
                password2 = st.text_input("🔒 Confirmar contraseña", type="password")
                
                submit = st.form_submit_button("Crear Cuenta", type="primary", use_container_width=True)
                
                if submit:
                    if not nombre or not email or not password:
                        st.warning("Por favor completa todos los campos")
                    elif password != password2:
                        st.error("Las contraseñas no coinciden")
                    elif len(password) < 6:
                        st.error("La contraseña debe tener mínimo 6 caracteres")
                    else:
                        success, message = registrar_usuario(email, password, nombre)
                        if success:
                            st.success(message)
                            st.info("👆 Ve a la pestaña 'Iniciar Sesión'")
                        else:
                            st.error(message)

# APLICACIÓN PRINCIPAL (Usuario logueado)
else:
    # Sidebar con info del usuario
    with st.sidebar:
        st.markdown(f'<div class="user-badge">👤 {st.session_state["user_nombre"]}</div>', unsafe_allow_html=True)
        st.caption(f"📧 {st.session_state['user_email']}")
        
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            cerrar_sesion()
            st.rerun()
        
        st.markdown("---")
        
        # Estadísticas rápidas
        tareas = obtener_tareas()
        total = len(tareas)
        completadas = sum(1 for t in tareas if t['completada'])
        pendientes = total - completadas
        
        st.metric("📊 Total", total)
        col1, col2 = st.columns(2)
        col1.metric("✅ Listas", completadas)
        col2.metric("⏳ Pendientes", pendientes)
    
    # Contenido principal
    st.title(f"📝 Hola, {st.session_state['user_nombre']}!")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📝 Tareas", "📅 Calendario", "📊 Estadísticas"])
    
    with tab1:
        # Agregar tarea
        with st.form("nueva_tarea", clear_on_submit=True):
            col1, col2, col3 = st.columns([3, 2, 2])
            
            with col1:
                texto = st.text_input("Nueva tarea", placeholder="¿Qué necesitas hacer?")
            with col2:
                categoria = st.selectbox("Categoría", list(CATEGORIAS.keys()))
            with col3:
                fecha = st.date_input("Fecha", min_value=date.today())
            
            col4, col5 = st.columns([1, 4])
            with col4:
                urgente = st.checkbox("🔴 Urgente")
            with col5:
                submit = st.form_submit_button("➕ Agregar Tarea", type="primary")
            
            if submit and texto:
                if agregar_tarea(texto, categoria, fecha, urgente):
                    st.success("✅ Tarea agregada!")
                    st.rerun()
        
        # Filtros
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            filtro_estado = st.radio("Filtrar:", ["Todas", "Pendientes", "Completadas"], horizontal=True)
        with col2:
            filtro_categoria = st.multiselect("Categorías:", list(CATEGORIAS.keys()), default=list(CATEGORIAS.keys()))
        
        # Mostrar tareas
        tareas = obtener_tareas()
        
        # Aplicar filtros
        if filtro_estado == "Pendientes":
            tareas = [t for t in tareas if not t['completada']]
        elif filtro_estado == "Completadas":
            tareas = [t for t in tareas if t['completada']]
        
        tareas = [t for t in tareas if t.get('categoria', '⚡ Otro') in filtro_categoria]
        
        if tareas:
            st.markdown("### 📌 Tus tareas")
            for tarea in tareas:
                with st.container():
                    col1, col2, col3, col4 = st.columns([0.5, 4, 1.5, 0.5])
                    
                    with col1:
                        completada = st.checkbox("", value=tarea['completada'], key=f"check_{tarea['id']}")
                        if completada != tarea['completada']:
                            actualizar_tarea(tarea['id'], {'completada': completada})
                            st.rerun()
                    
                    with col2:
                        cat = tarea.get('categoria', '⚡ Otro')
                        color = CATEGORIAS.get(cat, CATEGORIAS['⚡ Otro'])['color']
                        
                        html = f'<span class="categoria-badge" style="background-color: {color}; color: white;">{cat}</span> '
                        
                        if tarea['completada']:
                            html += f"~~{tarea['texto']}~~"
                        elif tarea.get('urgente'):
                            html += f"🔴 **{tarea['texto']}**"
                        else:
                            html += tarea['texto']
                        
                        st.markdown(html, unsafe_allow_html=True)
                    
                    with col3:
                        if tarea.get('fecha'):
                            fecha_str = datetime.fromisoformat(tarea['fecha']).strftime("%d/%m")
                            st.caption(f"📅 {fecha_str}")
                    
                    with col4:
                        if st.button("🗑️", key=f"del_{tarea['id']}"):
                            eliminar_tarea(tarea['id'])
                            st.rerun()
        else:
            st.info("No hay tareas. ¡Agrega una para empezar!")
    
    with tab2:
        st.header("📅 Calendario")
        
        col1, col2 = st.columns(2)
        with col1:
            mes = st.selectbox("Mes", range(1, 13), format_func=lambda x: calendar.month_name[x], index=datetime.now().month - 1)
        with col2:
            año = st.selectbox("Año", range(2024, 2030))
        
        # Calendario
        cal = calendar.monthcalendar(año, mes)
        dias = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
        
        cols = st.columns(7)
        for i, dia in enumerate(dias):
            cols[i].markdown(f"**{dia}**")
        
        tareas = obtener_tareas()
        
        for semana in cal:
            cols = st.columns(7)
            for i, dia in enumerate(semana):
                if dia == 0:
                    cols[i].write("")
                else:
                    fecha_str = f"{año}-{mes:02d}-{dia:02d}"
                    tareas_dia = [t for t in tareas if t.get('fecha') and t['fecha'].startswith(fecha_str)]
                    
                    if tareas_dia:
                        emojis = "".join([CATEGORIAS[t.get('categoria', '⚡ Otro')]["emoji"] for t in tareas_dia[:3]])
                        cols[i].markdown(f"**{dia}**\n{emojis}")
                    else:
                        cols[i].markdown(f"{dia}")
    
    with tab3:
        st.header("📊 Tus Estadísticas")
        
        tareas = obtener_tareas()
        
        if tareas:
            col1, col2, col3 = st.columns(3)
            
            total = len(tareas)
            comp = sum(1 for t in tareas if t['completada'])
            pend = total - comp
            
            col1.metric("📊 Total", total)
            col2.metric("✅ Completadas", comp)
            col3.metric("⏳ Pendientes", pend)
            
            if total > 0:
                st.progress(comp / total)
                st.caption(f"Has completado el {(comp/total)*100:.0f}% de tus tareas")
            
            # Por categoría
            st.markdown("---")
            for cat in CATEGORIAS.keys():
                tareas_cat = [t for t in tareas if t.get('categoria') == cat]
                if tareas_cat:
                    st.write(f"**{cat}**: {len(tareas_cat)} tareas")
        else:
            st.info("Sin datos aún. ¡Agrega tareas para ver estadísticas!")

# Footer
st.markdown("---")
st.caption("💾 PostgreSQL + 🔐 Autenticación | Powered by Supabase")




import streamlit as st
from datetime import datetime, date, timedelta
import calendar
from supabase import create_client, Client
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

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

def verificar_conexion_supabase():
    """Verifica si la conexión a Supabase está funcionando"""
    try:
        if not SUPABASE_URL or not SUPABASE_KEY:
            return False, "❌ Faltan credenciales de Supabase"
        
        # Intentar una consulta simple
        response = supabase.table('profiles').select("count").limit(1).execute()
        return True, "✅ Conexión a Supabase exitosa"
    except Exception as e:
        return False, f"❌ Error de conexión: {str(e)}"

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

# Inicializar tema en session state
if 'tema' not in st.session_state:
    st.session_state.tema = "claro"

# CSS personalizado según tema elegido
if st.session_state.tema == "oscuro":
    st.markdown("""
    <style>
        /* TEMA OSCURO - Estilo Notion */
        :root {
            --bg-primary: #1a1a1a;
            --bg-secondary: #0f0f0f;
            --bg-tertiary: #2d2d2d;
            --text-primary: #ffffff;
            --text-secondary: #b3b3b3;
            --text-tertiary: #808080;
            --border-light: #404040;
            --border-medium: #555555;
            --accent-blue: #4a9eff;
            --accent-green: #4caf50;
            --accent-orange: #ff9800;
            --accent-red: #f44336;
            --accent-purple: #9c27b0;
            --accent-gray: #757575;
        }
        
        .stApp {
            background-color: var(--bg-secondary) !important;
            color: var(--text-primary) !important;
            font-family: ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, "Apple Color Emoji", Arial, sans-serif !important;
        }
        
        .main .block-container {
            background-color: var(--bg-primary) !important;
            border-radius: 12px !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.3) !important;
            padding: 2rem !important;
            margin-top: 1rem !important;
            border: 1px solid var(--border-light) !important;
        }
        
        .stSidebar {
            background-color: var(--bg-primary) !important;
            border-right: 1px solid var(--border-light) !important;
        }
        
        .stButton button {
            background-color: var(--bg-primary) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--border-medium) !important;
            border-radius: 8px !important;
            font-weight: 500 !important;
            transition: all 0.2s ease !important;
        }
        
        .stButton button:hover {
            background-color: var(--bg-tertiary) !important;
            border-color: var(--text-secondary) !important;
        }
        
        .stTextInput input, .stSelectbox select, .stDateInput input {
            background-color: var(--bg-primary) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--border-medium) !important;
            border-radius: 8px !important;
            font-size: 14px !important;
        }
        
        .stTextInput input:focus, .stSelectbox select:focus, .stDateInput input:focus {
            border-color: var(--accent-blue) !important;
            box-shadow: 0 0 0 2px rgba(74, 158, 255, 0.2) !important;
        }
        
        .login-header {
            background: linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-purple) 100%);
            color: white;
            padding: 2.5rem;
            border-radius: 16px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 4px 12px rgba(74, 158, 255, 0.2);
        }
        
        .user-badge {
            background: linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-purple) 100%);
            color: white;
            padding: 12px 24px;
            border-radius: 24px;
            font-weight: 600;
            display: inline-block;
            margin-bottom: 1rem;
            box-shadow: 0 2px 8px rgba(74, 158, 255, 0.3);
        }
        
        .categoria-badge {
            padding: 6px 14px;
            border-radius: 16px;
            font-size: 12px;
            font-weight: 600;
            color: white;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            display: inline-block;
            margin: 2px;
            opacity: 0.9;
        }
        
        .stCheckbox {
            margin: 0.5rem 0;
        }
        
        .stCheckbox label {
            font-weight: 500;
            color: var(--text-primary);
        }
        
        .stSelectbox > div > div {
            background-color: var(--bg-primary) !important;
            border: 1px solid var(--border-medium) !important;
            border-radius: 8px !important;
        }
        
        .stTextInput > div > div > input {
            background-color: var(--bg-primary) !important;
            border: 1px solid var(--border-medium) !important;
            border-radius: 8px !important;
        }
        
        .stDateInput > div > div > input {
            background-color: var(--bg-primary) !important;
            border: 1px solid var(--border-medium) !important;
            border-radius: 8px !important;
        }
        
        div[data-testid="stSidebar"] {
            background-color: var(--bg-primary) !important;
        }
        
        /* Mejoras adicionales para elementos específicos */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: 500;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: var(--accent-blue) !important;
            color: white !important;
        }
        
        .stTabs [aria-selected="false"] {
            background-color: var(--bg-tertiary) !important;
            color: var(--text-secondary) !important;
        }
        
        .stMetric {
            background-color: var(--bg-tertiary) !important;
            border-radius: 12px !important;
            padding: 1rem !important;
            border: 1px solid var(--border-light) !important;
        }
        
        .stAlert {
            border-radius: 12px !important;
            border: none !important;
        }
        
        .stSuccess {
            background-color: rgba(15, 123, 15, 0.1) !important;
            border-left: 4px solid var(--accent-green) !important;
        }
        
        .stError {
            background-color: rgba(225, 98, 89, 0.1) !important;
            border-left: 4px solid var(--accent-red) !important;
        }
        
        .stInfo {
            background-color: rgba(35, 131, 226, 0.1) !important;
            border-left: 4px solid var(--accent-blue) !important;
        }
    </style>
    """, unsafe_allow_html=True)
else:
    # TEMA CLARO - Estilo Notion
    st.markdown("""
    <style>
        /* Variables de color estilo Notion */
        :root {
            --bg-primary: #ffffff;
            --bg-secondary: #f7f6f3;
            --bg-tertiary: #f1f1ef;
            --text-primary: #37352f;
            --text-secondary: #787774;
            --text-tertiary: #9b9a97;
            --border-light: #e9e9e7;
            --border-medium: #d9d9d7;
            --accent-blue: #2383e2;
            --accent-green: #0f7b0f;
            --accent-orange: #d9730d;
            --accent-red: #e16259;
            --accent-purple: #9065b0;
            --accent-gray: #6f6e69;
        }
        
        .stApp {
            background-color: var(--bg-secondary) !important;
            color: var(--text-primary) !important;
            font-family: ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, "Apple Color Emoji", Arial, sans-serif !important;
        }
        
        .main .block-container {
            background-color: var(--bg-primary) !important;
            border-radius: 12px !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
            padding: 2rem !important;
            margin-top: 1rem !important;
            border: 1px solid var(--border-light) !important;
        }
        
        .stSidebar {
            background-color: var(--bg-primary) !important;
            border-right: 1px solid var(--border-light) !important;
        }
        
        .stButton button {
            background-color: var(--bg-primary) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--border-medium) !important;
            border-radius: 8px !important;
            font-weight: 500 !important;
            transition: all 0.2s ease !important;
        }
        
        .stButton button:hover {
            background-color: var(--bg-tertiary) !important;
            border-color: var(--text-secondary) !important;
        }
        
        .stTextInput input, .stSelectbox select, .stDateInput input {
            background-color: var(--bg-primary) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--border-medium) !important;
            border-radius: 8px !important;
            font-size: 14px !important;
        }
        
        .stTextInput input:focus, .stSelectbox select:focus, .stDateInput input:focus {
            border-color: var(--accent-blue) !important;
            box-shadow: 0 0 0 2px rgba(35, 131, 226, 0.1) !important;
        }
        
        .login-header {
            background: linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-purple) 100%);
            color: white;
            padding: 2.5rem;
            border-radius: 16px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 4px 12px rgba(35, 131, 226, 0.15);
        }
        
        .user-badge {
            background: linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-purple) 100%);
            color: white;
            padding: 12px 24px;
            border-radius: 24px;
            font-weight: 600;
            display: inline-block;
            margin-bottom: 1rem;
            box-shadow: 0 2px 8px rgba(35, 131, 226, 0.2);
        }
        
        .categoria-badge {
            padding: 6px 14px;
            border-radius: 16px;
            font-size: 12px;
            font-weight: 600;
            color: white;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            display: inline-block;
            margin: 2px;
        }
        
        .stCheckbox {
            margin: 0.5rem 0;
        }
        
        .stCheckbox label {
            font-weight: 500;
            color: var(--text-primary);
        }
        
        .stSelectbox > div > div {
            background-color: var(--bg-primary) !important;
            border: 1px solid var(--border-medium) !important;
            border-radius: 8px !important;
        }
        
        .stTextInput > div > div > input {
            background-color: var(--bg-primary) !important;
            border: 1px solid var(--border-medium) !important;
            border-radius: 8px !important;
        }
        
        .stDateInput > div > div > input {
            background-color: var(--bg-primary) !important;
            border: 1px solid var(--border-medium) !important;
            border-radius: 8px !important;
        }
        
        /* Mejoras adicionales para elementos específicos */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: 500;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: var(--accent-blue) !important;
            color: white !important;
        }
        
        .stTabs [aria-selected="false"] {
            background-color: var(--bg-tertiary) !important;
            color: var(--text-secondary) !important;
        }
        
        .stMetric {
            background-color: var(--bg-tertiary) !important;
            border-radius: 12px !important;
            padding: 1rem !important;
            border: 1px solid var(--border-light) !important;
        }
        
        .stAlert {
            border-radius: 12px !important;
            border: none !important;
        }
        
        .stSuccess {
            background-color: rgba(76, 175, 80, 0.1) !important;
            border-left: 4px solid var(--accent-green) !important;
        }
        
        .stError {
            background-color: rgba(244, 67, 54, 0.1) !important;
            border-left: 4px solid var(--accent-red) !important;
        }
        
        .stInfo {
            background-color: rgba(35, 131, 226, 0.1) !important;
            border-left: 4px solid var(--accent-blue) !important;
        }
    </style>
    """, unsafe_allow_html=True)

# Funciones de autenticación
def registrar_usuario(email, password, nombre):
    try:
        # Verificar conexión a Supabase
        if not SUPABASE_URL or not SUPABASE_KEY:
            return False, "❌ Error de configuración: Faltan credenciales de Supabase"
        
        # Intentar registro
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
            try:
                # Crear perfil (opcional, puede fallar si la tabla no existe)
                supabase.table('profiles').insert({
                    "id": response.user.id,
                    "email": email,
                    "nombre": nombre
                }).execute()
            except Exception as profile_error:
                # Si falla la creación del perfil, no es crítico
                print(f"Warning: No se pudo crear perfil: {profile_error}")
            
            # Verificar si el usuario necesita confirmar email
            if hasattr(response.user, 'email_confirmed_at') and not response.user.email_confirmed_at:
                return True, "✅ Registro exitoso! Revisa tu email para confirmar la cuenta antes de iniciar sesión."
            else:
                return True, "✅ Registro exitoso! Ahora puedes iniciar sesión"
        else:
            return False, "❌ Error: No se pudo crear el usuario"
            
    except Exception as e:
        error_msg = str(e).lower()
        
        # Manejar errores específicos
        if "already registered" in error_msg or "user already registered" in error_msg:
            return False, "❌ Este email ya está registrado. Ve a 'Iniciar Sesión' o usa otro email."
        elif "duplicate key" in error_msg or "already exists" in error_msg:
            return False, "❌ Este email ya está registrado. Ve a 'Iniciar Sesión' o usa otro email."
        elif "invalid email" in error_msg:
            return False, "❌ Email inválido"
        elif "password" in error_msg and "weak" in error_msg:
            return False, "❌ La contraseña es muy débil"
        elif "network" in error_msg or "connection" in error_msg:
            return False, "❌ Error de conexión. Verifica tu internet"
        elif "supabase" in error_msg:
            return False, "❌ Error de configuración de Supabase"
        else:
            return False, f"❌ Error: {str(e)}"

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
        error_msg = str(e).lower()
        
        # Manejar errores específicos
        if "email not confirmed" in error_msg:
            st.error("❌ Email no confirmado. Revisa tu bandeja de entrada y haz clic en el enlace de confirmación.")
            st.info("💡 **Solución**: Ve a Supabase → Authentication → Settings → Desactiva 'Enable email confirmations'")
        elif "invalid login credentials" in error_msg:
            st.error("❌ Email o contraseña incorrectos")
        elif "too many requests" in error_msg:
            st.error("❌ Demasiados intentos. Espera unos minutos.")
        else:
            st.error(f"❌ Error: {str(e)}")
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

def buscar_tareas(termino_busqueda, categoria_filtro=None, estado_filtro=None, fecha_filtro=None):
    """Busca tareas basado en criterios múltiples"""
    tareas = obtener_tareas()
    
    if not tareas:
        return []
    
    resultados = []
    termino_lower = termino_busqueda.lower() if termino_busqueda else ""
    
    for tarea in tareas:
        # Búsqueda por texto (título y descripción)
        texto_match = True
        if termino_lower:
            texto_tarea = f"{tarea.get('texto', '')} {tarea.get('descripcion', '')}".lower()
            texto_match = termino_lower in texto_tarea
        
        # Filtro por categoría
        categoria_match = True
        if categoria_filtro and categoria_filtro != "Todas":
            categoria_match = tarea.get('categoria') == categoria_filtro
        
        # Filtro por estado
        estado_match = True
        if estado_filtro is not None:
            estado_match = tarea.get('completada', False) == estado_filtro
        
        # Filtro por fecha
        fecha_match = True
        if fecha_filtro:
            if fecha_filtro == "Hoy":
                hoy = date.today().isoformat()
                fecha_match = tarea.get('fecha') == hoy
            elif fecha_filtro == "Esta semana":
                hoy = date.today()
                inicio_semana = hoy - timedelta(days=hoy.weekday())
                fin_semana = inicio_semana + timedelta(days=6)
                fecha_tarea = datetime.fromisoformat(tarea.get('fecha', '1900-01-01')).date()
                fecha_match = inicio_semana <= fecha_tarea <= fin_semana
            elif fecha_filtro == "Vencidas":
                hoy = date.today().isoformat()
                fecha_match = tarea.get('fecha') and tarea.get('fecha') < hoy and not tarea.get('completada', False)
        
        if texto_match and categoria_match and estado_match and fecha_match:
            resultados.append(tarea)
    
    return resultados

def ordenar_tareas(tareas, criterio_ordenamiento):
    """Ordena las tareas según el criterio especificado"""
    if not tareas:
        return tareas
    
    if criterio_ordenamiento == "Fecha (Más reciente)":
        return sorted(tareas, key=lambda x: x.get('fecha', ''), reverse=True)
    elif criterio_ordenamiento == "Fecha (Más antigua)":
        return sorted(tareas, key=lambda x: x.get('fecha', ''), reverse=False)
    elif criterio_ordenamiento == "Alfabético (A-Z)":
        return sorted(tareas, key=lambda x: x.get('texto', '').lower())
    elif criterio_ordenamiento == "Alfabético (Z-A)":
        return sorted(tareas, key=lambda x: x.get('texto', '').lower(), reverse=True)
    elif criterio_ordenamiento == "Estado (Completadas primero)":
        return sorted(tareas, key=lambda x: x.get('completada', False), reverse=True)
    elif criterio_ordenamiento == "Estado (Pendientes primero)":
        return sorted(tareas, key=lambda x: x.get('completada', False), reverse=False)
    elif criterio_ordenamiento == "Urgentes primero":
        return sorted(tareas, key=lambda x: x.get('urgente', False), reverse=True)
    else:
        return tareas

def generar_estadisticas_avanzadas(tareas):
    """Genera estadísticas avanzadas y gráficos para las tareas"""
    if not tareas:
        return None, None, None, None, None
    
    # Convertir a DataFrame para análisis
    df = pd.DataFrame(tareas)
    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    df['completada'] = df['completada'].fillna(False)
    
    # 1. Gráfico de tareas por categoría
    categoria_counts = df['categoria'].value_counts()
    fig_categorias = px.pie(
        values=categoria_counts.values,
        names=categoria_counts.index,
        title="📊 Distribución por Categorías",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_categorias.update_traces(textposition='inside', textinfo='percent+label')
    fig_categorias.update_layout(
        showlegend=True,
        height=400,
        font=dict(size=12)
    )
    
    # 2. Gráfico de progreso semanal
    hoy = date.today()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    dias_semana = [inicio_semana + timedelta(days=i) for i in range(7)]
    nombres_dias = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
    
    tareas_por_dia = []
    for dia in dias_semana:
        tareas_dia = df[df['fecha'].dt.date == dia]
        completadas = len(tareas_dia[tareas_dia['completada'] == True])
        total = len(tareas_dia)
        tareas_por_dia.append({'dia': dia, 'completadas': completadas, 'total': total})
    
    df_semana = pd.DataFrame(tareas_por_dia)
    df_semana['dia_nombre'] = nombres_dias
    df_semana['porcentaje'] = (df_semana['completadas'] / df_semana['total'].replace(0, 1) * 100).round(1)
    
    fig_semana = go.Figure()
    fig_semana.add_trace(go.Bar(
        name='Completadas',
        x=df_semana['dia_nombre'],
        y=df_semana['completadas'],
        marker_color='#4CAF50'
    ))
    fig_semana.add_trace(go.Bar(
        name='Pendientes',
        x=df_semana['dia_nombre'],
        y=df_semana['total'] - df_semana['completadas'],
        marker_color='#FF9800'
    ))
    fig_semana.update_layout(
        title="📅 Progreso Semanal",
        barmode='stack',
        height=400,
        xaxis_title="Día",
        yaxis_title="Número de Tareas"
    )
    
    # 3. Métricas de productividad
    total_tareas = len(df)
    tareas_completadas = len(df[df['completada'] == True])
    tareas_pendientes = total_tareas - tareas_completadas
    porcentaje_completado = (tareas_completadas / total_tareas * 100) if total_tareas > 0 else 0
    
    # Tareas vencidas
    hoy_str = date.today().isoformat()
    tareas_vencidas = len(df[(df['fecha'].dt.date < date.today()) & (df['completada'] == False)])
    
    # Tareas urgentes
    tareas_urgentes = len(df[df.get('urgente', False) == True])
    
    # 4. Gráfico de tendencia mensual (simplificado)
    df['mes_str'] = df['fecha'].dt.strftime('%Y-%m')  # Formato string simple
    tendencia_data = []
    
    for mes in df['mes_str'].unique():
        tareas_mes = df[df['mes_str'] == mes]
        completadas = len(tareas_mes[tareas_mes['completada'] == True])
        pendientes = len(tareas_mes[tareas_mes['completada'] == False])
        
        tendencia_data.append({
            'mes': mes,
            'completadas': completadas,
            'pendientes': pendientes
        })
    
    if tendencia_data:
        df_tendencia = pd.DataFrame(tendencia_data)
        fig_tendencia = go.Figure()
        fig_tendencia.add_trace(go.Bar(
            name='Completadas',
            x=df_tendencia['mes'],
            y=df_tendencia['completadas'],
            marker_color='#4CAF50'
        ))
        fig_tendencia.add_trace(go.Bar(
            name='Pendientes',
            x=df_tendencia['mes'],
            y=df_tendencia['pendientes'],
            marker_color='#FF9800'
        ))
        fig_tendencia.update_layout(
            title="📈 Tendencia Mensual",
            barmode='stack',
            height=400,
            xaxis_title="Mes",
            yaxis_title="Número de Tareas"
        )
    else:
        fig_tendencia = None
    
    # 5. Resumen de métricas
    metricas = {
        'total_tareas': total_tareas,
        'tareas_completadas': tareas_completadas,
        'tareas_pendientes': tareas_pendientes,
        'porcentaje_completado': porcentaje_completado,
        'tareas_vencidas': tareas_vencidas,
        'tareas_urgentes': tareas_urgentes
    }
    
    return fig_categorias, fig_semana, fig_tendencia, metricas, df_semana

# PÁGINA DE LOGIN/REGISTRO
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    # Header con gradiente
    st.markdown('<div class="login-header"><h1>🔐 Sistema de Tareas</h1><p>Con base de datos PostgreSQL</p></div>', unsafe_allow_html=True)

    # Botón de tema en la esquina
    col_tema = st.columns([4, 1])[1]
    with col_tema:
        tema_icon = "🌙" if st.session_state.tema == "claro" else "☀️"
        tema_text = "Oscuro" if st.session_state.tema == "claro" else "Claro"
        if st.button(f"{tema_icon} {tema_text}", use_container_width=True, type="secondary"):
            st.session_state.tema = "oscuro" if st.session_state.tema == "claro" else "claro"
            st.rerun()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Botón de diagnóstico
        if st.button("🔧 Verificar Conexión", type="secondary", help="Verifica si la conexión a Supabase está funcionando"):
            conexion_ok, mensaje = verificar_conexion_supabase()
            if conexion_ok:
                st.success(mensaje)
            else:
                st.error(mensaje)
        
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

        st.markdown("---")
        
        # Selector de tema
        col1, col2 = st.columns([1, 2])
        with col1:
            st.write("🎨")
        with col2:
            tema_icon = "🌙" if st.session_state.tema == "claro" else "☀️"
            tema_text = "Tema Oscuro" if st.session_state.tema == "claro" else "Tema Claro"
            if st.button(f"{tema_icon} {tema_text}", use_container_width=True, type="secondary"):
                st.session_state.tema = "oscuro" if st.session_state.tema == "claro" else "claro"
                st.rerun()
        
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
                urgente = st.checkbox("🔴 Urgente", help="Marca esta tarea como urgente")
            with col5:
                submit = st.form_submit_button("➕ Agregar Tarea", type="primary")
            
            if submit and texto:
                if agregar_tarea(texto, categoria, fecha, urgente):
                    st.success("✅ Tarea agregada!")
                    st.rerun()
        
        # Barra de búsqueda y filtros avanzados
        st.markdown("---")
        st.subheader("🔍 Buscar y Filtrar Tareas")
        
        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
        
        with col1:
            termino_busqueda = st.text_input(
                "🔍 Buscar tareas", 
                placeholder="Buscar por texto...",
                help="Busca en el título y descripción de las tareas"
            )
        
        with col2:
            categoria_filtro = st.selectbox(
                "📂 Categoría",
                ["Todas"] + list(CATEGORIAS.keys()),
                help="Filtrar por categoría"
            )
        
        with col3:
            estado_filtro = st.selectbox(
                "📊 Estado",
                ["Todas", "Pendientes", "Completadas"],
                help="Filtrar por estado"
            )
            # Convertir a boolean para la función
            if estado_filtro == "Pendientes":
                estado_filtro = False
            elif estado_filtro == "Completadas":
                estado_filtro = True
            else:
                estado_filtro = None
        
        with col4:
            fecha_filtro = st.selectbox(
                "📅 Fecha",
                ["Todas", "Hoy", "Esta semana", "Vencidas"],
                help="Filtrar por fecha"
            )
            if fecha_filtro == "Todas":
                fecha_filtro = None
        
        # Aplicar búsqueda y filtros
        if termino_busqueda or categoria_filtro != "Todas" or estado_filtro is not None or fecha_filtro:
            tareas = buscar_tareas(termino_busqueda, categoria_filtro, estado_filtro, fecha_filtro)
            if tareas:
                st.success(f"🔍 Encontradas {len(tareas)} tarea(s)")
            else:
                st.info("🔍 No se encontraron tareas con esos criterios")
        else:
            tareas = obtener_tareas()
        
        # Botón para limpiar filtros y selector de ordenamiento
        col_clear1, col_clear2, col_clear3 = st.columns([1, 1, 1])
        
        with col_clear1:
            if termino_busqueda or categoria_filtro != "Todas" or estado_filtro is not None or fecha_filtro:
                if st.button("🔄 Limpiar Filtros", type="secondary", use_container_width=True):
                    st.rerun()
        
        with col_clear2:
            criterio_ordenamiento = st.selectbox(
                "🔄 Ordenar por:",
                [
                    "Fecha (Más reciente)",
                    "Fecha (Más antigua)", 
                    "Alfabético (A-Z)",
                    "Alfabético (Z-A)",
                    "Estado (Pendientes primero)",
                    "Estado (Completadas primero)",
                    "Urgentes primero"
                ],
                help="Selecciona cómo ordenar las tareas"
            )
        
        with col_clear3:
            st.write("")  # Espacio vacío para balance
        
        # Aplicar ordenamiento
        tareas = ordenar_tareas(tareas, criterio_ordenamiento)
        
        if tareas:
            st.markdown("### 📌 Tus tareas")
            for tarea in tareas:
                with st.container():
                    col1, col2, col3, col4 = st.columns([0.5, 4, 1.5, 0.5])
                    
                    with col1:
                        completada = st.checkbox("✓", value=tarea['completada'], key=f"check_{tarea['id']}", help="Marcar como completada")
                        if completada != tarea['completada']:
                            actualizar_tarea(tarea['id'], {'completada': completada})
                            st.rerun()
                    
                    with col2:
                        cat = tarea.get('categoria', '⚡ Otro')
                        color = CATEGORIAS.get(cat, CATEGORIAS['⚡ Otro'])['color']
                        
                        # Indicador de urgencia
                        urgente_indicator = ""
                        if tarea.get('urgente'):
                            urgente_indicator = '<span style="color: #ff4444; font-weight: bold; margin-right: 8px;">🔴 URGENTE</span>'
                        
                        # Badge de categoría
                        categoria_badge = f'<span class="categoria-badge" style="background-color: {color}; color: white;">{cat}</span> '
                        
                        # Texto de la tarea
                        if tarea['completada']:
                            texto_tarea = f'<span style="text-decoration: line-through; opacity: 0.6; color: #666;">{tarea["texto"]}</span>'
                        else:
                            texto_tarea = f'<span style="font-weight: 500;">{tarea["texto"]}</span>'
                        
                        # Combinar todo
                        html = urgente_indicator + categoria_badge + texto_tarea
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
        st.header("📊 Dashboard de Productividad")
        
        tareas = obtener_tareas()
        
        if tareas:
            # Generar estadísticas avanzadas
            fig_categorias, fig_semana, fig_tendencia, metricas, df_semana = generar_estadisticas_avanzadas(tareas)
            
            # Métricas principales
            st.subheader("🎯 Resumen General")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "📊 Total Tareas", 
                    metricas['total_tareas'],
                    help="Número total de tareas creadas"
                )
            
            with col2:
                st.metric(
                    "✅ Completadas", 
                    metricas['tareas_completadas'],
                    f"{metricas['porcentaje_completado']:.1f}%",
                    help="Tareas completadas y porcentaje de éxito"
                )
            
            with col3:
                st.metric(
                    "⏳ Pendientes", 
                    metricas['tareas_pendientes'],
                    help="Tareas aún por completar"
                )
            
            with col4:
                st.metric(
                    "🔴 Urgentes", 
                    metricas['tareas_urgentes'],
                    help="Tareas marcadas como urgentes"
                )
            
            # Barra de progreso general
            if metricas['total_tareas'] > 0:
                st.progress(metricas['porcentaje_completado'] / 100)
                st.caption(f"🎯 Has completado el {metricas['porcentaje_completado']:.1f}% de tus tareas")
            
            # Alertas importantes
            if metricas['tareas_vencidas'] > 0:
                st.warning(f"⚠️ Tienes {metricas['tareas_vencidas']} tarea(s) vencida(s) que necesitan atención")
            
            if metricas['tareas_urgentes'] > 0:
                st.error(f"🚨 Tienes {metricas['tareas_urgentes']} tarea(s) urgente(s) pendientes")
            
            st.markdown("---")
            
            # Gráficos
            col_graf1, col_graf2 = st.columns(2)
            
            with col_graf1:
                st.plotly_chart(fig_categorias, use_container_width=True)
            
            with col_graf2:
                st.plotly_chart(fig_semana, use_container_width=True)
            
            # Gráfico de tendencia mensual (si hay datos)
            if fig_tendencia:
                st.subheader("📈 Tendencia Mensual")
                st.plotly_chart(fig_tendencia, use_container_width=True)
            
            # Tabla de progreso semanal
            st.subheader("📅 Progreso Semanal Detallado")
            df_semana_display = df_semana[['dia_nombre', 'completadas', 'total', 'porcentaje']].copy()
            df_semana_display.columns = ['Día', 'Completadas', 'Total', 'Progreso (%)']
            st.dataframe(df_semana_display, use_container_width=True, hide_index=True)
            
            # Insights y recomendaciones
            st.markdown("---")
            st.subheader("💡 Insights y Recomendaciones")
            
            col_insight1, col_insight2 = st.columns(2)
            
            with col_insight1:
                # Día más productivo
                dia_mas_productivo = df_semana.loc[df_semana['completadas'].idxmax(), 'dia_nombre']
                st.info(f"📈 Tu día más productivo esta semana: **{dia_mas_productivo}**")
                
                # Categoría más común
                if not tareas:
                    categoria_mas_comun = "N/A"
                else:
                    categoria_counts = pd.DataFrame(tareas)['categoria'].value_counts()
                    categoria_mas_comun = categoria_counts.index[0]
                st.info(f"🏆 Categoría más activa: **{categoria_mas_comun}**")
            
            with col_insight2:
                # Recomendación de productividad
                if metricas['porcentaje_completado'] >= 80:
                    st.success("🌟 ¡Excelente productividad! Mantén este ritmo.")
                elif metricas['porcentaje_completado'] >= 60:
                    st.warning("📈 Buena productividad. Puedes mejorar completando más tareas.")
                else:
                    st.error("🎯 Necesitas enfocarte más. Intenta completar al menos 3 tareas hoy.")
                
                # Recomendación de tareas vencidas
                if metricas['tareas_vencidas'] > 0:
                    st.error(f"⏰ Prioriza las {metricas['tareas_vencidas']} tarea(s) vencida(s)")
                else:
                    st.success("✅ ¡Al día! No tienes tareas vencidas.")
        
        else:
            st.info("📊 Sin datos aún. ¡Agrega tareas para ver estadísticas detalladas!")
            
            # Mostrar ejemplo de lo que verán
            st.markdown("---")
            st.subheader("🎯 Lo que verás cuando tengas tareas:")
            
            col_demo1, col_demo2 = st.columns(2)
            
            with col_demo1:
                st.markdown("""
                **📊 Métricas Principales:**
                - Total de tareas
                - Tareas completadas
                - Porcentaje de éxito
                - Tareas urgentes
                """)
            
            with col_demo2:
                st.markdown("""
                **📈 Gráficos Visuales:**
                - Distribución por categorías
                - Progreso semanal
                - Tendencia mensual
                - Insights personalizados
                """)

# Footer
st.markdown("---")
st.caption("💾 PostgreSQL + 🔐 Autenticación | Powered by Supabase")
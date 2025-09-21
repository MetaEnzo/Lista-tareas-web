import streamlit as st
import json
import os
from datetime import datetime, date
import calendar

# Configuración de la página
st.set_page_config(
    page_title="Lista de Tareas - Día/Noche",
    page_icon="📝",
    layout="wide"
)

# Función para determinar el tema según la hora
def obtener_tema_automatico():
    hora_actual = datetime.now().hour
    # Modo día de 6 AM a 6 PM
    if 6 <= hora_actual < 18:
        return "dia"
    else:
        return "noche"

# Inicializar preferencia de tema
if 'tema_manual' not in st.session_state:
    st.session_state.tema_manual = False
if 'tema_seleccionado' not in st.session_state:
    st.session_state.tema_seleccionado = obtener_tema_automatico()

# Definir temas
TEMAS = {
    "dia": {
        "bg_primary": "#ffffff",
        "bg_secondary": "#f0f2f6", 
        "bg_sidebar": "#f8f9fa",
        "text_primary": "#262730",
        "text_secondary": "#555555",
        "accent": "#3498db",
        "border": "#e0e0e0",
        "card_bg": "#ffffff",
        "success": "#2ecc71",
        "warning": "#f39c12",
        "danger": "#e74c3c",
        "emoji": "🌞"
    },
    "noche": {
        "bg_primary": "#0e1117",
        "bg_secondary": "#1a1c23",
        "bg_sidebar": "#262730",
        "text_primary": "#fafafa",
        "text_secondary": "#a3a8b8",
        "accent": "#00d4ff",
        "border": "#4a4a5e",
        "card_bg": "#1e1e2e",
        "success": "#00ff88",
        "warning": "#ffaa00",
        "danger": "#ff4444",
        "emoji": "🌙"
    }
}

# Determinar tema actual
if not st.session_state.tema_manual:
    tema_actual = obtener_tema_automatico()
    st.session_state.tema_seleccionado = tema_actual
else:
    tema_actual = st.session_state.tema_seleccionado

colores = TEMAS[tema_actual]

# CSS dinámico según tema
st.markdown(f"""
<style>
    /* Tema general */
    .stApp {{
        background: linear-gradient(135deg, {colores['bg_primary']} 0%, {colores['bg_secondary']} 100%);
    }}
    
    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background: {colores['bg_sidebar']};
        border-right: 1px solid {colores['border']};
    }}
    
    /* Headers y texto */
    h1, h2, h3, h4, h5, h6 {{
        color: {colores['text_primary']} !important;
    }}
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        background-color: {colores['card_bg']};
        border-radius: 10px;
        padding: 5px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        color: {colores['text_secondary']};
        background-color: transparent;
    }}
    
    .stTabs [aria-selected="true"] {{
        background-color: {colores['accent']} !important;
        color: white !important;
    }}
    
    /* Cards y contenedores */
    .element-container {{
        background-color: {colores['card_bg']};
        border-radius: 8px;
        padding: 10px;
        margin: 5px 0;
    }}
    
    /* Botones */
    .stButton > button {{
        background-color: {colores['accent']};
        color: white;
        border: none;
        transition: all 0.3s;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }}
    
    /* Inputs */
    input, textarea, select {{
        background-color: {colores['card_bg']} !important;
        color: {colores['text_primary']} !important;
        border: 1px solid {colores['border']} !important;
    }}
    
    /* Métricas */
    [data-testid="metric-container"] {{
        background-color: {colores['card_bg']};
        border: 1px solid {colores['border']};
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }}
    
    /* Categorías badge mejorado */
    .categoria-badge {{
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        display: inline-block;
        margin: 2px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    
    /* Progress bars */
    .stProgress > div > div {{
        background-color: {colores['accent']};
    }}
    
    /* Info boxes */
    .stAlert {{
        background-color: {colores['card_bg']};
        color: {colores['text_primary']};
        border: 1px solid {colores['border']};
    }}
    
    /* Efecto de transición suave */
    * {{
        transition: background-color 0.3s ease, color 0.3s ease;
    }}
    
    /* Header especial con gradiente */
    .main-header {{
        background: linear-gradient(135deg, {colores['accent']} 0%, {colores['warning']} 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }}
</style>
""", unsafe_allow_html=True)

# Definir categorías y colores (adaptados al tema)
CATEGORIAS = {
    "🏢 Trabajo": {"color": colores['accent'], "emoji": "🏢"},
    "🏠 Personal": {"color": colores['success'], "emoji": "🏠"},
    "💪 Gym/Salud": {"color": colores['warning'], "emoji": "💪"},
    "📚 Estudio": {"color": "#9b59b6", "emoji": "📚"},
    "🛒 Compras": {"color": "#e91e63", "emoji": "🛒"},
    "⚡ Otro": {"color": colores['text_secondary'], "emoji": "⚡"}
}

# Archivo para guardar
ARCHIVO = "tareas_web.json"

# Funciones para persistencia
def cargar_tareas():
    if os.path.exists(ARCHIVO):
        with open(ARCHIVO, 'r') as f:
            tareas = json.load(f)
            for tarea in tareas:
                if 'categoria' not in tarea:
                    tarea['categoria'] = "⚡ Otro"
            return tareas
    return []

def guardar_tareas(tareas):
    with open(ARCHIVO, 'w') as f:
        json.dump(tareas, f)

# Inicializar
if 'tareas' not in st.session_state:
    st.session_state.tareas = cargar_tareas()

# SIDEBAR con selector de tema
with st.sidebar:
    st.markdown(f"### {colores['emoji']} Configuración de Tema")
    
    # Mostrar hora actual
    hora_actual = datetime.now().strftime("%H:%M")
    st.info(f"🕐 Hora actual: {hora_actual}")
    
    # Toggle manual/automático
    modo_manual = st.checkbox("Control manual del tema", value=st.session_state.tema_manual)
    st.session_state.tema_manual = modo_manual
    
    if modo_manual:
        tema_elegido = st.radio(
            "Selecciona el tema:",
            ["dia", "noche"],
            format_func=lambda x: f"{TEMAS[x]['emoji']} Modo {x.capitalize()}",
            index=0 if st.session_state.tema_seleccionado == "dia" else 1
        )
        st.session_state.tema_seleccionado = tema_elegido
    else:
        st.success(f"Tema automático activo: **Modo {tema_actual.capitalize()}**")
        st.caption("☀️ Día: 6 AM - 6 PM")
        st.caption("🌙 Noche: 6 PM - 6 AM")
    
    st.markdown("---")
    st.markdown("### 📊 Resumen Rápido")
    total_sidebar = len(st.session_state.tareas)
    pendientes_sidebar = sum(1 for t in st.session_state.tareas if not t['completada'])
    st.metric("Total tareas", total_sidebar)
    st.metric("Pendientes", pendientes_sidebar)

# Título principal con diseño especial
st.markdown(f'<div class="main-header"><h1>{colores["emoji"]} Mi Lista de Tareas</h1><p>Modo {tema_actual.capitalize()} activado</p></div>', unsafe_allow_html=True)

# TABS con los mismos estilos
tab1, tab2, tab3 = st.tabs(["📝 Lista de Tareas", "📅 Vista Calendario", "📊 Estadísticas"])

with tab1:
    # AGREGAR TAREA
    with st.form("nueva_tarea", clear_on_submit=True):
        st.markdown(f"### ➕ Agregar Nueva Tarea")
        col1, col2, col3 = st.columns([3, 1.5, 1.5])
        
        with col1:
            nueva_tarea = st.text_input("¿Qué necesitas hacer?", 
                                       placeholder="Escribe tu tarea aquí...")
        with col2:
            categoria = st.selectbox("Categoría", 
                                    options=list(CATEGORIAS.keys()),
                                    index=0)
        with col3:
            fecha = st.date_input("Fecha", 
                                min_value=date.today(),
                                format="DD/MM/YYYY")
        
        col4, col5, col6 = st.columns([1, 1, 3])
        with col4:
            urgente = st.checkbox("🔴 Urgente")
        with col5:
            submitted = st.form_submit_button("➕ Agregar", 
                                             type="primary", 
                                             use_container_width=True)

    if submitted and nueva_tarea:
        st.session_state.tareas.append({
            'texto': nueva_tarea,
            'fecha': fecha.strftime("%d/%m/%Y"),
            'categoria': categoria,
            'completada': False,
            'urgente': urgente
        })
        guardar_tareas(st.session_state.tareas)
        st.success("✅ Tarea agregada exitosamente!")
        st.rerun()

    # FILTROS
    st.markdown("### 🔍 Filtros")
    col1, col2 = st.columns(2)
    
    with col1:
        filtro_estado = st.radio("Estado:", 
                         ["Todas", "Pendientes", "Completadas"], 
                         horizontal=True)
    
    with col2:
        categorias_seleccionadas = st.multiselect(
            "Categorías:",
            options=list(CATEGORIAS.keys()),
            default=list(CATEGORIAS.keys())
        )

    # APLICAR FILTROS
    tareas_filtradas = st.session_state.tareas

    if filtro_estado == "Pendientes":
        tareas_filtradas = [t for t in tareas_filtradas if not t['completada']]
    elif filtro_estado == "Completadas":
        tareas_filtradas = [t for t in tareas_filtradas if t['completada']]

    tareas_filtradas = [t for t in tareas_filtradas 
                        if t.get('categoria', "⚡ Otro") in categorias_seleccionadas]

    # MOSTRAR TAREAS
    st.markdown("### 📌 Tareas")
    
    if not tareas_filtradas:
        st.info(f"No hay tareas para mostrar {colores['emoji']}")
    else:
        for i, tarea in enumerate(st.session_state.tareas):
            if tarea not in tareas_filtradas:
                continue
            
            categoria_actual = tarea.get('categoria', "⚡ Otro")
            color = CATEGORIAS[categoria_actual]["color"]
            
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([0.5, 3, 1.5, 1.5, 0.5])
                
                with col1:
                    completada = st.checkbox("", 
                                            value=tarea['completada'],
                                            key=f"check_{i}")
                    if completada != tarea['completada']:
                        st.session_state.tareas[i]['completada'] = completada
                        guardar_tareas(st.session_state.tareas)
                        st.rerun()
                
                with col2:
                    categoria_html = f'<span class="categoria-badge" style="background-color: {color}; color: white;">{categoria_actual}</span>'
                    
                    if tarea['completada']:
                        st.markdown(f"{categoria_html} ~~{tarea['texto']}~~", 
                                  unsafe_allow_html=True)
                    elif tarea.get('urgente'):
                        st.markdown(f"{categoria_html} 🔴 **{tarea['texto']}**", 
                                  unsafe_allow_html=True)
                    else:
                        st.markdown(f"{categoria_html} {tarea['texto']}", 
                                  unsafe_allow_html=True)
                
                with col3:
                    st.caption(f"📅 {tarea['fecha']}")
                
                with col4:
                    nueva_cat = st.selectbox("", 
                                            options=list(CATEGORIAS.keys()),
                                            index=list(CATEGORIAS.keys()).index(categoria_actual),
                                            key=f"cat_{i}",
                                            label_visibility="collapsed")
                    if nueva_cat != categoria_actual:
                        st.session_state.tareas[i]['categoria'] = nueva_cat
                        guardar_tareas(st.session_state.tareas)
                        st.rerun()
                
                with col5:
                    if st.button("🗑️", key=f"del_{i}"):
                        st.session_state.tareas.pop(i)
                        guardar_tareas(st.session_state.tareas)
                        st.rerun()

with tab2:
    st.header(f"📅 Vista de Calendario {colores['emoji']}")
    
    # Selector de mes y año
    col1, col2 = st.columns(2)
    with col1:
        mes = st.selectbox("Mes", 
                          options=list(range(1, 13)),
                          format_func=lambda x: calendar.month_name[x],
                          index=datetime.now().month - 1,
                          key="mes_cal")
    with col2:
        año = st.selectbox("Año", 
                          options=list(range(2024, 2030)),
                          index=list(range(2024, 2030)).index(datetime.now().year),
                          key="año_cal")
    
    # Crear calendario
    cal = calendar.monthcalendar(año, mes)
    dias_semana = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
    
    # Mostrar calendario con estilo mejorado
    st.markdown(f"<div style='background: {colores['card_bg']}; padding: 20px; border-radius: 10px;'>", unsafe_allow_html=True)
    
    cols = st.columns(7)
    for i, dia in enumerate(dias_semana):
        cols[i].markdown(f"**{dia}**")
    
    for semana in cal:
        cols = st.columns(7)
        for i, dia in enumerate(semana):
            if dia == 0:
                cols[i].write("")
            else:
                fecha_str = f"{dia:02d}/{mes:02d}/{año}"
                tareas_del_dia = [t for t in st.session_state.tareas 
                                 if t.get('fecha') == fecha_str and not t['completada']]
                
                if tareas_del_dia:
                    categorias_dia = set([t.get('categoria', "⚡ Otro") for t in tareas_del_dia])
                    emojis = "".join([CATEGORIAS[cat]["emoji"] for cat in categorias_dia])
                    
                    # Resaltar día actual
                    if fecha_str == datetime.now().strftime("%d/%m/%Y"):
                        cols[i].markdown(f"**🔵 {dia}**  \n{emojis}")
                    else:
                        cols[i].markdown(f"**{dia}**  \n{emojis}")
                else:
                    if fecha_str == datetime.now().strftime("%d/%m/%Y"):
                        cols[i].markdown(f"**🔵 {dia}**")
                    else:
                        cols[i].markdown(f"**{dia}**")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Lista de tareas del mes
    st.markdown("---")
    st.subheader(f"📋 Tareas del mes")
    
    tareas_mes = [t for t in st.session_state.tareas 
                  if t.get('fecha') and 
                  int(t['fecha'].split('/')[1]) == mes and 
                  int(t['fecha'].split('/')[2]) == año and
                  not t['completada']]
    
    if tareas_mes:
        for categoria in CATEGORIAS.keys():
            tareas_categoria = [t for t in tareas_mes if t.get('categoria') == categoria]
            if tareas_categoria:
                with st.expander(f"{categoria} ({len(tareas_categoria)} tareas)"):
                    for tarea in tareas_categoria:
                        urgente = "🔴 " if tarea.get('urgente') else ""
                        st.write(f"• {urgente}**{tarea['fecha']}** - {tarea['texto']}")
    else:
        st.info(f"No hay tareas pendientes este mes {colores['emoji']}")

with tab3:
    st.header(f"📊 Estadísticas {colores['emoji']}")
    
    # Métricas principales con diseño mejorado
    col1, col2, col3, col4 = st.columns(4)
    
    total = len(st.session_state.tareas)
    completadas = sum(1 for t in st.session_state.tareas if t['completada'])
    pendientes = total - completadas
    urgentes = sum(1 for t in st.session_state.tareas if t.get('urgente') and not t['completada'])
    
    col1.metric("📊 Total", total, delta=None)
    col2.metric("✅ Completadas", completadas, delta=f"{completadas/total*100:.0f}%" if total > 0 else "0%")
    col3.metric("⏳ Pendientes", pendientes)
    col4.metric("🔴 Urgentes", urgentes)
    
    # Estadísticas por categoría con barras de progreso
    st.markdown("---")
    st.subheader("📈 Progreso por Categoría")
    
    for categoria in CATEGORIAS.keys():
        tareas_cat = [t for t in st.session_state.tareas if t.get('categoria') == categoria]
        if tareas_cat:
            total_cat = len(tareas_cat)
            completadas_cat = sum(1 for t in tareas_cat if t['completada'])
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{categoria}**")
                if total_cat > 0:
                    progreso = completadas_cat / total_cat
                    st.progress(progreso)
            with col2:
                st.metric("", f"{completadas_cat}/{total_cat}", 
                         delta=f"{completadas_cat/total_cat*100:.0f}%" if total_cat > 0 else "0%",
                         label_visibility="collapsed")
    
    # Resumen del día
    st.markdown("---")
    st.subheader(f"📆 Resumen de Hoy")
    
    hoy = datetime.now().strftime("%d/%m/%Y")
    tareas_hoy = [t for t in st.session_state.tareas if t.get('fecha') == hoy]
    
    if tareas_hoy:
        col1, col2, col3 = st.columns(3)
        col1.metric("Tareas para hoy", len(tareas_hoy))
        col2.metric("Completadas", sum(1 for t in tareas_hoy if t['completada']))
        col3.metric("Pendientes", sum(1 for t in tareas_hoy if not t['completada']))
    else:
        st.info(f"No hay tareas programadas para hoy {colores['emoji']}")

# PIE DE PÁGINA
st.markdown("---")
st.caption(f"Hecho con Python + Streamlit 🚀 | Modo {tema_actual.capitalize()} {colores['emoji']} | [Ver código](https://github.com/MetaEnzo/Lista-tareas-web)")

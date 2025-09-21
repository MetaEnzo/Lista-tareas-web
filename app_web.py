import streamlit as st
import json
import os
from datetime import datetime, date
import calendar

# Configuración de la página
st.set_page_config(
    page_title="Lista de Tareas con Categorías",
    page_icon="📝",
    layout="wide"
)

# Definir categorías y colores
CATEGORIAS = {
    "🏢 Trabajo": {"color": "#3498db", "emoji": "🏢"},
    "🏠 Personal": {"color": "#2ecc71", "emoji": "🏠"},
    "💪 Gym/Salud": {"color": "#f39c12", "emoji": "💪"},
    "📚 Estudio": {"color": "#9b59b6", "emoji": "📚"},
    "🛒 Compras": {"color": "#e91e63", "emoji": "🛒"},
    "⚡ Otro": {"color": "#95a5a6", "emoji": "⚡"}
}

# Archivo para guardar
ARCHIVO = "tareas_web.json"

# Funciones para persistencia
def cargar_tareas():
    if os.path.exists(ARCHIVO):
        with open(ARCHIVO, 'r') as f:
            tareas = json.load(f)
            # Migrar tareas antiguas sin categoría
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

# CSS personalizado para categorías
st.markdown("""
<style>
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

# Título principal
st.title("📝 Mi Lista de Tareas con Categorías")
st.markdown("---")

# TABS
tab1, tab2, tab3 = st.tabs(["📝 Lista de Tareas", "📅 Vista Calendario", "📊 Estadísticas"])

with tab1:
    # AGREGAR TAREA
    with st.form("nueva_tarea", clear_on_submit=True):
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
        st.success("✅ Tarea agregada!")
        st.rerun()

    # FILTROS MEJORADOS
    st.markdown("### 📋 Filtros")
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
        st.info("No hay tareas para mostrar 📭")
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
                    # Mostrar con categoría y color
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
                    # Botón de editar categoría
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
    st.header("📅 Vista de Calendario")
    
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
    
    # Crear calendario con categorías
    cal = calendar.monthcalendar(año, mes)
    dias_semana = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
    
    # Mostrar días de la semana
    cols = st.columns(7)
    for i, dia in enumerate(dias_semana):
        cols[i].markdown(f"**{dia}**")
    
    # Mostrar calendario con tareas coloreadas por categoría
    for semana in cal:
        cols = st.columns(7)
        for i, dia in enumerate(semana):
            if dia == 0:
                cols[i].write("")
            else:
                fecha_str = f"{dia:02d}/{mes:02d}/{año}"
                tareas_del_dia = [t for t in st.session_state.tareas 
                                 if t.get('fecha') == fecha_str and not t['completada']]
                
                # Mostrar día con indicadores de categorías
                if tareas_del_dia:
                    categorias_dia = set([t.get('categoria', "⚡ Otro") for t in tareas_del_dia])
                    emojis = "".join([CATEGORIAS[cat]["emoji"] for cat in categorias_dia])
                    cols[i].markdown(f"**{dia}**  \n{emojis}")
                else:
                    cols[i].markdown(f"**{dia}**")
    
    # Lista de tareas del mes por categoría
    st.markdown("---")
    st.subheader("📋 Tareas del mes por categoría")
    
    tareas_mes = [t for t in st.session_state.tareas 
                  if t.get('fecha') and 
                  int(t['fecha'].split('/')[1]) == mes and 
                  int(t['fecha'].split('/')[2]) == año and
                  not t['completada']]
    
    if tareas_mes:
        # Agrupar por categoría
        for categoria in CATEGORIAS.keys():
            tareas_categoria = [t for t in tareas_mes if t.get('categoria') == categoria]
            if tareas_categoria:
                color = CATEGORIAS[categoria]["color"]
                st.markdown(f'<h4 style="color: {color};">{categoria} ({len(tareas_categoria)})</h4>', 
                          unsafe_allow_html=True)
                for tarea in tareas_categoria:
                    urgente = "🔴 " if tarea.get('urgente') else ""
                    st.write(f"  • {urgente}**{tarea['fecha']}** - {tarea['texto']}")
    else:
        st.info("No hay tareas pendientes este mes")

with tab3:
    st.header("📊 Estadísticas por Categoría")
    
    # Métricas generales
    total = len(st.session_state.tareas)
    completadas = sum(1 for t in st.session_state.tareas if t['completada'])
    pendientes = total - completadas
    urgentes = sum(1 for t in st.session_state.tareas if t.get('urgente') and not t['completada'])
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📊 Total", total)
    col2.metric("✅ Completadas", completadas)
    col3.metric("⏳ Pendientes", pendientes)
    col4.metric("🔴 Urgentes", urgentes)
    
    # Estadísticas por categoría
    st.markdown("---")
    st.subheader("📈 Distribución por Categoría")
    
    for categoria in CATEGORIAS.keys():
        tareas_cat = [t for t in st.session_state.tareas if t.get('categoria') == categoria]
        if tareas_cat:
            total_cat = len(tareas_cat)
            completadas_cat = sum(1 for t in tareas_cat if t['completada'])
            pendientes_cat = total_cat - completadas_cat
            
            color = CATEGORIAS[categoria]["color"]
            
            col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
            with col1:
                st.markdown(f'<span style="color: {color}; font-weight: bold; font-size: 18px;">{categoria}</span>', 
                          unsafe_allow_html=True)
            with col2:
                st.metric("Total", total_cat, label_visibility="collapsed")
            with col3:
                st.metric("Pendientes", pendientes_cat, label_visibility="collapsed")
            with col4:
                if total_cat > 0:
                    progreso = completadas_cat / total_cat
                    st.progress(progreso)
                    st.caption(f"{progreso*100:.0f}% completado")
    
    # Gráfico de progreso general
    if total > 0:
        st.markdown("---")
        st.subheader("🎯 Progreso General")
        progress = completadas / total
        st.progress(progress)
        st.write(f"Has completado el **{progress*100:.1f}%** de todas tus tareas")

# PIE DE PÁGINA
st.markdown("---")
st.caption("Hecho con Python + Streamlit 🚀 | Con categorías y colores | [Ver código](https://github.com/MetaEnzo/Lista-tareas-web)")

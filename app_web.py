import streamlit as st
import json
import os
from datetime import datetime, date
import calendar

# Configuración de la página
st.set_page_config(
    page_title="Lista de Tareas con Calendario",
    page_icon="📝",
    layout="wide"  # Cambiado a wide para el calendario
)

# Archivo para guardar
ARCHIVO = "tareas_web.json"

# Funciones para persistencia
def cargar_tareas():
    if os.path.exists(ARCHIVO):
        with open(ARCHIVO, 'r') as f:
            return json.load(f)
    return []

def guardar_tareas(tareas):
    with open(ARCHIVO, 'w') as f:
        json.dump(tareas, f)

# Inicializar
if 'tareas' not in st.session_state:
    st.session_state.tareas = cargar_tareas()

# Título principal
st.title("📝 Mi Lista de Tareas con Calendario")
st.markdown("---")

# CREAR TABS PARA ORGANIZAR
tab1, tab2, tab3 = st.tabs(["📝 Lista de Tareas", "📅 Vista Calendario", "📊 Estadísticas"])

with tab1:
    # AGREGAR TAREA
    with st.form("nueva_tarea", clear_on_submit=True):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            nueva_tarea = st.text_input("¿Qué necesitas hacer?", 
                                       placeholder="Escribe tu tarea aquí...")
        with col2:
            fecha = st.date_input("Fecha", 
                                min_value=date.today(),
                                format="DD/MM/YYYY")
        
        col3, col4, col5 = st.columns([1, 1, 3])
        with col3:
            urgente = st.checkbox("🔴 Urgente")
        with col4:
            submitted = st.form_submit_button("➕ Agregar", 
                                             type="primary", 
                                             use_container_width=True)

    if submitted and nueva_tarea:
        st.session_state.tareas.append({
            'texto': nueva_tarea,
            'fecha': fecha.strftime("%d/%m/%Y"),
            'completada': False,
            'urgente': urgente
        })
        guardar_tareas(st.session_state.tareas)
        st.success("✅ Tarea agregada!")
        st.rerun()

    # FILTROS
    st.markdown("### 📋 Tus Tareas")
    filtro = st.radio("Mostrar:", 
                      ["Todas", "Pendientes", "Completadas"], 
                      horizontal=True)

    # MOSTRAR TAREAS
    tareas_filtradas = st.session_state.tareas

    if filtro == "Pendientes":
        tareas_filtradas = [t for t in tareas_filtradas if not t['completada']]
    elif filtro == "Completadas":
        tareas_filtradas = [t for t in tareas_filtradas if t['completada']]

    if not tareas_filtradas:
        st.info("No hay tareas para mostrar 📭")
    else:
        for i, tarea in enumerate(st.session_state.tareas):
            if tarea not in tareas_filtradas:
                continue
                
            with st.container():
                col1, col2, col3, col4 = st.columns([0.5, 4, 1.5, 0.5])
                
                with col1:
                    completada = st.checkbox("", 
                                            value=tarea['completada'],
                                            key=f"check_{i}")
                    if completada != tarea['completada']:
                        st.session_state.tareas[i]['completada'] = completada
                        guardar_tareas(st.session_state.tareas)
                        st.rerun()
                
                with col2:
                    if tarea['completada']:
                        st.markdown(f"~~{tarea['texto']}~~")
                    elif tarea.get('urgente'):
                        st.markdown(f"🔴 **{tarea['texto']}**")
                    else:
                        st.markdown(tarea['texto'])
                
                with col3:
                    st.caption(f"📅 {tarea['fecha']}")
                
                with col4:
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
                          index=datetime.now().month - 1)
    with col2:
        año = st.selectbox("Año", 
                          options=list(range(2024, 2030)),
                          index=list(range(2024, 2030)).index(datetime.now().year))
    
    # Crear calendario
    cal = calendar.monthcalendar(año, mes)
    dias_semana = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
    
    # Mostrar días de la semana
    cols = st.columns(7)
    for i, dia in enumerate(dias_semana):
        cols[i].markdown(f"**{dia}**")
    
    # Mostrar calendario con tareas
    for semana in cal:
        cols = st.columns(7)
        for i, dia in enumerate(semana):
            if dia == 0:
                cols[i].write("")
            else:
                fecha_str = f"{dia:02d}/{mes:02d}/{año}"
                tareas_del_dia = [t for t in st.session_state.tareas 
                                 if t.get('fecha') == fecha_str and not t['completada']]
                tareas_completadas_dia = [t for t in st.session_state.tareas 
                                         if t.get('fecha') == fecha_str and t['completada']]
                
                # Determinar color según cantidad de tareas
                if len(tareas_del_dia) > 3:
                    color = "🔴"  # Muchas tareas
                elif len(tareas_del_dia) > 0:
                    color = "🟡"  # Algunas tareas
                else:
                    color = "⚪"  # Sin tareas
                
                with cols[i]:
                    st.markdown(f"**{dia}** {color}")
                    
                    if tareas_del_dia:
                        st.caption(f"📌 {len(tareas_del_dia)} pendientes")
                    if tareas_completadas_dia:
                        st.caption(f"✅ {len(tareas_completadas_dia)} completadas")
                    
                    # Mostrar primera tarea si existe
                    if tareas_del_dia:
                        primera = tareas_del_dia[0]['texto'][:15]
                        if len(primera) < len(tareas_del_dia[0]['texto']):
                            primera += "..."
                        st.caption(f"• {primera}")
    
    # Lista de tareas del mes
    st.markdown("---")
    st.subheader(f"📋 Resumen de {calendar.month_name[mes]} {año}")
    
    tareas_mes = []
    for tarea in st.session_state.tareas:
        if tarea.get('fecha'):
            try:
                dia, mes_t, año_t = tarea['fecha'].split('/')
                if int(mes_t) == mes and int(año_t) == año:
                    tareas_mes.append(tarea)
            except:
                pass
    
    if tareas_mes:
        tareas_mes.sort(key=lambda x: x['fecha'])
        for tarea in tareas_mes:
            icono = "✅" if tarea['completada'] else "⏳"
            urgente = "🔴 " if tarea.get('urgente') and not tarea['completada'] else ""
            st.write(f"{icono} **{tarea['fecha']}** - {urgente}{tarea['texto']}")
    else:
        st.info("No hay tareas para este mes")

with tab3:
    st.header("📊 Estadísticas")
    
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
    
    # Gráfico de progreso
    if total > 0:
        st.markdown("---")
        st.subheader("Progreso")
        progress = completadas / total
        st.progress(progress)
        st.write(f"Has completado el {progress*100:.1f}% de tus tareas")
    
    # Tareas por día
    st.markdown("---")
    st.subheader("📅 Distribución por días")
    
    from collections import defaultdict
    tareas_por_dia = defaultdict(int)
    
    for tarea in st.session_state.tareas:
        if tarea.get('fecha') and not tarea['completada']:
            tareas_por_dia[tarea['fecha']] += 1
    
    if tareas_por_dia:
        for fecha, cantidad in sorted(tareas_por_dia.items()):
            st.write(f"**{fecha}**: {'📌' * cantidad} ({cantidad} tareas)")
    else:
        st.info("No hay tareas pendientes con fecha")

# PIE DE PÁGINA
st.markdown("---")
st.caption("Hecho con Python + Streamlit 🚀 | [Ver código](https://github.com/MetaEnzo/Lista-tareas-web)")
            

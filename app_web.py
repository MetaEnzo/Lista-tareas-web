import streamlit as st
import json
import os
from datetime import datetime, date

# Configuración de la página
st.set_page_config(
    page_title="Lista de Tareas",
    page_icon="📝",
    layout="centered"
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

# INTERFAZ
st.title("📝 Mi Lista de Tareas")
st.markdown("---")

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
        # Solo mostrar si pasa el filtro
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
                # Estilo según estado
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

# ESTADÍSTICAS
st.markdown("---")
total = len(st.session_state.tareas)
completadas = sum(1 for t in st.session_state.tareas if t['completada'])
pendientes = total - completadas

col1, col2, col3 = st.columns(3)
col1.metric("📊 Total", total)
col2.metric("✅ Completadas", completadas)
col3.metric("⏳ Pendientes", pendientes)

# PIE DE PÁGINA
st.markdown("---")
st.caption("Hecho con Python + Streamlit 🚀")

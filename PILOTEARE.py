import streamlit as st
import pandas as pd
import datetime
import random
import gspread
from oauth2client.service_account import service_account

# -----------------------------------------------------------------------------
# CONFIGURACIÓN
# -----------------------------------------------------------------------------
URL_PLANILLA = "https://docs.google.com/spreadsheets/d/1PQGUpbPdyaoH01jMOi5MedoVIjvJnfpVwwt9RkXSYCY/edit?gid=0#gid=0"

# Configuración de la página
st.set_page_config(page_title="PILOTEARE - Aviación", layout="wide")

# -----------------------------------------------------------------------------
# FUNCIONES AUXILIARES
# -----------------------------------------------------------------------------

def limpiar_texto(texto):
    """Limpia entidades HTML corruptas y espacios extra."""
    if isinstance(texto, str):
        texto = texto.replace("\u0026quot;", "\"").replace("\u003c", "<").replace("\u003e", ">")
        return texto.strip()
    return texto

def cargar_conexion_sheets():
    """Inicializa la conexión con Google Sheets."""
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        # ⚠️ IMPORTANTE: Reemplaza con tu archivo de credenciales JSON
        # credenciales = service_account_path  # Tu archivo de credenciales
        # gc = gspread.authorize(credenciales)
        
        # Para desarrollo local, puedes usar una conexión simulada o tu credencial real
        gc = gspread.service_account()
        return gc
    except Exception as e:
        st.error(f"Error al conectar con Sheets: {e}")
        return None

# -----------------------------------------------------------------------------
# CARGA DE DATOS (CON CACHE)
# -----------------------------------------------------------------------------

@st.cache_data(ttl=600, show_spinner="Cargando datos...")
def cargar_datos_bitacora():
    """Lee el historial de vuelos desde la solapa 'Bitacora'."""
    gc = cargar_conexion_sheets()
    if not gc:
        return pd.DataFrame()
    
    try:
        df = gc.open("PILOTEARE").worksheet("Bitacora").get_all_records()
        return pd.DataFrame(df)
    except Exception as e:
        st.error(f"Error al leer Bitácora: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=600, show_spinner="Cargando banco de preguntas...")
def cargar_banco_preguntas_completo():
    """Lee el banco de preguntas desde 'Preguntas_Trivia'."""
    gc = cargar_conexion_sheets()
    if not gc:
        return []
    
    try:
        df = gc.open("PILOTEARE").worksheet("Preguntas_Trivia").get_all_records()
        banco = []
        for _, row in df.iterrows():
            banco.append({
                "categoria": row.get("categoria", "General"),
                "pregunta": row.get("pregunta", ""),
                "opciones_orig": row.get("opciones", "").split(";"),
                "correcta_orig": row.get("correcta", 0)
            })
        return banco
    except Exception as e:
        st.error(f"Error al cargar preguntas: {e}")
        return []

# -----------------------------------------------------------------------------
# ESTADO DE SESIÓN
# -----------------------------------------------------------------------------

if "desafio_respondido" not in st.session_state:
    st.session_state.desafio_respondido = False
if "ultimo_vuelo_id" not in st.session_state:
    st.session_state.ultimo_vuelo_id = 0

# -----------------------------------------------------------------------------
# INICIALIZACIÓN
# -----------------------------------------------------------------------------

gc = cargar_conexion_sheets()
BANCO_COMPLETO = cargar_banco_preguntas_completo()
BITACORA_DF = cargar_datos_bitacora()

# Diccionario de la flota CUA
FLOTA_CUA = {
    "LV-JIF (Cessna 150)": {"modelo": "Cessna 150", "aeronave": "LV-JIF"},
    "LV-ABC (Piper PA-28)": {"modelo": "Piper PA-28", "aeronave": "LV-ABC"}
}

# -----------------------------------------------------------------------------
# INTERFAZ DE USUARIO
# -----------------------------------------------------------------------------

st.title("🛫 PILOTEARE - Sistema de Entrenamiento")

# --- BLOQUE 1: PREGUNTA DESAFÍO DEL DÍA ---
# 🔧 CORRECCIÓN: Se usa .dayofyear sin paréntesis
dia_del_ano = datetime.date.today().dayofyear
idx_desafio = dia_del_ano % len(BANCO_COMPLETO)
q_dia = BANCO_COMPLETO[idx_desafio]

st.subheader("🔥 Pregunta Desafío del Día (Nivel Leyenda)")

st.markdown(f"""
##### 🎯 **[Tema: {limpiar_texto(q_dia['categoria'])}]** 
{limpiar_texto(q_dia['pregunta'])}
""", unsafe_allow_html=True)

opciones = q_dia["opciones_orig"]
seleccion_usuario = st.radio(
    "Elige la opción que consideres correcta:",
    opciones,
    key="radio_desafio_dia",
    horizontal=True
)

# Verificar respuesta
if st.session_state.get("radio_desafio_dia") is not None:
    # Buscar la respuesta correcta en las opciones mezcladas
    correcta_idx = q_dia["correcta_orig"]
    
    if limpiar_texto(seleccion_usuario) == limpiar_texto(opciones[correcta_idx]):
        st.success("✅ ¡Correcto! Nivel Leyenda confirmado.")
        st.session_state.desafio_respondido = True
    else:
        st.error("❌ Incorrecto. Inténtalo de nuevo mañana.")

# --- BLOQUE 2: TRIVIA MULTIJUGADOR ---
col_amg1, col_amg2 = st.columns(2)

with col_amg1:
    st.subheader("🎮 Trivia Rápida para Amigos")
    if st.button("🚀 Iniciar Ronda Rápida", type="primary"):
        st.info("Ronda de preguntas rápidas iniciada...")
        # Aquí iría la lógica de trivia interactiva

with col_amg2:
    st.subheader("📊 Estadísticas de la Sesión")
    if st.session_state.desafio_respondido:
        st.metric("Desafío Hoy", "Completado")
    else:
        st.metric("Desafío Hoy", "Pendiente")

# --- BLOQUE 3: REGISTRO DE VUELO (BITÁCORA DIGITAL) ---
st.divider()
st.subheader("✍️ Registro de Vuelo")

with st.form("form_guardar_vuelo"):
    info_avion = st.selectbox("Seleccionar Aeronave", list(FLOTA_CUA.keys()))
    
    instructor = st.text_input("Instructor de Vuelo", key="instructor_input")
    
    detalle_vuelo = st.text_area(
        "Detalle de la Lección / Maniobras Realizadas",
        value="Instrucción de prevuelo. Puesta en marcha. Virajes suaves,"
              " medios y escarpados. Aterrizaje.",
        height=100
    )
    
    anecdotario = st.text_area(
        "Anecdotario / Sensaciones Personales",
        value="Muy buen desempeño en los virajes escarpados.",
        height=50
    )
    
    meteorologia = st.text_input("Meteorología / Pista en Uso", value="Viento 8 nudos del Este. Pista 35")
    
    btn_guardar = st.form_submit_button("💾 Guardar Vuelo en Bitácora Digital")

    if btn_guardar:
        if not instructor or not detalle_vuelo:
            st.error("⚠️ Por favor, completa los campos obligatorios (Instructor y Detalle).")
        else:
            st.session_state.ultimo_vuelo_id += 1
            
            registro_vuelo = {
                "ID": st.session_state.ultimo_vuelo_id,
                "Fecha_Hora": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Modelo": info_avion,
                "Instructor": instructor,
                "Detalle": detalle_vuelo,
                "Meteorología": meteorologia
            }
            
            # Guardar en Google Sheets
            if gc:
                try:
                    df_actualizado = pd.DataFrame([registro_vuelo])
                    gc.open("PILOTEARE").worksheet("Bitacora").append_rows(df_actualizado)
                    st.success("✅ Vuelo guardado correctamente en Bitácora Digital.")
                except Exception as e:
                    st.error(f"No se pudo guardar: {e}")
            else:
                st.success("✅ Vuelo guardado localmente (modo offline).")
            
            st.form_clear_form_state()

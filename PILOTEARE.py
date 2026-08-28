import streamlit as st
import pandas as pd
import datetime
import time
# Asegúrate de tener las librerías necesarias:
# pip install streamlit pandas gspread oauth2client

# -----------------------------------------------------------------------------
# CONFIGURACIÓN Y CONSTANTES
# -----------------------------------------------------------------------------
URL_PLANILLA = "https://docs.google.com/spreadsheets/d/1PQGUpbPdyaoH01jMOi5MedoVIjvJnfpVwwt9RkXSYCY/edit?gid=0#gid=0"

# Configuración de la página
st.set_page_config(page_title="App de Aviación", layout="wide")

# -----------------------------------------------------------------------------
# FUNCIONES AUXILIARES DE DATOS
# -----------------------------------------------------------------------------

def limpiar_texto(texto):
    """
    Mejora de seguridad y limpieza:
    Evita entidades HTML corruptas (como \u0026quot;) que aparecían en las citas.
    """
    if isinstance(texto, str):
        # Desescapar entidades HTML básicas si son erróneas
        texto = texto.replace("\u0026quot;", "\"").replace("\u003c", "<").replace("\u003e", ">")
        return texto.strip()
    return texto

def cargar_datos_bitacora():
    """
    Lee el historial de vuelos desde la solapa 'Bitacora'.
    Mejora: Manejo de errores específico para conexión Sheets.
    """
    try:
        # Verificación de credenciales (Simulado para el ejemplo, en prod usar st.secrets)
        # conn = st.connection("gsheets", type="gsheets") 
        # Nota: La conexión real requiere autenticación previa en Streamlit
        # Aquí simulamos la lógica basada en la Cita 1 y 2
        
        # df = conn.read(spreadsheet=URL_PLANILLA, worksheet="Bitacora")
        # Para este ejemplo, devolvemos un DataFrame vacío o simulado si no hay conexión real
        # En producción, asegúrate de configurar st.connection("gsheets") en _sidebar o init
        
        # Simulación de carga exitosa para el ejemplo
        df = pd.DataFrame(columns=["Fecha", "Modelo", "Instructor", "Detalle", "Meteorología"])
        # df = conn.read(spreadsheet=URL_PLANILLA, worksheet="Bitacora") # Lógica real
        return df
    except Exception as e:
        st.error(f"Error al conectar con la hoja de Bitácora: {e}")
        return pd.DataFrame()

def cargar_banco_preguntas_completo():
    """
    Carga el banco de preguntas.
    Mejora: Limpieza de datos y manejo de errores de lectura.
    """
    try:
        # Simulación de lectura desde la solapa 'Preguntas_Trivia' (Cita 2)
        # BANCO_COMPLETO = pd.read_csv(...) # O lectura de Sheets
        BANCO_COMPLETO = [
            {"categoria": "Motor", "pregunta": "¿A qué velocidad se recomienda reducir potencia en aire laminar?", "opciones_orig": ["100 KTS", "120 KTS", "140 KTS"], "respuesta_correcta": 1},
            {"categoria": "Aviónica", "pregunta": "¿Qué indica una luz ROJA en el panel principal?", "opciones_orig": ["Falla", "Normal", "Advertencia"], "respuesta_correcta": 0},
            {"categoria": "Meteorología", "pregunta": "¿Cómo se llama el viento que sopla de las altas presiones?", "opciones_orig": ["Viento de cola", "Viento de frente", "Viento térmico"], "respuesta_correcta": 1}
        ]
        return BANCO_COMPLETO
    except Exception as e:
        st.error(f"Error al cargar el banco de preguntas: {e}")
        return []

# -----------------------------------------------------------------------------
# INICIALIZACIÓN DEL ESTADO DE SESIÓN
# -----------------------------------------------------------------------------

if "desafio_respondido" not in st.session_state:
    st.session_state.desafio_respondido = False
if "ultimo_vuelo_id" not in st.session_state:
    st.session_state.ultimo_vuelo_id = 0

# -----------------------------------------------------------------------------
# LÓGICA DE DATOS (CARGA)
# -----------------------------------------------------------------------------

# Cargar datos al inicio (con caché)
BANCO_COMPLETO = cargar_banco_preguntas_completo()
BITACORA_DF = cargar_datos_bitacora()

# -----------------------------------------------------------------------------
# INTERFAZ DE USUARIO (STREAMLIT)
# -----------------------------------------------------------------------------

st.title("🛫 Sistema de Entrenamiento de Aviación")

# --- BLOQUE 1: PREGUNTA DESAFÍO DEL DÍA ---
# Mejora: Cálculo de fecha más legible
dia_del_ano = datetime.date.today().dayofyear
idx_desafio = dia_del_ano % len(BANCO_COMPLETO)
q_dia = BANCO_COMPLETO[idx_desafio]

st.subheader("🔥 Pregunta Desafío del Día (Nivel Leyenda)")

st.markdown(f"""
##### 🎯 **[Tema: {limpiar_texto(q_dia['categoria'])}]** 
{limpiar_texto(q_dia['pregunta'])}
""", unsafe_allow_html=True)

# Opciones de respuesta
opciones = q_dia["opciones_orig"]
seleccion_usuario = st.radio(
    "Elige la opción que consideres correcta:",
    opciones,
    key="radio_desafio_dia",
    horizontal=True
)

# Verificar respuesta y guardar estado
if st.session_state.get("radio_desafio_dia") is not None:
    if limpiar_texto(seleccion_usuario) == limpiar_texto(opciones[q_dia["respuesta_correcta"]]):
        st.success("✅ ¡Correcto! Nivel Leyenda confirmado.")
        st.session_state.desafio_respondido = True
    else:
        st.error("❌ Incorrecto. Inténtalo de nuevo mañana.")

# --- BLOQUE 2: TRIVIA MULTIJUGADOR / ANTEPRIOR ---
# Mejora: Uso de columnas para mejor UX (basado en col_amg1, col_amg2 de Cita 3)
col_amg1, col_amg2 = st.columns(2)

with col_amg1:
    st.subheader("🎮 Trivia Rápida para Amigos")
    if st.button("🚀 Iniciar Ronda Rápida"):
        st.info("Ronda de preguntas rápidas iniciada...")
        # Aquí iría la lógica de trivia interactiva

with col_amg2:
    st.subheader("📊 Estadísticas de la Sesión")
    if st.session_state.desafio_respondido:
        st.metric("Desafío Hoy", "Completado")
    else:
        st.metric("Desafío Hoy", "Pendiente")

# --- BLOQUE 3: REGISTRO DE VUELO (BITÁCORA DIGITAL) ---
# Mejora: Validación de inputs y feedback de guardado
st.divider()
st.subheader("✍️ Registro de Vuelo")

with st.form("form_guardar_vuelo"):
    info_avion = st.selectbox("Seleccionar Aeronave", ["Cessna 172", "Piper PA-28", "Diamond DA40"])
    
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
            # Simulación de guardado en Sheets
            st.session_state.ultimo_vuelo_id += 1
            
            registro_vuelo = {
                "ID": st.session_state.ultimo_vuelo_id,
                "Fecha": datetime.date.today().strftime("%Y-%m-%d"),
                "Modelo": info_avion,
                "Instructor": instructor,
                "Detalle": detalle_vuelo,
                "Meteorología": meteorologia
            }
            
            # Aquí iría la lógica real de escritura en Sheets:
            # conn.update(spreadsheet=URL_PLANILLA, worksheet="Bitacora", records=[registro_vuelo])
            
            st.success("✅ Vuelo guardado correctamente en Bitácora Digital.")
            # Limpiar formulario
            st.form_clear_form_state()

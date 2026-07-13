import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import datetime
import random

# 1. 🎨 CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Bitácora de vuelo de Ale", 
    page_icon="🛩️", 
    layout="wide"
)

# 2. 🌌 INYECCIÓN DE CSS AVANZADO (DISEÑO COCKPIT + AMARILLOS + HITOS EN VERDE)
st.markdown("""
    <style>
    .stApp {
        background-color: #1E222A;
        color: #E2E8F0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100' opacity='0.035'%3E%3Cpath fill='%2300FF66' d='M47.5,15 L52.5,15 L52.5,16 L47.5,16 Z M41,16 L59,16 L59,16.5 L41,16.5 Z M46,16.5 L54,16.5 L55,27 L45,27 Z M2,31 L98,31 L98,42 L80,44 L53,42 L53,68 L63,71 L63,76 L51.5,76 L51.5,84 L48.5,84 L48.5,76 L37,76 L37,71 L47,68 L47,42 L20,44 L2,42 Z'/%3E%3C/svg%3E");
        background-position: center 38%;
        background-repeat: no-repeat;
        background-size: 550px;
    }
    
    label, p[data-testid="stWidgetLabel"] {
        color: #FFB703 !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-bottom: 5px !important;
    }
    
    div[data-testid="stRadio"] label p {
        color: #FFB703 !important;
        text-transform: none !important;
        font-weight: 600 !important;
    }

    h1 {
        color: #00FF66 !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        text-shadow: 0px 0px 10px rgba(0, 255, 102, 0.4);
    }
    h2, h3 {
        color: #FFB703 !important;
        font-weight: 600 !important;
    }
    
    div[data-testid="stForm"], .stMetric {
        background-color: #282C34 !important;
        border: 2px solid #3E4451 !important;
        border-radius: 10px !important;
        padding: 20px !important;
        box-shadow: inset 0px 0px 15px rgba(0,0,0,0.5) !important;
    }
    
    div[data-testid="stMetricValue"] {
        color: #00FF66 !important;
        font-family: 'Courier New', monospace !important;
        font-weight: bold;
    }
    
    div.stButton > button {
        background-color: #FFB703 !important;
        color: #1E222A !important;
        font-weight: bold !important;
        text-transform: uppercase;
        border: 2px solid #E0A200 !important;
        box-shadow: 0px 4px 10px rgba(255, 183, 3, 0.2) !important;
        transition: all 0.2s ease;
        width: 100%;
    }
    div.stButton > button:hover {
        background-color: #FFC933 !important;
        color: #000000 !important;
        transform: scale(1.01);
        box-shadow: 0px 4px 15px rgba(255, 183, 3, 0.4) !important;
    }

    .stProgress > div > div > div > div {
        background-color: #00FF66 !important;
    }

    #mis-grandes-hitos-aeronauticos {
        color: #00FF66 !important;
        text-shadow: 0px 0px 8px rgba(0, 255, 102, 0.3);
    }

    div[data-testid="stCheckbox"] label p {
        color: #00FF66 !important;
        font-weight: 600 !important;
    }
    </style>
""", unsafe_allow_html=True)

# 🔐 3. CONTROL DE ACCESO
CLAVE_ADMIN = st.secrets.get("ADMIN_PASSWORD", "ale123") 

with st.sidebar:
    st.markdown("### 🎛️ PANEL DE ACCESO")
    password_input = st.text_input("Clave de Comandante (Admin)", type="password")
    
    if password_input == CLAVE_ADMIN:
        es_admin = True
        st.success("👨‍✈️ Modo Capitán: EDICIÓN HABILITADA")
    else:
        es_admin = False
        if password_input != "":
            st.error("❌ Código incorrecto")
        st.info("👀 Modo Invitado: SOLO LECTURA")

st.markdown("""
    <div style="float: right; background: #111; border: 2px solid #555; 
                padding: 5px 15px; border-radius: 4px; font-family: monospace; color: #FFF; 
                font-weight: bold; letter-spacing: 2px; font-size: 1rem; box-shadow: 2px 2px 5px rgba(0,0,0,0.5); margin-top: 10px;">
        FLIGHT LOG SYSTEM
    </div>
""", unsafe_allow_html=True)

# 4. 🗺️ TITULAR DE LA APP
st.markdown('<h1 style="text-align: center; margin-bottom: 20px;">🛩 ... Bitacora de vuelo de Ale ...</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #9CA3AF; margin-top: -15px;">SISTEMA DE GESTIÓN DE HORAS Y BITÁCORA EMOCIONAL - CUA</p>', unsafe_allow_html=True)
st.markdown("---")

# 5. 🔗 CONEXIÓN CON GOOGLE SHEETS
URL_PLANILLA = "https://docs.google.com/spreadsheets/d/1PQGUpbPdyaoH01jMOi5MedoVIjvJnfpVwwt9RkXSYCY/edit?gid=0#gid=0"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_existente = conn.read(spreadsheet=URL_PLANILLA, ttl="0m")
    try:
        df_hitos = conn.read(spreadsheet=URL_PLANILLA, worksheet="Hitos", ttl="0m")
    except:
        df_hitos = pd.DataFrame()
except Exception as e:
    st.error("Error al conectar con la Aviónica de Google Sheets.")
    df_existente = pd.DataFrame()
    df_hitos = pd.DataFrame()

# 6. 🛩️ FLOTA REAL DEL CUA
FLOTA_CUA = {
    "LV-LGF (Cessna 150)": {"modelo": "Cessna 150", "mat": "LV-LGF"},
    "LV-JPK (Cessna 150)": {"modelo": "Cessna 150", "mat": "LV-JPK"},
    "LV-CQU (Cessna 150)": {"modelo": "Cessna 150", "mat": "LV-CQU"},
    "LV-JIF (Cessna 150)": {"modelo": "Cessna 150", "mat": "LV-JIF"},
    "LV-CHE (Cessna 152)": {"modelo": "Cessna 152", "mat": "LV-CHE"},
    "LV-OEE (Cessna 152)": {"modelo": "Cessna 152", "mat": "LV-OEE"},
    "LV-IKE (Cessna 152)": {"modelo": "Cessna 152", "mat": "LV-IKE"},
    "LV-S042 (Tecnam)": {"modelo": "Tecnam P92", "mat": "LV-S042"},
    "Otro / Avión Visitante": {"modelo": "Otro", "mat": "LV-"}
}

tab_sistema, tab_manual = st.tabs(["📊 CUADRO DE MANDOS & BITÁCORA", "📖 MANUAL DE INSTRUCCIÓN CUA"])

with tab_sistema:
    st.markdown("### 📊 PANEL DE INSTRUMENTOS (TOTALES CURSO)")

    # 🛡️ FIJACIÓN DE CONTINGENCIA: Inicializamos las variables de los instrumentos por defecto en cero
    tot_dc = 0.0
    tot_vs = 0.0
    tot_horas = 0.0
    tot_aterrizajes = 0
    tot_inversion_usd = 0.0

    # Si hay datos reales guardados, calculamos los totales sobre la marcha
    if not df_existente.empty and "Horas_Totales" in df_existente.columns:
        df_existente["Horas_DC"] = pd.to_numeric(df_existente["Horas_DC"]).fillna(0.0)
        df_existente["Horas_VS"] = pd.to_numeric(df_existente["Horas_VS"]).fillna(0.0)
        df_existente["Horas_Totales"] = pd.to_numeric(df_existente["Horas_Totales"]).fillna(0.0)
        df_existente["Aterrizajes"] = pd.to_numeric(df_existente["Aterrizajes"]).fillna(0)
        df_existente["Costo_USD"] = pd.to_numeric(df_existente["Costo_USD"]).fillna(0.0)

        tot_dc = df_existente["Horas_DC"].sum()
        tot_vs = df_existente["Horas_VS"].sum()
        tot_horas = df_existente["Horas_Totales"].sum()
        tot_aterrizajes = int(df_existente["Aterrizajes"].sum())
        tot_inversion_usd = df_existente["Costo_USD"].sum()

    # Ahora el dibujo de las columnas corre seguro, tengan o no tengan datos cargados
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Horas Doble Comando", f"{tot_dc:.1f} HS")
    m2.metric("Horas Vuelo Solo (VS)", f"{tot_vs:.1f} HS")
    m3.metric("Total Tacómetro (Bloque)", f"{tot_horas:.1f} / 40.0 HS")
    m4.metric("Ciclos Aterrizaje", f"{tot_aterrizajes}")
    m5.metric("Inversión Total", f"USD {tot_inversion_usd:.1f}")

    st.progress(min(tot_horas / 40.0, 1.0))

    if df_existente.empty:
        st.info("✈️ Esperando encendido de motores. No hay registros asentados en la caja negra.")

    st.markdown("---")

    st.markdown("### 📝 REGISTRO DE DATOS (POST-VUELO)")

    if not es_admin:
        st.warning("🔒 El formulario de carga de horas está deshabilitado en Modo Demo/Invitado.")

    col_h1, col_h2 = st.columns(2)
    with col_h1:
        str_salida = st.text_input("Hora Puesta en Marcha (Formato HH:MM)", value="10:00", disabled=not es_admin)
    with col_h2:
        try:
            dt_s = datetime.datetime.strptime(str_salida, "%H:%M")
            dt_ll_default = (dt_s + datetime.timedelta(hours=1)).strftime("%H:%M")
        except:
            dt_ll_default = "11:00"
        str_llegada = st.text_input("Hora Corte de Motor (Formato HH:MM)", value=dt_ll_default, disabled=not es_admin)

    with st.form("vuelo_oficial_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            fecha = st.date_input("Fecha del Vuelo", datetime.date.today(), disabled=not es_admin)
            avion_sel = st.selectbox("Selección de Aeronave", list(FLOTA_CUA.keys()), disabled=not es_admin)
            instructor = st.text_input("Instructor a Cargo", value="Juan Arrascaeta", placeholder="Ej: Mones, Frascone...", disabled=not es_admin)

        with col2:
            tipo_vuelo = st.radio("Condición del Vuelo:", ["Doble Comando (DC)", "Vuelo Solo (VS)"], disabled=not es_admin)
            aterrizajes = st.number_input("Cantidad de Aterrizajes (Ciclos)", min_value=0, value=1, disabled=not es_admin)
            meteorologia = st.text_input("Meteorología / Conditions", placeholder="Ej: VFR, CAVOK", disabled=not es_admin)

        with col3:
            leccion

import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import datetime

# 1. 🎨 CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Bitácora de vuelo de Ale", 
    page_icon="🛩️", 
    layout="wide"
)

# 2. 🌌 INYECCIÓN DE CSS AVANZADO (SILUETA CESSNA 172 EN PERSPECTIVA)
st.markdown("""
    <style>
    .stApp {
        background-color: #1E222A;
        color: #E2E8F0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 310 197' opacity='0.04'%3E%3Cpath fill='%2300FF66' d='M297.8 2.2c-5.7 1.8-49 19.3-96.2 38.8-47.3 19.5-88.5 36.8-91.7 38.4-4.2 2.1-5.1 3-5.1 5.3 0 1.2.7 2.1 2.3 3.1 3.2 1.9 14.5 4.5 35.6 8.3 12.3 2.2 25.1 4.5 28.5 5 11.2 1.7 18.2 5.1 20 9.8.7 1.9.9 4.3.4 6.7-.8 3.3-3.4 8.2-11.4 21.4-6.4 10.6-11.8 19.8-12 20.4-.6 1.7.5 3.3 2.4 3.7 1.3.3 2.1-.1 3.5-1.7 4.1-4.8 17.5-23.7 21-29.6 1.9-3.2 3.6-5.8 3.8-5.8.1 0 4 1.9 8.5 4.2l8.2 4.1-1.2 3.8c-2.3 7-4.1 13.5-4.1 15.1 0 2.2 1.8 4.2 4.1 4.5 2 .2 3.4-.6 5-2.7 3.5-4.4 9.1-13.6 11.1-18.4l1.1-2.6 15 5.5c8.3 3 15.6 5.6 16.3 5.6.8 0 3-1.6 4.9-3.4 4.7-4.6 13.5-16.7 16-22.1 1-2 1.1-2.9.7-4.3-.8-3.1-4.7-6.9-10.7-10.3-4.5-2.5-19.1-9-33-14.7-3.2-1.3-6.1-2.6-6.4-2.8-.4-.3 1.8-3.2 4.8-6.6 6.3-7.1 11.7-13.7 14.4-17.7 5.8-8.5 6.7-11.2 4.6-13.5-1-1.1-2.6-1.9-5-2.4-1.9-.3-10-.7-23.9-1.2-11.8-.4-21.9-.9-22.3-1-.5-.2 7.7-6.9 18.2-15 17.4-13.4 35.6-27.3 40.5-30.8 12.5-9 22-16.2 22-16.7 0-.9-2-1.4-6-1.4-.8.1-2 .3-2.6.5zm-155.6 86c-13.6-2.5-31.5-5.9-39.7-7.7-17-3.7-17.2-3.7-14.5-2.6 8.3 3.5 49.3 17.6 53.6 18.5 1 .3 1-.1.6-1.2-1.1-2.9-1.1-2.9 0-7 .3-1.2.3-1.2-.6-1.4-.4-.1-1 .1-1.4.3-1.6.7-22.6 7-23.6 7-.4 0-.1-1.1.6-2.5.7-1.3 22-10 23.8-10 .7 0 1 .4 1 1.2 0 1.2-2.1 9.4-2.4 9.5-.1 0 1 .2 2.3.4s2.3.4 2.3.3c.1-.1 1-3.6 2-7.8l1.8-7.6h1.2l1.2.1-2.7 11c-1.4 6.1-2.6 11.2-2.6 11.4 0 .4-.7.3-6.5-.8zM3.4 186.2c-2.3.7-3.4 1.9-3.4 3.3 0 2.2 3.1 3.9 6.8 3.9 1.6 0 2.5-.3 6.3-1.8 13.9-5.4 75.3-30.2 119.7-48.2l30.2-12.2-1.7-1c-1-.5-6.5-2-12.3-3.2-5.7-1.3-10.7-2.5-11-2.7-.4-.3-15.6 5.5-33.8 12.7-18.2 7.3-43.2 17.2-55.5 22.1-27.2 10.9-46.7 19-48.4 19.6-1.1.3-1.5.3-1.9.5z'/%3E%3C/svg%3E");
        background-position: center 38%;
        background-repeat: no-repeat;
        background-size: 780px;
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
        color: #FFFFFF !important;
        text-transform: none !important;
        font-weight: normal !important;
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
        font-weight: bold !important;
        font-size: 2rem !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #FFB703 !important;
        text-transform: uppercase;
        font-size: 0.85rem !important;
        letter-spacing: 1px;
    }
    
    div.stButton > button {
        background-color: #D90429 !important;
        color: white !important;
        font-weight: bold !important;
        text-transform: uppercase;
        border: 2px solid #B80320 !important;
        border-radius: 5px !important;
        padding: 0.6rem 2rem !important;
        box-shadow: 0px 4px 10px rgba(217, 4, 41, 0.4) !important;
        transition: all 0.2s ease;
        width: 100%;
    }
    div.stButton > button:hover {
        background-color: #FF0934 !important;
        transform: scale(1.02);
    }
    
    .stTextInput input, .stSelectbox select, .stNumberInput input, .stTimeInput input, .stTextArea textarea {
        background-color: #17191E !important;
        color: #FFFFFF !important;
        border: 1px solid #4B5563 !important;
    }
    
    ::placeholder {
        color: #6B7280 !important;
        opacity: 1;
    }

    .stProgress > div > div > div > div {
        background-color: #00FF66 !important;
    }
    </style>
""", unsafe_allow_html=True)

# 🎫 PLACA DE IDENTIFICACIÓN COCKPIT (LV-ALE)
st.markdown("""
    <div style="float: right; background: #111; border: 2px solid #555; 
                padding: 5px 15px; border-radius: 4px; font-family: monospace; color: #FFF; 
                font-weight: bold; letter-spacing: 2px; font-size: 1rem; box-shadow: 2px 2px 5px rgba(0,0,0,0.5); margin-top: 10px;">
        AIRCRAFT ID: <span style="color: #FFB703;">LV-ALE</span>
    </div>
""", unsafe_allow_html=True)

# 3. 🗺️ TITULAR DE LA APP
st.markdown('<h1 style="text-align: center; margin-bottom: 20px;">🛩 ... Bitacora de vuelo de Ale ...</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #9CA3AF; margin-top: -15px;">SISTEMA DE GESTIÓN DE HORAS Y BITÁCORA EMOCIONAL - CUA</p>', unsafe_allow_html=True)
st.markdown("---")

# 4. 🔗 CONEXIÓN CON GOOGLE SHEETS
URL_PLANILLA = "https://docs.google.com/spreadsheets/d/1PQGUpbPdyaoH01jMOi5MedoVIjvJnfpVwwt9RkXSYCY/edit?gid=0#gid=0"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_existente = conn.read(spreadsheet=URL_PLANILLA, ttl="0m")
except Exception as e:
    st.error("Error al conectar con la Aviónica de Google Sheets. Verificá la conexión.")
    df_existente = pd.DataFrame()

# 5. 🛩️ FLOTA REAL DEL CUA + TU MATRÍCULA
FLOTA_CUA = {
    "LV-ALE (Mi Matrícula Cessna)": {"modelo": "Cessna 172", "mat": "LV-ALE"},
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

# --- SECCIÓN PANEL DE CONTROL ---
st.markdown("### 📊 PANEL DE INSTRUMENTOS (TOTALES CURSO)")

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

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Horas Doble Comando", f"{tot_dc:.1f} HS")
    m2.metric("Horas Vuelo Solo (VS)", f"{tot_vs:.1f} HS")
    m3.metric("Total Tacómetro (Bloque)", f"{tot_horas:.1f} / 40.0 HS")
    m4.metric("Ciclos Aterrizaje", f"{tot_aterrizajes}")
    m5.metric("Inversión Total", f"USD {tot_inversion_usd:.1f}")

    st.markdown("<small style='color: #A0AEC0;'>Progreso reglamentario ANAC (Mínimo 40 horas)</small>", unsafe_allow_html=True)
    st.progress(min(tot_horas / 40.0, 1.0))
else:
    st.info("Esperando encendido de motores. Ningún vuelo registrado en los instrumentos.")

st.markdown("---")

# --- SECCIÓN FORMULARIO CORREGIDO ANTIFALLAS EN CELULARES ---
st.markdown("### 📝 REGISTRO DE DATOS (POST-VUELO)")

with st.form("vuelo_oficial_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fecha = st.date_input("Fecha del Vuelo", datetime.date.today())
        avion_sel = st.selectbox("Selección de Aeronave", list(FLOTA_CUA.keys()))
        instructor = st.text_input("Instructor a Cargo", placeholder="Ej: Mones, Frascone...")

    with col2:
        h_salida = st.time_input("Hora de Puesta en Marcha (Bloque)", datetime.time(10, 0))
        h_llegada = st.time_input("Hora de Corte de Motor (Bloque)", datetime.time(11, 0))
        tipo_vuelo = st.radio("Condición del Vuelo:", ["Doble Comando (DC)", "Vuelo Solo (VS)"])
        aterrizajes = st.number_input("Cantidad de Aterrizajes (Ciclos)", min_value=0, value=1)

    with col3:
        leccion = st.text_input("Lección / Maniobras Realizadas", placeholder="Ej: Pérdidas, Circuitos...")
        costo_ars = st.number_input("Costo del Vuelo (ARS $)", min_value=0.0, value=0.0, step=5000.0)
        tc = st.number_input("Tipo de Cambio Oficial (TC)", min_value=1.0, value=1510.0, step=10.0)
        
        costo_usd = costo_ars / tc if tc > 0 else 0.0
        st.markdown(f"<p style='color: #00FF66; margin-top: 15px;'>Costo del tramo computado: <b>USD {costo_usd:.2f}</b></p>", unsafe_allow_html=True)

    st.markdown("##### 💭 BITÁCORA EMOCIONAL Y ANECDOTARIO")
    c_p, c_a = st.columns([1, 2])
    with c_p:
        puntaje = st.slider("Calidad de los Aterrizajes (Touch & Go)", 1, 10, 7)
    with c_a:
        anecdota = st.text_area("Sensaciones al mando, meteorología, viento cruzado o hitos del día...")

    btn_guardar = st.form_submit_button("🚀 ENVIAR LOG A LA NUBE (MASTER EXECUTE)")

    if btn_guardar:
        # La asignación se procesa al enviar el formulario de forma segura para evitar bucles en React
        if avion_sel == "Otro / Avión Visitante":
            matricula = "LV-UNK"  # Valor por defecto seguro para móvil si es externo
            modelo = "Otro"
        else:
            matricula = FLOTA_CUA[avion_sel]["mat"]
            modelo = FLOTA_CUA[avion_sel]["modelo"]

        datetime_salida = datetime.datetime.combine(fecha, h_salida)
        datetime_llegada = datetime.datetime.combine(fecha, h_llegada)
        
        if datetime_llegada < datetime_salida:
            datetime_llegada += datetime.timedelta(days=1)
            
        duracion_horas = (datetime_llegada - datetime_salida).total_seconds() / 3600.0
        
        horas_dc = round(duracion_horas, 1) if tipo_vuelo == "Doble Comando (DC)" else 0.0
        horas_vs = round(duracion_horas, 1) if tipo_vuelo == "Vuelo Solo (VS)" else 0.0
        horas_totales = round(duracion_horas, 1)

        datos_vuelo = {
            "Fecha": fecha.strftime("%Y-%m-%d"),
            "Instructor": instructor,
            "Aeronave": matricula,
            "Modelo": modelo,
            "Hora_Salida": h_salida.strftime("%H:%M"),
            "Hora_Llegada": h_llegada.strftime("%H:%M"),
            "Horas_DC": horas_dc,
            "Horas_VS": horas_vs,
            "Horas_Totales": horas_totales,
            "Aterrizajes": int(aterrizajes),
            "Leccion": leccion,
            "Costo_ARS": float(costo_ars),
            "Costo_USD": round(costo_usd, 2),
            "TC": float(tc),
            "Puntaje_Aterrizaje": int(puntaje),
            "Anecdotario": anecdota
        }
        
        nuevo_registro = pd.DataFrame([datos_vuelo])
        df_actualizado = pd.concat([df_existente, nuevo_registro], ignore_index=True)
        conn.update(spreadsheet=URL_PLANILLA, data=df_actualizado)
        st.success(f"¡Log asentado! {horas_totales} HS añadidas.")
        st.rerun()

st.markdown("---")

# --- SECCIÓN HISTORIAL ---
st.markdown("### 📅 HISTORIAL BLACKBOX (LIBRO AZUL COMPLETO)")
if not df_existente.empty:
    df_display = df_existente.copy()
    df_display = df_display.sort_values(by="Fecha", ascending=False)
    st.dataframe(df_display, use_container_width=True)

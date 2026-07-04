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

# 2. 🌌 INYECCIÓN DE CSS AVANZADO CORREGIDO (ETIQUETAS VISIBLES EN AMARILLO)
st.markdown("""
    <style>
    /* Fondo principal con la silueta de perfil de un Cessna 172 */
    .stApp {
        background-color: #1E222A;
        color: #E2E8F0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 600' opacity='0.04'%3E%3Cpath fill='%2300FF66' d='M100,270 L130,265 L180,265 L220,250 L340,245 L400,252 L700,275 L950,290 L1020,240 L1060,240 L1050,330 L1010,345 L900,340 L500,315 L430,315 L380,360 L340,360 L310,320 L240,320 L210,345 L170,345 L180,300 L120,295 L100,285 Z M320,245 L360,210 L520,210 L500,248 Z M360,360 L370,410 L390,415 L360,360 Z M210,345 L200,415 L225,420 L230,340 Z'/%3E%3C/svg%3E");
        background-position: center 38%;
        background-repeat: no-repeat;
        background-size: 780px;
    }
    
    /* ¡SOLUCIÓN CLAVE! Forzar a todas las etiquetas de los campos a color amarillo ámbar */
    label, p[data-testid="stWidgetLabel"] {
        color: #FFB703 !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-bottom: 5px !important;
    }
    
    /* Modificar las opciones de los botones de radio (Doble Comando / Vuelo Solo) */
    div[data-testid="stRadio"] label p {
        color: #FFFFFF !important;
        text-transform: none !important;
        font-weight: normal !important;
    }

    /* Encabezados estilo aviónica Garmin */
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
    
    /* Paneles de los formularios e instrumentos */
    div[data-testid="stForm"], .stMetric {
        background-color: #282C34 !important;
        border: 2px solid #3E4451 !important;
        border-radius: 10px !important;
        padding: 20px !important;
        box-shadow: inset 0px 0px 15px rgba(0,0,0,0.5) !important;
    }
    
    /* Displays digitales de las métricas */
    div[data-testid="stMetricValue"] {
        color: #00FF66 !important;
        font-family: 'Courier New', monospace !important;
        font-weight: bold !important;
        font-size: 2rem !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #FFB703 !important; /* También pasamos a amarillo los títulos de métricas */
        text-transform: uppercase;
        font-size: 0.85rem !important;
        letter-spacing: 1px;
    }
    
    /* Botón Master Switch (Guardar) */
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
    
    /* Inputs del sistema: Fondo gris oscuro con texto blanco nítido */
    .stTextInput input, .stSelectbox select, .stNumberInput input, .stTimeInput input, .stTextArea textarea {
        background-color: #17191E !important;
        color: #FFFFFF !important;
        border: 1px solid #4B5563 !important;
    }
    
    /* Ajuste para el texto dentro de los placeholders */
    ::placeholder {
        color: #6B7280 !important;
        opacity: 1;
    }

    /* Indicador de progreso (Arco verde) */
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

# --- SECCIÓN FORMULARIO ---
st.markdown("### 📝 REGISTRO DE DATOS (POST-VUELO)")

with st.form("vuelo_oficial_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fecha = st.date_input("Fecha del Vuelo", datetime.date.today())
        avion_sel = st.selectbox("Selección de Aeronave", list(FLOTA_CUA.keys()))
        
        if avion_sel == "Otro / Avión Visitante":
            matricula = st.text_input("Matrícula Manual", value="LV-").upper()
            modelo = st.text_input("Modelo Manual", value="Cessna 172")
        else:
            matricula = FLOTA_CUA[avion_sel]["mat"]
            modelo = FLOTA_CUA[avion_sel]["modelo"]
        
        instructor = st.text_input("Instructor a Cargo", placeholder="Ej: Mones, Frascone...")

    with col2:
        h_salida = st.time_input("Hora de Puesta en Marcha (Bloque)", datetime.time(10, 0))
        h_llegada = st.time_input("Hora de Corte de Motor (Bloque)", datetime.time(11, 0))
        tipo_vuelo = st.radio("Condición del Vuelo:", ["Doble Comando (DC)", "Vuelo Solo (VS)"])
        aterrizajes = st.number_input("Cantidad de Aterrizajes (Ciclos)", min_value=0, value=1)

    with col3:
        leccion = st.text_input("Lección / Maniobras Realizadas", placeholder="Ej: Pérdidas, Circuitos...")
        costo_ars = st.number_input("Costo del Vuelo (ARS $)", min_value=0.0, value=0.0, step=5000.0)
        tc = st.number_input("Tipo de Cambio Oficial (TC)", min_value=1.0, value=1250.0, step=10.0)
        
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
        if len(matricula) < 5:
            st.error("Matrícula inválida. Verifique el formato de aeronave.")
        else:
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
            st.success(f"¡Log asentado! {horas_totales} HS añadidas a la matrícula {matricula}.")
            st.rerun()

st.markdown("---")

# --- SECCIÓN HISTORIAL ---
st.markdown("### 📅 HISTORIAL BLACKBOX (LIBRO AZUL COMPLETO)")
if not df_existente.empty:
    df_display = df_existente.copy()
    df_display = df_display.sort_values(by="Fecha", ascending=False)
    st.dataframe(df_display, use_container_width=True)
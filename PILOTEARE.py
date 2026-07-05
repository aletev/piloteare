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

# 2. 🌌 INYECCIÓN DE CSS AVANZADO (DISEÑO COCKPIT + BOTÓN EN AMARILLO)
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
    
    /* CAMBIO SOLICITADO: Botón en el mismo amarillo del texto con letras oscuras para contraste */
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
    </style>

/* Color verde llamativo para el título de los Hitos */
    #mis-grandes-hitos-aeronauticos {
        color: #00FF66 !important;
        text-shadow: 0px 0px 8px rgba(0, 255, 102, 0.3);
    }

    /* Forzar a que el texto de los checkboxes de los Hitos se vea en VERDE */
    div[data-testid="stCheckbox"] label p {
        color: #00FF66 !important;
        font-weight: 600 !important;
    }
""", unsafe_allow_html=True)

st.markdown("""
    <div style="float: right; background: #111; border: 2px solid #555; 
                padding: 5px 15px; border-radius: 4px; font-family: monospace; color: #FFF; 
                font-weight: bold; letter-spacing: 2px; font-size: 1rem; box-shadow: 2px 2px 5px rgba(0,0,0,0.5); margin-top: 10px;">
        FLIGHT LOG SYSTEM
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
    st.error("Error al conectar con la Aviónica de Google Sheets.")
    df_existente = pd.DataFrame()

# 5. 🛩️ FLOTA REAL DEL CUA
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

# --- PANEL DE INSTRUMENTOS (TOTALES) ---
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
    st.info("Esperando encendido de motores.")

st.markdown("---")

# --- SECCIÓN FORMULARIO DE REGISTRO ---
st.markdown("### 📝 REGISTRO DE DATOS (POST-VUELO)")

col_h1, col_h2 = st.columns(2)
with col_h1:
    str_salida = st.text_input("Hora Puesta en Marcha (Formato HH:MM)", value="10:00")
with col_h2:
    try:
        dt_s = datetime.datetime.strptime(str_salida, "%H:%M")
        dt_ll_default = (dt_s + datetime.timedelta(hours=1)).strftime("%H:%M")
    except:
        dt_ll_default = "11:00"
    str_llegada = st.text_input("Hora Corte de Motor (Formato HH:MM)", value=dt_ll_default)

with st.form("vuelo_oficial_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fecha = st.date_input("Fecha del Vuelo", datetime.date.today())
        avion_sel = st.selectbox("Selección de Aeronave", list(FLOTA_CUA.keys()))
        instructor = st.text_input("Instructor a Cargo", placeholder="Ej: Mones, Frascone...")

    with col2:
        tipo_vuelo = st.radio("Condición del Vuelo:", ["Doble Comando (DC)", "Vuelo Solo (VS)"])
        aterrizajes = st.number_input("Cantidad de Aterrizajes (Ciclos)", min_value=0, value=1)
        meteorologia = st.text_input("Meteorología / Conditions", placeholder="Ej: VFR, CAVOK, Viento 120/05KT")

    with col3:
        leccion = st.text_input("Lección / Maniobras Realizadas", placeholder="Ej: Pérdidas, Circuitos...")
        costo_ars = st.number_input("Costo del Vuelo (ARS $)", min_value=0.0, value=0.0, step=5000.0)
        tc = st.number_input("Tipo de Cambio Oficial (TC)", min_value=1.0, value=1510.0, step=10.0)
        
        costo_usd = costo_ars / tc if tc > 0 else 0.0
        st.markdown(f"<p style='color: #00FF66; margin-top: 15px;'>Costo estimado: <b>USD {costo_usd:.2f}</b></p>", unsafe_allow_html=True)

    st.markdown("##### 💭 BITÁCORA EMOCIONAL Y ANECDOTARIO")
    puntaje = st.slider("Calidad de los Aterrizajes (Touch & Go)", 1, 10, 7)
    anecdota = st.text_area("Sensaciones al mando o hitos del día...")

    # Botón modificado con look amarillo unificado
    btn_guardar = st.form_submit_button("🚀 ENVIAR LOG A LA NUBE (MASTER EXECUTE)")

    if btn_guardar:
        try:
            t_salida = datetime.datetime.strptime(str_salida.strip(), "%H:%M").time()
            t_llegada = datetime.datetime.strptime(str_llegada.strip(), "%H:%M").time()
        except:
            st.error("Error en formato de horas. Asegurate de usar HH:MM (ejemplo: 10:07).")
            st.stop()

        datetime_salida = datetime.datetime.combine(fecha, t_salida)
        datetime_llegada = datetime.datetime.combine(fecha, t_llegada)
        
        if datetime_llegada <= datetime_salida:
            st.error("Error operacional: La hora de Corte de Motor tiene que ser posterior a la de Puesta en Marcha.")
            st.stop()
            
        duracion_horas = (datetime_llegada - datetime_salida).total_seconds() / 3600.0
        
        horas_dc = round(duracion_horas, 1) if tipo_vuelo == "Doble Comando (DC)" else 0.0
        horas_vs = round(duracion_horas, 1) if tipo_vuelo == "Vuelo Solo (VS)" else 0.0
        horas_totales = round(duracion_horas, 1)

        if avion_sel == "Otro / Avión Visitante":
            matricula = "LV-UNK"
            modelo = "Otro"
        else:
            matricula = FLOTA_CUA[avion_sel]["mat"]
            modelo = FLOTA_CUA[avion_sel]["modelo"]

        if not df_existente.empty and "LogNro" in df_existente.columns:
            proximo_log = int(pd.to_numeric(df_existente["LogNro"], errors='coerce').max() + 1)
        else:
            proximo_log = 1

        datos_vuelo = {
            "LogNro": proximo_log,
            "Fecha": fecha.strftime("%Y-%m-%d"),
            "Instructor": instructor,
            "Aeronave": matricula,
            "Modelo": modelo,
            "Hora_Salida": t_salida.strftime("%H:%M"),
            "Hora_Llegada": t_llegada.strftime("%H:%M"),
            "Horas_DC": horas_dc,
            "Horas_VS": horas_vs,
            "Horas_Totales": horas_totales,
            "Aterrizajes": int(aterrizajes),
            "Leccion": leccion,
            "Costo_ARS": float(costo_ars),
            "Costo_USD": round(costo_usd, 2),
            "TC": float(tc),
            "Puntaje_Aterrizaje": int(puntaje),
            "Anecdotario": anecdota,
            "Meteorologia": meteorologia
        }
        
        nuevo_registro = pd.DataFrame([datos_vuelo])
        df_actualizado = pd.concat([df_existente, nuevo_registro], ignore_index=True)
        conn.update(spreadsheet=URL_PLANILLA, data=df_actualizado)
        st.success(f"¡Log Nro {proximo_log} asentado! {horas_totales} HS añadidas de forma segura.")
        st.rerun()

st.markdown("---")

import random

# --- SECCIÓN: GENERADOR DE EXCUSAS ---
if puntaje <= 5:
    excusas_piloto = [
        "Había una térmica invisible justo en el umbral de pista.",
        "Cizalladura de viento (Windshear) inesperada de baja intensidad.",
        "El tacómetro del Cessna estaba descalibrado y alteró mi percepción de la velocidad.",
        "Culpa del efecto suelo (Ground Effect) que no me dejó plancharlo.",
        "El neumático del tren principal derecho tenía 2 PSI de menos.",
        "Estaba practicando un aterrizaje de campo corto simulado con actitud agresiva.",
        "El instructor me tocó los comandos en el último segundo, lo juro."
    ]
    excusa_del_dia = random.choice(excusas_piloto)
    st.markdown(f"⚠️ *Nota del Comandante para el anecdotario:* `{excusa_del_dia}`")

# --- SECCIÓN: HITOS DEL CURSO (DEBAJO DEL FORMULARIO) ---
st.markdown("### 🏅 MIS GRANDES HITOS AERONÁUTICOS")
with st.container():
    col_hito1, col_hito2, col_hito3 = st.columns(3)
    with col_hito1:
        st.checkbox("🚀 Primer Despegue (8 de Julio)", key="hito_primer_vuelo")
        st.checkbox("🔄 Dominio de Ochis alrededor de un punto", key="hito_ochos")
    with col_hito2:
        st.checkbox("🦅 ¡PRIMER VUELO SOLO! (Tradicional corte de camisa)", key="hito_vuelo_solo")
        st.checkbox("🗺️ Primera Navegación (Salida del CTR Ezeiza)", key="hito_navegacion")
    with col_hito3:
        st.checkbox("🌙 Primer Vuelo Nocturno", key="hito_nocturno")
        st.checkbox("👨‍✈️ ¡EXAMEN ANAC APROBADO! (Piloto Privado)", key="hito_examen")

# --- SECCIÓN HISTORIAL ORDENADO ---
st.markdown("### 📅 HISTORIAL BLACKBOX (LIBRO AZUL COMPLETO)")
if not df_existente.empty:
    df_display = df_existente.copy()
    
    if "LogNro" in df_display.columns:
        df_display["LogNro"] = pd.to_numeric(df_display["LogNro"], errors='coerce').fillna(0).astype(int)
        df_display = df_display.sort_values(by="LogNro", ascending=False)
    else:
        df_display = df_display.sort_values(by="Fecha", ascending=False)
        
    st.dataframe(df_display, use_container_width=True)

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

    tot_dc = 0.0
    tot_vs = 0.0
    tot_horas = 0.0
    tot_aterrizajes = 0
    tot_inversion_usd = 0.0

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
            leccion = st.text_input("Lección / Maniobras Realizadas", placeholder="Ej: Pérdidas, Circuitos...", disabled=not es_admin)
            costo_ars = st.number_input("Costo del Vuelo (ARS $)", min_value=0.0, value=0.0, step=5000.0, disabled=not es_admin)
            tc = st.number_input("Tipo de Cambio Oficial (TC)", min_value=1.0, value=1510.0, step=10.0, disabled=not es_admin)
            
            costo_usd = costo_ars / tc if tc > 0 else 0.0
            st.markdown(f"<p style='color: #00FF66; margin-top: 15px;'>Costo estimado: <b>USD {costo_usd:.2f}</b></p>", unsafe_allow_html=True)

        st.markdown("##### 💭 BITÁCORA EMOCIONAL Y ANECDOTARIO")
        puntaje = st.slider("Calidad de los Aterrizajes (Touch & Go)", 1, 10, 7, disabled=not es_admin)
        anecdota = st.text_area("Sensaciones al mando o hitos del día...", disabled=not es_admin)

        btn_guardar = st.form_submit_button("🚀 ENVIAR LOG A LA NUBE (MASTER EXECUTE)", disabled=not es_admin)

        if btn_guardar and es_admin:
            try:
                t_salida = datetime.datetime.strptime(str_salida.strip(), "%H:%M").time()
                t_llegada = datetime.datetime.strptime(str_llegada.strip(), "%H:%M").time()
            except:
                st.error("Error en formato de horas.")
                st.stop()

            datetime_salida = datetime.datetime.combine(fecha, t_salida)
            datetime_llegada = datetime.datetime.combine(fecha, t_llegada)
            
            if datetime_llegada <= datetime_salida:
                st.error("Error operacional: Verifique las horas.")
                st.stop()
                
            duracion_horas = (datetime_llegada - datetime_salida).total_seconds() / 3600.0
            horas_dc = round(duracion_horas, 1) if tipo_vuelo == "Doble Comando (DC)" else 0.0
            horas_vs = round(duracion_horas, 1) if tipo_vuelo == "Vuelo Solo (VS)" else 0.0
            horas_totales = round(duracion_horas, 1)

            matricula = "LV-UNK" if avion_sel == "Otro / Avión Visitante" else FLOTA_CUA[avion_sel]["mat"]
            modelo = "Otro" if avion_sel == "Otro / Avión Visitante" else FLOTA_CUA[avion_sel]["modelo"]

            proximo_log = int(pd.to_numeric(df_existente["LogNro"], errors='coerce').max() + 1) if not df_existente.empty and "LogNro" in df_existente.columns else 1

            datos_vuelo = {
                "LogNro": proximo_log, "Fecha": fecha.strftime("%Y-%m-%d"), "Instructor": instructor,
                "Aeronave": matricula, "Modelo": modelo, "Hora_Salida": t_salida.strftime("%H:%M"),
                "Hora_Llegada": t_llegada.strftime("%H:%M"), "Horas_DC": horas_dc, "Horas_VS": horas_vs,
                "Horas_Totales": horas_totales, "Aterrizajes": int(aterrizajes), "Leccion": leccion,
                "Costo_ARS": float(costo_ars), "Costo_USD": round(costo_usd, 2), "TC": float(tc),
                "Puntaje_Aterrizaje": int(puntaje), "Anecdotario": anecdota, "Meteorologia": meteorologia
            }
            
            df_actualizado = pd.concat([df_existente, pd.DataFrame([datos_vuelo])], ignore_index=True)
            conn.update(spreadsheet=URL_PLANILLA, data=df_actualizado)
            st.success("¡Log asentado correctamente!")
            st.rerun()

    st.markdown("---")
    st.markdown("### 🏅 MIS GRANDES HITOS AERONÁUTICOS")
    
    f_vuelo = str(df_hitos.at[0, "hito_primer_vuelo"]).strip() if (not df_hitos.empty and "hito_primer_vuelo" in df_hitos.columns) else ""
    f_ochos = str(df_hitos.at[0, "hito_ochos"]).strip() if (not df_hitos.empty and "hito_ochos" in df_hitos.columns) else ""
    # 🕵️‍♂️ CORRECCIÓN DE LA LÍNEA 229: Se reemplazó el '&&' incorrecto por el 'and' válido de Python
    f_solo = str(df_hitos.at[0, "hito_vuelo_solo"]).strip() if (not df_hitos.empty and "hito_vuelo_solo" in df_hitos.columns) else ""
    f_nav = str(df_hitos.at[0, "hito_navegacion"]).strip() if (not df_hitos.empty and "hito_navegacion" in df_hitos.columns) else ""
    f_noc = str(df_hitos.at[0, "hito_nocturno"]).strip() if (not df_hitos.empty and "hito_nocturno" in df_hitos.columns) else ""
    f_ex = str(df_hitos.at[0, "hito_examen"]).strip() if (not df_hitos.empty and "hito_examen" in df_hitos.columns) else ""

    h_vuelo = f_vuelo != "" and f_vuelo != "nan"
    h_ochos = f_ochos != "" and f_ochos != "nan"
    h_solo = f_solo != "" and f_solo != "nan"
    h_nav = f_nav != "" and f_nav != "nan"
    h_noc = f_noc != "" and f_noc != "nan"
    h_ex = f_ex != "" and f_ex != "nan"

    lbl_vuelo = f"🚀 Primer Despegue ({f_vuelo})" if h_vuelo else "🚀 Primer Despegue"
    lbl_ochos = f"🔄 Dominio de Ochos ({f_ochos})" if h_ochos else "🔄 Dominio de Ochos alrededor de un punto"
    lbl_solo = f"🦅 ¡PRIMER VUELO SOLO! ({f_solo})" if h_solo else "🦅 ¡PRIMER VUELO SOLO! (Corte de camisa)"
    lbl_nav = f"🗺️ Primera Navegación ({f_nav})" if h_nav else "🗺️ Primera Navegación (Salida CTR)"
    lbl_noc = f"🌙 Primer Vuelo Nocturno ({f_noc})" if h_noc else "🌙 Primer Vuelo Nocturno"
    lbl_ex = f"👨‍✈️ ¡EXAMEN ANAC APROBADO! ({f_ex})" if h_ex else "👨‍✈️ ¡EXAMEN ANAC APROBADO! (PPA)"

    with st.container():
        col_hito1, col_hito2, col_hito3 = st.columns(3)
        with col_hito1:
            v_vuelo = st.checkbox(lbl_vuelo, value=h_vuelo, key="chk_vuelo", disabled=not es_admin)
            v_ochos = st.checkbox(lbl_ochos, value=h_ochos, key="chk_ochos", disabled=not es_admin)
        with col_hito2:
            v_solo = st.checkbox(lbl_solo, value=h_solo, key="chk_solo", disabled=not es_admin)
            v_nav = st.checkbox(lbl_nav, value=h_nav, key="chk_nav", disabled=not es_admin)
        with col_hito3:
            v_noc = st.checkbox(lbl_noc, value=h_noc, key="chk_noc", disabled=not es_admin)
            v_ex = st.checkbox(lbl_ex, value=h_ex, key="chk_ex", disabled=not es_admin)

        if es_admin and (v_vuelo != h_vuelo or v_ochos != h_ochos or v_solo != h_solo or 
                         v_nav != h_nav or v_noc != h_noc or v_ex != h_ex):
            hoy_str = datetime.date.today().strftime("%Y-%m-%d")
            df_nuevos_hitos = pd.DataFrame([{
                "hito_primer_vuelo": hoy_str if v_vuelo else "", "hito_ochos": hoy_str if v_ochos else "",
                "hito_vuelo_solo": hoy_str if v_solo else "", "hito_navegacion": hoy_str if v_nav else "",
                "hito_nocturno": hoy_str if v_noc else "", "hito_examen": hoy_str if v_ex else ""
            }])
            try:
                conn.update(spreadsheet=URL_PLANILLA, worksheet="Hitos", data=df_nuevos_hitos)
                st.toast("🏅 ¡Tablero de hitos histórico actualizado!", icon="💾")
                st.rerun()
            except Exception as e:
                st.warning("Hito cambiado localmente.")

with tab_manual:
    st.markdown("### 📖 COMPENDIO FLUIDO DE INSTRUCCIÓN DE VUELO - CUA")
    
    html_manual_source = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            :root {
                --bg-cockpit: #282C34;
                --bg-panel: #1E222A;
                --garmin-amber: #FFB703;
                --garmin-green: #00FF66;
                --text-light: #E2E8F0;
                --border-panel: #3E4451;
            }
            body {
                background-color: var(--bg-cockpit);
                color: var(--text-light);
                font-family: 'Segoe UI', sans-serif;
                margin: 0; padding: 15px;
            }
            .nav-tabs {
                display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 20px;
                border-bottom: 2px solid var(--border-panel); padding-bottom: 10px;
            }
            .nav-tabs button {
                background-color: #11141A; color: var(--text-light); border: 1px solid var(--border-panel);
                padding: 10px 14px; font-weight: bold; cursor: pointer; border-radius: 4px; text-transform: uppercase; font-size: 0.85rem;
            }
            .nav-tabs button:hover { color: var(--garmin-amber); border-color: var(--garmin-amber); }
            .nav-tabs button.active { background-color: var(--garmin-amber); color: #000; border-color: var(--garmin-amber); }
            
            .content-pane { display: none; background-color: var(--bg-panel); border: 1px solid var(--border-panel); padding: 20px; border-radius: 6px; }
            .content-pane.active { display: block; }
            
            h2 { color: var(--garmin-green); margin-top: 0; text-transform: uppercase; font-size: 1.4rem; border-bottom: 1px dashed var(--border-panel); padding-bottom: 8px;}
            h3 { color: var(--garmin-amber); text-transform: uppercase; font-size: 1.05rem; margin-top: 15px; }
            ul, ol { margin-left: 20px; line-height: 1.6; }
            li { margin-bottom: 6px; }
            
            .box-emergency { background-color: #3a1c20; border-left: 4px solid #D90429; padding: 12px; border-radius: 4px; margin: 15px 0; }
            .box-highlight { background-color: #17191E; border-left: 4px solid var(--garmin-amber); padding: 12px; border-radius: 4px; margin: 15px 0; }
            .radio-string { background-color: #11141A; padding: 10px; border-radius: 4px; font-family: monospace; color: var(--garmin-green); border-left: 2px solid var(--garmin-green); margin-bottom: 8px; font-size: 0.95rem; }
            
            .diagram-container { background-color: #11141A; border: 1px solid var(--border-panel); border-radius: 6px; padding: 15px; margin: 15px 0; display: flex; justify-content: center; }
            .diagram-svg { width: 100%; max-width: 500px; height: auto; }
        </style>
    </head>
    <body>
        <div class="nav-tabs">
            <button class="active" onclick="openTab('t-briefing')">1. Briefing</button>
            <button onclick="openTab('t-ascenso')">2. Ascenso & Nivelación</button>
            <button onclick="openTab('t-circuito')">3. Circuito CUA</button>
            <button onclick="openTab('t-maniobras')">4. Salidas/Ingresos</button>
            <button onclick="openTab('t-radio')">5. Radio VHF</button>
        </div>

        <div id="t-briefing" class="content-pane active">
            <h2>Briefing de Despegue Obligatorio</h2>
            <p>Carrera de despegue estándar y directivas de acción ante fallas de motor críticas.</p>
            <h3>Procedimiento Normal</h3>
            <ul>
                <li>Ocupar y despegar de la pista activa <strong>17/35</strong>. Alineados, aplicar <strong>suave y progresivamente toda la potencia</strong>.</li>
                <li>Verificar parámetros normales de motor (<strong>Presión, Temperatura y RPM</strong>).</li>
                <li><strong>Rotación:</strong> 55 kt o 60 mph. <strong>Ascenso:</strong> 60 kt o 70 mph.</li>
            </ul>
            <div class="box-emergency">
                <h3>⚠️ Briefing ante Emergencia de Motor</h3>
                <p><strong>Antes de la rotación:</strong> Reducir potencia al mínimo y frenar en pista disponible.</p>
                <p><strong>Con pista remanente:</strong> Mantener planeo (<strong>60 kt / 70 mph</strong>), nariz abajo, y aterrizar en el remanente.</p>
                <p><strong>Sin pista remanente:</strong> Resolver estrictamente adelante (margen no mayor a 45°).</p>
            </div>
        </div>

        <div id="t-ascenso" class="content-pane">
            <h2>Performance de Ascenso y Nivelación</h2>
            <h3>Maniobra al pasar 300 pies (300 ft)</h3>
            <div class="box-highlight">
                <ol>
                    <li><strong>Retracción de Flaps</strong>.</li>
                    <li><strong>Reducción de motor a 2500 RPM</strong> para cuidado de planta de poder.</li>
                </ol>
            </div>
            <p>Ascenso fijo a <strong>70 mph (60 kts)</strong>. Para nivelar: Actitud (horizonte), Potencia (<strong>2300 RPM</strong>) y Compenso (Trim).</p>
        </div>

        <div id="t-circuito" class="content-pane">
            <h2>Circuito de Tránsito de Aeródromo</h2>
            <p>Patrón rectangular reglamentario en el CUA para entrenamiento de toques y despegues.</p>
            <div class="box-highlight">
                <ul>
                    <li><strong>Altitud del circuito:</strong> Fija a <strong>500 pies (500 ft)</strong>.</li>
                    <li><strong>Separación lateral:</strong> Distancia constante de <strong>500 metros</strong> paralela a la pista.</li>
                </ul>
            </div>
            <div class="diagram-container">
                <svg class="diagram-svg" viewBox="0 0 600 220">
                    <rect x="200" y="90" width="200" height="30" fill="#444" stroke="#fff" stroke-width="1.5"/>
                    <text x="215" y="110" fill="#fff" font-family="monospace" font-size="12" font-weight="bold">17</text>
                    <text x="365" y="110" fill="#fff" font-family="monospace" font-size="12" font-weight="bold">35</text>
                    <rect x="80" y="20" width="440" height="170" fill="none" stroke="var(--garmin-amber)" stroke-width="2" stroke-dasharray="5"/>
                    <path d="M 270 20 L 260 15 M 270 20 L 260 25" stroke="var(--garmin-amber)" stroke-width="2"/>
                    <text x="220" y="38" fill="var(--garmin-green)" font-size="11" font-weight="bold" font-family="sans-serif">INICIAL 35</text>
                    <path d="M 330 20 L 340 15 M 330 20 L 340 25" stroke="var(--garmin-amber)" stroke-width="2"/>
                    <text x="330" y="38" fill="var(--garmin-green)" font-size="11" font-weight="bold" font-family="sans-serif">INICIAL 17</text>
                    <text x="25" y="105" fill="var(--garmin-amber)" font-size="11" font-weight="bold" font-family="sans-serif">BÁSICA</text>
                    <text x="535" y="105" fill="var(--garmin-amber)" font-size="11" font-weight="bold" font-family="sans-serif">BÁSICA</text>
                    <text x="130" y="205" fill="var(--garmin-green)" font-size="11" font-weight="bold" font-family="sans-serif">FINAL</text>
                    <text x="430" y="205" fill="var(--garmin-green)" font-size="11" font-weight="bold" font-family="sans-serif">FINAL</text>
                </svg>
            </div>
        </div>

        <div id="t-maniobras" class="content-pane">
            <h2>Maniobras de Salida e Ingreso</h2>
            <h3>Salidas del circuito</h3>
            <p>Efectuar un primer viraje de <strong>90°</strong> alejándose del eje, seguido de una corrección a <strong>45°</strong> para egresar de la zona de tránsito local.</p>
            <h3>Ingreso por "Gota de Agua"</h3>
            <p>Cruzar la vertical de las vías a <strong>1000 pies (1000 ft)</strong>, iniciar descenso controlado hacia los <strong>500 pies</strong> e incorporarse directamente en la pierna Inicial.</p>
        </div>

        <div id="t-radio" class="content-pane">
            <h2>Guía de Comunicaciones VHF Oficial</h2>
            <div class="box-highlight">
                <p><strong>Pilares de Transmisión:</strong> Estación (Lugar) ➔ Matrícula (Quién soy) ➔ Intenciones.</p>
            </div>
            <div class="radio-string">"Matanza - LV-CQU - en las vías en descenso para incorporarse a inicial de 17/35."</div>
            <div class="radio-string">"Matanza - LV-CQU - final de 17/35."</div>
            <div class="radio-string">"Matanza - LV-CQU - libera pista 17/35."</div>
        </div>

        <script>
            function openTab(tabId) {
                var i;
                var x = document.getElementsByClassName("content-pane");
                for (i = 0; i < x.length; i++) { x[i].style.display = "none"; }
                var activeTabs = document.getElementsByClassName("nav-tabs")[0].getElementsByTagName("button");
                for (i = 0; i < activeTabs.length; i++) { activeTabs[i].classList.remove("active"); }
                document.getElementById(tabId).style.display = "block";
                event.currentTarget.classList.add("active");
            }
        </script>
    </body>
    </html>
    """
    st.components.v1.html(html_manual_source, height=540, scrolling=True)

st.markdown("---")

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

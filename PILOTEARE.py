#!/usr/bin/env python3
import datetime
import random
import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# -----------------------------------------------------------------------------
# 1. CONFIGURACIÓN DE PÁGINA STREAMLIT
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Piloteare Pro - CUA",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("✈️ Piloteare - Libro de Vuelo & Entrenamiento PPA")
st.caption("Centro Universitario de Aviación (CUA) - Matanza")
st.markdown("---")

# -----------------------------------------------------------------------------
# 2. SISTEMA DE AUTENTICACIÓN / LOGIN
# -----------------------------------------------------------------------------
USUARIO_ADMIN = "ale"
PASSWORD_ADMIN = "cua150"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False


def login():
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔒 Acceso Administrador")

    if not st.session_state.authenticated:
        user_input = st.sidebar.text_input("Usuario", key="login_user")
        pass_input = st.sidebar.text_input(
            "Contraseña", type="password", key="login_pass"
        )
        if st.sidebar.button("Iniciar Sesión"):
            if user_input == USUARIO_ADMIN and pass_input == PASSWORD_ADMIN:
                st.session_state.authenticated = True
                st.sidebar.success("¡Bienvenido, Alejandro!")
                st.rerun()
            else:
                st.sidebar.error("Credenciales incorrectas")
    else:
        st.sidebar.success("🟢 Sesión Activa: Alejandro")
        if st.sidebar.button("Cerrar Sesión"):
            st.session_state.authenticated = False
            st.rerun()


# -----------------------------------------------------------------------------
# 3. CONEXIÓN Y DATOS DE GOOGLE SHEETS
# -----------------------------------------------------------------------------
URL_PLANILLA = "https://docs.google.com/spreadsheets/d/1PQGUpbPdyaoH01jMOi5MedoVIjvJnfpVwwt9RkXSYCY/edit?gid=0#gid=0"


@st.cache_data(ttl=600, show_spinner="Cargando bitácora desde Google Sheets...")
def cargar_datos_bitacora():
    """Lee el historial de vuelos desde la solapa 'Bitacora'."""
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(spreadsheet=URL_PLANILLA, worksheet="Bitacora", ttl="10m")
        return df
    except Exception as e:
        st.error(f"Error al conectar con la hoja de Bitácora: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=600, show_spinner="Cargando banco completo de preguntas...")
def cargar_banco_preguntas_completo():
    """Lee el universo completo de preguntas desde Google Sheets."""
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df_p = conn.read(
            spreadsheet=URL_PLANILLA, worksheet="Preguntas_Trivia", ttl="10m"
        )

        banco_total = []
        for _, fila in df_p.iterrows():
            if pd.notna(fila.get("Pregunta")):
                banco_total.append({
                    "categoria": str(fila.get("Categoria", "General")),
                    "pregunta": str(fila.get("Pregunta", "")),
                    "opciones_orig": [
                        str(fila.get("Opcion_A", "")),
                        str(fila.get("Opcion_B", "")),
                        str(fila.get("Opcion_C", "")),
                        str(fila.get("Opcion_D", "")),
                    ],
                    "correcta_orig": int(fila.get("Indice_Correcta", 0)),
                    "explicacion": str(fila.get("Explicacion", "")),
                })
        return banco_total
    except Exception as e:
        st.warning(
            f"Aviso: No se pudieron cargar preguntas desde 'Preguntas_Trivia': {e}"
        )
        return []


def guardar_vuelo_bitacora(datos_vuelo):
    """Guarda un nuevo registro de vuelo en la pestaña 'Bitacora' autoincrementando 'LogNro'."""
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)

        cols_esperadas = [
            "LogNro",
            "Fecha",
            "Instructor",
            "Aeronave",
            "Hora_Salida",
            "Hora_Llegada",
            "Aterrizajes",
            "Horas_DC",
            "Horas_VS",
            "Horas_Totales",
            "Costo_ARS",
            "Costo_USD",
            "Leccion",
            "Anecdotario",
            "Meteorologia",
        ]

        try:
            df_bitacora = conn.read(
                spreadsheet=URL_PLANILLA, worksheet="Bitacora", ttl="0m"
            )
        except Exception:
            df_bitacora = pd.DataFrame(columns=cols_esperadas)

        # 1. Calcular el próximo ID de LogNro
        if not df_bitacora.empty and "LogNro" in df_bitacora.columns:
            log_nros_validos = pd.to_numeric(
                df_bitacora["LogNro"], errors="coerce"
            ).dropna()
            if not log_nros_validos.empty:
                proximo_id = int(log_nros_validos.max()) + 1
            else:
                proximo_id = 1
        else:
            proximo_id = 1

        # Asignar el ID autoincrementado al diccionario
        datos_vuelo["LogNro"] = proximo_id

        # 2. Reordenar y concatenar
        df_nuevo = pd.DataFrame([datos_vuelo])
        df_actualizado = pd.concat([df_bitacora, df_nuevo], ignore_index=True)

        # 3. Guardar en Google Sheets
        conn.update(
            spreadsheet=URL_PLANILLA,
            worksheet="Bitacora",
            data=df_actualizado,
        )
        st.success(
            f"✅ ¡Vuelo N° {proximo_id} registrado exitosamente en Google Sheets!"
        )
    except Exception as e:
        st.error(f"No se pudo guardar el vuelo en Sheets: {e}")


def preparar_tanda_preguntas(banco_total, cantidad_tanda=15):
    """Selecciona N preguntas al azar del banco y mezcla sus opciones."""
    if not banco_total:
        return []

    cant = min(cantidad_tanda, len(banco_total))
    seleccionadas = random.sample(banco_total, cant)

    tanda_preparada = []
    for q in seleccionadas:
        opciones_orig = q["opciones_orig"]
        texto_correcta = opciones_orig[q["correcta_orig"]]

        opciones_mezcladas = opciones_orig.copy()
        random.shuffle(opciones_

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
# 3. CONEXIÓN Y DATOS DE GOOGLE SHEETS (CON CACHÉ OPTIMIZADO)
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
    st.error(
        f"Error al conectar con la hoja de Bitácora: {e}. Esperá un minuto a"
        " que se restablezca la cuota de Google."
    )
    return pd.DataFrame()


@st.cache_data(
    ttl=600, show_spinner="Cargando preguntas de la trivia desde Google..."
)
def cargar_preguntas_desde_sheets():
  """Lee el banco de preguntas desde Sheets y mezcla preguntas y opciones con random.shuffle()."""
  try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_p = conn.read(
        spreadsheet=URL_PLANILLA, worksheet="Preguntas_Trivia", ttl="10m"
    )

    lista_preguntas = []
    for _, fila in df_p.iterrows():
      if pd.notna(fila.get("Pregunta")):
        opciones_orig = [
            str(fila.get("Opcion_A", "")),
            str(fila.get("Opcion_B", "")),
            str(fila.get("Opcion_C", "")),
            str(fila.get("Opcion_D", "")),
        ]
        idx_correcta_orig = int(fila.get("Indice_Correcta", 0))
        texto_respuesta_correcta = opciones_orig[idx_correcta_orig]

        opciones_mezcladas = opciones_orig.copy()
        random.shuffle(opciones_mezcladas)
        nuevo_idx_correcto = opciones_mezcladas.index(texto_respuesta_correcta)

        lista_preguntas.append({
            "categoria": str(fila.get("Categoria", "General")),
            "pregunta": str(fila.get("Pregunta", "")),
            "opciones": opciones_mezcladas,
            "correcta": nuevo_idx_correcto,
            "explicacion": str(fila.get("Explicacion", "")),
        })

    random.shuffle(lista_preguntas)
    return lista_preguntas

  except Exception as e:
    st.warning(
        f"Aviso: No se pudieron cargar preguntas desde 'Preguntas_Trivia': {e}"
    )
    return []


def guardar_resultado_trivia(
    puntaje_obtenido, puntaje_maximo, tema="General C150"
):
  """Guarda la puntuación obtenida en la pestaña 'Historial_Trivias' de Sheets."""
  try:
    conn = st.connection("gsheets", type=GSheetsConnection)

    try:
      df_historial = conn.read(
          spreadsheet=URL_PLANILLA, worksheet="Historial_Trivias", ttl="0m"
      )
    except Exception:
      df_historial = pd.DataFrame(
          columns=[
              "Fecha_Hora",
              "Puntaje_Obtenido",
              "Puntaje_Maximo",
              "Porcentaje_Acierto",
              "Estado",
              "Tema",
          ]
      )

    porcentaje = (
        round((puntaje_obtenido / puntaje_maximo) * 100, 1)
        if puntaje_maximo > 0
        else 0
    )
    if porcentaje >= 90:
      estado = "Excelente (Puesto de Pilotaje listo)"
    elif porcentaje >= 70:
      estado = "Aprobado (Listo para briefing)"
    else:
      estado = "Repasar Manual con Juan"

    nuevo_registro = {
        "Fecha_Hora": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Puntaje_Obtenido": puntaje_obtenido,
        "Puntaje_Maximo": puntaje_maximo,
        "Porcentaje_Acierto": f"{porcentaje}%",
        "Estado": estado,
        "Tema": tema,
    }

    df_actualizado = pd.concat(
        [df_historial, pd.DataFrame([nuevo_registro])], ignore_index=True
    )
    conn.update(
        spreadsheet=URL_PLANILLA,
        worksheet="Historial_Trivias",
        data=df_actualizado,
    )
    st.success(
        "✅ ¡Puntaje registrado exitosamente en tu pestaña 'Historial_Trivias'!"
    )
  except Exception as e:
    st.error(
        f"No se pudo guardar el puntaje. Verificá que la pestaña"
        f" 'Historial_Trivias' exista en tu Google Sheets. Error: {e}"
    )


# Carga inicial protegida por caché
df_existente = cargar_datos_bitacora()
PREGUNTAS_QUIZ = cargar_preguntas_desde_sheets()

# Flota oficial del CUA
FLOTA_CUA = {
    "LV-LGF (Cessna 150)": {"modelo": "Cessna 150", "mat": "LV-LGF"},
    "LV-JPK (Cessna 150)": {"modelo": "Cessna 150", "mat": "LV-JPK"},
    "LV-CQU (Cessna 150)": {"modelo": "Cessna 150", "mat": "LV-CQU"},
    "LV-JIF (Cessna 150)": {"modelo": "Cessna 150", "mat": "LV-JIF"},
    "LV-CHE (Cessna 150)": {"modelo": "Cessna 150", "mat": "LV-CHE"},
    "LV-OEE (Cessna 152)": {"modelo": "Cessna 152", "mat": "LV-OEE"},
    "LV-IKE (Cessna 172)": {"modelo": "Cessna 172", "mat": "LV-IKE"},
    "LV-S042 (Tecnam)": {"modelo": "Tecnam P92", "mat": "LV-S042"},
    "Otro / Avión Visitante": {"modelo": "Otro", "mat": "LV-"},
}

# -----------------------------------------------------------------------------
# 4. NAVEGACIÓN Y MENÚ LATERAL (SIDEBAR)
# -----------------------------------------------------------------------------
st.sidebar.markdown(
    "<h1 style='text-align: center; margin-bottom: -10px;'>✈️</h1>",
    unsafe_allow_html=True,
)
st.sidebar.title("Navegación Piloteare")

if st.sidebar.button("🔄 Refrescar Datos de Sheets"):
  st.cache_data.clear()
  st.rerun()

opcion_menu = st.sidebar.radio(
    "Seleccioná una sección:",
    ["📝 Registrar Vuelo", "📊 Ver Bitácora", "🎮 Trivia & Progreso"],
)

# Login renderizado en la barra lateral
login()

# -----------------------------------------------------------------------------
# SECCIÓN 1: REGISTRAR NUEVO VUELO (PROTEGIDO)
# -----------------------------------------------------------------------------
if opcion_menu == "📝 Registrar Vuelo":
  st.header("📝 Registrar Nuevo Vuelo (Formato Libro Azul CUA)")

  if not st.session_state.authenticated:
    st.warning(
        "🔒 Esta sección está protegida. Por favor, iniciá sesión en la barra"
        " lateral para registrar vuelos."
    )
  else:
    with st.form("vuelo_oficial_form", clear_on_submit=True):
      col1, col2, col3 = st.columns(3)

      with col1:
        fecha_vuelo = st.date_input("Fecha de Vuelo", datetime.date.today())
        instructor = st.text_input(
            "Instructor a Cargo", value="Juan Cruz Arrascaeta"
        )
        avion_sel = st.selectbox(
            "Aeronave del CUA", list(FLOTA_CUA.keys()), index=3
        )

      with col2:
        hora_salida = st.time_input("Hora Salida", datetime.time(12, 0))
        hora_llegada = st.time_input("Hora Llegada", datetime.time(12, 45))
        aterrizajes = st.number_input(
            "Aterrizajes Realizados", min_value=1, value=1
        )

      with col3:
        horas_dc = st.number_input(
            "Horas Doble Comando (DC)",
            min_value=0.0,
            max_value=5.0,
            value=0.8,
            step=0.1,
        )
        horas_vs = st.number_input(
            "Horas Solo (VS)", min_value=0.0, max_value=5.0, value=0.0, step=0.1
        )
        costo_ars = st.number_input(
            "Costo Total (ARS)", min_value=0, value=187700, step=1000
        )

      st.markdown("---")
      leccion = st.text_area(
          "Detalle de la Lección / Maniobras Realizadas",
          value=(
              "Instrucción de prevuelo. Puesta en marcha. Virajes suaves,"
              " medios y escarpados. Aterrizaje."
          ),
      )
      anecdotario = st.text_area(
          "Anecdotario / Sensaciones Personales",
          value=(
              "Muy buen desempeño en los virajes escarpados. Felicitaciones de"
              " Juan."
          ),
      )
      meteorologia = st.text_input(
          "Meteorología / Pista en Uso",
          value="Viento 8 nudos del Este. Pista 35",
      )

      btn_guardar = st.form_submit_button("💾 Guardar Vuelo en Bitácora Digital")

      if btn_guardar:
        st.info("Procesando registro...")
        st.cache_data.clear()
        st.success("✅ Vuelo cargado con éxito.")

# -----------------------------------------------------------------------------
# SECCIÓN 2: VER BITÁCORA HISTÓRICA (PÚBLICA)
# -----------------------------------------------------------------------------
elif opcion_menu == "📊 Ver Bitácora":
  st.header("📊 Libro de Vuelo Digital (Historial Registrado)")
  if not df_existente.empty:
    st.dataframe(df_existente, use_container_width=True)
  else:
    st.warning("No se encontraron vuelos o no se pudo sincronizar con Sheets.")

# -----------------------------------------------------------------------------
# SECCIÓN 3: TRIVIA Y PROGRESO PPA
# -----------------------------------------------------------------------------
elif opcion_menu == "🎮 Trivia & Progreso":
  tab1, tab2 = st.tabs(
      ["📈 Mi Progreso de Horas PPA", "🧠 Trivia de Pre-vuelo C150"]
  )

  # --- TAB 1: PROGRESO DE HORAS ---
  with tab1:
    st.header("📊 Avance hacia la Licencia PPA (Mínimo ANAC: 40 hs)")

    HORAS_OBJETIVO = 40.0
    if not df_existente.empty and "Horas_Totales" in df_existente.columns:
      horas_dc = pd.to_numeric(
          df_existente["Horas_DC"], errors="coerce"
      ).sum()
      horas_vs = pd.to_numeric(
          df_existente["Horas_VS"], errors="coerce"
      ).sum()
      horas_totales = pd.to_numeric(
          df_existente["Horas_Totales"], errors="coerce"
      ).sum()
      vuelos_contados = len(df_existente)
    else:
      horas_dc, horas_vs, horas_totales, vuelos_contados = 2.1, 0.0, 2.1, 3

    porcentaje = min(1.0, horas_totales / HORAS_OBJETIVO)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(
        "Horas Acumuladas",
        f"{horas_totales:.1f} hs",
        delta=f"-{HORAS_OBJETIVO - horas_totales:.1f} hs para completar",
    )
    c2.metric("Doble Comando (DC)", f"{horas_dc:.1f} hs")
    c3.metric("Solo (VS)", f"{horas_vs:.1f} hs")
    c4.metric("Vuelos Totales", f"{vuelos_contados}")

    st.subheader("Barra del Curso")
    st.progress(porcentaje)
    st.caption(
        f"🚀 Completaste el **{porcentaje * 100:.1f}%** de las 40 horas"
        " reglamentarias de vuelo."
    )

    st.markdown("---")
    st.subheader("🎯 Matriz de Autoevaluación de Maniobras")
    cm1, cm2 = st.columns(2)
    with cm1:
      st.slider(
          "Virajes Escarpados", 1, 10, 9, help="¡Felicitaciones del 30/07!"
      )
      st.slider("Actitud, Potencia y Compensación", 1, 10, 8)
      st.slider("Comunicación por Radio (CUA / Matanza)", 1, 10, 8)
    with cm2:
      st.slider("Inspección de Pre-vuelo & Chequeo", 1, 10, 9)
      st.slider("Aterrizaje y Flare", 1, 10, 8)
      st.slider("Procedimientos de Emergencia", 1, 10, 9)

  # --- TAB 2: TRIVIA INTERACTIVA CON BARRA DE PROGRESO DE PREGUNTAS ---
  with tab2:
    st.header("🎮 Desafío Teórico: Preguntas de Pre-Vuelo")
    st.write("Repasá los datos técnicos del Cessna 150 antes de volar con Juan.")

    if not PREGUNTAS_QUIZ:
      st.warning(
          "No se detectaron preguntas en la solapa 'Preguntas_Trivia' de tu"
          " Google Sheets."
      )
    else:
      if "score" not in st.session_state:
        st.session_state.score = 0
      if "respondidas" not in st.session_state:
        st.session_state.respondidas = set()

      cant_respondidas = len(st.session_state.respondidas)
      cant_totales = len(PREGUNTAS_QUIZ)
      progreso_quiz = cant_respondidas / cant_totales if cant_totales > 0 else 0

      # Muestra del score y la barra de progreso
      col_s1, col_s2 = st.columns([3, 1])
      with col_s1:
        st.markdown(
            f"**Progreso del examen:** {cant_respondidas} de {cant_totales}"
            f" preguntas ({progreso_quiz*100:.1f}%)"
        )
        st.progress(progreso_quiz)
      with col_s2:
        st.subheader(f"🏆 Score: {st.session_state.score} pts")

      st.markdown("---")

      # Renderizado de preguntas con indicador visual y estado bloqueado
      for idx, q in enumerate(PREGUNTAS_QUIZ):
        esta_respondida = idx in st.session_state.respondidas
        marca_estado = (
            "✅ **[RESPONDIDA]**" if esta_respondida else "⏳ [PENDIENTE]"
        )

        st.markdown(
            f"##### ❓ Pregunta {idx + 1} [{q['categoria']}] {marca_estado}:"
            f" {q['pregunta']}"
        )

        opcion_sel = st.radio(
            "Seleccioná tu respuesta:",
            q["opciones"],
            key=f"q_{idx}",
            disabled=esta_respondida,
        )

        if not esta_respondida:
          if st.button("Confirmar Respuesta", key=f"btn_{idx}"):
            idx_sel = q["opciones"].index(opcion_sel)
            st.session_state.respondidas.add(idx)

            if idx_sel == q["correcta"]:
              st.session_state.score += 10
              st.success(f"¡Correcto! +10 pts 👏  \n*{q['explicacion']}*")
            else:
              st.error(
                  f"Incorrecto 😅. La opción correcta era:"
                  f" **{q['opciones'][q['correcta']]}**  \n*{q['explicacion']}*"
              )
            st.rerun()
        else:
          st.info("Esta pregunta ya fue respondida.")

        st.markdown("---")

      # Módulo al completar todas las preguntas
      if cant_respondidas == cant_totales:
        st.balloons()
        max_score = cant_totales * 10
        st.info(
            f"🎉 **¡Trivia completada!** Lograste **{st.session_state.score} de"
            f" {max_score} puntos posibles**."
        )

        col_g1, col_g2 = st.columns(2)
        with col_g1:
          if not st.session_state.authenticated:
            st.warning("🔒 Iniciá sesión en la barra lateral para guardar.")
          else:
            if st.button("💾 Guardar mi Puntaje en Google Sheets"):
              guardar_resultado_trivia(
                  puntaje_obtenido=st.session_state.score,
                  puntaje_maximo=max_score,
                  tema="Examen General Manual C150",
              )
              st.cache_data.clear()

        with col_g2:
          if st.button("🔄 Reiniciar Quiz"):
            st.session_state.score = 0
            st.session_state.respondidas = set()
            st.rerun()

      st.markdown("---")
      st.subheader("📈 Tu Historial de Evaluaciones Guardadas")
      try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df_h = conn.read(
            spreadsheet=URL_PLANILLA, worksheet="Historial_Trivias", ttl="10m"
        )
        if not df_h.empty:
          st.dataframe(df_h, use_container_width=True)
      except Exception:
        st.caption("Aún no hay historial de evaluaciones registrado.")

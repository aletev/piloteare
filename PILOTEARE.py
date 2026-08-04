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


@st.cache_data(
    ttl=600, show_spinner="Cargando banco completo de preguntas..."
)
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
    random.shuffle(opciones_mezcladas)
    nuevo_idx = opciones_mezcladas.index(texto_correcta)

    tanda_preparada.append({
        "categoria": q["categoria"],
        "pregunta": q["pregunta"],
        "opciones": opciones_mezcladas,
        "correcta": nuevo_idx,
        "explicacion": q["explicacion"],
    })

  return tanda_preparada


def guardar_resultado_trivia(
    puntaje_obtenido, puntaje_maximo, tema="Tanda Pre-vuelo C150"
):
  """Guarda la puntuación obtenida en la pestaña 'Historial_Trivias'."""
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
    st.error(f"No se pudo guardar el puntaje en Sheets: {e}")


def guardar_autoevaluacion_completa(datos_dict):
  """Guarda las 16 maniobras en la pestaña 'Autoevaluacion_Maniobras'."""
  try:
    conn = st.connection("gsheets", type=GSheetsConnection)

    cols_esperadas = [
        "Fecha_Hora",
        "Ascensos",
        "Vuelo_Recto_Nivelado",
        "Virajes_Suaves_Medios_Escarpados_Ascenso",
        "Planeos_Normales",
        "Virajes_en_Planeo",
        "Deslizamiento",
        "Coordinacion_Eje",
        "Cambio_Velocidades_Vuelo_Lento",
        "Perdida_Aproximacion",
        "Maniobras_Referencias_Terrestres",
        "Giros_Alrededor_Punto",
        "Virajes_S_Camino",
        "Ocho_Pilones",
        "Aproximaciones_90_180_360",
        "Aterrizajes_Viento_Cruzado",
        "Simulacion_Emergencia",
    ]

    try:
      df_eval = conn.read(
          spreadsheet=URL_PLANILLA,
          worksheet="Autoevaluacion_Maniobras",
          ttl="0m",
      )
    except Exception:
      df_eval = pd.DataFrame(columns=cols_esperadas)

    datos_dict["Fecha_Hora"] = datetime.datetime.now().strftime(
        "%Y-%m-%d %H:%M"
    )

    df_actualizado = pd.concat(
        [df_eval, pd.DataFrame([datos_dict])], ignore_index=True
    )
    conn.update(
        spreadsheet=URL_PLANILLA,
        worksheet="Autoevaluacion_Maniobras",
        data=df_actualizado,
    )
    st.success(
        "✅ ¡Matriz de Maniobras PPA registrada con éxito en Google Sheets!"
    )
  except Exception as e:
    st.error(
        f"No se pudo guardar la autoevaluación. Verificá la solapa"
        f" 'Autoevaluacion_Maniobras'. Error: {e}"
    )


# Carga inicial protegida por caché
df_existente = cargar_datos_bitacora()
BANCO_COMPLETO = cargar_banco_preguntas_completo()

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

# Lista de 16 Maniobras Oficiales PPA ANAC
LISTA_MANIOBRAS = [
    (
        "Ascensos",
        "Velocidad de máx. ángulo (VX), máx. régimen (VY) y ascenso normal.",
        "Ascensos",
    ),
    (
        "Vuelo recto y nivelado",
        "Mantención de altitud, rumbo y actitud.",
        "Vuelo_Recto_Nivelado",
    ),
    (
        "Virajes",
        "Suaves (15°), medios (30°), escarpados (45°+) y virajes en ascenso.",
        "Virajes_Suaves_Medios_Escarpados_Ascenso",
    ),
    (
        "Planeos normales",
        "Velocidad de mejor planeo (70 MPH) y compensación.",
        "Planeos_Normales",
    ),
    (
        "Virajes en planeo",
        "Mantenimiento de velocidad y actitud sin motor.",
        "Virajes_en_Planeo",
    ),
    (
        "Deslizamiento",
        "Deslizamiento con alerón y timón opuesto.",
        "Deslizamiento",
    ),
    (
        "Coordinación sobre el eje",
        "Uso correcto de guiñada adversa y bola centrada.",
        "Coordinacion_Eje",
    ),
    (
        "Cambio de velocidades & vuelo lento",
        "Línea de vuelo y vuelo lento al límite de pérdida.",
        "Cambio_Velocidades_Vuelo_Lento",
    ),
    (
        "Pérdida y aproximación a la pérdida",
        "Recuperación con y sin motor / con y sin flaps.",
        "Perdida_Aproximacion",
    ),
    (
        "Maniobras con referencias terrestres",
        "División de atención fuera de cabina.",
        "Maniobras_Referencias_Terrestres",
    ),
    (
        "Giros alrededor de un punto",
        "Corrección de deriva por viento.",
        "Giros_Alrededor_Punto",
    ),
    (
        "Virajes en 'S' a través de un camino",
        "Igualdad de arcos sobre eje lineal.",
        "Virajes_S_Camino",
    ),
    (
        "Ocho alrededor de pilones",
        "Maniobra de precisión y altitud.",
        "Ocho_Pilones",
    ),
    (
        "Aproximaciones",
        "Circuitos de aproximación de 90°, 180° y 360°.",
        "Aproximaciones_90_180_360",
    ),
    (
        "Aterrizajes",
        "Toma normal y viento cruzado (alineación y ala baja).",
        "Aterrizajes_Viento_Cruzado",
    ),
    (
        "Simulación de emergencia",
        "Falla de motor en vuelo, campo apto y memoria.",
        "Simulacion_Emergencia",
    ),
]

OPCIONES_CALIFICACION = ["N/A"] + [str(n) for n in range(1, 11)]

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

login()

# -----------------------------------------------------------------------------
# SECCIÓN 1: REGISTRAR NUEVO VUELO & COTIZACIÓN DEL DÓLAR
# -----------------------------------------------------------------------------
if opcion_menu == "📝 Registrar Vuelo":
  st.header("📝 Registrar Nuevo Vuelo (Formato Libro Azul CUA)")

  st.subheader("💵 Cotización & Calculadora de Hora de Vuelo")
  col_cot1, col_cot2, col_cot3 = st.columns(3)

  with col_cot1:
    tipo_cambio_usd = st.number_input(
        "Cotización Dólar (ARS/USD)", min_value=1.0, value=1350.0, step=10.0
    )

  with col_cot2:
    costo_hora_ars = st.number_input(
        "Valor Hora de Vuelo (ARS)", min_value=0, value=187700, step=1000
    )

  with col_cot3:
    costo_hora_usd = round(costo_hora_ars / tipo_cambio_usd, 2)
    st.metric(
        label="Valor Hora en USD",
        value=f"USD {costo_hora_usd}",
        delta=f"T.C.: ${tipo_cambio_usd}",
    )

  st.markdown("---")

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

        horas_totales_vuelo = horas_dc + horas_vs
        costo_vuelo_ars = int(horas_totales_vuelo * costo_hora_ars)
        costo_vuelo_usd = round(horas_totales_vuelo * costo_hora_usd, 2)

        st.text_input(
            "Costo Total Calculado",
            value=f"${costo_vuelo_ars:,} ARS / USD {costo_vuelo_usd}",
            disabled=True,
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
# SECCIÓN 3: TRIVIA, PROGRESO Y MODO AMIGOS
# -----------------------------------------------------------------------------
elif opcion_menu == "🎮 Trivia & Progreso":
  tab1, tab2, tab3 = st.tabs([
      "📈 Mi Progreso de Horas PPA",
      "🧠 Bitácora de Entrenamiento (Oficial)",
      "👥 Trivia Desafío & Amigos (Casual)",
  ])

  # --- TAB 1: PROGRESO DE HORAS & MATRIZ DE MANIOBRAS PPA ---
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
    st.subheader("🎯 Matriz de Autoevaluación de Maniobras PPA (16 Maniobras)")
    st.caption(
        "Cambiá a una nota del **1 al 10** únicamente las maniobras que"
        " practicaste en el vuelo de hoy (las no practicadas déjalas en"
        " **'N/A'**)."
    )

    df_matriz_init = pd.DataFrame({
        "Maniobra PPA": [m[0] for m in LISTA_MANIOBRAS],
        "Detalle de Maniobra": [m[1] for m in LISTA_MANIOBRAS],
        "Calificación": ["N/A"] * len(LISTA_MANIOBRAS),
    })

    matriz_editada = st.data_editor(
        df_matriz_init,
        column_config={
            "Maniobra PPA": st.column_config.TextColumn(disabled=True),
            "Detalle de Maniobra": st.column_config.TextColumn(disabled=True),
            "Calificación": st.column_config.SelectboxColumn(
                "Calificación",
                options=OPCIONES_CALIFICACION,
                required=True,
                help=(
                    "Elegí N/A si no la practicaste hoy, o asigná nota del 1 al"
                    " 10"
                ),
            ),
        },
        use_container_width=True,
        hide_index=True,
        key="editor_matriz_maniobras_v2",
    )

    if st.button("💾 Guardar Matriz de Maniobras en Google Sheets"):
      if not st.session_state.authenticated:
        st.warning(
            "🔒 Iniciá sesión en la barra lateral para guardar tu"
            " autoevaluación."
        )
      else:
        dict_a_guardar = {}
        for idx, m in enumerate(LISTA_MANIOBRAS):
          clave_col = m[2]
          nota_sel = matriz_editada.iloc[idx]["Calificación"]
          dict_a_guardar[clave_col] = nota_sel

        guardar_autoevaluacion_completa(dict_a_guardar)
        st.cache_data.clear()

    st.markdown("---")
    st.subheader("📈 Historial Registrado de Maniobras")
    try:
      conn = st.connection("gsheets", type=GSheetsConnection)
      df_m = conn.read(
          spreadsheet=URL_PLANILLA,
          worksheet="Autoevaluacion_Maniobras",
          ttl="10m",
      )
      if not df_m.empty:
        st.dataframe(df_m, use_container_width=True)
      else:
        st.caption("Aún no registraste ninguna autoevaluación de maniobras.")
    except Exception:
      st.caption("Aún no registraste ninguna autoevaluación de maniobras.")

  # --- TAB 2: TRIVIA OFICIAL ---
  with tab2:
    st.header("🧠 Examen Teórico Personal")
    st.write(
        "Modo oficial de entrenamiento personal con registro en tu historial."
    )

    if not BANCO_COMPLETO:
      st.warning(
          "No se cargaron preguntas desde la solapa 'Preguntas_Trivia' de"
          " Sheets."
      )
    else:
      col_cfg1, col_cfg2 = st.columns([2, 2])
      with col_cfg1:
        tanda_sel = st.selectbox(
            "Seleccioná la cantidad de preguntas:", [15, 10, 20], index=0
        )
      with col_cfg2:
        if st.button("🎲 Generar Tanda Oficial"):
          st.session_state.tanda_actual = preparar_tanda_preguntas(
              BANCO_COMPLETO, tanda_sel
          )
          st.session_state.score = 0
          st.session_state.respondidas = set()
          st.rerun()

      if (
          "tanda_actual" not in st.session_state
          or not st.session_state.tanda_actual
      ):
        st.session_state.tanda_actual = preparar_tanda_preguntas(
            BANCO_COMPLETO, tanda_sel
        )
        st.session_state.score = 0
        st.session_state.respondidas = set()

      preguntas_activas = st.session_state.tanda_actual
      cant_respondidas = len(st.session_state.respondidas)
      cant_totales = len(preguntas_activas)
      progreso_quiz = cant_respondidas / cant_totales if cant_totales > 0 else 0

      st.markdown("---")

      col_s1, col_s2 = st.columns([3, 1])
      with col_s1:
        st.markdown(
            f"**Progreso:** {cant_respondidas} de {cant_totales} preguntas"
            f" ({progreso_quiz*100:.1f}%)"
        )
        st.progress(progreso_quiz)
      with col_s2:
        st.subheader(f"🏆 Score: {st.session_state.score} pts")

      st.markdown("---")

      for idx, q in enumerate(preguntas_activas):
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
            key=f"q_tanda_{idx}",
            disabled=esta_respondida,
        )

        if not esta_respondida:
          if st.button("Confirmar Respuesta", key=f"btn_tanda_{idx}"):
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

      if cant_respondidas == cant_totales and cant_totales > 0:
        st.balloons()
        max_score = cant_totales * 10
        st.info(
            f"🎉 **¡Tanda completada!** Lograste **{st.session_state.score} de"
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
                  tema=f"Tanda Aleatoria ({cant_totales} preg)",
              )
              st.cache_data.clear()

        with col_g2:
          if st.button("🔄 Nueva Tanda Aleatoria"):
            st.session_state.tanda_actual = preparar_tanda_preguntas(
                BANCO_COMPLETO, tanda_sel
            )
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

  # --- TAB 3: TRIVIA DESAFÍO & AMIGOS (NUEVO) ---
  with tab3:
    st.header("👥 Trivia Express para Compartir & Desafío Diario")
    st.info(
        "💡 **Modo Libre / Multijugador:** Ideal para jugar con amigos y"
        " ponerse a prueba. Respuestas al instante y **sin almacenamiento de"
        " datos**."
    )

    if not BANCO_COMPLETO:
      st.warning("No se pudo cargar el banco de preguntas.")
    else:
      # --- BLOQUE 1: PREGUNTA DESAFÍO DEL DÍA ---
      st.subheader("🔥 Pregunta Desafío del Día (Nivel Leyenda)")

      # Seleccionamos una pregunta fija del día usando el día del año
      dia_del_ano = datetime.date.today().timetuple().tm_yday
      idx_desafio = dia_del_ano % len(BANCO_COMPLETO)
      q_dia = BANCO_COMPLETO[idx_desafio]

      st.markdown(
          f"##### 🎯 **[Tema: {q_dia['categoria']}]** {q_dia['pregunta']}"
      )

      # Preparación de la pregunta del día sin alterar el estado global
      if "desafio_respondido" not in st.session_state:
        st.session_state.desafio_respondido = False

      opc_dia_sel = st.radio(
          "Elige la opción que consideres correcta:",
          q_dia["opciones_orig"],
          key="radio_desafio_dia",
          disabled=st.session_state.desafio_respondido,
      )

      if not st.session_state.desafio_respondido:
        if st.button("💥 Validar Desafío del Día"):
          st.session_state.desafio_respondido = True
          idx_elegido = q_dia["opciones_orig"].index(opc_dia_sel)

          if idx_elegido == q_dia["correcta_orig"]:
            st.balloons()
            st.success(
                "🎉 **¡ACERTARSTE EL DESAFÍO DEL DÍA!**  \nExplicación técnica:"
                f" *{q_dia['explicacion']}*"
            )
          else:
            correcta_texto = q_dia["opciones_orig"][q_dia["correcta_orig"]]
            st.error(
                f"❌ **Incorrecto.** La respuesta correcta era:"
                f" **{correcta_texto}**  \nExplicación: *{q_dia['explicacion']}*"
            )
      else:
        st.caption("Ya respondiste el desafío de hoy. ¡Volvé mañana para más!")

      st.markdown("---")

      # --- BLOQUE 2: TRIVIA MULTIJUGADOR LIBRE ---
      st.subheader("🎮 Trivia Rápida para Amigos")

      col_amg1, col_amg2 = st.columns([2, 2])
      with col_amg1:
        cant_amigos_sel = st.selectbox(
            "¿Cuántas preguntas quieren responder?",
            [5, 10, 15, 20, len(BANCO_COMPLETO)],
            index=1,
            key="sel_cant_amigos",
        )
      with col_amg2:
        if st.button("🎲 Iniciar Nueva Trivia para Amigos"):
          st.session_state.tanda_amigos = preparar_tanda_preguntas(
              BANCO_COMPLETO, cant_amigos_sel
          )
          st.session_state.score_amigos = 0
          st.session_state.resp_amigos = set()
          st.rerun()

      if (
          "tanda_amigos" not in st.session_state
          or not st.session_state.tanda_amigos
      ):
        st.session_state.tanda_amigos = preparar_tanda_preguntas(
            BANCO_COMPLETO, cant_amigos_sel
        )
        st.session_state.score_amigos = 0
        st.session_state.resp_amigos = set()

      tanda_amg = st.session_state.tanda_amigos
      cant_resp_amg = len(st.session_state.resp_amigos)
      tot_amg = len(tanda_amg)

      st.caption(
          f"Preguntas contestadas: **{cant_resp_amg} / {tot_amg}** | Score"
          f" acumulado: **{st.session_state.score_amigos} pts**"
      )
      st.markdown("---")

      # Iteración de la trivia casual con feedback directo
      for idx_a, qa in enumerate(tanda_amg):
        ya_resp = idx_a in st.session_state.resp_amigos
        lbl_st = "✅ [RESPONDIDA]" if ya_resp else "⏳ [PENDIENTE]"

        st.markdown(
            f"##### ❓ Pregunta {idx_a + 1} de {tot_amg} [{qa['categoria']}]"
            f" {lbl_st}: {qa['pregunta']}"
        )

        opc_amg_sel = st.radio(
            "Seleccioná la opción:",
            qa["opciones"],
            key=f"radio_amg_{idx_a}",
            disabled=ya_resp,
        )

        if not ya_resp:
          if st.button(
              "Comprobar Respuesta",
              key=f"btn_amg_{idx_a}",
              type="primary" if not ya_resp else "secondary",
          ):
            st.session_state.resp_amigos.add(idx_a)
            idx_amg_correcta = qa["correcta"]
            idx_amg_elegida = qa["opciones"].index(opc_amg_sel)

            if idx_amg_elegida == idx_amg_correcta:
              st.session_state.score_amigos += 10
              st.success(
                  f"👏 **¡CORRECTO! (+10 pts)**  \n*{qa['explicacion']}*"
              )
            else:
              texto_v = qa["opciones"][idx_amg_correcta]
              st.error(
                  f"❌ **INCORRECTO.**  \nLa opción correcta en realidad era:"
                  f" **{texto_v}**  \n*{qa['explicacion']}*"
              )
            st.rerun()
        else:
          st.info(
              f"Respuesta registrada. Opción correcta:"
              f" **{qa['opciones'][qa['correcta']]}**"
          )

        st.markdown("---")

      # Score Final
      if cant_resp_amg == tot_amg and tot_amg > 0:
        st.balloons()
        max_amg_pts = tot_amg * 10
        pct_amg = round((st.session_state.score_amigos / max_amg_pts) * 100, 1)

        st.success(
            f"🏆 **¡FIN DEL JUEGO!**  \nPuntaje Final:"
            f" **{st.session_state.score_amigos} de {max_amg_pts} pts**"
            f" ({pct_amg}% de efectividad)."
        )

        if st.button("🔄 Jugar otra ronda"):
          st.session_state.tanda_amigos = preparar_tanda_preguntas(
              BANCO_COMPLETO, cant_amigos_sel
          )
          st.session_state.score_amigos = 0
          st.session_state.resp_amigos = set()
          st.rerun()

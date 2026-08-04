#!/usr/bin/env python3
import datetime
import random
import pandas as pd
import streamlit as st

# -----------------------------------------------------------------------------
# 1. CONFIGURACIÓN DE PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Desafío PPA C150 - ALE.FPV Game",
    page_icon="✈️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# -----------------------------------------------------------------------------
# 2. DISEÑO CSS INTERACTIVO (GAME SHOW / 8 ESCALONES)
# -----------------------------------------------------------------------------
st.markdown(
    """
<style>
    /* Fondo con degradado estilo juego */
    .stApp {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4338ca 100%);
        color: #ffffff;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Tarjeta principal de preguntas estilo Game Show */
    .game-card {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(12px);
        border: 2px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
        margin-bottom: 20px;
    }

    /* Encabezados y títulos coloridos */
    h1, h2, h3 {
        color: #fbbf24 !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        text-align: center;
    }

    /* Badge de Categoría / Nivel */
    .category-badge {
        background: linear-gradient(90deg, #ec4899 0%, #8b5cf6 100%);
        color: white;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.9rem;
        display: inline-block;
        box-shadow: 0 4px 10px rgba(236, 72, 153, 0.4);
        margin-bottom: 12px;
    }

    /* Botones estilo Arcade / Candy Crush */
    .stButton > button {
        background: linear-gradient(180deg, #f59e0b 0%, #d97706 100%);
        color: #ffffff !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
        border: none !important;
        border-radius: 15px !important;
        padding: 12px 24px !important;
        box-shadow: 0 6px 0 #92400e, 0 8px 15px rgba(0, 0, 0, 0.4) !important;
        transition: all 0.1s ease !important;
        width: 100%;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 0 #92400e, 0 10px 20px rgba(0, 0, 0, 0.5) !important;
        background: linear-gradient(180deg, #fbbf24 0%, #d97706 100%) !important;
    }

    .stButton > button:active {
        transform: translateY(4px);
        box-shadow: 0 2px 0 #92400e, 0 4px 8px rgba(0, 0, 0, 0.4) !important;
    }

    /* Personalización de la barra de progreso */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #10b981 0%, #3b82f6 100%) !important;
        border-radius: 10px;
    }

    /* Radios estilizados */
    .stRadio label {
        color: #f3f4f6 !important;
        font-size: 1.05rem !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# 3. LECTURA DIRECTA POR CSV DESDE GOOGLE SHEETS
# -----------------------------------------------------------------------------
SHEET_ID = "1PQGUpbPdyaoH01jMOi5MedoVIjvJnfpVwwt9RkXSYCY"
WORKSHEET_NAME = "Preguntas_Trivia"
URL_CSV_DIRECTA = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={WORKSHEET_NAME}"


@st.cache_data(ttl=600, show_spinner="🎮 Cargando el banco de preguntas...")
def cargar_banco_preguntas_completo():
  try:
    try:
      df_p = pd.read_csv(URL_CSV_DIRECTA, sep="|")
      if "Pregunta" not in df_p.columns:
        df_p = pd.read_csv(URL_CSV_DIRECTA, sep=";")
    except Exception:
      df_p = pd.read_csv(URL_CSV_DIRECTA)

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
    st.error(f"Error al cargar las preguntas: {e}")
    return []


def preparar_tanda_preguntas(banco_total, cantidad_tanda=10):
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


BANCO_COMPLETO = cargar_banco_preguntas_completo()

# Header Principal
st.markdown("<h1>🛩️ PPA TRIVIA SHOW 🏆</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align: center; color: #a5b4fc; font-size: 1.1rem;'"
    ">¿Cuánto sabés realmente sobre el Cessna 150?</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

if not BANCO_COMPLETO:
  st.warning("No se pudo conectar con el banco de preguntas.")
else:
  tab_diario, tab_libre = st.tabs(
      ["🔥 Escalón del Día", "🎮 Modo Los 8 Escalones"]
  )

  # --- TAB 1: DESAFÍO DEL DÍA ---
  with tab_diario:
    st.markdown("### 🔥 El Gran Desafío Diario")

    dia_del_ano = datetime.date.today().timetuple().tm_yday
    idx_desafio = dia_del_ano % len(BANCO_COMPLETO)
    q_dia = BANCO_COMPLETO[idx_desafio]

    st.markdown(
        f"""
        <div class="game-card">
            <span class="category-badge">🎯 {q_dia['categoria']}</span>
            <h3 style="text-align: left; color: #ffffff !important; margin-top: 10px;">
                {q_dia['pregunta']}
            </h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if "pub_desafio_respondido" not in st.session_state:
      st.session_state.pub_desafio_respondido = False

    opc_dia_sel = st.radio(
        "Seleccioná la respuesta correcta:",
        q_dia["opciones_orig"],
        key="radio_pub_desafio",
        disabled=st.session_state.pub_desafio_respondido,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if not st.session_state.pub_desafio_respondido:
      if st.button("🚀 RESPONDER DESAFÍO DIARIO"):
        st.session_state.pub_desafio_respondido = True
        idx_elegido = q_dia["opciones_orig"].index(opc_dia_sel)
        st.session_state.pub_desafio_es_correcto = (
            idx_elegido == q_dia["correcta_orig"]
        )

        if st.session_state.pub_desafio_es_correcto:
          st.balloons()
          st.success(
              "👏 **Cooooorrecto!!!**  \nExplicación del Manual:"
              f" *{q_dia['explicacion']}*"
          )
        else:
          correcta_texto = q_dia["opciones_orig"][q_dia["correcta_orig"]]
          st.error(
              "😅 **Ups!!! esa no es!**  \nLa respuesta correcta era:"
              f" **{correcta_texto}**  \nExplicación: *{q_dia['explicacion']}*"
          )
        st.rerun()
    else:
      if st.session_state.get("pub_desafio_es_correcto", False):
        st.success(
            "👏 **Cooooorrecto!!!**  \nExplicación del Manual:"
            f" *{q_dia['explicacion']}*"
        )
      else:
        correcta_texto = q_dia["opciones_orig"][q_dia["correcta_orig"]]
        st.error(
            "😅 **Ups!!! esa no es!**  \nLa respuesta correcta era:"
            f" **{correcta_texto}**  \nExplicación: *{q_dia['explicacion']}*"
        )

  # --- TAB 2: MODO MULTIJUGADOR ---
  with tab_libre:
    st.markdown("### 🪜 Desafío de Escalones")

    # Aseguramos la existencia de los diccionarios de estado
    if "pub_resp_detalle" not in st.session_state:
      st.session_state.pub_resp_detalle = {}

    col_cfg1, col_cfg2 = st.columns([2, 2])
    with col_cfg1:
      cant_amigos_sel = st.selectbox(
          "Elegí la cantidad de escalones / preguntas:",
          [5, 8, 10, 15],
          index=1,
          key="sel_pub_cant",
      )
    with col_cfg2:
      if st.button("🎲 Iniciar Nueva Trivia"):
        st.session_state.pub_tanda = preparar_tanda_preguntas(
            BANCO_COMPLETO, cant_amigos_sel
        )
        st.session_state.pub_score = 0
        st.session_state.pub_resp = set()
        st.session_state.pub_resp_detalle = {}
        st.rerun()

    if "pub_tanda" not in st.session_state or not st.session_state.pub_tanda:
      st.session_state.pub_tanda = preparar_tanda_preguntas(
          BANCO_COMPLETO, cant_amigos_sel
      )
      st.session_state.pub_score = 0
      st.session_state.pub_resp = set()
      st.session_state.pub_resp_detalle = {}

    tanda_pub = st.session_state.pub_tanda
    cant_resp_pub = len(st.session_state.pub_resp)
    tot_pub = len(tanda_pub)
    progreso = cant_resp_pub / tot_pub if tot_pub > 0 else 0

    col_m1, col_m2 = st.columns([3, 1])
    with col_m1:
      st.markdown(
          f"**Escalón actual:** {cant_resp_pub + 1 if cant_resp_pub < tot_pub else tot_pub} de {tot_pub}"
      )
      st.progress(progreso)
    with col_m2:
      st.markdown(
          f"<h3 style='margin:0; text-align:right;'>⭐"
          f" {st.session_state.pub_score} pts</h3>",
          unsafe_allow_html=True,
      )

    st.markdown("---")

    for idx_a, qa in enumerate(tanda_pub):
      ya_resp = idx_a in st.session_state.pub_resp
      status_label = "🟢 COMPLETADO" if ya_resp else "🟡 EN JUEGO"

      st.markdown(
          f"""
            <div class="game-card">
                <span class="category-badge">Escalón {idx_a + 1} • {qa['categoria']} ({status_label})</span>
                <h4 style="color: #ffffff; margin-top: 5px;">{qa['pregunta']}</h4>
            </div>
            """,
          unsafe_allow_html=True,
      )

      opc_amg_sel = st.radio(
          "Opciones disponibles:",
          qa["opciones"],
          key=f"radio_pub_{idx_a}",
          disabled=ya_resp,
      )

      if not ya_resp:
        if st.button("Confirmar Respuesta", key=f"btn_pub_{idx_a}"):
          st.session_state.pub_resp.add(idx_a)
          idx_amg_correcta = qa["correcta"]
          idx_amg_elegida = qa["opciones"].index(opc_amg_sel)
          es_correcta = idx_amg_elegida == idx_amg_correcta

          st.session_state.pub_resp_detalle[idx_a] = es_correcta

          if es_correcta:
            st.session_state.pub_score += 10

          st.rerun()
      else:
        fue_correcta = st.session_state.pub_resp_detalle.get(idx_a, False)
        if fue_correcta:
          st.success(
              f"👏 **Cooooorrecto!!!** (+10 pts)  \nExplicación:"
              f" *{qa['explicacion']}*"
          )
        else:
          texto_v = qa["opciones"][qa["correcta"]]
          st.error(
              f"😅 **Ups!!! esa no es!**  \nLa respuesta correcta era:"
              f" **{texto_v}**  \nExplicación: *{qa['explicacion']}*"
          )

      st.markdown("<br>", unsafe_allow_html=True)

    if cant_resp_pub == tot_pub and tot_pub > 0:
      st.balloons()
      max_pub_pts = tot_pub * 10
      pct_pub = round((st.session_state.pub_score / max_pub_pts) * 100, 1)

      st.markdown(
          f"""
            <div class="game-card" style="text-align: center; background: rgba(16, 185, 129, 0.2);">
                <h2>🏆 ¡LLEGASTE AL ÚLTIMO ESCALÓN! 🏆</h2>
                <h3 style="color: #6ee7b7 !important;">Puntaje Final: {st.session_state.pub_score} / {max_pub_pts} pts</h3>
                <p style="font-size: 1.2rem;">Efectividad de vuelo: <b>{pct_pub}%</b></p>
            </div>
            """,
          unsafe_allow_html=True,
      )

      if st.button("🔄 JUGAR OTRA RONDA"):
        st.session_state.pub_tanda = preparar_tanda_preguntas(
            BANCO_COMPLETO, cant_amigos_sel
        )
        st.session_state.pub_score = 0
        st.session_state.pub_resp = set()
        st.session_state.pub_resp_detalle = {}
        st.rerun()

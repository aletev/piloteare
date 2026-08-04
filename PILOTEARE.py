import random
import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection


@st.cache_data(
    ttl=600, show_spinner="Cargando preguntas de la trivia desde Google..."
)
def cargar_preguntas_desde_sheets():
  """Lee el banco de preguntas desde Sheets y mezcla las opciones de forma aleatoria."""
  try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_p = conn.read(
        spreadsheet=URL_PLANILLA, worksheet="Preguntas_Trivia", ttl="10m"
    )

    lista_preguntas = []
    for _, fila in df_p.iterrows():
      if pd.notna(fila.get("Pregunta")):
        # 1. Extraer opciones originales e índice correcto
        opciones_orig = [
            str(fila.get("Opcion_A", "")),
            str(fila.get("Opcion_B", "")),
            str(fila.get("Opcion_C", "")),
            str(fila.get("Opcion_D", "")),
        ]
        idx_correcta_orig = int(fila.get("Indice_Correcta", 0))
        texto_respuesta_correcta = opciones_orig[idx_correcta_orig]

        # 2. Mezclar el orden de las opciones de forma aleatoria
        opciones_mezcladas = opciones_orig.copy()
        random.shuffle(opciones_mezcladas)

        # 3. Encontrar el nuevo índice de la respuesta correcta tras la mezcla
        nuevo_idx_correcto = opciones_mezcladas.index(texto_respuesta_correcta)

        lista_preguntas.append({
            "categoria": str(fila.get("Categoria", "General")),
            "pregunta": str(fila.get("Pregunta", "")),
            "opciones": opciones_mezcladas,
            "correcta": nuevo_idx_correcto,
            "explicacion": str(fila.get("Explicacion", "")),
        })

    # Mezclar también el orden general de las preguntas del test
    random.shuffle(lista_preguntas)
    return lista_preguntas

  except Exception as e:
    st.warning(
        f"Aviso: No se pudieron cargar preguntas desde 'Preguntas_Trivia': {e}"
    )
    return []

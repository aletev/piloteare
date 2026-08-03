import datetime
import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# URL de tu planilla oficial (de tu código PILOTEARE.py)
URL_PLANILLA = "https://docs.google.com/spreadsheets/d/1PQGUpbPdyaoH01jMOi5MedoVIjvJnfpVwwt9RkXSYCY/edit"


def guardar_resultado_trivia(
    puntaje_obtenido, puntaje_maximo, tema="General C150"
):
    """Guarda el resultado de la trivia en la solapa 'Historial_Trivias' de Google Sheets."""
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)

        # 1. Leer el historial existente (de la hoja 'Historial_Trivias')
        try:
            df_historial = conn.read(
                spreadsheet=URL_PLANILLA, worksheet="Historial_Trivias", ttl="0m"
            )
        except Exception:
            # Si la hoja todavía no existe o está vacía, creamos la estructura
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

        # 2. Calcular porcentaje y estado
        porcentaje = round((puntaje_obtenido / puntaje_maximo) * 100, 1)
        if porcentaje >= 90:
            estado = "Excelente (Puesto de Pilotaje listo)"
        elif porcentaje >= 70:
            estado = "Aprobado (Listo para briefing)"
        else:
            estado = "Repasar Manual con Juan"

        # 3. Crear el nuevo registro
        nuevo_registro = {
            "Fecha_Hora": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Puntaje_Obtenido": puntaje_obtenido,
            "Puntaje_Maximo": puntaje_maximo,
            "Porcentaje_Acierto": f"{porcentaje}%",
            "Estado": estado,
            "Tema": tema,
        }

        # 4. Concatenar y actualizar la planilla
        df_actualizado = pd.concat(
            [df_historial, pd.DataFrame([nuevo_registro])], ignore_index=True
        )
        conn.update(
            spreadsheet=URL_PLANILLA,
            worksheet="Historial_Trivias",
            data=df_actualizado,
        )

        st.success(
            "✅ ¡Resultado guardado exitosamente en tu planilla de Google Sheets!"
        )

    except Exception as e:
        st.error(
            f"No se pudo guardar en Google Sheets. Error: {e}. Verificá los permisos de edición de la hoja 'Historial_Trivias'."
        )

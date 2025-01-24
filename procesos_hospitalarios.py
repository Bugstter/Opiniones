import streamlit as st
import pandas as pd
from io import BytesIO
import matplotlib.pyplot as plt

# Título de la aplicación
st.title("Procesamiento de Datos de Solicitudes Hospitalarias")

# Subir archivo
st.header("Paso 1: Cargar archivo Excel")
uploaded_file = st.file_uploader("Sube tu archivo Excel aquí", type=["xlsx"], key="upload_step")

if uploaded_file is not None:
    # Leer el archivo cargado y mostrarlo
    st.write("Vista previa del archivo original:")
    data = pd.read_excel(uploaded_file, skiprows=5)
    st.write(data.head())  # Mostrar las primeras filas del archivo
    
    # Procesamiento de datos
    st.header("Paso 2: Procesamiento de datos")
    
    # Reemplazar "HOSPITAL NACIONAL" por "HN" en la columna 'Establecimiento'
    data['Establecimiento'] = data['Establecimiento'].str.replace(
        r'HOSPITAL NACIONAL', 'HN', regex=True
    )
    
    # Crear tabla pivot
    cleaned_data = data.pivot_table(
        index='Establecimiento',       # Columna de hospitales
        columns='Valoraciones',        # Columna de valoraciones
        values='Cantidad de opiniones',  # Columna a contar
        aggfunc='sum',                 # Función de agregación
        fill_value=0                   # Rellenar valores faltantes con 0
    ).reset_index()
    
    # Mostrar los datos procesados
    st.write("Datos procesados:")
    st.write(cleaned_data)

    # Descargar el archivo procesado
    st.header("Paso 3: Descargar archivo procesado")
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        cleaned_data.to_excel(writer, index=False, sheet_name='Datos_Limpios')
    output.seek(0)
    
    # Crear botón de descarga
    st.download_button(
        label="Descargar archivo Excel procesado",
        data=output,
        file_name="Datos_Limpios_Solicitudes.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # Paso 4: Filtrar datos y generar gráfico
    st.header("Paso 4: Generar gráfico de opiniones")
    
    # Configurar el índice para los nombres de los establecimientos
    cleaned_data.set_index('Establecimiento', inplace=True)

    # Filtrar solo los hospitales
    filtered_data = cleaned_data[cleaned_data.index.str.contains(r'\bHN\b|\bHospital\b', case=False, na=False)]

    # Mostrar datos filtrados
    st.write("Datos filtrados (solo hospitales):")
    st.write(filtered_data)

    # Crear el gráfico
    st.header("Gráfico de Opiniones por Categoría de Satisfacción")

    # Colores específicos para las categorías de satisfacción
    colors = {
        'INSATISFECHO': 'red',
        'SATISFECHO': 'yellow',
        'MUY SATISFECHO': 'limegreen'
    }

    fig, ax = plt.subplots(figsize=(16, 10))
    filtered_data.plot(
        kind='bar',
        stacked=True,
        ax=ax,
        color=[colors.get(col, 'gray') for col in filtered_data.columns]
    )

    # Añadir etiquetas dentro de las barras
    for p in ax.patches:
        height = p.get_height()
        if height > 0:  # Evitar mostrar etiquetas en las barras vacías
            ax.text(p.get_x() + p.get_width() / 2, p.get_y() + height / 2, f'{int(height)}',
                    ha='center', va='center', color='black')

    # Personalizar el gráfico
    ax.set_title('Opiniones por Categoría de Satisfacción (Solo Hospitales)')
    ax.set_xlabel('Establecimiento')
    ax.set_ylabel('Cantidad de Opiniones')
    ax.set_xticklabels(filtered_data.index, rotation=45, ha='right')
    ax.legend(title='Valoraciones', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()

    # Mostrar el gráfico en Streamlit
    st.pyplot(fig)

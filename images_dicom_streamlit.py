import pydicom
import numpy as np
import matplotlib.pyplot as plt
import os
from skimage import measure
import pyvista as pv
import streamlit as st
import pandas as pd

# ---------------------
# Título y Advertencia
# ---------------------

st.markdown("<h1 style='color:#308ced; text-align:center;'>Visualización y Segmentación de Imágenes DICOM</h1>", unsafe_allow_html=True)
# Mostrar mensaje de advertencia con las especificaciones
st.warning("""
    **Advertencia: Especificaciones para las imágenes DICOM y el directorio**
    - **Descompresión**: Si alguna imagen está comprimida en **JPEG 2000**, el código intentará descomprimirla automáticamente. Los archivos en otros formatos no serán procesados.
    - **Directorio**: Ingresa la ruta completa del directorio que contiene las imágenes DICOM (.dcm)*
    - **Formato de archivo**: El código solo cargará archivos DICOM con la extensión **`.dcm`**. Asegúrate de que todas las imágenes sean archivos con esa extensión.
    - **Posición Z**: Las imágenes deben tener información sobre su posición en el espacio (`ImagePositionPatient[2]`). Esto es necesario para ordenar correctamente los cortes en el volumen.
""")

# ---------------------------------------
# Descipción importación y procesamiento
# ---------------------------------------
st.markdown("""
    <h1 style='color:#308ced; font-size: 30px; text-align: center;'>Importación de imágenes DICOM y procesamiento</h1>
    <p style='font-size: 16px; color:#308ced; text-align: justify;'>
        En esta sección, podrás cargar el directorio que contiene las imágenes DICOM que deseas procesar. El sistema se encargará de leer los archivos, ordenarlos según su posición en el eje Z y convertir los cortes DICOM en un volumen 3D que se puede utilizar para la segmentación de estructuras anatómicas. Además se muestra la imagén original, su histograma y metadatos.
    </p>
""", unsafe_allow_html=True)

# -----------------------------------------------------
# Pedir la ruta del directorio y cargar imágenes DICOM
# -----------------------------------------------------

# Ruta del directorio
dicom_dir = st.text_input("Introduce el directorio con imágenes DICOM:")

# Función para cargar las imágenes DICOM
def load_dicom_series(directory):
    slices = []
    for filename in sorted(os.listdir(directory)):
        filepath = os.path.join(directory, filename)
        if filename.endswith(".dcm"):
            try:
                dicom_data = pydicom.dcmread(filepath, force=True)
                # Descomprimir si es necesario
                if dicom_data.file_meta.TransferSyntaxUID in pydicom.uid.JPEG2000TransferSyntaxes:
                    dicom_data.decompress()  # Fuerza la descompresión
                slices.append(dicom_data)
            except Exception as e:
                st.error(f"Error al leer el archivo {filename}: {e}")
                continue              
    # Ordenar por eje Z (suponiendo que ImagePositionPatient[2] existe)
    try:
        slices.sort(key=lambda x: x.ImagePositionPatient[2])  # Ordena por eje Z
    except AttributeError:
        st.error("Los archivos DICOM no contienen la información ImagePositionPatient adecuada.")
    return slices

# Verificar si el directorio es válido
if dicom_dir:
    if os.path.exists(dicom_dir) and os.path.isdir(dicom_dir):
        st.success("Directorio cargado exitosamente.")
        # Cargar las imágenes DICOM automáticamente
        slices = load_dicom_series(dicom_dir)
    else:
        st.error("El directorio especificado no existe o no es válido.")

# --------------------------------------------------
# Función para convertir slices a un arreglo NumPy
# --------------------------------------------------
def dicom_to_numpy(slices):
    # Extrae los datos de píxeles de cada corte DICOM y los almacena en una lista
    image_arrays = [slice.pixel_array for slice in slices]
    # Apila las matrices 2D para crear un volumen 3D
    volume = np.stack(image_arrays, axis=0)
    return volume # Retornamos el volumen 3D generado
# Aplicar solo si 'slices' esté definido (solo si las imagenes fueron cargadas correctamente)
if 'slices' in locals() and slices:  # Verificar si 'slices' existe y tiene datos
    volume = dicom_to_numpy(slices) # Convierte los cortes DICOM en un volumen 3D
    st.info(f"El volumen DICOM tiene una forma de: {volume.shape}")

# ----------------------------------------------------------------------------
# Funciones para mostrar un corte DICOM seleccionado, histogramas y metadatos
# ----------------------------------------------------------------------------

# Función para mostrar un corte DICOM seleccionado
def visualize_slice(volume, slice_idx=0):
    plt.imshow(volume[slice_idx], cmap="gray")
    plt.title(f"Slice {slice_idx}")
    plt.axis("off")
    st.pyplot(plt)

# Función para convertir los valores de la imagen a Hounsfield Units (HU) - para el histograma
def convert_to_hu(dicom_data, image):
    # Obtener RescaleSlope y RescaleIntercept de los metadatos DICOM
    rescale_slope = dicom_data.get('RescaleSlope', 1)  # Si no están, usar 1 por defecto
    rescale_intercept = dicom_data.get('RescaleIntercept', 0)  # Si no están, usar 0 por defecto
    # Convertir la imagen a HU
    hu_image = image * rescale_slope + rescale_intercept
    return hu_image

# Función para mostrar el histograma de intensidad
def visualize_intensity_histogram(volume, slice_idx=0):
    # Extraer los datos del corte
    data_slice = volume[slice_idx].flatten()
    # Filtrar el rango de intensidades de interés
    filtered_data = data_slice[(data_slice >= 100)]  # Filtrar valores en el rango de 100 a 3000
    # Crear la figura para el histograma
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(filtered_data, bins=50, color="black", alpha=0.75)
    ax.set_title(f"Histograma de Intensidad de Slice {slice_idx}")
    ax.set_xlabel("Valor de Intensidad")
    ax.set_ylabel("Frecuencia")
    ax.set_xlim(100, None)  # Limitar el eje x
    # Mostrar el histograma
    st.pyplot(fig)

# Función para mostrar el histograma de Hounsfield Units (HU)
def visualize_hu_histogram(volume, dicom_data, slice_idx=0):
    # Convertir el corte a Hounsfield Units (HU)
    hu_image = convert_to_hu(dicom_data, volume[slice_idx])
    # Extraer los datos de la imagen en HU
    hu_data = hu_image.flatten()
    # Filtrar el rango de Hounsfield Units de interés
    filtered_hu_data = hu_data[(hu_data >= -900)]  # Filtrar según el rango de HU
    # Crear la figura para el histograma
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(filtered_hu_data, bins=50, color="black", alpha=0.75)
    ax.set_title(f"Histograma de Hounsfield Units (HU) de Slice {slice_idx}")
    ax.set_xlabel("HU")
    ax.set_ylabel("Frecuencia")
    ax.set_xlim(-900, None)  # Limitar el eje x
    # Mostrar el histograma
    st.pyplot(fig)

# Función para mostrar toda la metadata en dos columnas
def show_metadata(dicom_data):
    # Crear dos columnas
    col1, col2 = st.columns(2)
    # Crear un diccionario con los tags y valores
    metadata_dict = {}   
    for tag in dicom_data.dir():
        value = getattr(dicom_data, tag, 'No valor disponible')      
        # Solo agregar valores legibles
        if isinstance(value, (str, int, float)):
            metadata_dict[tag] = str(value)
    # Ordenar los items por el tag para mejor presentación
    sorted_metadata = sorted(metadata_dict.items())
    # Dividir los elementos en dos listas para mostrar en las columnas
    mid = len(sorted_metadata) // 2
    metadata_left = sorted_metadata[:mid]
    metadata_right = sorted_metadata[mid:]
    # Mostrar metadata en las dos columnas
    with col1:
        for tag, value in metadata_left:
            st.markdown(f"**{tag}:** {value}")
    with col2:
        for tag, value in metadata_right:
            st.markdown(f"**{tag}:** {value}")

# Aplicar solo si 'volume' esté definido
if 'volume' in locals():
    total_slices = volume.shape[0]  # Obtener el número total de cortes en el volumen
    # Selección del corte a visualizar con número de entrada
    slice_idx = st.number_input(
        "Por favor, ingresa un índice de corte en el rango de 0 a {}:".format(total_slices - 1),
        min_value=0, max_value=total_slices - 1, value=0, step=1
    )   
    # Visualizar el corte seleccionado
    dicom_data = slices[slice_idx]  # Obtener el dicom_data del corte seleccionado (previamente pedido)
    st.markdown("""<h2 style="text-align: center; color: #ba6ac8; font-size: 30px;">Visualización</h2>""", unsafe_allow_html=True)
    visualize_slice(volume, slice_idx)
  
    # Visualizar los histogramas por separado
    st.markdown("""<h2 style="text-align: center; color: #ba6ac8; font-size: 30px;">Histogramas</h2>""", unsafe_allow_html=True)
    visualize_intensity_histogram(volume, slice_idx)
    visualize_hu_histogram(volume, dicom_data, slice_idx)

    # Mostrar la metadata del corte seleccionado
    st.markdown("""<h2 style="text-align: center; color: #ba6ac8; font-size: 30px;">Metadata</h2>""", unsafe_allow_html=True)
    show_metadata(slices[slice_idx])

# ------------------------------------------------------------------------------------
# Decripción Visualización en 2D de la Estructura Segmentada en un Corte
# ------------------------------------------------------------------------------------

st.markdown("""
    <div style="text-align: justify; max-width: 800px; margin: 0 auto;">
        <h1 style='color:#308ced; font-size: 30px; text-align: center;'>Visualización 2D de la Estructura Segmentada en un Corte</h1>
        <p style='font-size: 16px; color:#308ced; font-style: italic;'> 
            La segmentación se realiza utilizando las Unidades Hounsfield (HU), una escala que mide la densidad de los tejidos en imágenes médicas. Cada tipo de tejido se identifica dentro de un rango específico de HU. En este trabajo, el enfoque principal es la segmentación ósea. A continuación, se muestran algunos de los valores utilizados en este caso.
        </p>
        <div style="display: flex; justify-content: space-between; flex-wrap: wrap;">
            <div style="width: 48%; padding-right: 2%;">
                <p style='font-size: 16px; color:#308ced;'> 
                    • <b>Hueso cortical</b>: 600 - 3000<br>
                    • <b>Hueso trabecular</b>: 200 - 400 HU<br>
                </p>
            </div>
            <div style="width: 48%; padding-left: 2%;">
                <p style='font-size: 16px; color:#308ced;'> 
                    • <b>Pulmón</b>: -500 HU<br>
                    • <b>Músculo</b>: 35 - 55 HU<br>
                </p>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# -----------------------------------------------
# Convertir las imágenes a Hounsfield Units (HU)
# -----------------------------------------------

# Función para convertir los valores de la imagen a Hounsfield Units (HU)
def transform_to_hu(dicom_data, image):
    # Obtener RescaleSlope y RescaleIntercept de los metadatos DICOM
    rescale_slope = dicom_data.get('RescaleSlope', 1)  # Si no están, usar 1 por defecto
    rescale_intercept = dicom_data.get('RescaleIntercept', 0)  # Si no están, usar 0 por defecto
    # Convertir la imagen a HU
    hu_image = image * rescale_slope + rescale_intercept
    return hu_image

# Aplicar solo si 'volume' esté definido
if 'volume' in locals() and slices:  # Verificar si 'slices' existe y tiene datos
    hu_images = []
    for slice_data in slices:
        hu_image = transform_to_hu(slice_data, slice_data.pixel_array)  # Convertir cada corte a HU
        hu_images.append(hu_image)
    # Convertir la lista de imágenes a un volumen 3D
    hu_image = np.stack(hu_images, axis=0)

# ----------------------------------------------
# Segmentación de la imagen usando una máscara
# -----------------------------------------------

# Función para visualizar una imagen dada un índice de corte
def visualize_slice(image, slice_idx):
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.imshow(image[slice_idx], cmap='gray')  # Mostrar la imagen en escala de grises
    ax.set_title(f"Slice {slice_idx}")
    ax.axis('off')  # Opcional, para ocultar los ejes
    st.pyplot(fig)

# Definir los rangos para cada estructura
structure_ranges = {
    "Hueso cortical": (600, 3000),
    "Hueso trabecular": (200, 400),
    "Grasa subcutánea": (-100, -50),
    "Músculo": (35, 55),
    "Pulmón": (-500),
    "Hígado": (40, 60),
}

# Función para segmentar estructuras en la imagen
def segment_structure(images, lower, upper):
    binary_mask = (images > lower) & (images < upper) # Crea una máscara binaria donde True indica que el píxel está dentro del rango (lower, upper).
    return binary_mask.astype(np.uint8) # Convierte la máscara binaria a una imagen de 0 y 1 (True → 1, False → 0).

structure_name = st.selectbox("Elige la estructura que deseas segmentar:", list(structure_ranges.keys()))

# Obtener el rango de la estructura seleccionada (siempre válido)
lower, upper = structure_ranges[structure_name]

# Aplicar solo si 'hu_image' esté definido (si las imagenes HU están disponibles)
if 'hu_image' in locals():
    # Realizar la segmentación de la imagen con los valores seleccionados
    segmented_image = segment_structure(hu_image, lower, upper)
    st.success(f"Segmentación de {structure_name} completada.")

    # Usar el índice de corte ya seleccionado previamente
    if 'slice_idx' in locals():
        # Visualizar la imagen segmentada en el corte seleccionado
        visualize_slice(segmented_image, slice_idx) # Llamar a la función
    else:
        st.warning("No se ha seleccionado un índice de corte previamente.")
else:
    st.warning("No se han cargado imágenes DICOM aún.")

# -------------------------------------------------------------------------------------
# Descripción Visualización 3D de la Estructura Segmentada en todo el Volúmen de Datos
# -------------------------------------------------------------------------------------

st.markdown("""
    <div style="text-align: justify; max-width: 800px; margin: 0 auto;">
        <h1 style='color:#308ced; font-size: 30px; text-align: center;'>Visualización 3D de la Estructura Segmentada en todo el Volúmen de Datos</h1>
        <p style='font-size: 16px; color:#308ced; font-style: italic;'> 
            En esta sección, podrás visualizar de manera interactiva la estructura segmentada en 3D a lo largo de todo el volumen de las imágenes DICOM.
        </p>
    </div>
""", unsafe_allow_html=True)

# -----------------
# Visualización 3D
# -----------------

# Función para generar malla 3D
def generate_mesh(volume, threshold=20):
    verts, faces, _, _ = measure.marching_cubes(volume, level=threshold)
    faces = np.hstack([np.full((faces.shape[0], 1), 3), faces])  # Convertir a formato de PyVista
    return pv.PolyData(verts, faces)

if st.button('Mostrar visualización 3D'):
    # Mostrar el modelo 3D de la estructura segmentada
    mesh = generate_mesh(segmented_image, threshold=0)
    plotter = pv.Plotter()
    plotter.add_mesh(mesh, color="lightblue", opacity=0.5)
    plotter.show()

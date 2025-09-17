import pydicom
import numpy as np
import matplotlib.pyplot as plt
import os
from skimage import measure
import pyvista as pv
import tkinter as tk
from tkinter import filedialog

# Carga imágenes DICOM de un directorio
def load_dicom_series(directory):
    slices = []
    for filename in sorted(os.listdir(directory)):
        filepath = os.path.join(directory, filename)
        if filename.endswith(".dcm"):
            dicom_data = pydicom.dcmread(filepath, force=True)
            if dicom_data.file_meta.TransferSyntaxUID in pydicom.uid.JPEG2000TransferSyntaxes:
                dicom_data.decompress()  # Force decompression
            slices.append(dicom_data)
    slices.sort(key=lambda x: x.ImagePositionPatient[2])  # Ordena por eje Z
    return slices

# Convertir a arreglo NumPy
def dicom_to_numpy(slices):
    images = np.stack([s.pixel_array for s in slices])
    return images.astype(np.int16)  # Convertir a 16-bits de luminiscencia

# Visualiza un slice
def visualize_slice(images, slice_idx=50):
    plt.imshow(images[slice_idx], cmap="gray")
    plt.title(f"Slice {slice_idx}")
    plt.axis("off")
    plt.show()

# Unidades Hounsfield
def transform_to_hu(slices, images):
    intercept = slices[0].get('RescaleIntercept', 0)
    slope = slices[0].get('RescaleSlope', 1)
    images_hu = images * slope + intercept
    return images_hu

# Segmentación con los rangos proporcionados
def segment_structure(images, lower, upper):
    binary_mask = (images > lower) & (images < upper)
    return binary_mask.astype(np.uint8)

# Definir los rangos para cada estructura anatómica
structure_ranges = {
    1: ("Hueso cortical", (1000, np.inf)),
    2: ("Hueso trabecular", (300, 800)),
    3: ("Cerebro (materia gris)", (40, 40)),
    4: ("Cerebro (materia blanca)", (30, 30)),
    5: ("Grasa subcutánea", (-115, -100)),
    6: ("Hígado", (45, 50)),
    7: ("Pulmones", (-950, -650)),
    8: ("Músculo", (45, 50)),
    9: ("Corteza renal", (25, 30)),
    10: ("Bazo", (40, 45)),
}

# Función para seleccionar un rango basado en el número de estructura
def get_structure_range(structure_number):
    return structure_ranges.get(structure_number, (None, (None, None)))

# Función para mostrar metadata
def show_metadata(dicom_data):
    print("\nMetadata del corte:")
    for tag in dicom_data.dir():
        value = getattr(dicom_data, tag, 'No valor disponible')
        if isinstance(value, (str, int, float)):
            print(f"{tag}: {value}")
        else:
            print(f"{tag}: Valor no legible")

# Función para verificar si las imágenes están en formato DICOM
def check_dicom_format(directory):
    dicom_files = [filename for filename in os.listdir(directory) if filename.endswith(".dcm")]
    if len(dicom_files) == 0:
        print("No se encontraron archivos DICOM en el directorio.")
        add_extension = input("¿Deseas agregar la extensión '.dcm' a los archivos que no la tienen? (si/no): ").strip().lower()
        if add_extension == "si":
            add_dcm_extension(directory)
            dicom_files = [filename for filename in os.listdir(directory) if filename.endswith(".dcm")]
            if len(dicom_files) == 0:
                print("No se encontraron archivos DICOM ni después de agregar las extensiones.")
                return False
        else:
            return False
    return True

# Función para agregar la extensión '.dcm' a los archivos que no la tienen
def add_dcm_extension(directory):
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if not filename.endswith(".dcm"):
            new_filepath = filepath + ".dcm"
            os.rename(filepath, new_filepath)
            print(f"Renombrado: {filename} -> {new_filepath}")

# Función para abrir el diálogo y seleccionar el directorio
def select_directory():
    root = tk.Tk()
    root.withdraw()
    return filedialog.askdirectory(title="Selecciona el directorio con imágenes DICOM")

# Función para generar malla 3D
def generate_mesh(images, threshold=20):
    verts, faces, _, _ = measure.marching_cubes(images, level=threshold)
    faces = np.hstack([np.full((faces.shape[0], 1), 3), faces])  # Convertir a formato de PyVista
    return pv.PolyData(verts, faces)

# Función principal con opción para segmentar más estructuras
def main():
    dicom_dir = select_directory()

    if dicom_dir:
        print(f"Directorio seleccionado: {dicom_dir}")

        if not check_dicom_format(dicom_dir):
            print("Las imágenes no están en formato DICOM o no se han renombrado correctamente.")
            return

        dicom_slices = load_dicom_series(dicom_dir)
        ct_images = dicom_to_numpy(dicom_slices)
        ct_images_hu = transform_to_hu(dicom_slices, ct_images)
        
        total_slices = len(dicom_slices)
        print(f"El volumen tiene {total_slices} cortes.")

        slice_idx = int(input(f"Selecciona el índice del corte (0 a {total_slices-1}): "))
        visualize_slice(ct_images, slice_idx)
        show_metadata(dicom_slices[slice_idx])

        while True:
            print("\nSelecciona una estructura para segmentar:")
            for num, (name, _) in structure_ranges.items():
                print(f"{num}: {name}")

            try:
                structure_number = int(input("\nIngresa el número de la estructura: "))
                structure_name, (lower, upper) = get_structure_range(structure_number)

                if structure_name is None:
                    print("Número inválido. Intenta de nuevo.")
                    continue

                print(f"\nSegmentando {structure_name}...")

                segmented_image = segment_structure(ct_images_hu, lower, upper)

                visualize_slice(segmented_image, slice_idx)

                mesh = generate_mesh(segmented_image, threshold=0)
                plotter = pv.Plotter()
                plotter.add_mesh(mesh, color="lightblue", opacity=0.5)
                plotter.show()

                otra = input("¿Deseas segmentar otra estructura? (si/no): ").strip().lower()
                if otra == "no":
                    print("Fin del proceso de segmentación.")
                    break

            except ValueError:
                print("Entrada inválida. Ingresa un número válido.")

if __name__ == "__main__":
    main()

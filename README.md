
<div align="center">

<h1>🧠 Visualización y Segmentación de Imágenes DICOM</h1>

<p>
  <img src="https://img.shields.io/badge/Python-blue" alt="Python">
  <img src="https://img.shields.io/badge/Streamlit-App-red" alt="Streamlit">
  <img src="https://img.shields.io/badge/DICOM-Imágenes%20médicas-lightgrey" alt="DICOM">
</p>

</div>

Este proyecto está diseñado para cargar, procesar y visualizar imágenes médicas en formato DICOM. Permite convertir una serie de cortes en un volumen 3D, segmentar estructuras anatómicas mediante umbrales de Unidades Hounsfield (HU) y visualizar tanto los cortes en 2D como la reconstrucción 3D de las estructuras segmentadas, junto con sus metadatos organizados de forma clara.

Incluye una demostración interactiva desarrollada con Streamlit, que facilita la segmentación y visualización de manera intuitiva. La herramienta es especialmente útil para la exploración de estructuras óseas en estudios de tomografía computarizada (TC).

---

## 🎯 Objetivo

Desarrollar una herramienta que permita:

- Cargar series de imágenes DICOM
- Construir volúmenes 3D a partir de cortes
- Aplicar segmentación basada en umbrales de HU
- Visualizar imágenes en 2D y reconstrucciones en 3D
- Analizar histogramas de intensidad
- Organizar y mostrar metadatos clínicos

---

## 📂 Estructura del repositorio

```text
Segmentacion-de-imagenes-DICOM-2D-y-3D/
├── images/                    # Imágenes de ejemplo y resultados
├── images_dicom.py            # Carga, procesamiento y segmentación DICOM
├── images_dicom_streamlit.py  # Aplicación interactiva con Streamlit
├── environment.yml            # Entorno y dependencias del proyecto
└── README.md                  # Documentación del repositorio
```
---

<h2>⚙️ Requisitos</h2>

<div align="center">

<table>
  <tr>
    <th>Herramienta</th>
    <th>Uso en el proyecto</th>
  </tr>
  <tr>
    <td><strong>Python 3.x</strong></td>
    <td>Lenguaje principal</td>
  </tr>
  <tr>
    <td><strong>OpenCV</strong></td>
    <td>Procesamiento de imágenes</td>
  </tr>
  <tr>
    <td><strong>NumPy</strong></td>
    <td>Operaciones numéricas y matriciales</td>
  </tr>
  <tr>
    <td><strong>Matplotlib</strong></td>
    <td>Visualización de imágenes e histogramas</td>
  </tr>
  <tr>
    <td><strong>Pandas</strong></td>
    <td>Organización de datos y metadatos</td>
  </tr>
  <tr>
    <td><strong>Streamlit</strong></td>
    <td>Interfaz interactiva</td>
  </tr>
</table>

</div>

---

## 🖼️ Ejemplos de resultados

A continuación se muestran ejemplos del uso de la herramienta para la carga, segmentación y visualización de imágenes DICOM.

<table>
  <tr>
    <td align="center" width="50%">
      <strong>📌 Visualización de cortes</strong><br><br>
      <img src="images/3.png" alt="Visualización de cortes DICOM" width="95%">
    </td>
    <td align="center" width="50%">
      <strong>📊 Histograma</strong><br><br>
      <img src="images/5.png" alt="Histograma de intensidades" width="95%">
    </td>
  </tr>
  <tr>
    <td align="center" width="50%">
      <strong>🧩 Segmentación</strong><br><br>
      <img src="images/4.png" alt="Segmentación de imágenes DICOM" width="95%">
    </td>
    <td align="center" width="50%">
      <strong>🧱 Renderizado 3D</strong><br><br>
      <img src="images/1.png" alt="Renderizado 3D de segmentaciones" width="95%">
    </td>
  </tr>
</table>

---

## 🚀 Instalación

### Con conda

```bash
conda env create -f environment.yml
conda activate nombre_del_entorno

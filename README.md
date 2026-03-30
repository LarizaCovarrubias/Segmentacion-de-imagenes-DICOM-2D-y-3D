# 🧠 Visualización y Segmentación de Imágenes DICOM

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

## 📂 Contenido del repositorio

- `data/`: estructura esperada para archivos DICOM  
- `notebooks/`: notebooks para exploración y pruebas  
- `src/`: código fuente modularizado  
- `results/`: resultados generados  
- `docs/`: documentación adicional  
- `environment.yml`: archivo para recrear el ambiente de trabajo  

---

## ⚙️ Requisitos

- Python 3.x  
- OpenCV  
- NumPy  
- Matplotlib  
- Pandas  
- Streamlit

---

## 🖼️ Ejemplos de resultados

A continuación se muestran ejemplos del uso de la herramienta para la carga, segmentación y visualización de imágenes DICOM.

### 📌 Visualización de cortes

![Visualización de cortes](images/3.png)

---

### 📊 Histograma

![Histograma](images/5.png)

---

### 🧩 Segmentación

![Segmentación](images/4.png)

---

### 🧱 Renderizado 3D de segmentaciones

![Renderizado 3D](images/1.png)

---

## 🚀 Instalación

### Con conda

```bash
conda env create -f environment.yml
conda activate nombre_del_entorno

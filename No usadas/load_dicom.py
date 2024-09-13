__author__ = 'Alejo Chacon'
import os
import tkinter as tk
from tkinter import filedialog
import pydicom
import numpy as np

def load_dicom(file_type):
    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana principal

    folder_path = filedialog.askdirectory(title=f"Seleccione la carpeta que contiene la resonancia {file_type}")

    if not folder_path:
        print('No se seleccionó ninguna carpeta. Operación cancelada.')
        return []

    dicom_data = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.dcm'):
            file_path = os.path.join(folder_path, file_name)
            ds = pydicom.dcmread(file_path)

            # Obtener el valor de intensidad del píxel en la posición (0, 0)
            reference_pixel_value = ds.pixel_array[0, 0]

            # Restar el valor de referencia a todos los píxeles de la imagen
            modified_pixel_array = ds.pixel_array - reference_pixel_value

            # Actualizar los datos de píxeles en el objeto DICOM
            ds.PixelData = modified_pixel_array.tobytes()

            dicom_data.append(ds)

    print(f'Se han cargado {len(dicom_data)} archivos DICOM desde la carpeta {folder_path}')
    return dicom_data
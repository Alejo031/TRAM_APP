from load_registration import load_registration_dicom
from compare_registered_mri import compare_mri
from apply_lut import apply_lut, apply_histogram
import tkinter as tk
from tkinter import filedialog
from back_to_slices import convert_3d_image_to_slices
from subtract_mri import subtract_mri
from visualize_sitk import show_sitk_image
from Dicom_Reader_Writer import get_dicom, rgb_to_dicom, monochrome_to_PET_dicom
import SimpleITK as sitk
from RegisterImages.WithDicomReg import registerDicom
import numpy as np 
from comparar_percentiles_lut import comparar_percentiles
import time
from respuesta_binaria import solicitar_respuesta_binaria

from mri_registration_tool import ground_registration


# Habilito el uso de ventanas
root = tk.Tk()
root.withdraw()  # Ocultar la ventana principal

#Obtengo las direcciones de la resonancia temprana y la resonancia tardía
print("Seleccione la carpeta donde se encuentran la resonancia temprana")
time.sleep(2)
t1_path = filedialog.askdirectory(title=f"Seleccione la carpeta que contiene la resonancia temprana")
print("Seleccione la carpeta donde se encuentran la resonancia tardía")
time.sleep(2)
t2_path = filedialog.askdirectory(title=f"Seleccione la carpeta que contiene la resonancia tardía")

#Cargo resonancias temprana y tardía en 3D
t1_img, t1_metadata = get_dicom(t1_path)
t2_img, t2_metadata = get_dicom(t2_path)
resampled3D = ground_registration(t1_img, t2_img)

t1_image = t1_img
t2_image = resampled3D


#Se dividen las resonancias en cortes individuales
t1_list = convert_3d_image_to_slices(t1_image)
t2_list = convert_3d_image_to_slices(t2_image)
t2_aux = convert_3d_image_to_slices(t2_img)
#Compara los resultados de la registracion
print("Verifique que la registracion haya sido aplicada correctamente")
time.sleep(2)
compare_mri(t1_list, t2_aux, "t1 MRI", "t2 MRI Original", "Imagenes originales")
print("Si los resultados no son correctos cierre la aplicación, ya que los resultados no serán válidos")
time.sleep(2)
compare_mri(t1_list, t2_list, "t1 MRI", "t2 MRI", "Verifique que la registración se haya aplicado correctamente")

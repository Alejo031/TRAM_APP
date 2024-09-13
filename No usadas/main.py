from load_dicom import load_dicom
from visualize_dicom import visualize_dicom
from load_registration import load_registration_dicom
from compare_registered_mri import compare_mri
from apply_lut import apply_lut
from sitk_dicom_viewer import mostrar_resonancia
from obtener_uid import get_series_instance_uid
from DicomRTTool import DicomReaderWriter
from RegisterImages.WithDicomReg import registerDicom, pydicom, sitk
import tkinter as tk
from tkinter import filedialog
from back_to_slices import convert_3d_image_to_slices

from subtract_mri import subtract_mri
from visualize_sitk import show_sitk_image
from visualize_trams import VisualizadorImagenes

from Dicom_Reader_Writer import get_dicom, image_to_dicom

def load_dicom_series(directory):
    reader = sitk.ImageSeriesReader()
    dicom_series = reader.GetGDCMSeriesFileNames(directory)
    reader.SetFileNames(dicom_series)
    image = reader.Execute()
    return image


root = tk.Tk()
root.withdraw()  # Ocultar la ventana principal

dicom_registration = load_registration_dicom()

fixed_path = filedialog.askdirectory(title=f"Seleccione la carpeta que contiene la resonancia fija")
moving_path = filedialog.askdirectory(title=f"Seleccione la carpeta que contiene la resonancia movil")

fixed_image = load_dicom_series(fixed_path)
moving_image = load_dicom_series(moving_path)

#moving_metadata = get_dicom(moving_path)

# Verifica si las imágenes se han leído correctamente
if fixed_image.GetSize() == (0, 0, 0):
    raise ValueError("La imagen fija DICOM no se ha leído correctamente o está vacía.")
if moving_image.GetSize() == (0, 0, 0):
    raise ValueError("La imagen móvil DICOM no se ha leído correctamente o está vacía.")

# Realiza el casting
fixed_image = sitk.Cast(fixed_image, sitk.sitkFloat32)
moving_image = sitk.Cast(moving_image, sitk.sitkFloat32)
resampled_moving = registerDicom(fixed_image=fixed_image, moving_image=moving_image, moving_series_instance_uid=get_series_instance_uid(moving_path),
                                                  dicom_registration=dicom_registration)

registered_image = convert_3d_image_to_slices(resampled_moving)
fixed_image_slices = convert_3d_image_to_slices(fixed_image)


resta = subtract_mri(registered_image, fixed_image_slices)

tram =  apply_lut(resta,5)
#show_sitk_image(tram)

image_to_dicom(tram, moving_metadata)
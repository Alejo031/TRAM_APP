__author__ = 'Alejo Chacon'
import os
import pydicom
import SimpleITK as sitk
import tkinter as tk
from tkinter import filedialog
from load_dicom import load_dicom
from load_registration import load_registration_dicom
from RegisterImages.WithDicomReg import registerDicom
from dicom_to_sitk import convert_pydicom_to_sitk_image_and_metadata
from sitk_to_dicom import combine_sitk_image_and_metadata_to_dicom
from RegisterImages.WithDicomReg import register_images_with_dicom_reg
from slices_to_3d import convert_slices_to_3d_image
from back_to_slices import convert_3d_image_to_slices
from sitk_dicom_viewer import mostrar_resonancia

from compare_registered_mri import compare_mri


def register_dicom_images():
    """
    Permite al usuario explorar su ordenador para seleccionar archivos DICOM de registración y resonancias.
    Realiza la registración de las resonancias y devuelve las imágenes fija y móvil registradas.
    """
    # Cargar archivo de registración DICOM
    registration_file = load_registration_dicom()
    if registration_file is None:
        return None, None

    # Cargar carpeta que contiene archivos DICOM de resonancia fija
    fixed_image_files = load_dicom("fija")
    if fixed_image_files is None:
        return None, None

    # Cargar carpeta que contiene archivos DICOM de resonancia móvil
    moving_image_files = load_dicom("móvil")
    if moving_image_files is None:
        return None, None

    # Convertir los archivos DICOM a imágenes SimpleITK
    fixed_img_sitk, fixed_metadata = convert_pydicom_to_sitk_image_and_metadata(fixed_image_files)
    moving_img_sitk, moving_metadata = convert_pydicom_to_sitk_image_and_metadata(moving_image_files)

    # Convertir el stack de cortes en un archivo volumetrico (matriz anchoXaltoXcantidad)
    fixed_img_3d = sitk.JoinSeries(fixed_img_sitk)
    moving_img_3d = sitk.JoinSeries(moving_img_sitk)


    resampled_mri = []
    #print(moving_image_files[0].SeriesInstanceUID)

    resampled = registerDicom(fixed_image=fixed_img_3d, moving_image=moving_img_3d, moving_series_instance_uid=moving_image_files[0].SeriesInstanceUID,
                              dicom_registration=registration_file)

    #resampled = register_images_with_dicom_reg(fixed_image=fixed_img_3d, moving_image=moving_img_3d, dicom_registration=registration_file)


    resampled_moving = convert_3d_image_to_slices(resampled)
    resampled_mri = combine_sitk_image_and_metadata_to_dicom(moving_image_files, resampled_moving)


    compare_mri(fixed_img_sitk, resampled_moving)

    return fixed_image_files, resampled_mri
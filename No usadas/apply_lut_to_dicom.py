__author__ = 'Alejo Chacon'
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import pydicom

def apply_lut_to_dicom_sequence(dicom_data, lut):
    """
    Aplica una Look-Up Table (LUT) a una secuencia de imágenes DICOM en escala de grises para convertirlas en imágenes a color.

    Parameters:
    dicom_data (list): Lista de objetos DICOM cargados con pydicom.
    lut (str or LinearSegmentedColormap): La Look-Up Table (LUT) para mapear la imagen. Puede ser el nombre de una LUT de matplotlib o un objeto LinearSegmentedColormap.

    Returns:
    list: Lista de objetos DICOM con las imágenes coloreadas.
    """
    colored_dicom_data = []

    if isinstance(lut, str):
        cmap = plt.get_cmap(lut)
    elif isinstance(lut, LinearSegmentedColormap):
        cmap = lut
    else:
        raise ValueError("LUT debe ser un nombre de cmap de matplotlib o un objeto LinearSegmentedColormap")

    for ds in dicom_data:
        img = ds.pixel_array
        img_normalized = (img - np.min(img)) / (np.max(img) - np.min(img))  # Normalizar la imagen a [0, 1]
        img_colored = cmap(img_normalized)  # Aplicar la LUT
        img_colored = (img_colored[:, :, :3] * 255).astype(np.uint8)  # Convertir a uint8 y eliminar el canal alfa

        # Crear una nueva instancia de objeto DICOM con los datos modificados
        modified_ds = ds.copy()
        
        # Actualizar los píxeles de la nueva instancia con los datos de img_colored
        modified_ds.PixelData = img_colored.tobytes()
        
        # Actualizar otros metadatos relevantes
        modified_ds.SamplesPerPixel = 3
        modified_ds.PhotometricInterpretation = 'RGB'
        modified_ds.BitsAllocated = 8
        modified_ds.BitsStored = 8
        modified_ds.HighBit = 7
        modified_ds.PixelRepresentation = 0
        modified_ds.PlanarConfiguration = 0  # Colores por píxel

        colored_dicom_data.append(modified_ds)

    return colored_dicom_data
import tkinter as tk
from tkinter import filedialog
from Dicom_Reader_Writer import get_dicom, rgb_to_dicom, monochrome_to_dicom, monochrome_to_PET_dicom
import SimpleITK as sitk
from back_to_slices import convert_3d_image_to_slices









import math

def custom_round(value):
    """Aplica las reglas de redondeo especificadas a un valor."""
    integer_part = int(value)  # Parte entera del valor
    first_decimal = int((value * 10) % 10)  # Primer decimal del valor

    if first_decimal in [0, 1, 2]:
        return float(f"{integer_part:.2f}")  # Redondear hacia abajo al número entero
    elif first_decimal in [3, 4, 5, 6, 7]:
        return float(f"{integer_part + 0.5:.2f}")  # Redondear a .5
    elif first_decimal in [8, 9]:
        return float(f"{integer_part + 1:.2f}")  # Redondear hacia arriba al número entero siguiente

def actualizar_posiciones(metadata_list):
    """Modifica 'Slice Location' y actualiza 'Image Position Patient' manteniendo la coherencia con 'Image Orientation Patient'."""
    
    # Obtener el incremento constante entre cortes basado en los dos primeros valores de slice location
    original_slice_locations = [float(metadata["0020|1041"]) for metadata in metadata_list]
    slice_increment = abs(original_slice_locations[1] - original_slice_locations[0])
    slice_increment = round(slice_increment, 2)  # Redondeo a 2 decimales

    # Redondear 'Slice Location' inicial
    initial_slice_location = custom_round(original_slice_locations[0])

    # Obtener 'Image Orientation Patient' del primer corte
    if "0020|0037" in metadata_list[0]:
        image_orientation = metadata_list[0]["0020|0037"].split("\\")
        # Convertir a float
        image_orientation = [float(val) for val in image_orientation]
    else:
        # Si no está presente, asumir orientación axial estándar
        image_orientation = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0]  # Orientación axial
        for metadata in metadata_list:
            metadata["0020|0037"] = "\\".join([str(val) for val in image_orientation])

    # Vector normal al plano de la imagen (producto cruz de los dos vectores de orientación)
    row_cosines = image_orientation[0:3]
    col_cosines = image_orientation[3:6]
    normal_vector = [
        row_cosines[1]*col_cosines[2] - row_cosines[2]*col_cosines[1],
        row_cosines[2]*col_cosines[0] - row_cosines[0]*col_cosines[2],
        row_cosines[0]*col_cosines[1] - row_cosines[1]*col_cosines[0]
    ]
    
    # Normalizar el vector normal
    norm = math.sqrt(sum([val**2 for val in normal_vector]))
    normal_vector = [val / norm for val in normal_vector]
    
    # Obtener 'Image Position Patient' del primer corte y convertir a float
    if "0020|0032" in metadata_list[0]:
        first_image_position = [float(val) for val in metadata_list[0]["0020|0032"].split("\\")]
    else:
        # Si no está presente, usar origen (0,0,0)
        first_image_position = [0.0, 0.0, 0.0]
        metadata_list[0]["0020|0032"] = "\\".join([str(val) for val in first_image_position])
    
    for i, metadata in enumerate(metadata_list):
        # Actualizar 'Slice Location'
        new_slice_location = initial_slice_location + i * slice_increment
        metadata["0020|1041"] = f"{new_slice_location:.2f}"
    
        # Calcular nueva 'Image Position Patient' desplazando a lo largo del vector normal
        displacement = [normal_vector[j] * slice_increment * i for j in range(3)]
        new_image_position = [
            first_image_position[j] + displacement[j] for j in range(3)
        ]
        # Redondear a dos decimales
        new_image_position = [round(val, 2) for val in new_image_position]
        metadata["0020|0032"] = "\\".join([f"{val:.2f}" for val in new_image_position])
    
    return metadata_list









# Habilito el uso de ventanas
root = tk.Tk()
root.withdraw()  # Ocultar la ventana principal


fixed_path = filedialog.askdirectory(title=f"Seleccione la carpeta que contiene la resonancia fija")
moving_path = filedialog.askdirectory(title=f"Seleccione la carpeta que contiene la resonancia movil")

#Cargo resonancias fija y móvil en 3D
fixed_image, fixed_metadata = get_dicom(fixed_path)
moving_image, moving_metadata = get_dicom(moving_path)

fixed_slices = convert_3d_image_to_slices(fixed_image)
moving_slices = convert_3d_image_to_slices(moving_image)

truncated_fixed = actualizar_posiciones(fixed_metadata)
truncated_moving = actualizar_posiciones(moving_metadata)

print("modificado")

monochrome_to_dicom(moving_slices, truncated_moving)

monochrome_to_dicom(fixed_slices, truncated_fixed)
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
from mri_registration_tool import heavy_registration, fast_registration
import os
import subprocess
import sys
import pkg_resources

def instalar_faltantes_desde_requerimientos():
    """
    Lee el archivo requirements.txt, verifica si las dependencias están instaladas
    y si no lo están, las instala automáticamente.
    """
    requirements_file = 'requirements.txt'
    
    try:
        # Leer el archivo requirements.txt
        with open(requirements_file, 'r') as f:
            requerimientos = f.read().splitlines()
        
        # Verificar e instalar los paquetes que faltan
        for requerimiento in requerimientos:
            paquete = requerimiento.split('==')[0]  # Obtiene el nombre del paquete
            try:
                # Verifica si el paquete está instalado
                pkg_resources.require(requerimiento)
            except pkg_resources.DistributionNotFound:
                # El paquete no está instalado, entonces lo instala
                print(f"El paquete {paquete} no está instalado. Instalando...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", requerimiento])
            except pkg_resources.VersionConflict:
                # Si hay un conflicto de versiones, también lo instala
                print(f"Conflicto de versión encontrado para {paquete}. Actualizando...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", requerimiento])
    
    except FileNotFoundError:
        print(f"No se encontró el archivo {requirements_file}. Asegúrate de que exista en el directorio.")
    except Exception as e:
        print(f"Error al procesar los requerimientos: {e}")


# Generar el archivo requirements.txt al finalizar la ejecución
def generar_requirements():
    with open('requirements.txt', 'w') as f:
        # Llama a pip freeze y guarda la salida en el archivo requirements.txt
        subprocess.run(['pip', 'freeze'], stdout=f)


def invert_image_list(image_list):
    inverted_images = []

    for img in image_list:
        # Convertir la imagen a un array NumPy
        img_array = sitk.GetArrayFromImage(img)
        
        # Multiplicar los valores de los píxeles por -1
        inverted_array = -img_array
        
        # Convertir el array invertido de vuelta a una imagen SimpleITK
        inverted_img = sitk.GetImageFromArray(inverted_array)
        inverted_img.CopyInformation(img)
        
        inverted_images.append(inverted_img)

    return inverted_images 




# Habilito el uso de ventanas
root = tk.Tk()
root.withdraw()  # Ocultar la ventana principal

#Bienvenida
print("Bienvenido a NERV: Neuroimaging Evaluator for Response Verification")
print("")
print("")

time.sleep(3)

#Verificación de paquetes instalados:
print("Aguarde mientras se verifica que los paquetes necesarios esten instalados")
print("Esta función solo es necesaria al trabajar con el script. Si ve este mensaje en el ejecutable comente la siguiente sección del código y vuelva a crearlo")
# Descarga los paquetes de python necesarios para correr el programa. Utilizar cuando se hace un pull desde el repositorio a 
# partir de un .txt que se encuentra en la carpeta del main
instalar_faltantes_desde_requerimientos()
# Crea el archivo "requerimientos.txt" con la lista de paquetes necesarios para ejecutar el programa
generar_requirements()

print("Esta herramienta permite aplicar registraciones externas o utilizar una herramienta de registración propia")
time.sleep(2)

respuesta0 = solicitar_respuesta_binaria("¿Desea cargar un archivo de registro?")
if (respuesta0 == True):
    #Cargo archivo de registro
    print("Seleccione el archivo de registro")
    time.sleep(2)
    dicom_registration = load_registration_dicom()

    #Obtengo las direcciones de la resonancia fija y la móvil
    print("Seleccione la carpeta donde se encuentran la resonancia fija")
    time.sleep(2)
    fixed_path = filedialog.askdirectory(title=f"Seleccione la carpeta que contiene la resonancia fija")
    fixed_image, fixed_metadata = get_dicom(fixed_path)
    print(f"Se cargó la imagen fija desde la carpeta: {fixed_path}")
    time.sleep(2)
    print("Seleccione la carpeta donde se encuentran la resonancia móvil")
    moving_path = filedialog.askdirectory(title=f"Seleccione la carpeta que contiene la resonancia movil")
    moving_image, moving_metadata = get_dicom(moving_path)
    print(f"Se cargó la imagen móvil desde la carpeta: {moving_path}")


    #Se aplica la matriz de registración
    resampled3D = registerDicom(fixed_image=fixed_image, moving_image=moving_image, 
                            moving_series_instance_uid=moving_metadata[0].get("0020|000e"),
                            dicom_registration=dicom_registration)
    

    #Se determina cual de las resonancias se realizó primero
    print("Para implementar el protocolo TRAM es necesario saber cual de las resonancias se realizó primero")
    respuesta = solicitar_respuesta_binaria("¿Es la resonancia fija la temprana?")
    if(respuesta==True):
        t1_image = fixed_image
        t1_metadata = fixed_metadata
        t2_image = resampled3D
        t2_metadata = moving_metadata

    elif(respuesta==False):
        t1_image = resampled3D
        t1_metadata = moving_metadata
        t2_image = fixed_image
        t2_metadata = fixed_metadata


else:
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

    #Elijo el tipo de registro que quiero usar
    print("El programa dispone de dos estrategias para aplicar la registracion: una lenta de alta precisión y una rápida de menor precisión")
    aux = False
    while (aux == False):
        respuesta3 = input(f"¿Qué estrategia desea aplicar? (RAPIDA/PRECISA)").strip().lower()
        if respuesta3 in ["rápida", "rapida"]:
            resampled3D = fast_registration(t1_img, t2_img)
            aux = True
        elif respuesta3 in ["precisa"]:
            resampled3D = heavy_registration(t1_img, t2_img)
            aux = True
        else:
            print("Respuesta no válida, intente de nuevo")


    t1_image = t1_img
    t2_image = resampled3D


#Se dividen las resonancias en cortes individuales
t1_list = convert_3d_image_to_slices(t1_image)
t2_list = convert_3d_image_to_slices(t2_image)

#Compara los resultados de la registracion
print("Verifique que la registracion haya sido aplicada correctamente")
time.sleep(2)
print("Si los resultados no son correctos cierre la aplicación, ya que los resultados no serán válidos")
time.sleep(2)
compare_mri(t1_list, t2_list, "t1 MRI", "t2 MRI", "Verifique que la registración se haya aplicado correctamente")

print("Aguarde mientras se procesan las resonancias")

#Se restan las resonancias
subtraction = subtract_mri(t1_list, t2_list)
#Se aplica el mapa de colores para TRAM
tram = apply_lut(subtraction, 5, "jet_r")
show_sitk_image(tram, lut='jet_r', window_title='TRAM RGB')

#Ajuste manual de los percentiles de la LUT
resp1 = solicitar_respuesta_binaria("¿Desea ajustar el recorte de valores en la LUT a color?")
p1=5
if(resp1 == True):
    print("")
    print("Disminuya el % recortado para aumentar la especificidad y disminuir la sensibilidad, aumentelo para lograr el efecto contrario")
    time.sleep(3)
    aux1 = tram
    control = False
    while(control!=True):
        p2 = float(input(f"Ingrese el percentil de cola que desea excluir (Por defecto 5%)  ").strip().lower())
        aux2 = apply_lut(subtraction, p2, "jet_r")
        print("Se grafican el tram con el percentil anterior y el actual")
        comparar_percentiles(aux1, aux2, p1, p2, "Comparar recorte de percentiles RGB")
        resp2 = solicitar_respuesta_binaria("¿Desea probar otro valor?")
        if(resp2 == True):
            p1=p2
            aux1 = aux2
        else:
            control = True
    resp3 = solicitar_respuesta_binaria("¿Desea utilizar último valor ingresado?")
    if(resp3==True):
        tram = aux2

    else:
        resp4 = solicitar_respuesta_binaria("¿Desea conservar el anterior? En negativo se conserva el original")
        if(resp4 == True):
            tram = aux1


#Convertir la resta de resonancias en una imagen SimpleITK y recastearla como un entero de 32 bits
subtraction_sitk = []
for s_img in subtraction:
    sub = sitk.Cast(s_img, sitk.sitkInt32)
    subtraction_sitk.append(sub)


# Obtención del TRAM en escala de grises. No es necesario graficar ya que es un paso intermedio para llegar a la version PET-CT del TRAM.
# Queda comentada la sección en la que si visualiza y ajusta el histograma por si en algun momento le sirve a alguien

# Ajuste del rango dinamico de la imagen en blanco y negro
p3=0
tram_bw = apply_histogram(subtraction_sitk, p3)
#show_sitk_image(tram_bw, lut='gray', window_title='TRAM Grayscale')
#resp1 = solicitar_respuesta_binaria("¿Desea ajustar el recorte de valores en la LUT en escala de grises?")
#if(resp1==True):
#    print("Disminuya el % recortado para aumentar la especificidad y disminuir la sensibilidad, aumentelo para lograr el efecto contrario")
#    time.sleep(7)
#    aux3 = tram_bw
#    control = False
#    while(control!=True):
#        p4 = float(input(f"Ingrese el percentil de cola que desea excluir (Por defecto 0%)  ").strip().lower())
#        aux4 = apply_histogram(subtraction_sitk, p4)
#        print("Se grafican el tram con el percentil anterior y el actual")
#        compare_mri(aux3, aux4, str(p3)+"%", str(p4)+"%", "Comparar recorte de percentiles en escala de grises")
#        resp2 = solicitar_respuesta_binaria("¿Desea probar otro valor?")
#        if(resp2 == True):
#            p3=p4
#            aux3 = aux4
#        else:
#            control = True
#    resp3 = solicitar_respuesta_binaria("¿Desea utilizar último valor ingresado?")
#    if(resp3==True):
#        tram_bw = aux4
#    else:
#        resp4 = solicitar_respuesta_binaria("¿Desea conservar el anterior? En negativo se conserva el original")
#        if(resp4 == True):
#            tram_bw = aux3

#Muestro los dos TRAMs al mismo tiempo
#compare_mri(tram, tram_bw, "TRAM RGB", "TRAM Grayscale", "TRAM RGB  y TRAM Grayscale")

print("Se muestran el TRAM a color y la version PET-CT en escala de grises exportable a ARIA")
print("El TRAM PET-CT no se recorta ya que la LUT puede ser ajustada dentro de ARIA")
time.sleep(5)
tram_pet = invert_image_list(tram_bw)
compare_mri(tram, tram_pet, "RGB", "PET inverted", "TRAM RGB y TRAM adaptado para PET-CT")
#Se pregunta si el usuario quiere guardar los TRAMs obtenidos
respuesta2 = solicitar_respuesta_binaria("¿Desea guardar el resultado RGB?")
if(respuesta2 == True):
    rgb_tram = []

    for img in tram:
        img_R = img[0]
        img_G = img[1]
        img_B = img[2]
        R = sitk.GetArrayFromImage(img_R)
        G = sitk.GetArrayFromImage(img_G)
        B = sitk.GetArrayFromImage(img_B)

        rgb_array = np.stack((R,G,B), axis=-1)
        rgb = sitk.GetImageFromArray(rgb_array, isVector=True)

        rgb_tram.append(rgb)
    
    rgb_to_dicom(rgb_tram, t1_metadata)
        
#respuesta3 = solicitar_respuesta_binaria("¿Desea guardar el resultado monocromático?")    
#if(respuesta3 == True):    
#    monochrome_to_dicom(tram_bw, moving_metadata)

respuesta4 = solicitar_respuesta_binaria("¿Desea guardar el resultado como PET?")
if(respuesta4 == True):    
    monochrome_to_PET_dicom(tram_pet, t1_metadata)

print("")
print("Gracias por utilizar NERV")
time.sleep(1)
print("Este programa se autodestruirá en:")
print("5")
time.sleep(1)
print("4")
time.sleep(1)
print("3")
time.sleep(1)
print("2")
time.sleep(1)
print("1")
time.sleep(1)
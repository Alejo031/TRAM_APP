__author__ = 'Alejo Chacon'
# Graficador de histograma

import SimpleITK as sitk
import matplotlib.pyplot as plt

def plot_sitk_histogram(image):
    """
    Grafica el histograma de una imagen SimpleITK.
    
    Parámetros:
        image (sitk.Image): Imagen en formato SimpleITK.
    """
    # Convertir la imagen a un arreglo de numpy
    image_array = sitk.GetArrayViewFromImage(image)
    
    # Aplanar la imagen para obtener los valores de intensidad
    flattened_image = image_array.flatten()
    
    # Crear el histograma
    plt.figure(figsize=(10, 6))
    plt.hist(flattened_image, bins=50, color='blue', alpha=0.7)
    
    # Etiquetas y título
    plt.title('Histograma de la imagen')
    plt.xlabel('Valor de intensidad')
    plt.ylabel('Frecuencia')
    
    # Mostrar la gráfica
    plt.grid(True)
    plt.show()

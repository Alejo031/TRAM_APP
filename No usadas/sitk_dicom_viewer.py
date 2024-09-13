__author__ = 'Alejo Chacon'
import SimpleITK as sitk
import matplotlib.pyplot as plt
import numpy as np

"""
Crea una clase para poder visualizar una lista de imágenes y moverse entre ellas utilizando las flechas del teclado o el índice de la imagen
"""
class ImageViewer:
    def __init__(self, images):
        self.images = [sitk.GetArrayFromImage(image) for image in images]
        self.num_images = len(self.images)
        self.current_image_index = 0

        self.fig, self.ax = plt.subplots()
        self.img_plot = self.ax.imshow(self.images[self.current_image_index][0, :, :], cmap='gray')
        self.update_title()

        self.fig.canvas.mpl_connect('key_press_event', self.on_key)

    def update_title(self):
        self.ax.set_title(f'Image {self.current_image_index + 1}/{self.num_images}')
        self.img_plot.set_data(self.images[self.current_image_index][0, :, :])
        self.img_plot.figure.canvas.draw()

    def on_key(self, event):
        if event.key == 'right':
            self.next_image()
        elif event.key == 'left':
            self.previous_image()

    def next_image(self):
        if self.current_image_index < self.num_images - 1:
            self.current_image_index += 1
            self.update_title()

    def previous_image(self):
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.update_title()

def mostrar_resonancia(images):
    """
    Recibe una lsita de imágenes SimpleITK y las muestra en una ventana. Pueden ser recorridas utilizando las flechas o el indice de la imagen
    :param images: Lista de imágenes SimpleITK
    """
    # Creamos una única instancia de ImageViewer que contiene todas las imágenes
    viewer = ImageViewer(images)
    plt.show()



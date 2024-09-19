__author__ = 'Alejo Chacon'
import SimpleITK as sitk
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import TextBox


class ImageViewer:
    """
    Crea una clase para visualizar una lista de imágenes y poder recorrerlas con las flechas del teclado o con el índice de la imagen. En el lateral derecho
    muestra la distribucion de los colores de la LUT. Por defecto muestra el colormap "jet_r" pero es posible que muestre ótro pasando el nombre como parámetro
    """

    def __init__(self, image_list, lut='jet_r', window_title='Image Viewer'):
        self.images = [sitk.GetArrayViewFromImage(img) for img in image_list]
        self.num_images = len(self.images)
        self.current_index = 0

        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        
        self.fig.canvas.manager.set_window_title(window_title)

        self.img_plot = self.ax.imshow(np.squeeze(self.images[self.current_index]), cmap='gray')
        self.ax.set_title(f'Image {self.current_index + 1}/{self.num_images}')
        self.ax.axis('off')

        self.axbox = plt.axes([0.3, 0.05, 0.4, 0.075])
        self.text_box = TextBox(self.axbox, 'Go to image #', initial='1')
        self.text_box.on_submit(self.go_to_image)

        self.fig.canvas.mpl_connect('key_press_event', self.on_key)

        self.add_lut_legend(lut)
        
        plt.show()

    def add_lut_legend(self, lut):
        # Get the colormap from matplotlib
        cmap = plt.get_cmap(lut)
        
        # Number of colors in the colormap
        num_colors = cmap.N
        
        # Create an axes for the legend
        ax_legend = self.fig.add_axes([0.8, 0.1, 0.05, 0.8], facecolor='black')
        
        for i in range(num_colors):
            y = i / num_colors
            color = cmap(i / num_colors)
            ax_legend.add_patch(plt.Rectangle((0, y), 1, 1 / num_colors, color=color))
        
        ax_legend.set_xticks([])
        ax_legend.set_yticks([])

    def update_image(self):
        self.img_plot.set_data(np.squeeze(self.images[self.current_index]))
        self.ax.set_title(f'Image {self.current_index + 1}/{self.num_images}')
        self.fig.canvas.draw()

    def on_key(self, event):
        if event.key.isdigit():
            num = int(event.key)
            if 1 <= num <= self.num_images:
                self.current_index = num - 1
                self.update_image()
        elif event.key == 'right':
            self.next_image()
        elif event.key == 'left':
            self.previous_image()

    def go_to_image(self, text):
        try:
            index = int(text) - 1
            if 0 <= index < self.num_images:
                self.current_index = index
                self.update_image()
        except ValueError:
            pass

    def next_image(self):
        if self.current_index < self.num_images - 1:
            self.current_index += 1
            self.update_image()

    def previous_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.update_image()

def show_sitk_image(image_list, lut='jet_r', window_title='SITK Viewer'):
    """Permite visualizar una lista de imágenes SimpleITK y recorrerlas con las flechas del teclado o el índice de imagen. En el lateral derecho muestra la distribución
    de colores de la LUT. Por defecto se muestra la LUT "jet:r" pero es posible pasar otra como parámetro
    :param image_list: lista de imágenes que se quiere visualizar
    :param lut: LUT que se desea poner como referencia en el lateral de la ventana
    """
    viewer = ImageViewer(image_list, lut, window_title)
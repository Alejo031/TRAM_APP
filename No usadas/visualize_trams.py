import SimpleITK as sitk
import matplotlib.pyplot as plt


class VisualizadorImagenes:
    def __init__(self, lista1, lista2, lista3):
        self.lista1 = lista1
        self.lista2 = lista2
        self.lista3 = lista3
        self.index = 0

        self.fig, self.axes = plt.subplots(2, 2, figsize=(10, 10))
        self.axes[1, 1].axis('off')
        
        self.update_images()

        self.fig.canvas.mpl_connect('key_press_event', self.on_key)
        plt.show()

    def update_images(self):
        self.axes[0, 0].imshow(sitk.GetArrayViewFromImage(self.lista1[self.index]))
        self.axes[0, 0].set_title('TRAM')
        self.axes[0, 0].axis('off')

        self.axes[0, 1].imshow(sitk.GetArrayViewFromImage(self.lista2[self.index]), cmap='gray')
        self.axes[0, 1].set_title('Imagen t1')
        self.axes[0, 1].axis('off')

        self.axes[1, 0].imshow(sitk.GetArrayViewFromImage(self.lista3[self.index]), cmap='gray')
        self.axes[1, 0].set_title('Imagen t2')
        self.axes[1, 0].axis('off')

        self.fig.canvas.draw()

    def on_key(self, event):
        if event.key == 'right':
            self.index = (self.index + 1) % len(self.lista1)
            self.update_images()
        elif event.key == 'left':
            self.index = (self.index - 1) % len(self.lista1)
            self.update_images()
        elif event.key == 'enter':
            num_str = input("Ingrese el número de la imagen a la que desea ir: ")
            try:
                num = int(num_str)
                if 0 <= num < len(self.lista1):
                    self.index = num
                    self.update_images()
                else:
                    print(f"Número fuera de rango. Debe estar entre 0 y {len(self.lista1) - 1}.")
            except ValueError:
                print("Entrada inválida. Por favor ingrese un número entero.")
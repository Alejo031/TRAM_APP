__author__ = 'Alejo Chacon'
import matplotlib.pyplot as plt

def visualize_dicom(dicom_data):
    current_index = 0
    total_images = len(dicom_data)

    fig, ax = plt.subplots()

    def show_image():
        ax.clear()
        img = dicom_data[current_index].pixel_array
        ax.imshow(img, cmap='gray')
        ax.set_title(f'Imagen {current_index + 1} de {total_images}')
        fig.canvas.draw()

    def on_key(event):
        nonlocal current_index
        if event.key == 'right':
            current_index = (current_index + 1) % total_images
            show_image()
        elif event.key == 'left':
            current_index = (current_index - 1) % total_images
            show_image()

    fig.canvas.mpl_connect('key_press_event', on_key)
    show_image()
    plt.show()
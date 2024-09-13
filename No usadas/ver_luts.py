import matplotlib.pyplot as plt
import numpy as np

# Generar datos de muestra
gradient = np.linspace(0, 1, 256)
gradient = np.vstack((gradient, gradient))

# Función para visualizar los colormaps
def plot_color_gradients(cmap_list):
    nrows = len(cmap_list)
    fig, axes = plt.subplots(nrows=nrows, figsize=(6, 2 * nrows))
    fig.subplots_adjust(top=1, bottom=0, left=0, right=1)
    for ax, cmap_name in zip(axes, cmap_list):
        ax.imshow(gradient, aspect='auto', cmap=plt.get_cmap(cmap_name))
        ax.set_axis_off()
        ax.set_title(cmap_name, loc='left', fontsize=12)
    plt.show()

# Listar colormaps por categorías
cmap_categories = {
    'Perceptually Uniform Sequential': ['viridis', 'plasma', 'inferno', 'magma', 'cividis'],
    'Sequential': ['Blues', 'BuGn', 'BuPu', 'GnBu', 'Greens', 'Greys', 'Oranges', 'OrRd', 'PuBu', 'PuBuGn', 'PuRd', 'Purples', 'RdPu', 'Reds', 'YlGn', 'YlGnBu', 'YlOrBr', 'YlOrRd'],
    'Diverging': ['PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu', 'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic'],
    'Cyclic': ['twilight', 'twilight_shifted', 'hsv'],
    'Qualitative': ['tab10', 'tab20', 'tab20b', 'tab20c', 'Pastel1', 'Pastel2', 'Paired', 'Accent', 'Dark2', 'Set1', 'Set2', 'Set3'],
    'Miscellaneous': ['flag', 'prism', 'ocean', 'gist_earth', 'terrain', 'gist_stern', 'gnuplot', 'gnuplot2', 'CMRmap', 'cubehelix', 'brg', 'gist_rainbow', 'rainbow', 'jet', 'nipy_spectral', 'gist_ncar']
}

# Visualizar todos los colormaps
for category, cmap_list in cmap_categories.items():
    print(f"Category: {category}")
    plot_color_gradients(cmap_list)
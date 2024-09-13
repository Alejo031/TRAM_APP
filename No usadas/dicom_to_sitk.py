__author__ = 'Alejo Chacon'
import SimpleITK as sitk
import pydicom

# Función para convertir un objeto pydicom.Dataset a sitk.Image y extraer los metadatos
def convert_pydicom_to_sitk_image_and_metadata(dicom_list):
    """ 
    Esta funcion recibe un arreglo de elementos dicom (ya cargados, no sirve pasarle la lista de direcciones) y los separa en
    una variable SimpleITK con el arreglo de matrices de pixeles y una variable con el arreglo de los metadatos asociados a cada imágen
    :param dicom_list: arreglo de elementos dicom
    :param sitk_image: arreglo de imagenes formateadas como SimpleITK
    :param metadata: arreglo de metadatos asociados a las imagenes de sitk_image
    """

    sitk_images = []
    metadata_list = []
    for dicom_data in dicom_list:
        # Convert the DICOM dataset to a SimpleITK image
        numpy_image = dicom_data.pixel_array
        sitk_image = sitk.GetImageFromArray(numpy_image)

        # Transfer all metadata elements
        metadata = {}
        for tag in dicom_data.keys():
            metadata[tag] = dicom_data[tag]

        sitk_images.append(sitk_image)
        metadata_list.append(metadata)
    
    return sitk_images, metadata_list
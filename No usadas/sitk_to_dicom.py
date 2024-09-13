__author__ = 'Alejo Chacon'
import SimpleITK as sitk
import pydicom
from pydicom.dataset import Dataset, FileDataset

def combine_sitk_image_and_metadata_to_dicom(dicom_files, sitk_images):
    """
    Combine a list of DICOM datasets with a list of SimpleITK images, modifying the pixel arrays of the DICOM datasets
    with the pixel information from the SimpleITK images.
    :param dicom_files: List of DICOM datasets
    :param sitk_images: List of SimpleITK images
    :return: List of modified DICOM datasets
    """
    modified_dicom_files = []
    for dicom_file, sitk_image in zip(dicom_files, sitk_images):
        # Convert FileDataset to Dataset while preserving file_meta
        if isinstance(dicom_file, FileDataset):
            dicom_dataset = Dataset()
            dicom_dataset.file_meta = dicom_file.file_meta  # Preserve file_meta
            for tag, value in dicom_file.items():
                dicom_dataset[tag] = value
            dicom_file = dicom_dataset

        # Modify the pixel array in the DICOM dataset with the pixel information from the SimpleITK image
        numpy_image = sitk.GetArrayFromImage(sitk_image)
        dicom_file.PixelData = numpy_image.tobytes()

        # Copy all metadata elements from the original DICOM dataset to the new one
        for tag in dicom_file.keys():
            if tag not in dicom_file and tag != "PixelData":
                dicom_file[tag] = dicom_file[tag]

        modified_dicom_files.append(dicom_file)

    return modified_dicom_files
import pydicom

def compare_dicom_elements(dicom_element_1, dicom_element_2):
    """
    Compare two DICOM datasets to check if they have the same format.

    :param dicom_element_1: First DICOM dataset.
    :param dicom_element_2: Second DICOM dataset.
    :return: True if the DICOM datasets have the same format, False otherwise.
    """
    # Check if the DICOM datasets have the same number of attributes
    if len(dicom_element_1) != len(dicom_element_2):
        return False

    # Check if all attributes in the first DICOM dataset are present in the second DICOM dataset
    for attribute in dicom_element_1:
        if attribute not in dicom_element_2:
            return False

    # Check if all attributes in the second DICOM dataset are present in the first DICOM dataset
    for attribute in dicom_element_2:
        if attribute not in dicom_element_1:
            return False

    # Check if the values of corresponding attributes are the same
    for attribute in dicom_element_1:
        if getattr(dicom_element_1, attribute) != getattr(dicom_element_2, attribute):
            return False

    return True

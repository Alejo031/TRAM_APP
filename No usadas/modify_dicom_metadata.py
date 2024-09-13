def modify_dicom_metadata(dicom_data, parameter, new_value):
    for ds in dicom_data:
        setattr(ds, parameter, new_value)
    print(f'Se ha modificado el parámetro "{parameter}" en todas las imágenes DICOM.')
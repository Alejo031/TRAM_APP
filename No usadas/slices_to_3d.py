import SimpleITK as sitk

def convert_slices_to_3d_image(sitk_slices):
    """
    Convert a list of SimpleITK image slices to a 3D image.
    """
    # Ensure the slices are sorted by position along the z-axis
    sitk_slices.sort(key=lambda x: x.GetOrigin()[2])
    
    # Combine slices into a 3D image
    return sitk.JoinSeries(sitk_slices)
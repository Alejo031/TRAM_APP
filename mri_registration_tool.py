import itk
import SimpleITK as sitk
import time
from load_registration import load_registration_dicom
from RegisterImages.WithDicomReg import registerDicom
import tkinter as tk
from tkinter import filedialog
from back_to_slices import convert_3d_image_to_slices

def recast_itk(image):
    # Convertir la imagen sitkImage a un array NumPy
    np_array = sitk.GetArrayFromImage(image)

    # Convertir el array NumPy a una imagen ITK
    itk_image = itk.GetImageFromArray(np_array)

    # Asegurarse de que sea de tipo itk.Image[itk.F, 3]
    itk_image = itk.cast_image_filter(itk_image, ttype=(type(itk_image), itk.Image[itk.F, 3]))

    return itk_image

def recast_sitk(image):
    # Convertir la imagen ITK a un array NumPy
    np_array = itk.array_view_from_image(image)

    # Convertir el array NumPy a una imagen SimpleITK
    sitk_image = sitk.GetImageFromArray(np_array)   

    # Asegurarse de que sea de tipo sitkFloat32
    sitk_image = sitk.Cast(sitk_image, sitk.sitkFloat32)

    return sitk_image


def fast_registration(fixed_image, moving_image):
    # Transformación inicial (centrar imágenes)
    initial_transform = sitk.CenteredTransformInitializer(
        sitk.Cast(fixed_image, moving_image.GetPixelID()), 
        moving_image, 
        sitk.Euler3DTransform(), 
        sitk.CenteredTransformInitializerFilter.MOMENTS
    )
    
    registration_method = sitk.ImageRegistrationMethod()

    # Métrica de información mutua con más bins
    registration_method.SetMetricAsMattesMutualInformation(numberOfHistogramBins=100)

    # Estrategia de muestreo: NONE (Denso, toma todos los pixeles), REGULAR (Regular, pixeles distribuidos uniformemente),
    # RANDOM (Aleatorio, toma puntos al azar pero puede dar resultados inconsistentes)
    registration_method.SetMetricSamplingStrategy(registration_method.RANDOM)
    # Porcentaje de pixeles tomados para el muestreo (Comentar si uso muestreo denso)
    registration_method.SetMetricSamplingPercentage(0.25)

    # Interpolador lineal para precisión
    registration_method.SetInterpolator(sitk.sitkLinear)

    # Optimizador con más iteraciones y criterios de convergencia ajustados
    total_iterations = 100
    registration_method.SetOptimizerAsGradientDescent(
        learningRate=1.0, 
        numberOfIterations=total_iterations, 
        convergenceMinimumValue=1e-6, 
        convergenceWindowSize=10
    )
    
    registration_method.SetOptimizerScalesFromPhysicalShift() 

    # Transformación rígida final
    final_transform = sitk.Euler3DTransform(initial_transform)
    registration_method.SetInitialTransform(final_transform)

    # Factores de reducción de resolución y suavizado por niveles
    registration_method.SetShrinkFactorsPerLevel(shrinkFactors=[6, 3, 1])
    registration_method.SetSmoothingSigmasPerLevel(smoothingSigmas=[3, 1, 0])
    registration_method.SmoothingSigmasAreSpecifiedInPhysicalUnitsOn()

    # Ejecutar registración
    final_transform = registration_method.Execute(sitk.Cast(fixed_image, sitk.sitkFloat32), 
                                                  sitk.Cast(moving_image, sitk.sitkFloat32))

    # Aplicar la transformación resultante
    resampled_image = sitk.Resample(
        moving_image, 
        fixed_image, 
        final_transform, 
        sitk.sitkLinear, 
        0.0, 
        moving_image.GetPixelID()
    )

    return resampled_image


def precise_registration(fixed_image, moving_image):
    # Transformación inicial (centrar imágenes)
    initial_transform = sitk.CenteredTransformInitializer(
        sitk.Cast(fixed_image, moving_image.GetPixelID()), 
        moving_image, 
        sitk.Euler3DTransform(), 
        sitk.CenteredTransformInitializerFilter.MOMENTS
    )
    
    registration_method = sitk.ImageRegistrationMethod()

    # Métrica de información mutua con más bins
    registration_method.SetMetricAsMattesMutualInformation(numberOfHistogramBins=300)

    # Estrategia de muestreo: NONE (Denso, toma todos los pixeles), REGULAR (Regular, pixeles distribuidos uniformemente),
    # RANDOM (Aleatorio, toma puntos al azar pero puede dar resultados inconsistentes)
    registration_method.SetMetricSamplingStrategy(registration_method.NONE)
    # Porcentaje de pixeles tomados para el muestreo (Comentar si uso muestreo denso)
    # registration_method.SetMetricSamplingPercentage(0.25)

    # Interpolador lineal para precisión
    registration_method.SetInterpolator(sitk.sitkBSpline)

    # Optimizador con más iteraciones y criterios de convergencia ajustados
    total_iterations = 600

    #registration_method.SetOptimizerAsGradientDescent(
    #    learningRate=1.0, 
    #    numberOfIterations=total_iterations, 
    #    convergenceMinimumValue=1e-10, 
    #    convergenceWindowSize=10
    #)

    registration_method.SetOptimizerAsRegularStepGradientDescent(
    learningRate=1.0, 
    minStep=1e-6, 
    numberOfIterations=total_iterations, 
    relaxationFactor=0.5,
    gradientMagnitudeTolerance=1e-4
)


    registration_method.SetOptimizerScalesFromPhysicalShift() 

    # Transformación rígida final
    final_transform = sitk.AffineTransform(fixed_image.GetDimension())
    registration_method.SetInitialTransform(final_transform)

    # Factores de reducción de resolución y suavizado por niveles
    registration_method.SetShrinkFactorsPerLevel(shrinkFactors=[4, 2, 1])
    registration_method.SetSmoothingSigmasPerLevel(smoothingSigmas=[2, 1, 0])
    registration_method.SmoothingSigmasAreSpecifiedInPhysicalUnitsOn()

    # Ejecutar registración
    final_transform = registration_method.Execute(sitk.Cast(fixed_image, sitk.sitkFloat32), 
                                                  sitk.Cast(moving_image, sitk.sitkFloat32))

    # Aplicar la transformación resultante
    resampled_image = sitk.Resample(
        moving_image, 
        fixed_image, 
        final_transform, 
        sitk.sitkLinear, 
        0.0, 
        moving_image.GetPixelID()
    )

    return resampled_image





def registration_tool(t1_image, t1_metadata, t2_image, t2_metadata):
    """ 
    Permite al usuario elegir entre todas las opciones de registración disponibles: Externa, la cual requiere de un archivo DICOM 
    con una matriz de transformación; o Interna, la cual aplica uno de los algoritmos de registración disponibles (registración
    rápida pero poco exacta o registración precisa pero con costo computacional alto). Recibe dos variables con matrices 3D con los
    cortes de las resonancias en t1 y t2, junto con sus metadatos y devuelve dos listas con los cortes de los estudios, uno de los
    cuales ha sido registrado respecto del otro 
    
    Parámeters:
    :param t1_image: variable con una matriz tridimensional de los cortes del estudio obtenida a los 5 minutos de la inyección de contraste
    :param t1_metadata: metadatos de la resonancia t1
    :param t2_image: variable con una matriz tridimensional de los cortes del estudio obtenida a los 70-100 minutos de la inyección de contraste
    :param t2_metadata: metadatos de la resonancia t2
    
    Returns:
    :param t1_list: stack de los cortes de la resonancia t1
    :param t2_list: stack de los cortes de la resonancia t2
    """

    aux = 'False'
    # Creo un bucle que me permita elegir el tipo de registración que deseo aplicar (interna, externa, rápida o precisa)
    while (aux == 'False'):
        resp0 = input("Ingrese el tipo de registración deseada (INTERNA/EXTERNA):").strip().lower()

        if resp0 in ['externo', 'externa', 'ext']:
            # Cargo el archivo de registración
            print("Seleccione el archivo de registración")
            dicom_registration = load_registration_dicom()

            # Defino cual es la imagen fija y cual la móvil
            print("Para aplicar la matriz de registro es necesario saber sobre cual de las resonancias se aplicó la transformación.")
            resp1 = input("¿Cuál de las resonancias es la fija? (TEMPRANA/t1 o TARDÍA/t2): ").strip().lower()
            if resp1 in ['temprana', 't1']:
                # Aplico la matriz de registración
                resampled3D = registerDicom(t1_image, t2_image, t2_metadata[0].get("0020|000e"), dicom_registration)
                # Divido los stacks de resonancias en cortes individuales
                t1_list = convert_3d_image_to_slices(t1_image)
                t2_list = convert_3d_image_to_slices(resampled3D)
                # Aplico condicion de salida del bucle
                aux = True


            elif resp1 in ['tardía', 'tardia', 't2']:
                # Aplico la matriz de registración
                resampled3D = registerDicom(t2_image, t1_image, t1_metadata[0].get("0020|000e"), dicom_registration)
                # Divido los stacks de resonancias en cortes individuales
                t1_list = convert_3d_image_to_slices(resampled3D)
                t2_list = convert_3d_image_to_slices(t2_image)
                # Aplico condicion de salida del bucle
                aux = True

            else:
                print("Respuesta inválida, intente de nuevo")

        elif resp0 in ["interno", "interna", "int"]:

            # Elijo el método de registración deseado
            print("Este programa cuenta con dos tipos de registración interna:")
            time.sleep(1)
            print("Registración rápida: se ejecuta a mayor velocidad pero puede tener errores")
            time.sleep(1)
            print("Registración precisa: es más lenta pero el resultado tiene un gran grado de exactitúd")

            resp2 = input("Ingrese el método de registración deseado (Preciso/Rápido): ").strip().lower()

            if resp2 in ["rápida", "rapida", "rápido", "rapido"]:
                resampled_t2 = fast_registration(t1_image, t2_image)
                t1_list = convert_3d_image_to_slices(t1_image)
                t2_list = convert_3d_image_to_slices(resampled_t2)
                aux = True


            elif resp2 in ["precisa", "preciso"]:
                resampled_t2 = precise_registration(t1_image, t2_image)
                t1_list = convert_3d_image_to_slices(t1_image)
                t2_list = convert_3d_image_to_slices(resampled_t2)
                aux = True


            else:
                print("Respuesta inválida, intente nuevamente")

    return t1_list, t2_list
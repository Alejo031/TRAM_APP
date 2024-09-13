import subprocess
import tempfile
import shutil
import os
import itk
from itkwidgets import compare, checkerboard
import numpy as np
import SimpleITK as sitk

# Callbacks for plotting registration progress.
import registration_callbacks



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


def heavy_registration(fixed_image, moving_image):
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

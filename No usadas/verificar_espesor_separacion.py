def check_uniformity(metadata_list):
    thicknesses = [float(d['0018|0050']) for d in metadata_list]
    locations = [float(d['0020|1041']) for d in metadata_list]
    
    # Verificar si todos los espesores son iguales
    same_thickness = all(t == thicknesses[0] for t in thicknesses)
    
    # Calcular las diferencias entre ubicaciones de cortes
    location_diffs = [locations[i+1] - locations[i] for i in range(len(locations) - 1)]
    
    # Verificar si todas las diferencias entre ubicaciones de cortes son iguales
    same_location_diff = all(diff == location_diffs[0] for diff in location_diffs)
    
    # Calcular la no uniformidad acumulada (suponiendo que la no uniformidad es la misma para cada corte)
    non_uniformity_accumulated = sum(abs(location_diffs[i] - location_diffs[0]) for i in range(len(location_diffs)))
    
    return same_thickness, same_location_diff, non_uniformity_accumulated

def check_dicom_metadata_consistency(list1, list2):
    same_thickness1, same_location_diff1, non_uniformity_acc1 = check_uniformity(list1)
    same_thickness2, same_location_diff2, non_uniformity_acc2 = check_uniformity(list2)
    
    # Verificar diferencias entre las dos listas
    thickness_difference_between_lists = abs(float(list1[0]['0018|0050']) - float(list2[0]['0018|0050'])) if list1 and list2 else None
    location_difference_between_lists = abs(float(list1[0]['0020|1041']) - float(list2[0]['0020|1041'])) if list1 and list2 else None
    
    return {
        'list1_uniform_thickness': same_thickness1,
        'list1_uniform_location_diff': same_location_diff1,
        'list1_non_uniformity_accumulated': non_uniformity_acc1,
        'list2_uniform_thickness': same_thickness2,
        'list2_uniform_location_diff': same_location_diff2,
        'list2_non_uniformity_accumulated': non_uniformity_acc2,
        'thickness_difference_between_lists': thickness_difference_between_lists,
        'location_difference_between_lists': location_difference_between_lists
    }
def get_difference_by_different_keys(list1, list2, key1, key2):
    """
    Returns items from list1 where key1 values don't match any key2 values in list2
    
    Args:
        list1: First list of dictionaries
        list2: Second list of dictionaries
        key1: Key to use for comparison in list1 items
        key2: Key to use for comparison in list2 items
    
    Returns:
        List of dictionaries from list1 that don't have matching values in list2
    """
    # Create set of all values from list2's key2
    list2_values = {str(d.get(key2)) for d in list2}

    # Return items from list1 where key1 value not in list2's key2 values
    return [d for d in list1 if d.get(key1) not in list2_values]


def flatten_nested_dicts(nested_dict, parent_key='', separator='_'):
    """
    Aplana un diccionario anidado, incluyendo listas de diccionarios en su interior,
    y devuelve una lista única con todos los diccionarios de las listas internas.
    
    Args:
        nested_dict: El diccionario de entrada potencialmente anidado
        parent_key: Clave padre para construir claves compuestas (uso interno)
        separator: Separador para claves compuestas
        
    Returns:
        Lista plana con todos los diccionarios encontrados en listas internas
    """
    items = []
    
    # Si es un diccionario
    if isinstance(nested_dict, dict):
        for k, v in nested_dict.items():
            new_key = f"{parent_key}{separator}{k}" if parent_key else k
            # print(parent_key)
            # Si el valor es una lista de diccionarios
            if k == 'title' and len(v) > 0:
                title = v
            if isinstance(v, list) and all(isinstance(i, dict) for i in v):
                # items.extend(v)  # Agregamos todos los diccionarios de la lista
                for item in v:
                    # Add the new key before appending
                    item['zona_display'] = title
                    items.append(item)
            else:
                # Llamada recursiva para seguir explorando
                items.extend(flatten_nested_dicts(v, new_key, separator))
    
    # Si es una lista (pero no de diccionarios)
    elif isinstance(nested_dict, list):
        for item in nested_dict:
            items.extend(flatten_nested_dicts(item, parent_key, separator))
    
    return items
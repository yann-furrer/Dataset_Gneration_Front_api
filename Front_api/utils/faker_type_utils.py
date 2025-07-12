def extract_all_faker_types(obj):
    faker_types = []

    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == "fakerType":
                faker_types.append(value)
            else:
                faker_types.extend(extract_all_faker_types(value))

    elif isinstance(obj, list):
        for item in obj:
            faker_types.extend(extract_all_faker_types(item))

    return faker_types
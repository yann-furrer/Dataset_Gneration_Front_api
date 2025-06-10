import re
import json

def get_type_by_name(value):
    """
    Détermine (type, fakerType, rules) pour une valeur donnée.
    """
    # 1) Objet
    if isinstance(value, dict):
        return "object", None, None
    # 2) Liste (array)
    if isinstance(value, list):
        return "array", None, None
    # 3) Booléen
    if isinstance(value, bool):
        return "boolean", None, [{"probability": 0.5}]
    # 4) Nombre
    if isinstance(value, (int, float)):
        return "number", None, None
    # 5) Chaîne
    if isinstance(value, str):
        if re.fullmatch(r"ID_\d+", value):
            return "id", None, None
        if value == "email":
            return "faker", "email", ""
        return "string", None, None
    # 6) Non géré
    raise NotImplementedError(f"Type non géré pour {value!r}")

def parse_node(fieldname, value):
    """
    Construit récursivement un nœud:
    - fieldname: nom du champ
    - value: valeur brute
    """
    t, faker_type, rules = get_type_by_name(value)
    node = {
        "fieldname": fieldname,
        "type": t,
        "children": []
    }

    # 1) Objet → descente récursive
    if t == "object":
        for k, v in value.items():
            node["children"].append(parse_node(k, v))
        return node

    # 2) Array → chaque élément renommé en key_1, key_2, …
    if t == "array":
        for idx, elt in enumerate(value, start=1):
            child_name = f"{fieldname}_{idx}"
            node["children"].append(parse_node(child_name, elt))
        return node

    # 3) Cas primitifs → ajout éventuel de fakerType et rules
    if faker_type is not None:
        node["fakerType"] = faker_type
    if rules is not None:
        node["rules"] = rules

    return node

def build_schema(input_data, root_name="rule_1"):
    return [{
        "fieldname": root_name,
        "type": "object",
        "children": [
            parse_node(k, v) for k, v in input_data.items()
        ]
    }]

if __name__ == "__main__":
    # Exemple avec données imbriquées et un array
    input_data = {
        "join_2": "ID_123456",
        "join_3bis": {
            "join_3A": "example",
            "yann": {
                "test": "example",
                "test2": [1, 2, 3, {"test3": "example"}]
            },
            "join_terger": "example",
            "join_3&&&": "example",
            "frfuhr": {
                "fe": "email",
                "dzefr": False
            }
        }
    }

    schema = build_schema(input_data)
    print(json.dumps(schema, indent=4, ensure_ascii=False))

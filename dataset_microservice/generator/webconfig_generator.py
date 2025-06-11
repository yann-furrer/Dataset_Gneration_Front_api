import re, asyncio
import json, sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from utils.faker_handler import FakerHandler



class WebConfigGenerator(FakerHandler):
    """
    Classe pour générer un schéma de configuration au format  de la structure sur le web à partir d'une structure de données.
    """
    def __init__(self, client_id = "12345"):
        super().__init__(client_id)

    # -----------------------
    # 1) Extraction des placeholders
    # -----------------------
    def extract_placeholders(self, value, placeholders=None):
        """
        Parcourt récursivement `value` et collecte dans `placeholders`
        toutes les chaînes susceptibles de devenir un fakerType.
        """
        
        if placeholders is None:
            placeholders = set()

        if isinstance(value, dict):
            for v in value.values():
                self.extract_placeholders(v, placeholders)

        elif isinstance(value, list):
            for elt in value:
                self.extract_placeholders(elt, placeholders)

        elif isinstance(value, str):
            # print(f"Traitement de la chaîne: {value}")
            # On exclut ce qu'on sait déjà gérer
            if re.fullmatch(r"ID_\d+", value):  
                return placeholders
            if value == "email":
                return placeholders
            # Tout le reste on lève comme placeholder
            placeholders.add(value)

        return placeholders

    # -----------------------
    # 2) Appel batch à votre API pour définir les fakerTypes
    # -----------------------
    async def batch_define_faker_types(self, placeholders):
        """
        Découpe en paquets, lance une tâche pour chaque paquet,
        attend toutes les réponses et fusionne dans un seul dict.
        """
        placeholders_value = []
        placeholders = list(placeholders)
        tasks = []
        for elem in placeholders:
            print(f"Traitement du placeholder: {elem}")
            if not isinstance(elem, str):
                raise ValueError(f"Placeholder doit être une chaîne de caractères, trouvé: {elem!r}")
            task = asyncio.create_task(self.generate_faker_list_IA_auto(elem, self.client_id))

            tasks.append(task)
     
        # print(f"Nombre de placeholders à traiter: {len(tasks)}")
        # print(tasks)
        # fusion
        mapping = {}
        for enum, d in enumerate(await asyncio.gather(*tasks)):
            print(f"Réponse de la tâche: {d}")
            print(f"Mapping des placeholders: {mapping}")
            mapping[placeholders[enum]] = d
        return mapping
       
    # -----------------------
    # 3) Nouvelle version de get_type_by_name qui prend le mapping
    # -----------------------
    def get_type_by_name(self, value, placeholder_mapping):
        if isinstance(value, dict):
            return "object", None, None
        if isinstance(value, list):
            return "array", None, None
        if isinstance(value, bool):
            return "boolean", None, [{"probability": 0.5}]
        if isinstance(value, (int, float)):
            return "number", None, None

        # Chaîne
        if isinstance(value, str):
            if re.fullmatch(r"ID_\d+", value):
                return "id", None, None
            if value == "email":
                return "faker", "email", ""
            # Si c'est dans le mapping on retourne du faker
            if value in placeholder_mapping:
                info = placeholder_mapping[value]
                return "faker", info, ""
            # Sinon on retombe sur string « simple »
            return "string", None, None

        raise NotImplementedError(f"Type non géré pour {value!r}")

    # -----------------------
    # 4) Construction du schéma
    # -----------------------
    def parse_node(self, fieldname, value, placeholder_mapping):
        t, faker_type, rules = self.get_type_by_name(value, placeholder_mapping)
        node = {
            "fieldname": fieldname,
            "type": t,
            "children": []
        }

        if t == "object":
            for k, v in value.items():
                node["children"].append(self.parse_node(k, v, placeholder_mapping))
            return node

        if t == "array":
            for idx, elt in enumerate(value, start=1):
                child_name = f"{fieldname}_{idx}"
                node["children"].append(self.parse_node(child_name, elt, placeholder_mapping))
            return node

        if faker_type is not None:
            print(f"Adding fakerType: {faker_type} for field: {fieldname}")
            node["fakerType"] = faker_type
            del node["type"]  # On n'a plus besoin de type si on a fakerType
        if rules is not None:
            node["rules"] = rules

        return node

    async def build_schema(self, input_data, root_name="rule_1"):
        # 1) extraction des placeholders
        placeholders = self.extract_placeholders(input_data)

        # 2) définition en batch
        placeholder_mapping = await self.batch_define_faker_types(placeholders)

        # 3) génération du schéma
        root = {
            "fieldname": root_name,
            "type": "object",
            "children": [
                self.parse_node(k, v, placeholder_mapping)
                for k, v in input_data.items()
            ]
        }
        return [root]

    # -----------------------
    # 5) Exemple
    # -----------------------
# if __name__ == "__main__":
#         input_data ={"smartphone": {"marque": "Samsung", "modele": "Galaxy S23",  "caracteristiques": {"ecran": "6.1 pouces", "ram": "8 Go", "stockage": "128 Go","typedecheuveux": "bouclé", "listpays" :["chine", "russie","Afrique du sud"]}, "prix": 899}}

#         # schema = build_schema(input_data)
#         # print(json.dumps(schema, indent=4, ensure_ascii=False))
# test = WebConfigGenerator()
# schema = asyncio.run( test.build_schema(input_data))
# print(json.dumps(schema, indent=4, ensure_ascii=False))
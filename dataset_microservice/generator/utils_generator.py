import re, yaml
from dateutil import parser
import datetime
from typing import Any
# Used to extract values from a data structure and call get_type_name on each value
# The gpt call api in get_type_name work quickly with a list of values
def extract_keys(data):
    keys = []
    if isinstance(data, dict):
        for key, value in data.items():
            keys.append(key)
            keys.extend(extract_keys(value))
    elif isinstance(data, list):
        if not data:  # Liste vide
            keys.append('')
        else:
            for item in data:
                if isinstance(item, (dict, list)):
                    keys.extend(extract_keys(item))
                else:
                    keys.append('')  # Un '' pour chaque valeur "feuille" sans clé
    return keys

def extract_keys_values(data, values=None, keys=None):
    """
    Parcourt récursivement 'data' et retourne deux listes :
    - les valeurs (respectant la structure d'origine)
    - les clés (ou "" quand il n'y a pas de clé)
    """
    if values is None:
        values = []
    if keys is None:
        keys = []

    if isinstance(data, dict):
        # Les clés rencontrées à ce niveau
        current_keys = list(data.keys())
        keys.extend(current_keys)
        # Les valeurs de ce niveau
        values.append({})
        for value in data.values():
            
            extract_keys_values(value, values, keys)
    elif isinstance(data, list):
        print("listt :",  data)
        keys.append([])
        values.append([])
        for item in data:
            print
            extract_keys_values(item, values, keys)
    else:
        values.append(data)
        keys.append("")

    return values, keys


def get_type_name(value):
    print("value", value, type(value))
    """
    Trouve le type d'un objet en fonction de sa valeur.
    """
    # Simule un appel réseau ou une opération asynchrone
    if isinstance(value, dict):
        return "object"
    elif isinstance(value, list):
        return "array"
    elif value.isnumeric() :
        print("value is numeric")
        if isinstance(value, int):
            return "integer"
        elif isinstance(value, float):
            return "float"
        return "integer"
    elif isinstance(value, float):
        return "integer"
    elif isinstance(value, bool):
        return "boolean"
    
    elif isinstance(value, str):
        if value.isdigit() and not value.startswith("0"): # si le string est un nombre
            return "integer"
        if bool(re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", value)):
            return "email"
        if bool(re.match(r"^(\+?\d{1,3})?\s?(\d{2}[\s.-]?\d{2}[\s.-]?\d{2}[\s.-]?\d{2}[\s.-]?\d{2})$", value)):
            return "phone"
        if bool(re.match(r"^\d{4}-\d{2}-\d{2}$", value)):
            return "date"
        if bool(re.match(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", value)):
            return "ip"

        # if bool(re.match(r"^http(s)?:\/\/((\d+\.\d+\.\d+\.\d+)|(([\w-]+\.)+([a-z,A-Z][\w-]*)))(:[1-9][0-9]*)?(\/([\w-.\/:%+@&=]+[\w- .\/?:%+@&=]*)?)?(#(.*))?$/i"), value):
        #     #url
        #     return "string"
     
        if bool(re.search(r'[0-9]', value)) or bool(re.search(r'[a-zA-Z]', value)) or bool(re.search(r'[^a-zA-Z0-9]', value)):
          
          return "GPT1"
        else :
            return "string"
    else:
        return "string"
    


def get_date_range( date_input):
        """
        Prend une date sous n'importe quel format et retourne deux dates :
        - Une date avec -1 an
        - Une date avec +1 an
        Le tout au format "YYYY-MM-DD".

        :param date_input: str | int - Une date sous forme de chaîne ou de timestamp.
        :return: tuple(str, str) - (date -1 an, date +1 an) au format "YYYY-MM-DD".
        """
        # Vérifier si c'est un timestamp en millisecondes et le convertir
        if isinstance(date_input, int) or (isinstance(date_input, str) and date_input.isdigit()):
            if len(str(date_input)) == 13:  # Unix timestamp en millisecondes
                date_obj = datetime.utcfromtimestamp(int(date_input) / 1000)
            else:
                return "Invalid date input"
        
        elif isinstance(date_input, str):
            try:
                date_obj = parser.parse(date_input)  # Parse automatiquement la date
            except (ValueError, OverflowError):
                print('invalid date format')
                return "Invalid date format"
        
        else:
            return "Invalid input"

        # Calcul des dates -1 an et +1 an
        date_minus_1_year = date_obj.replace(year=date_obj.year - 1).strftime("%Y-%m-%d")
        date_plus_1_year = date_obj.replace(year=date_obj.year + 1).strftime("%Y-%m-%d")

        return date_minus_1_year, date_plus_1_year







class YamlUtils:
    
    def write_yaml(self, file_data: Any, file_name: str = "default.yaml"):
        """Ecrit les données YAML dans un fichier."""
        print("write_yaml : ", file_name)
        path = "./config/"+file_name+".yaml"
        print(yaml.dump(file_data, allow_unicode=True, sort_keys=False, indent=1))
        # with open(path, 'w+') as f:
        #     yaml.dump(file_data, f, allow_unicode=True, sort_keys=False, indent=1)


    def configure_dataset_yaml(self, type_of_value: str, example_value : str )-> dict:
        """
        Retourne des paramètre de configuration supplémentaires
        pour certains types de valeurs
        
        """
        if type_of_value == "id":
            len_id = len(str(example_value))
            includeLetters = bool(re.search(r'[a-zA-Z]', example_value))
            includeNumbers = example_value.isnumeric()
            includeSpecialChars = bool(re.search(r'[^a-zA-Z0-9]', example_value))
            return {"rules": {"range":{"len": len_id, "includeLetters": includeLetters, "includeNumbers": includeNumbers, "includeSpecialChars": includeSpecialChars }}}
        elif type_of_value == "date":
            # print("type_of_value : ", type_of_value)
            # print("example_value : ", example_value)
            format = self.detect_date_format(example_value)
            print("format : ", format)
            print("example_value : ", example_value)
            start_date , end_date = get_date_range(example_value)
            return {"rules": {"range":{"start": start_date, "end": end_date, "format": format}}}
        

    def return_key_type(self, value: str):
        """
        Retourne le type de la clé d'un dictionnaire.
        """
        if value in  ["number", "string", "bool", "array", "object", "date"]:
            return "type"
        else:
            return "fakerType"

    def get_value_from_path(self, data: dict, path: str):
        """
        Récupère une valeur dans un dictionnaire en suivant un chemin.

        :param data: Le dictionnaire source.
        :param path: Le chemin sous la forme "root.exemple.data".
        :return: La valeur trouvée ou None si le chemin est invalide.
        """
        keys = path.split(".")[1:]  # Ignore "root"
        current = data

        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current
    
    def build_structure(self, flat_data, type_of_builder = "bones" or "field", dataset_name : str = "Default Dataset", number_of_records: int = 10, entrypath: str = "root" ):
        """
        Construit une structure hiérarchique à partir d'une liste de champs aplanis.
        """
        #sécuriser le nombre de records max à 1000
        number_of_records = number_of_records if number_of_records <= 1000 else 1000
        # Déterminer la clé principale pour la racine
        root_key = "bones" if type_of_builder == "bones" else "fields"

        # Définir la structure racine
        root = {'datasetName': dataset_name, 'numberOfRecords': number_of_records, root_key: []} if type_of_builder == "fields" else {root_key: []}    
        stack = [(root, -1, True)]  # Stack: (nœud, niveau, est-ce la racine ?)

        for item in flat_data:
            # print("item : ", item)
            # permet d'ajouter le paramètre entrypoint dans le yaml si c'est le bone qui est recherché
            node = {'fieldName': item['name'], self.return_key_type(item['exemple_value']): item['exemple_value']}
            if entrypath.split(".")[-1] == item['name'] and type_of_builder == "bones":
                node.update({'entrypoint': True})
            if item['exemple_value'] == "date" or item['exemple_value'] == "id":
                # print("id --_> ", item['name'], item["exemple_value"])
                node.update(self.configure_dataset_yaml(item['exemple_value'], item['value']))
            
            current_level = item['level']

            # Ajuster le niveau hiérarchique
            while stack and stack[-1][1] >= current_level:
                stack.pop()

            parent_node, _, is_root = stack[-1]

            # Pour la racine, on garde "bones" (si défini) sinon, on passe à "fields"
            child_key = "bones" if is_root and type_of_builder == "bones" else "fields"

            # Ajouter les enfants à la bonne clé
            if child_key not in parent_node:
                parent_node[child_key] = []
            parent_node[child_key].append(node)

            # Après la racine, on passe à "fields"
            stack.append((node, current_level, False))

        return root
    
    def insert_in_dict(self, d, key, value, position):
        """
        Insère une clé/valeur à une position spécifique dans un dict.

        :param d: Dictionnaire initial
        :param key: Clé à insérer
        :param value: Valeur associée
        :param position: Position (index) où insérer la clé/valeur
        :return: Nouveau dictionnaire avec l'insertion
        """
        # Créer un nouvel ordre en réorganisant les items
        new_dict = {}
        for i, (k, v) in enumerate(d.items()):
            if i == position:
                new_dict[key] = value  # Ajouter la nouvelle clé/valeur à la position spécifiée
            new_dict[k] = v  # Ajouter les autres éléments
        if position >= len(d):  # Si la position est après la fin, ajouter à la fin
            new_dict[key] = value
        return new_dict
    
    def add_value_to_object(self, obj, path, key, value):
        """
        Ajoute une clé et une valeur dans un objet en suivant un chemin donné.
        
        :param obj: L'objet racine contenant les données.
        :param path: Chemin sous forme de string, ex: "root.data.chance".
        :param key: La clé à ajouter.
        :param value: La valeur associée à la clé.
        """
        # On retire "root" du chemin car obj est déjà root
        keys = path.split(".")[1:]  
        
        current = obj
        for k in keys:
            if k not in current:
                current[k] = {}  # Création du chemin s'il n'existe pas
            current = current[k]  # Accès au niveau suivant

        # Ajout de la nouvelle clé et valeur
        current[key] = value


    def detect_date_format(self, date_input):
        """
        Détecte le format d'une date et le retourne sous forme d'une string format (ex: "%Y-%m-%d").
        Si c'est un timestamp en millisecondes, retourne "unix".
        
        :param date_input: str | int - La date sous forme de chaîne ou de timestamp.
        :return: str - Le format détecté (ex: "%Y-%m-%d") ou "unix" si timestamp.
        """
        # Si l'entrée est un entier, vérifier s'il s'agit d'un timestamp en millisecondes
        if isinstance(date_input, int) or (isinstance(date_input, str) and date_input.isdigit()):
            if len(str(date_input)) == 13:  # Timestamp en millisecondes
                return "unix"
        
        if isinstance(date_input, str):
            try:
                parsed_date = parser.parse(date_input)  # Détection automatique du format
                format_str = date_input
                
                # Remplacement des éléments reconnus par leur format respectif
                format_str = re.sub(r'\b\d{4}\b', "%Y", format_str)  # Année à 4 chiffres
                format_str = re.sub(r'\b\d{2}\b', "%m", format_str, 1)  # Premier nombre à 2 chiffres = Mois
                format_str = re.sub(r'\b\d{2}\b', "%d", format_str, 1)  # Deuxième nombre à 2 chiffres = Jour

                # Nettoyage des caractères non standards
                return format_str if "%" in format_str else "Unknown format"

            except (ValueError, OverflowError):
                return "Invalid date format"

        return "Invalid input"
    








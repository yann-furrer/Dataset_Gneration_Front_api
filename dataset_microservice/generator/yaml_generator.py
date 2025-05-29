import os, sys, time, json
import asyncio
from typing import Any, List, Tuple, Dict

# Ajouter le dossier racine (project/) au chemin d'import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from utils.chatgpt_api import ChatGPTAsyncClient
from generator.utils_generator import extract_keys, get_type_name, YamlUtils, extract_keys_values
# start_time = time.time()
faker_functions = json.load(open("generator/faker_data/faker_category.json"))



class GPTClassifier:
    def __init__(self, prompt_file: str) -> None:
        """Initialise le classificateur avec l'API Key et charge les prompts."""
        self.gpt_client = ChatGPTAsyncClient(api_key= os.getenv("OPENAI_API_KEY"))
   
    async def classify_values(self, yaml_data: dict, pass_first_index: bool = False) -> List[str]:
        """
        Classe les valeurs du dictionnaire en fonction de leur type.
        Fait appel à l'API GPT si nécessaire.
        """

        # [{}, '101', 'Alice Johnson', 'Software Engineer', 'id123', [], '0612345678', 'JavaScript', 'AWS', {}, 101, 'furrer.yann@gmail.com', '0612345678', '127.0.0.1', '1990-01-01', 'bordeaux', [], 'Python', 'JavaScript', 'AWS']
        extracted_values , r = extract_keys_values(yaml_data)
        extracted_keys =  extract_keys(yaml_data)
        type_list = []
        type_to_gpt_list = []

        # Déterminer le type de chaque valeur
        print("extracted_values : ", extracted_values[1:])
        for i, value in enumerate(extracted_values[1:]):

            print("value key : ", value, extracted_keys[i])
            # print("key : ", extracted_keys)
            value_type = get_type_name(value)
            print("value_type : ", value_type)
            if value_type.startswith("GPT"):
                type_to_gpt_list.append((i, value_type, value, extracted_keys[i]))
            else:
                type_list.append(value_type)

        # Si des types nécessitent un appel à GPT, les traiter
        if type_to_gpt_list:
            # print("[type_list]", type_to_gpt_list)
            gpt_category_results = await self._gpt_classify_category(type_to_gpt_list)
            print("gpt_category_results : ", gpt_category_results)
            gpt_results = await self._gpt_classify_values(type_to_gpt_list, gpt_category_results)
            for (index, _, _, _), gpt_type in zip(type_to_gpt_list, gpt_results):
                type_list.insert(index, gpt_type)
        #ne compte pas {} ou [] de départ

        if pass_first_index:
            return type_list
        else:
            return type_list
        

    async def _gpt_classify_category(self, type_to_gpt_list: List[Tuple[int, str, Any]]) -> List[str]:
        """Effectue les appels GPT pour classifier les catégories nécessitant une intervention IA."""
        
        tasks = []
        # print("type_to_gpt_list : ", type_to_gpt_list)
        for _, gpt_type, value, key in type_to_gpt_list:
            print(str(f"{{'{key}': '{value}'}}"))
            # print(" --->",gpt_type.split("GPT"))
            # prompt_index = int(gpt_type.split("GPT")[1])
            system_message_prompt = self.gpt_client.select_prompt(0)
            task = asyncio.create_task(
                self.gpt_client.make_api_call(
                    str(f"{{'{key}': '{value}'}}"),
                    system_message_prompt,
                    max_tokens=20,
                    temperature=1,
                    response_format="text"
                )
            )
            tasks.append(task)
        return await asyncio.gather(*tasks)

    async def _gpt_classify_values(self, type_to_gpt_list: List[Tuple[int, str, Any]], gpt_category_results: List[str]) -> List[str]:
        """Effectue les appels GPT pour classifier les valeurs nécessitant une intervention IA."""
        tasks = []
        for counter, (_, gpt_type, value, key) in enumerate(type_to_gpt_list):
            prompt_index = int(gpt_type.split("GPT")[1])
            system_message_prompt = self.gpt_client.select_prompt(prompt_index)
            # print( " category -->",counter,  _ , gpt_type, value)
            # print("gpt_category_results : ", gpt_category_results[counter])
            # print("concat : ", faker_functions["faker.providers."+gpt_category_results[counter]])
            # print("fkaerteest : ", faker_functions["faker.providers.person"])
            # print("faker : ", faker_functions["faker.providers."+gpt_category_results[counter]])

            system_message_prompt = system_message_prompt.replace("{fonction}", '" '.join(faker_functions["faker.providers."+gpt_category_results[counter]]))
            print(str(f"{{'{key}': '{value}'}}"))
            task = asyncio.create_task(
                self.gpt_client.make_api_call(
                     str(f"{{'{key}': '{value}'}}"),
                    system_message_prompt,
                    max_tokens=20,
                    temperature=1,
                    response_format="text"
                )
            )
            tasks.append(task)
        return await asyncio.gather(*tasks)


    async def _gpt_nned_realism(self, type_to_gpt_list: List[Tuple[int, str, Any]]) -> List[str]:
        """Effectue les appels GPT pour classifier les catégories nécessitant une intervention IA."""
        
        tasks = []
        # print("type_to_gpt_list : ", type_to_gpt_list)
        for _, gpt_type, value, key in type_to_gpt_list:
            print(str(f"{{'{key}': '{value}'}}"))
            # print(" --->",gpt_type.split("GPT"))
            # prompt_index = int(gpt_type.split("GPT")[1])
            system_message_prompt = self.gpt_client.select_prompt(0)
            task = asyncio.create_task(
                self.gpt_client.make_api_call(
                    str(f"{{'{key}': '{value}'}}"),
                    system_message_prompt,
                    max_tokens=20,
                    temperature=1,
                    response_format="text"
                )
            )
            tasks.append(task)
        return await asyncio.gather(*tasks)










class YamlGenerator(YamlcUtils):
    def __init__(self, dataset_name: str, sample_data: dict,number_of_records: int, entrytpath: str = "root") -> None:
        """Initialise le générateur de YAML avec les paramètres."""
       
        self.dataset_name = dataset_name
        self.sample_data = sample_data
        self.number_of_records = number_of_records
        self.entrytpath = entrytpath # point d'entrée du json
        self.index = 0  # Index pour parcourir type_list
        
    def get_next_type(self, type_list : List[str] = None) -> str:
        """
        Retourne le prochain type dans self.type_list et incrémente l'index.
        """
        # print("type list\n", type_list)
        if self.index < len(type_list):
            type_name = type_list[self.index]
            self.index += 1

            return type_name

        return "unknown"  # Valeur par défaut si la liste est épuisée
    
    def get_value_from_path(self, data):
        return super().get_value_from_path(data, self.entrytpath)
    
    def build_structure(self, flat_data, type_of_builder="bone" or "field"):
        return super().build_structure(flat_data, type_of_builder, self.dataset_name, self.number_of_records, self.entrytpath)
    
    def flatten_object(self, obj, level=0, parent_key='', type_list: List[str] = None, is_root=False):
        """
        Aplati une structure imbriquée en une liste de champs avec leurs types et niveaux.
        Args:obj (dict): Objet à flatten
            level (int): Niveau de l'objet
            parent_key (str): Clé parente de l'objet
            parent_start (str): Clé de départ de l'objet
        """

        items = []
        # print("type_list flatten: ",type_list)
        if isinstance(obj, dict):
            for key, value in obj.items():
                # on remplace la valeur {} ou [] par le type sous forme de nom
                
                type_name = "array" if value == [] else "object" if value == {} else self.get_next_type(type_list)
                # print("type_name : ---> ", type_name)
                items.append({'name': key, 'exemple_value': type_name, 'value': value, 'level': level})
                if isinstance(value, (dict, list)):
                    items.extend(self.flatten_object(value, level + 1, parent_key=key, type_list=type_list))
        
        elif isinstance(obj, list):
            for idx, item in enumerate(obj, start=1):
                type_name = self.get_next_type(type_list)
                name = f"{parent_key}_{idx}"
                # Inclure l'indice pour différencier les éléments de liste
                items.append({'name': name, 'exemple_value': type_name, 'level': level})
               
                if isinstance(item, (dict, list)):
                    items.extend(self.flatten_object(item, level + 1, parent_key=name, type_list=type_list))

        else:
            print("type non gérée : ", type(obj))
            
        if is_root:
            # SI nous accedons simplement au chemin de base nous devons supprumer les accolades représentant l'objet {} ou []
            # car le générateur le gère par défaut 
            return items[1:]
        return items
    

    async def process_section(self, 
        section_data: Any,
        section_key: str,
        is_root: bool,
        pass_first_index: bool = False
    ) -> Dict[str, Any]:
        """
        Traite une section du YAML :
          - Classification
          - Flattening
          - Construction de la structure finale
          Construit la structure du YAML en fonction de la valeur de entrytpath.
        """
        classifier = GPTClassifier("Dataset_Back_compute/utils/prompt.txt")
        type_list = await classifier.classify_values(section_data, pass_first_index=pass_first_index)
        self.index = 0  # Réinitialisation de l'index avant de flatten l'objet
        flattened = self.flatten_object(section_data, type_list=type_list, is_root=is_root)
        return self.build_structure(flattened, section_key)





    async def execute(self, isApi: bool = True) -> Dict[str, Any]:
        """
        Traite les données YAML en fonction de la valeur de entrytpath.
        Pour entrytpath == "root", on retourne uniquement les 'fields'.
        Sinon, on traite à la fois les 'bones' et les 'fields'.
        :param isApi: bool - True si l'exécution est effectuée par l'API, False sinon.
        """

        # Instanciation des outilsx
        # generator = YamlGenerator(dataset_name=self.dataset_name, ,number_of_records=self.number_of_records, entrytpath=self.entrytpath)
        

    
        if self.entrytpath == "root":
            print("Traitement en mode 'root'")
            yaml_structured = self.get_value_from_path(self.sample_data)
            print('yaml_structured', yaml_structured)
            built_structure = await self.process_section( yaml_structured, "fields", is_root=True, pass_first_index=True)
            if isApi == False:
                # Ecriture du fichier dans le dossier config
                self.write_yaml(built_structure, self.dataset_name)
                print("write finished")
                return built_structure
            else:
                print("finished")
                print(built_structure)
                return built_structure

        else:
            print("Traitement en mode champ imbriqué")
            # Extraction de la section fields depuis le chemin donné
            yaml_structured_fields = self.get_value_from_path(yaml_data)
            print('yaml_structured_fields', yaml_structured_fields)

            # Préparation de la section bones : on part d'une copie du YAML d'origine
            yaml_structured_bones = yaml_data.copy()
            # On détermine la clé à vider (la dernière clé de entrytpath)
            bone_key_to_delete = next(reversed(self.entrytpath.split(".")))
            if bone_key_to_delete in yaml_structured_bones:
                yaml_structured_bones[bone_key_to_delete] = {} if isinstance(yaml_structured_bones[bone_key_to_delete], dict) else []

            # Traitement séparé des bones et des fields
            built_bones = await self.process_section(yaml_structured_bones, "bones", is_root=False)
            built_fields = await self.process_section(yaml_structured_fields, "fields", is_root=False, pass_first_index=True)

            # Intégration des bones dans les fields
            yaml_generated = self.insert_in_dict(built_fields, "bones", built_bones["bones"], 2)
          
            if isApi == False:
                self.write_yaml(yaml_generated, self.dataset_name)
                print("finished")
                return yaml_generated
            else:
                print("finished")
                return yaml_generated






 



    












    
































yaml_data = {
        "id": "101",
        "name": "Alice Johnson",
        "role": "Software Engineer",
        "test_id" : 'id123',
        "sk": ["0612345678", "JavaScript", "AWS"],
        "company": "AWS",
        "entreprise": "AZURE",
        "hh": {
            "yann": 101,
            "mail": "furrer.yann@gmail.com",
            "number": "0612345678",
            "iptest": "127.0.0.1",
            "date de naissance": "1990-01-01",
            "ville": "bordeaux",
            "skills": ["Python", "JavaScript", "AWS"]
        }
    }



optician =[{
    "id": "client_id_1" ,
    "firstname": "Yann",
    "name": "Furrer",
    "ville": "Bordeaux",
    "date de naissance": "1990-01-01",
    "type de mutuel": 0.5,
    "budget": 1000,
    "travail": "soudeur",
    "forme du visage": "rectangulaire",
    "marque favorite" : "Rayban" 

}]

if __name__ == "__main__":
    test_generator = YamlGenerator(dataset_name="yann",sample_data=yaml_data, number_of_records=1000, entrytpath="root")
    a = asyncio.run(test_generator.execute(False))
    end_time = time.time()

    # print(f"Temps d'exécution : {end_time - start_time:.6f} secondes")
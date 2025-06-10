# Gère toutes les fonctions permettant d'utiliser des types fakers
import os, sys, json, uuid
import asyncio
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from utils.mongo_db_provider import MongoDBManager
from utils.chatgpt_api import ChatGPTAsyncClient
from typing import List, Optional
from collections import defaultdict



with open("./utils/prompt_sample.txt", "r", encoding="utf-8") as fichier:
    prompt_txt = fichier.read()
# Séparer les prompts en utilisant le séparateur "=seprateur="
prompts_list = prompt_txt.split("==separateur==")

with open("./generator/faker_data/faker_category.json", "r", encoding="utf-8") as fichier:
    faker_category: dict = defaultdict(list)
    faker_category : dict = json.load(fichier)
    faker_cateogry_keys = list(faker_category.keys())

class FakerHandler(MongoDBManager, ChatGPTAsyncClient):
    def __init__(self, faker_type_name: str = None, faker_type_id: str = None, client_id: str = "12345") -> None:
        MongoDBManager.__init__(self)
        ChatGPTAsyncClient.__init__(self)
        self.client_id = client_id
        self.faker_type_name = faker_type_name
        self.faker_type_id = faker_type_id
        self.faker_category_list: dict = defaultdict(list)  # Crée automatiquement des listes pour les nouvelles clés
        self.faker_category_keys: dict = defaultdict(list)  # Crée automatiquement des listes pour les nouvelles clés
        self.faker_category_list , self.faker_category_keys = self.initfaker_category(self.client_id)


  
    #note pour plus tard : ajouter la pagination pour les types fakers
    # https://codebeyondlimits.com/articles/pagination-in-mongodb-the-only-right-way-to-implement-it-and-avoid-common-mistakes
    def get_faker_type_on_mongo_db_by_client_id(self, client_id: str) -> Optional[dict]:
        """
        Récupère un type faker par son ID et son client_id.
        
        Args:
            client_id (str): L'ID du client pour lequel le type faker est associé.
        
        Returns:
            dict: Le type faker trouvé ou None si aucun type faker n'est trouvé.
        """
        if not client_id:
            raise ValueError("Aucun client_id fourni.")
        # Implémentation de la recherche dans la base de données MongoDB
        result = self.find_many({"client_id": client_id})
        return result


    def clean_string(self,faker_category):
        # Si la chaîne est vide ou déjà correcte, on la retourne telle quelle
        #strip() pour enlever les espaces superflus
        faker_category = faker_category.rstrip(' ').replace('\n', '').strip()

        if not faker_category or (faker_category.startswith('[') and faker_category.endswith(']')):
            return faker_category

        # Si la chaîne commence par [ mais ne se termine pas par ]
        if faker_category.startswith('[') and not faker_category.endswith(']'):
            # On ajoute le ] manquant
            if faker_category.endswith(',"'):
                print("passe1")
                faker_category = faker_category[:-2] + ']'
            elif faker_category.endswith(', "'):
                print("passe2")
                faker_category = faker_category[:-3] + ']'
            elif faker_category.endswith(',  "'):

                faker_category = faker_category[:-4] + ']'
            elif faker_category.endswith(','):
                print("passe4")
                faker_category = faker_category[:-1] + ']'
            elif faker_category.endswith('"'):
                print("passe5")
                faker_category = faker_category + ']'
            else:
                print("passe6")
                faker_category = faker_category + '"]'
        else:
            # Cas où la chaîne ne commence pas par [, on l'ajoute
            faker_category = '["' + faker_category + '"]'

        return faker_category
    

    def insert_faker_type_on_mongo_db(self, faker_type_name: str, faker_type_id: str, faker_list: List[str], category: str,  client_id: str, description : str = "No description") -> bool:
        """
        Insère un type faker dans la base de données MongoDB.
        """
        if not faker_type_name and not faker_type_id and not faker_list and not client_id and not category:
            raise ValueError("Nom, ID et valeurs requises pour l'insertion.")
        # Implémentation de l'insertion dans la base de données MongoDB
        self.add_one({"faker_type_name": faker_type_name, "client_id": client_id, 
                "faker_type_id": faker_type_id, "description": description,
                "category": category, "list": json.loads(faker_list)})


    #  fonction pour supprimer un type faker par son nom ou id sur mongo db 
    def delete_faker_type_on_mongo_db(self, faker_type_id: str = None, client_id: str = None) -> bool:
        """
        Supprime un type faker de la base de données MongoDB.
        
        Args:
            faker_type_name (str): Le nom du type faker à supprimer.
        """
        if not faker_type_id and not client_id:
            raise ValueError("Aucun type faker à supprimer.")
        # Implémentation de la suppression dans la base de données MongoDB
        return self.delete_one_by_filter({"faker_type_id": faker_type_id , "client_id": client_id})


    def update_faker_type_on_mongo_db(self, faker_id: str, new_faker_list: List[str], client_id: str) -> bool:
        """
        Met à jour les valeurs d'un type faker dans la base de données MongoDB.
        
        Args:
            faker_id (str): L'ID du type faker à mettre à jour.
            faker_values (List[str]): La liste des nouvelles valeurs par défaut.
        """
        if not faker_id or not new_faker_list:
            raise ValueError("ID du type faker et valeurs requises pour la mise à jour.")
        # Implémentation de la mise à jour dans la base de données MongoDB
        result = self.update_one({"faker_id": faker_id, "client_id": client_id}, {"$set": {"list": new_faker_list}})


    # Fonction pour générer une liste de valeurs Faker automatiquement via l'API ChatGPT
    async def generate_faker_list_IA_auto(self, elem_to_analyze: dict, client_id: str ) -> str:
        """
        Génère une liste de valeurs Faker automatiquement via l'API ChatGPT.
        
        Args:
            elem_to_analyze (str): L'élément à analyser pour générer des valeurs Faker ex "compagny": "AWS".
        
        Returns:
            List[str]: Une liste de valeurs Faker générées.
        """
      
        faker_exist_response = await self.check_faker_type_exists(faker_type_name=str(elem_to_analyze), client_id=client_id)
      
        if faker_exist_response["newCategory"] == False:
            print("Le type faker existe dans la base de données MongoDB.")
            return faker_exist_response["function"]
        
        else :
            faker_info :str = await self.make_api_call(str(elem_to_analyze), system_message=prompts_list[4].replace("{categories}", str(faker_cateogry_keys)), max_tokens=120, temperature=1, response_format="text") 
            faker_data :str = await self.make_api_call(str(elem_to_analyze), system_message=prompts_list[1], max_tokens=150, temperature=1, response_format="text")
            faker_info = json.loads(faker_info)
            faker_data = self.clean_string(faker_data) # Nettoyage de la chaîne pour s'assurer qu'elle est au format JSON valide

            self.insert_faker_type_on_mongo_db(
                faker_type_name=faker_info.get("name", None),
                faker_type_id=str(uuid.uuid4().hex[:12] ), # Génère un ID unique pour le type faker, 
                faker_list=faker_data,  # La liste sera remplie par la suite
                category=faker_info.get("category", None),  # Utilise la catégorie par défaut si non trouvée
                client_id=client_id,
            )
            #Les default dict ne sont pas initialisés
            if not self.faker_category_list.get(faker_info.get("category", None)):
                self.faker_category_list[faker_info.get("category", None)] = []
                
                self.faker_category_list[faker_info.get("category", None)].append(faker_data)
            else:
                self.faker_category_list[faker_info.get("category", None)].append(faker_data)
            # Retourne le nom du type faker généré
            return faker_info.get("name", None)

        

    async def check_faker_type_exists(self, faker_type_name: str, client_id: str) -> dict:
        """
        Vérifie si un type faker existe déjà dans la base de données MongoDB.
        
        Args:
            faker_type_name (str): Le nom du type faker à vérifier.
            client_id (str): L'ID du client pour lequel le type faker est associé.
        """
        if not faker_type_name or not client_id:
            raise ValueError("Nom et ID du client requis pour la vérification.")

        check_faker_info = await self.make_api_call(str(faker_type_name), 
                        system_message=prompts_list[2].replace("{liste categories}", str(self.faker_category_keys)), 
                        max_tokens=120, temperature=0, response_format="text"
                        )
        check_faker_info = json.loads(check_faker_info)

        if check_faker_info["newCategory"] == False: # cas ou la catégorie existe déjà  
            function_name = await self.make_api_call(str(faker_type_name), 
                        system_message=prompts_list[3].replace("{fonction}", str(self.faker_category_list[check_faker_info["category"]])), 
                        max_tokens=120, temperature=1, response_format="text"
                        )
            if function_name != "empty":
                
                return check_faker_info.update({"function": function_name})
        
        return check_faker_info
        


    def initfaker_category(self, client_id: str) -> dict:
        """
        Initialise la liste des catégories Faker à partir du fichier JSON.
        """
        faker_category_user_list : dict = self.get_faker_type_on_mongo_db_by_client_id(client_id=client_id)
        faker_category = defaultdict(list)  # Crée automatiquement des listes pour les nouvelles clés

        for item in faker_category_user_list:
            faker_category[item["category"]].append(item["faker_type_name"])

        return dict(faker_category), list(faker_category.keys())
        
# a = FakerHandler()
# # a.check_faker_type_exists(faker_type_name="company", client_id="12345")
# asyncio.run(a.generate_faker_list_IA_auto({"company": "AWS"}, client_id="12345"))
# # asyncio.run(a.check_faker_type_exists({"gay": "kljkjnjknhkj"}, client_id="12345"))
# # a.update_faker_type_on_mongo_db(faker_id="12345", new_faker_list=["new_value1", "new_value2"])
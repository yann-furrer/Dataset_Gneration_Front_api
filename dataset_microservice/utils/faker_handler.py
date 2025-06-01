# Gère toutes les fonctions permettant d'utiliser des types fakers
import os, sys
from utils.mongo_db_provider import MongoDBManager
from utils.chatgpt_api import ChatGPTAsyncClient
from typing import List, Optional



class FakerHandler(MongoDBManager, ChatGPTAsyncClient):
    def __init__(self, faker_type_name: str = None, faker_type_id: str = None):
        MongoDBManager.__init__(self)
        ChatGPTAsyncClient.__init__(self)
        self.faker_type_name = faker_type_name
        self.faker_type_id = faker_type_id


  
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


    def insert_faker_type_on_mongo_db(self, faker_type_name: str, faker_type_id: str, faker_list: List[str], category: str,  client_id: str, description : str) -> bool:
        """
        Insère un type faker dans la base de données MongoDB.
        
        Args:
            faker_type_name (str): Le nom du type faker à insérer.
            faker_type_id (str): L'ID du type faker à insérer.
            faker_list (List[str]): La liste des valeurs par défaut.
        """
        if not faker_type_name and not faker_type_id and not faker_list and not client_id and not category:
            raise ValueError("Nom, ID et valeurs requises pour l'insertion.")
        # Implémentation de l'insertion dans la base de données MongoDB
        result = self.add_one({"faker_type_name": faker_type_name, "client_id": client_id, "faker_type_id": faker_type_id, "description": description, "category": category, "list": faker_list})


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
    def genereate_faker_list_IA_auto(self):
        pass
    # Fonction pour générer une liste de valeurs Faker via l'API ChatGPT à parti des informations fournies par l'utilisateur
    def genereate_faker_list_IA(self, description: Optional[str], faker_value_input: Optional[dict],) -> List[str]:
        pass

# test
# a = FakerHandler()
# a.delete_faker_type_on_mongo_db(faker_type_name="test_faker")
# a.update_faker_type_on_mongo_db(faker_id="12345", new_faker_list=["new_value1", "new_value2"])
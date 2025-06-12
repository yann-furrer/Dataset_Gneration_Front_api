import os, sys
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, PyMongoError
from dotenv import load_dotenv
from typing import Dict, List, Any, Optional, Union
from bson import ObjectId
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

load_dotenv()

class MongoDBManager:
    def __init__(self):
        """
        Initialise la connexion à MongoDB
        x
        Args:
            database_name: Nom de la base de données (par défaut utilise 'Faker')
        """
        self.connection_string = os.getenv("MONGO_DB")
        self.database_name = os.getenv("MONGO_DB_NAME")
        self.client = None
        self.db = None
        self._connect()
    
    def _connect(self):
        """Établit la connexion à MongoDB"""
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client[self.database_name]
            print(f"✅ Connexion réussie à la base de données: {self.database_name}")
        except Exception as e:
            print(f"❌ Erreur de connexion à MongoDB: {e}")
            raise
    
    def get_collection(self, collection_name: str = None):
        """
        Récupère une collection
        
        Args:
            collection_name: Nom de la collection (par défaut utilise la variable d'environnement)
        
        Returns:
            Collection MongoDB
        """
        collection_name = collection_name or os.getenv("MONGO_DB_COLLECTION")
        return self.db[collection_name]
    
    # ======================== FONCTIONS D'AJOUT ========================
    
    def add_one(self, document: Dict[str, Any], collection_name: str = None) -> bool:
        """
        Ajoute un seul document
        
        Args:
            document: Document à ajouter
            collection_name: Nom de la collection
        
        Returns:
            ID du document inséré ou None en cas d'erreur
        """
        try:
            collection = self.get_collection(collection_name)
            result = collection.insert_one(document)
            print(f"✅ Document ajouté avec l'ID: {result.inserted_id}")
            return True
        except DuplicateKeyError:
            print(f"❌ Erreur: Document avec cet ID existe déjà")
            return False
        except PyMongoError as e:
            print(f"❌ Erreur lors de l'ajout: {e}")
            return False
    
    def add_many(self, documents: List[Dict[str, Any]], collection_name: str = None) -> List[str]:
        """
        Ajoute plusieurs documents
        
        Args:
            documents: Liste des documents à ajouter
            collection_name: Nom de la collection
        
        Returns:
            Liste des IDs des documents insérés
        """
        try:
            collection = self.get_collection(collection_name)
            result = collection.insert_many(documents, ordered=False)
            inserted_ids = [str(id) for id in result.inserted_ids]
            print(f"✅ {len(inserted_ids)} documents ajoutés")
            return inserted_ids
        except Exception as e:
            print(f"❌ Erreur lors de l'ajout multiple: {e}")
            return []
    
    # ======================== FONCTIONS DE SUPPRESSION ========================
    
    def delete_one_by_id(self, document_id: Union[str, ObjectId], collection_name: str = None) -> bool:
        """
        Supprime un document par son ID
        
        Args:
            document_id: ID du document à supprimer
            collection_name: Nom de la collection
        
        Returns:
            True si supprimé, False sinon
        """
        try:
            collection = self.get_collection(collection_name)
            # Gère les ObjectId et les strings
            if isinstance(document_id, str) and len(document_id) == 24:
                try:
                    document_id = ObjectId(document_id)
                except:
                    pass  # Garde la string si ce n'est pas un ObjectId valide
            
            result = collection.delete_one({"_id": document_id})
            if result.deleted_count > 0:
                print(f"✅ Document avec l'ID {document_id} supprimé")
                return True
            else:
                print(f"❌ Aucun document trouvé avec l'ID {document_id}")
                return False
        except PyMongoError as e:
            print(f"❌ Erreur lors de la suppression: {e}")
            return False
    
    def delete_one_by_filter(self, filter_dict: Dict[str, Any], collection_name: str = None) -> bool:
        """
        Supprime un document selon un filtre
        
        Args:
            filter_dict: Dictionnaire de filtrage
            collection_name: Nom de la collection
        
        Returns:
            True si supprimé, False sinon
        """
        try:
            collection = self.get_collection(collection_name)
            result = collection.delete_one(filter_dict)
            if result.deleted_count > 0:
                print(f"✅ Document supprimé selon le filtre: {filter_dict}")
                return True
            else:
                print(f"❌ Aucun document trouvé avec le filtre: {filter_dict}")
                return False
        except PyMongoError as e:
            print(f"❌ Erreur lors de la suppression: {e}")
            return False
    
    def delete_many(self, filter_dict: Dict[str, Any], collection_name: str = None) -> int:
        """
        Supprime plusieurs documents selon un filtre
        
        Args:
            filter_dict: Dictionnaire de filtrage
            collection_name: Nom de la collection
        
        Returns:
            Nombre de documents supprimés
        """
        try:
            collection = self.get_collection(collection_name)
            result = collection.delete_many(filter_dict)
            print(f"✅ {result.deleted_count} documents supprimés")
            return result.deleted_count
        except PyMongoError as e:
            print(f"❌ Erreur lors de la suppression multiple: {e}")
            return 0
    
    # ======================== FONCTIONS DE RECHERCHE ========================


    def get_grouped_faker_types_by_client(
        self,
        client_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Récupère pour un client donné la liste des faker_types
        groupés par category, chacun ne conservant que faker_type_id et faker_type_name.
        """
        try:
            coll = self.get_collection()
            pipeline = [
                { "$match": { "client_id": client_id }},

                # parser JSON si besoin
                { "$addFields": {
                    "category": {
                      "$function": {
                        "body": """
                          function(cat) {
                            try { 
                              const o = JSON.parse(cat);
                              return o.category || cat;
                            }
                            catch(e) { return cat; }
                          }
                        """,
                        "args": ["$category"],
                        "lang": "js"
                      }
                    }
                }},

                # on renomme dans le $push
                { "$sort": { "category": 1, "faker_type_name": 1 }},

                { "$group": {
                    "_id": "$category",
                    "types": {
                        "$push": {
                            "id":   "$faker_type_id",
                            "name": "$faker_type_name"
                        }
                    }
                }},

                { "$project": {
                    "_id": 0,
                    "category": "$_id",
                    "types": 1
                }}
            ]

            docs = list(coll.aggregate(pipeline))
            # transforme la liste en mappage clé=categorie → valeur=types
            return { d["category"]: d["types"] for d in docs }  

        except PyMongoError as e:
            print(f"❌ Erreur lors de l’agrégation groupée: {e}")
            return []
    
    def find_one(self, filter_dict: Dict[str, Any] = None, collection_name: str = None) -> Optional[Dict]:
        """
        Trouve un document
        
        Args:
            filter_dict: Dictionnaire de filtrage
            collection_name: Nom de la collection
        
        Returns:
            Document trouvé ou None
        """
        try:
            collection = self.get_collection(collection_name)
            filter_dict = filter_dict or {}
            return collection.find_one(filter_dict)
        except PyMongoError as e:
            print(f"❌ Erreur lors de la recherche: {e}")
            return None
    
    def find_many(self, filter_dict: Dict[str, Any] = None, collection_name: str = None, limit: int = 0, projection_dict: Dict[str, Any] = None) -> List[Dict]:
        """
        Trouve plusieurs documents
        
        Args:
            filter_dict: Dictionnaire de filtrage
            collection_name: Nom de la collection
            limit: Limite du nombre de résultats (0 = pas de limite)
        
        Returns:
            Liste des documents trouvés
        """
        try:
            collection = self.get_collection(collection_name)
            filter_dict = filter_dict or {}
            cursor = collection.find(filter_dict, projection=projection_dict)  # Exclut l'ID par défaut
            if limit > 0:
                cursor = cursor.limit(limit)
            return list(cursor)
        except PyMongoError as e:
            print(f"❌ Erreur lors de la recherche multiple: {e}")
            return []
    
    def count_documents(self, filter_dict: Dict[str, Any] = None, collection_name: str = None) -> int:
        """
        Compte les documents selon un filtre
        
        Args:
            filter_dict: Dictionnaire de filtrage
            collection_name: Nom de la collection
        
        Returns:
            Nombre de documents
        """
        try:
            collection = self.get_collection(collection_name)
            filter_dict = filter_dict or {}
            return collection.count_documents(filter_dict)
        except PyMongoError as e:
            print(f"❌ Erreur lors du comptage: {e}")
            return 0
    
    # ======================== FONCTIONS DE MISE À JOUR ========================
    
    def update_one(self, filter_dict: Dict[str, Any], update_dict: Dict[str, Any], collection_name: str = None) -> bool:
        """
        Met à jour un document
        
        Args:
            filter_dict: Dictionnaire de filtrage
            update_dict: Dictionnaire de mise à jour
            collection_name: Nom de la collection
        
        Returns:
            True si mis à jour, False sinon
        """
        try:
            collection = self.get_collection(collection_name)
            # Ajoute $set si pas d'opérateur MongoDB
            if not any(key.startswith('$') for key in update_dict.keys()):
                update_dict = {"$set": update_dict}
            
            result = collection.update_one(filter_dict, update_dict)
            if result.modified_count > 0:
                print(f"✅ Document mis à jour")
                return True
            else:
                print(f"❌ Aucun document modifié")
                return False
        except PyMongoError as e:
            print(f"❌ Erreur lors de la mise à jour: {e}")
            return False
        
    def update_one_by_filter(self, filter_query: Dict[str, Any], update_query : Dict[str, Any]) -> bool:
         """
         Met à jour un document selon un filtre
         
         Args:
               filter_dict: Dictionnaire de filtrage
               update_dict: Dictionnaire de mise à jour
               collection_name: Nom de la collection
         
         Returns:
               True si mis à jour, False sinon
         """
         return self.update_one(filter_query, update_query)
    
    # ======================== FONCTIONS UTILITAIRES ========================
    
    def drop_collection(self, collection_name: str = None) -> bool:
        """
        Supprime une collection entière
        
        Args:
            collection_name: Nom de la collection
        
        Returns:
            True si supprimée, False sinon
        """
        try:
            collection = self.get_collection(collection_name)
            collection.drop()
            print(f"✅ Collection {collection_name or os.getenv('MONGO_DB_COLLECTION')} supprimée")
            return True
        except PyMongoError as e:
            print(f"❌ Erreur lors de la suppression de la collection: {e}")
            return False
    
    def close_connection(self):
        """Ferme la connexion à MongoDB"""
        if self.client:
            self.client.close()
            print("✅ Connexion fermée")

# ======================== EXEMPLE D'UTILISATION ========================

# if __name__ == "__main__":
#     # Initialisation
#     db_manager = MongoDBManager()
    
#     # Données d'exemple
#     item_1 = {
#         "_id": "U1IT00001",
#         "item_name": "Blender",
#         "max_discount": "10%",
#         "batch_number": "RR450020FRG",
#         "price": 340,
#         "category": "kitchen appliance"
#     }
    
#     item_2 = {
#         "_id": "U1IT00002",
#         "item_name": "Egg",
#         "category": "food",
#         "quantity": 12,
#         "price": 36,
#         "item_description": "brown country eggs"
#     }
    
#     # =============== EXEMPLES D'AJOUT ===============
#     print("\n=== AJOUT DE DOCUMENTS ===")
#     # Ajouter un document
#     db_manager.add_one(item_1)
    
#     # Ajouter plusieurs documents
#     db_manager.add_many([item_1, item_2])
    
#     # =============== EXEMPLES DE RECHERCHE ===============
#     print("\n=== RECHERCHE DE DOCUMENTS ===")
#     # Trouver un document
#     found_item = db_manager.find_one({"item_name": "Blender"})
#     print(f"Document trouvé: {found_item}")
    
#     # Trouver tous les documents d'une catégorie
#     food_items = db_manager.find_many({"category": "food"})
#     print(f"Articles alimentaires: {len(food_items)}")
    
#     # Compter les documents
#     total_items = db_manager.count_documents()
#     print(f"Total d'articles: {total_items}")
    
#     # =============== EXEMPLES DE SUPPRESSION ===============
#     print("\n=== SUPPRESSION DE DOCUMENTS ===")
#     # Supprimer par ID
#     # db_manager.delete_one_by_id("U1IT00001")
    
#     # Supprimer par filtre
#     # db_manager.delete_one_by_filter({"item_name": "Egg"})
    
#     # Supprimer plusieurs documents
#     # db_manager.delete_many({"category": "food"})
    
#     # =============== EXEMPLES DE MISE À JOUR ===============
#     print("\n=== MISE À JOUR DE DOCUMENTS ===")
#     # Mettre à jour le prix
#     db_manager.update_one(
#         {"_id": "U1IT00001"},
#         {"price": 350, "updated": True}
#     )
    
#     # Fermer la connexion
#     db_manager.close_connection()

import os
import boto3
from botocore.exceptions import NoCredentialsError
from botocore.config import Config
from datetime import datetime
from dotenv import load_dotenv

import requests
load_dotenv()

class S3Manager:
    def __init__(self):
        """Initialisation de la connexion AWS S3 avec la signature v4 et les credentials depuis .env."""
        self.config = Config(signature_version='s3v4')
        self.session = boto3.Session(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
            region_name=os.getenv("AWS_REGION", "eu-north-1")
        )
        
        self.s3_client = self.session.client('s3', region_name=os.getenv("AWS_REGION", "eu-north-1"), config=self.config)
        self.bucket_name = os.getenv("BUCKET_NAME")

    def upload_file(self, file_path, client_id, end_format=".json"):
        file_path = "./dataset/"+file_path+"."+end_format
        """Upload un fichier dans un sous-dossier S3 basé sur le client_id."""
        # timestamp = datetime.now().strftime("%Y-%m-%d")
        # object_key = f"{client_id}/{os.path.basename(file_path)}"
        object_key = f"{client_id}/{ os.path.basename(file_path)}"
        try:
            self.s3_client.upload_file(file_path, self.bucket_name, object_key, ExtraArgs={'ACL': 'private'})
            print(f"✅ Fichier uploadé: {object_key}")
            return object_key
        except NoCredentialsError:
            print("❌ Erreur: Credentials AWS manquants")
            return None
        except Exception as e:
            print(f"❌ Erreur lors de l'upload: {e}")
            return None

    def generate_presigned_url(self, client_id, file_name, expiration=900)-> str:
        """Génère une URL pré-signée pour qu'un utilisateur télécharge son fichier."""
        object_key = f"{client_id}/{file_name}"
        
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': object_key},
                ExpiresIn=expiration
            )
            return url
        except Exception as e:
            print(f"❌ Erreur lors de la génération de l'URL pré-signée: {e}")
            return None
        
    def delete_uploaded_file_locally(self, file_path, yaml_path, rule_path = None,  end_format=".json"):
        #supprimes les fichiers locaux après la génération
        dataset_path = "./dataset/"+file_path+end_format
        yaml_path = "./config/"+yaml_path
        rule_path = "./config/"+rule_path if rule_path else None
        rule_reverse_path = "./config/"+rule_path.replace(".json", "_reversed.json") if rule_path else None



        """Supprime le fichier téléchargé localement."""
        try:
            for file in [dataset_path, yaml_path, rule_path, rule_reverse_path]:
                os.remove(file)
           
                print(f"✅ Fichier supprimé: {file}")
        except FileNotFoundError:
                print(f"❌ Fichier non trouvé: {file}")
        except Exception as e:
                print(f"❌ Erreur lors de la suppression du fichier: {e}")

    def download_file(self, client_id, dataset_config_id):
        """Télécharge un fichier depuis le bucket S3 en fonction du client_id et du datasetConfigId."""
        dataset_system_name :str = requests.get(f"{os.getenv('API_URL')}/get_dataset_system_name?datasetConfigId={dataset_config_id}&userId={client_id}").json()
        dataset_system_name = dataset_system_name["dataset_system_name"]
        print("dataset_system_name ", dataset_system_name, flush=True)
        object_key = f"{client_id}/{dataset_system_name}"
        try:
            self.s3_client.download_file(self.bucket_name, object_key, "./datapool/"+dataset_system_name)
            print(f"✅ Fichier téléchargé: {dataset_system_name}")
            return dataset_system_name
        except Exception as e:
            print(f"❌ Erreur lors du téléchargement du fichier: {e}")
            return None
       
# # Exemple d'utilisation
# if __name__ == "__main__":
#     s3_manager = S3Manager()
#     client_id = "client_123"
#     file_path = "./config/e.py"
#     print(os.path.basename(file_path))

#     # Upload fichier
#     file_key = s3_manager.upload_file(file_path, client_id)
#     # s3_manager.delete_uploaded_file_locally(file_path)
#     # Génération de l'URL sécurisée pour téléchargement
#     if file_key:
#         url = s3_manager.generate_presigned_url(client_id, os.path.basename(file_key))
#         print(f"🔗 URL sécurisée: {url}")

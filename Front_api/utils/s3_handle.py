import os
import boto3
from botocore.exceptions import NoCredentialsError
from botocore.config import Config
from datetime import datetime
from dotenv import load_dotenv

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
        self.s3_url_expiration = os.getenv("S3_URL_EXPIRATION", 3600)
        
        self.s3_client = self.session.client('s3', region_name=os.getenv("AWS_REGION", "eu-north-1"), config=self.config)
        self.bucket_name = os.getenv("BUCKET_NAME")

    def upload_file(self, file_path, client_id, end_format=".json"):
        file_path = "./dataset/"+file_path+end_format
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

    def generate_presigned_url(self, client_id :str, file_name: str)-> str:
        """Génère une URL pré-signée pour qu'un utilisateur télécharge son fichier."""
        object_key = f"{client_id}/{file_name}"
        
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': object_key},
                ExpiresIn=self.s3_url_expiration
            )
            return url
        except Exception as e:
            print(f"❌ Erreur lors de la génération de l'URL pré-signée: {e}")
            return None
        
    def delete_uploaded_file_locally(self, file_path, end_format=".json"):
        file_path = "./dataset/"+file_path+end_format
        """Supprime le fichier téléchargé localement."""
        try:
            os.remove(file_path)
            print(f"✅ Fichier supprimé: {file_path}")
        except FileNotFoundError:
            print(f"❌ Fichier non trouvé: {file_path}")
        except Exception as e:
            print(f"❌ Erreur lors de la suppression du fichier: {e}")
       
    def delete_s3_file(self, client_id :str, file_name: str) ->bool:
        """Supprime le fichier S3 d'un client."""
        object_key = f"{client_id}/{file_name}"
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=object_key)
            print(f"✅ Fichier supprimé: {object_key}")
            return True
        except Exception as e:
            print(f"❌ Erreur lors de la suppression du fichier: {e}")
            return False
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
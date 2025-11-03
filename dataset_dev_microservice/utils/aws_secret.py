# Use this code snippet in your app.
# If you need more information about configurations
# or implementing the sample code, visit the AWS docs:
# https://aws.amazon.com/developer/language/python/
import json
import boto3
from botocore.exceptions import ClientError

print("test")
def get_secret():

    secret_name = "dev/syntetica/microservice-dev"
    region_name = "eu-west-3"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    secret = get_secret_value_response['SecretString']
    return secret


# Crée un fichier .env à partir du secret récupéré
def create_env_file_from_secret():
    """
    Récupère le secret depuis AWS Secrets Manager et crée un fichier .env
    """
    secret_obj = get_secret()
# 1️⃣ Convertir en dict si le secret est une chaîne JSON
    if isinstance(secret_obj, str):
        try:
            secret_obj = json.loads(secret_obj)
        except json.JSONDecodeError:
            raise ValueError("Le secret fourni n'est pas un JSON valide")

    # 2️⃣ Créer le contenu du fichier .env
    lines = []
    for key, value in secret_obj.items():
        if value is None:
            continue
        lines.append(f"{key}={value}")

    env_content = "\n".join(lines)
    print(env_content)
    # 3️⃣ Écrire le fichier .env
    with open(".env", "w", encoding="utf-8") as f:
        f.write(env_content)

    print("✅ Fichier .env créé avec succès")


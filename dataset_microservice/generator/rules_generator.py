import os
import sys
from typing import TypedDict
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from utils.pg_db_provider import session , text
from utils.chatgpt_api import ChatGPTAsyncClient
load_dotenv()

with open("./generator/rules_prompt.txt", "r") as file:
    prompt = file.read()



class Condition(TypedDict):
    name: str
    operator: str
    value: bool


class ActionParams(TypedDict):
    field_name: str
    value: str
    random_anomalie_number: int
    avoid_field: list[str]


class RulesGenerator(ChatGPTAsyncClient):
    """
    Cette classe permet de générer des règles pour les jeux de données
    depuis une description textuelle.

    """

    def __init__(self):
        super().__init__() # Initialisation du client ChatGPT
        
        self.rules = [{}]
        self.dict_var = {}  # Dictionnaire pour stocker les variables et leurs types
        self.yaml_config = {}



    async def generate_rules(self, user_prompt: str) -> str:
        """
        Génère un dataset de type sample via l'API ChatGPT.
        Args:
            user_prompt (str): Prompt utilisé pour générer le dataset.
           
        Returns:
            str: Le dataset de type sample généré via l'API ChatGPT.
        """

        system_prompt = prompt.replace("[variables]", str(self.dict_var))
        dataset_sampled = await self.make_api_call(prompt=user_prompt, system_message=system_prompt, max_tokens=400, temperature=1, response_format="text")
        return dataset_sampled

    def get_yaml_config_file_by_id(self, user_id: str, dataset_id: str):
        """Récupère le fichier de configuration YAML par son ID."""
        SELECT_YAML_CONTENT_BY_DATASET_CONFIG_ID = """
            SELECT "yamlContent" FROM public."DatasetConfig" WHERE "datasetId" = :datasetId AND "userId" = :userId;
            """

        try:
            request = session.execute(
                text(SELECT_YAML_CONTENT_BY_DATASET_CONFIG_ID),
                {"datasetId": dataset_id, "userId": user_id},
            )
            response = request.fetchone()
            self.yaml_config = (
                dict(response._mapping)["yamlContent"] if response else []
            )

        except Exception as e:
            print(
                f"Erreur lors de la récupération du fichier de configuration YAML : {e}"
            )


    def parse_yaml_config(self, yaml_config: dict, dict_of_variables=None) -> dict:
        if dict_of_variables is None:
            dict_of_variables = []

        for variable in yaml_config["fields"]:
            name = variable["fieldName"]
            type_variable = variable.get("type") or variable.get("fakerType")

            if type_variable == "object" or type_variable == "array"  and "fields" in variable:
                # Appel récursif avec accumulation
                self.parse_yaml_config(variable, dict_of_variables)
            else:
                dict_of_variables.append({"nom": name, "type": type_variable})
        self.dict_var = dict_of_variables
        return dict_of_variables


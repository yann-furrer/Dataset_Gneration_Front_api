# from core.dataset_config.dataset_config_select import core_select_rules_config_by_dataset_config_id
from fastapi import HTTPException
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("FRONT_API_URL")
rules_test = [
    {
        "conditions": {
            "all": [
                {"name": "bool", "operator": "is_true", "value": True},
                {"name": "test", "operator": "is_true", "value": True},
            ]
        },
        "actions": [
            {
                "name": "setNull",
                "params": {
                    "field_name": "all",
                    "value": "null",
                    "random_anomalie_number": 3,
                    "avoid_field": ["payload", "lecteur"],
                },
            }
        ],
        "occurrences": 100,
    },
    {
        "conditions": {
            "all": [{"name": "bool1", "operator": "is_false", "value": True}]
        },
        "actions": [{"name": "nothing"}],
        "occurrences": 12,
    },
]


class RulesUtils:
    def __init__(
        self,
        rules_content: dict,
        rules_id: str,
        dataset_config_id: str,
        api_key: str,
        type_config: str = "rules_id",
    ):
        self.rules_content = rules_content
        self.rules_id = rules_id
        self.dataset_config_id = dataset_config_id
        self.api_key = api_key
        self.type_config = type_config  # peut etre rules_id ou rules_content
        self.rules_content: dict = self._get_rules_content()

    def _get_rules_content(self) -> dict:
        if self.type_config == "rules_id":
            pass
            # self.rules_content = self.get_rules_content_by_rules_id()
        elif self.type_config == "rules_content":
            self.rules_content = self.rules_content
        else:
            raise ValueError("type_config must be rules_id or rules_content")
        return self.rules_content

    def get_dataset_config_variables(self) -> dict:
        response = requests.get(
            f"{API_URL}/dev/rules/get_yaml_content_by_dataset_config_id?datasetId={self.dataset_config_id}&api_key={self.api_key}"
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(
                status_code=400,
                detail="Error while selecting dataset config by dataset id",
                headers={"WWW-Authenticate": "Bearer"},
            )

        print(response.json())

    def load_specified_faker(self):
        pass

    def load_dataset_config(self):
        pass

    def check_rules(self)-> list:
        # variables_dict : dict = self.get_dataset_config_variables()
        variables_dict = {
            "join_2": "id",
            "join_3bis": "object",
            "salaire": "integer",
            "email": "email",
            "taille": "integer",
        }
        variables_name_list: list = list(variables_dict.keys())
        data = self.rules_content
        operator_list = {
            "bool": ["is_true", "is_false"],
            "integer": [
                "less_than",
                "greater_than",
                "less_than_or_equal_to",
                "greater_than_or_equal_to",
                "equal_to",
                "not_equal",
            ],
            "float": [
                "less_than",
                "greater_than",
                "less_than_or_equal_to",
                "greater_than_or_equal_to",
                "equal_to",
                "not_equal",
            ],
            "string": ["contains", "not_contains", "equal_to", "not_equal"],
            "id": ["equal_to", "not_equal"],
            "date": [
                "less_than",
                "greater_than",
                "less_than_or_equal_to",
                "greater_than_or_equal_to",
                "equal_to",
                "not_equal",
            ],
        }
        
        temp_error_dict = []
        for condition in data:
            # print("fds",data[0], "\n")
            # Gère le cas ou une occurrence est manquante
            if data[0].get("occurrences") < 1:
                temp_error_dict.append({"occurences": "must be greater than 10"})
            # Gère le cas ou il n'y a pas de condition dans le all
            elif len(condition["conditions"].get("all", [])) < 1:
                temp_error_dict.append({"all": "must be defined"})
            # Gère le cas vérifiant les opérateurs
            elif len(condition["conditions"].get("all", [])) >= 1:
                condition_list = condition["conditions"].get("all", [])
                print("condition_list -->", condition_list, "\n")
                for elem in condition_list:
                    print("elem -->", elem)
                    variable_name = elem.get("name", None)
                    operator = elem.get("operator", "")
                    operator_value = elem.get("value")

                    variable_type: str = variables_dict.get(
                        condition_list[0].get("name"), "error"
                    )
                    # Veriffie si la varibale existe dans le dataset config et le rules
                    if variable_name not in variables_name_list:
                        temp_error_dict.append(
                            f"must be a valid variable {elem.get('name')}"
                        )
                    # Vérification du type
                    if variables_dict.get(variable_name, "Error") in (
                        "integer",
                        "float",
                        "string",
                        "id",
                        "bool",
                    ) and variables_dict.get(variable_name, "Error") not in (
                        "array",
                        "object",
                    ):
                        temp_error_dict.append(
                            {
                                "operator": f"le type de la variable n'est pas valide {variable_type}"
                            }
                        )
                    # Vérification de l'opérateur
                    elif operator not in operator_list.get(variable_type, ()) or variable_type in ("array", "object"):
                        temp_error_dict.append(
                            {
                                "operator": f"le type de la variable n'est pas valide {variable_type}"
                            }
                        )
                    # Vérification de la valeur
                    elif operator in operator_list.get(variable_type) or variable_type not in ("array", "object"):
                        
                        if variable_type in ("integer", "float") and type(operator_value) not in (int, float):
                            temp_error_dict.append(
                                {
                                    "operateur value": f"la valeur de l'operateur n'est pas valide {operator_value}, {variable_name}"
                                }
                            )
                        elif variable_type in ("string", "id", "date") and type(operator_value) not in (str, int):
                            #voir plus tard pour vriament analyser les types de date ...
                            temp_error_dict.append(
                                {
                                    "operateur value": f"la valeur de l'operateur n'est pas valide {operator_value}, {variable_name}"
                                }
                            )
                        elif variable_type in ("bool") and type(operator_value) not in (bool, int):
                            temp_error_dict.append(
                                {
                                    "operateur value": f"la valeur de l'operateur n'est pas valide {operator_value}, {variable_name}"
                                }
                            )
                        elif variable_type not in ("bool", "integer", "float", "string", "id", "date", "array", "object") and type(operator_value) is not str:
                            #pour les types fakers qui sont en général des chaines de caractères
                            temp_error_dict.append(
                                {
                                    "operateur value": f"la valeur de l'operateur n'est pas valide {operator_value}, {variable_name}"
                                }
                            )

        #Note pour plus tard ajouter le check des données faker du user
        return temp_error_dict

                    



# test = RulesUtils(
#     rules_content=rules_test,
#     rules_id="",
#     dataset_config_id="388467e9bfef42a8a5d88a93d84d919d",
#     api_key="dsg-867407fa5a0c4456",
# )

# res = test.check_rules()
# print(res)
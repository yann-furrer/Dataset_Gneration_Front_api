import json, yaml, re

# Ouvre la liste des types fakers
with open("./core/fakerlist.json", "r") as f:
    faker_list = json.load(f)
    set_faker_list = set(faker_list)






def list_variables_type(yaml_content: dict, number_list: list = None, date_list: list = None) -> tuple[list, list]:
    """
    Liste récursivement les champs de type number (integer, float) et date
    """
    if number_list is None:
        number_list = []
    if date_list is None:
        date_list = []

    for variable in yaml_content.get("fields", []):
        field_name = variable.get("fieldName", "<inconnu>")
        var_type = variable.get("type", "empty")
        if var_type in ("integer", "float"):
            number_list.append(field_name)
        elif var_type == "date":
            date_list.append(field_name)

        # Récursivité : si c’est un objet ou un tableau contenant d’autres champs
        if var_type in ("array", "object") and "fields" in variable:
            list_variables_type(variable, number_list, date_list)
    return number_list, date_list



def check_fakertype_is_valid(fakerType : str) -> bool:
    """
    Vérifie si le type est valide
    """
    if fakerType in set_faker_list:
        return True
    else :
        return False



def parsing_value(yaml_content : str, number_list : list, date_list : list, end_format: str) -> bool:
    error_list = []
    for variable in yaml_content.get("fields", []):
        field_name = variable.get("fieldName", "<inconnu>")
        faker_type = variable.get("fakerType")
        var_type = variable.get("type", "empty")

        # 3. Si c'est un type composite, lancer la récursion
        if var_type in ("array", "object"):
            temp_error_list = check_rules_is_valid(variable, var_type, number_list, date_list, end_format)
            if temp_error_list != []:
                error_list.extend(temp_error_list)
            parsing_value(variable, number_list, date_list, end_format)
        # 1. Vérifie si un fakerType est défini
        if faker_type:
            if not check_fakertype_is_valid(faker_type):
                error_list.append(
                    f"Dans le champ '{field_name}', le fakerType '{faker_type}' n'existe pas. Détail : {variable}"
                )
        
        # 2. Sinon on vérifie le type
        else:
            temp_error_list = check_rules_is_valid(variable, var_type, number_list, date_list, end_format)
            if temp_error_list != []:
                error_list.extend(temp_error_list)

    return error_list


def check_yaml_is_valid(yaml_content : dict, user_id : str = "", end_format: str = "") -> list:
    """
    Parse le yaml et vérifie si tous les champs types sont valides
    retourne la liste des erreurs trouvées
    isvalid : bool
    error : list
    """
    number_list, date_list = list_variables_type(yaml_content)
    errors = parsing_value(yaml_content, number_list, date_list, end_format)
    isvalid = True
    if errors != []:
        isvalid = False
    error_list : dict = { "isvalid" : isvalid, "error" : errors}


    return error_list










def check_rules_is_valid(rules : dict, type_config : str, number_list : list, date_list : list, end_format: str) -> list:
        """
        Vérifie si les règles sont valides
        """
        error_list = []
        if type_config in ("float", "integer"):
            for field in rules:
                if not re.match(r"^wf\d+$", field) and field not in ("fieldName", "type", "rules", "correlation", "correlation_target", "allowedValues", "seasonnality"):
                    error_list.append(f"Dans le champ '{rules.get('fieldName')}', le champ '{field}' n'est pas valide.")

                elif not field.startswith("wf") and re.match(r"^wf\d+$", field) :
                    error_list.append(f"Dans le champ '{rules.get('fieldName')}', le champ '{field}' n'est pas valide. vous avec un problème de workflow")

                elif field == "allowedValues" and isinstance(rules.get("allowedValues"), list):
                    if not all(isinstance(x, (int, float)) for x in rules.get("allowedValues")):
                        error_list.append(f"Dans le champ '{rules.get('fieldName')}', le champ 'allowedValues' : {rules.get('allowedValues')} n'est pas valide il doit être un nombre ou un float.")
                                # Vérofoier si allowedValues est défini
                if field == "seasonnality" :
                    if isinstance(rules.get("seasonnality"), str):
                        if rules.get("seasonnality") not in date_list:
                            error_list.append(f"Dans le champ '{rules.get('fieldName')}', le champ 'seasonality' : {rules.get('seasonality')} n'est pas dans la liste des champs de type date.")
                    else : 
                        error_list.append(f"Dans le champ '{rules.get('fieldName')}', le champ 'seasonality' : {rules.get('seasonality')} n'est pas valide c'est une string indiquant un champ de type date.")

                if field == "correlation_target":
                            if isinstance(rules.get("correlation_target"), str):
                                if rules.get("correlation_target") not in number_list:
                                    error_list.append(f"Dans le champ '{rules.get('fieldName')}', le champ 'correlation_target' : {rules.get('correlation_target')} n'est pas dans la liste des champs de type integer ou float.")
                            else:  
                                error_list.append(f"Dans le champ '{rules.get('fieldName')}', le champ 'correlation_target' : {rules.get('correlation_target')} n'est pas valide c'est une string indiquant un champ de type integer ou float.")

                if field == "correlation":
                    if  isinstance(rules.get("correlation"), (int, float)):
                        if -1 < rules.get("correlation") > 1:
                            error_list.append(f"Dans le champ '{rules.get('fieldName')}', le champ 'correlation' : {rules.get('correlation')} n'est pas valide c'est une valeur entre -1 et 1.")
                    else:
                        error_list.append(f"Dans le champ '{rules.get('fieldName')}', le champ 'correlation' : {rules.get('correlation')} n'est pas valide elle doit être un nombre ou un float.")
                    
                
                
                
                if field == "rules":
                    for rule in rules.get("rules"):
                   
                        if rule not in ( "range", "correlation", "coorelation_target"):
                            error_list.append(f"Dans le champ '{rules.get('fieldName')}', le champ '{rule}' n'est pas valide ou. mal imbriqué.")
                            
                        
                        if rules.get("rules").get("range") != None or rules.get("rules").get("range") != None:
                            if not isinstance(rules.get("rules").get("range").get("min"), int) or not isinstance(rules.get("rules").get("range").get("max"), int):
                                error_list.append(f"Dans le champ '{rules.get('fieldName')}', le champ 'range' : {rules.get('range')} n'est pas valide c'est une valeur entre -1 et 1.")
                                
                
        if type_config in ("boolean"):
            for rule in rules:
                if rule not in ("fieldName", "type", "rules"):
                    error_list.append(f"Dans le champ '{rules.get('fieldName')}', le champ '{rule}' n'est pas valide.")
                if rule == "rules":
                    if rules.get("rules") is not  None:
                        for elem in rules.get("rules").get("range"):
                            
                            if elem == "probability":
                                if isinstance(rules.get("rules").get("range").get("probability"), (int , float)):
                                    if 0 < rules.get("rules").get("range").get("probability") > 1:
                                        error_list.append(f"Dans le champ '{rules.get('fieldName')}', le champ 'probability' : {rules.get('probability')} n'est pas valide c'est une valeur entre 0 et 1.")
                                else :
                                    error_list.append(f"Dans le champ '{rules.get('fieldName')}', le champ 'probability' : {rules.get('probability')} n'est pas valide cela doit être un nombre ou un float.")
                            else:
                                error_list.append(f"Dans le champ '{rules.get('fieldName')}', le champ {elem} n'est pas valide.")
                    else :
                        error_list.append(f"Dans le champ '{rules.get('fieldName')}', le champ 'rules ne peux pas être vide ")

        if type_config in ("date"):
            for rule in rules:
                if rule not in ("fieldName", "type", "rules", "format"):
                        error_list.append(f"Dans le champ '{rules.get('fieldName')}', le champ '{rule}' n'est pas valide.")
                elif rule == "rules":
                    rules_values = rules.get("rules")
                    if any(char.isalpha() for char in rules_values.get("range").get("start")) and any(char.isalpha() for char in rules_values.get("range").get("end")):
                        error_list.append(f"Dans le champ '{rules.get('fieldName')}', le champ 'range' : {rules.get('range')} n'est pas valide, il ne doit pas contenir de lettre.")
                    if rules_values.get("series") is not None:
                        if rules_values.get("series") not in ["days", "months", "years", "hours", "minutes"]:
                            error_list.append(f"Dans le champ '{rules.get('fieldName')}', le champ 'series' : {rules.get('series')} n'est pas valide il ne peut être 'days', 'months', 'years', 'hours' ou 'minutes'.")
                    
                    #Améloire la vérification de format
                  
                    if not isinstance(rules_values.get("format"), str):   
                        error_list.append(f"Dans le champ '{rules.get('fieldName')}', le champ 'format' : {rules.get('format')} n'est pas valide il doit être une string.")
                    if rules_values.get("series_gap") != None: 
                        if not isinstance(rules_values.get("series_gap"), int):
                            error_list.append(f"Dans le champ '{rules.get('fieldName')}', le champ 'series_gap' : {rules.get('series_gap')} n'est pas valide il doit être un nombre entier.")
               

        if type_config in ("id"):
                for rule in rules:
                    print(" pattern_part_of_dataset -->", rules.get("pattern_part_of_dataset"), type(rules.get("pattern_part_of_dataset")))

                    if rule not in ("fieldName", "type", "rules", "includeLetters", "includeNumbers", "includeSpecialChars", "start_by", "pattern", "pattern_max_cycle", "pattern_part_of_dataset"):
                        error_list.append(f"Dans le champ '{rules.get('fieldName')}', le champ '{rule}' n'est pas valide.")
                   
                    elif rule == "includeLetters" and isinstance(rules.get("includeLetters"), bool):
                        error_list.append(f"Dans le champ '{rules.get('fieldName')}', le champ 'includeLetters' : {rules.get('includeLetters')} n'est pas valide il doit être un booléen.")
                   
                    elif rule == "includeNumbers" and isinstance(rules.get("includeNumbers"), bool):
                        error_list.append(f"Dans le champ '{rules.get('fieldName')}', le champ 'includeNumbers' : {rules.get('includeNumbers')} n'est pas valide il doit être un booléen.")
                   
                    elif rule == "includeSpecialChars" and isinstance(rules.get("includeSpecialChars"), bool):
                        error_list.append(f"Dans le champ '{rules.get('fieldName')}', le champ 'includeSpecialChars' : {rules.get('includeSpecialChars')} n'est pas valide il doit être un booléen.")
                   
                    elif rule == "start_by" and isinstance(rules.get("includeLetters"), str):
                        error_list.append(f"Dans le champ '{rules.get('fieldName')}', le champ 'start_by' : {rules.get('start_by')} n'est pas valide il doit être une string.")
                   
                    elif rule == "pattern" and rules.get("pattern") != "type":
                        error_list.append(f"Dans le champ '{rules.get('fieldName')}', le champ 'pattern' : {rules.get('pattern')} n'est pas valide il doit être égale à 'type'.")
                   
                    elif rule == "pattern_max_cycle" and isinstance(rules.get("pattern_max_cycle"), (int, float)) is False:
                        error_list.append(f"Dans le champ '{rules.get('fieldName')}', le champ 'pattern_max_cycle' : {rules.get('pattern_max_cycle')} n'est pas valide il doit être un nombre entier.")
                   
                    elif rule == "pattern_part_of_dataset" and isinstance(rules.get("pattern_part_of_dataset"), (int, float)) is False:
                        error_list.append(f"Dans le champ '{rules.get('fieldName')}', le champ 'pattern_part_of_dataset' : {rules.get('pattern_part_of_dataset')} n'est pas valide il doit être un nombre entier.")
        
                    elif rule == "pattern_part_of_dataset" and isinstance(rules.get("pattern_part_of_dataset"), (int, float)) and 0 < rules.get("pattern_part_of_dataset") >= 1:
                        error_list.append(f"Dans le champ '{rules.get('fieldName')}', le champ 'pattern_part_of_dataset' : {rules.get('pattern_part_of_dataset')} n'est pas valide il doit être un nombre entre 0 et 1.")
                    
                    elif rule == "pattern_max_cycle" and isinstance(rules.get("pattern_max_cycle"), (int, float)) and 0 < rules.get("pattern_max_cycle") > 50 :
                            error_list.append(f"Dans le champ '{rules.get('fieldName')}', le champ 'pattern_max_cycle' : {rules.get('pattern_max_cycle')} n'est pas valide il doit être un nombre entre 0 et 50.")
                    

                  
        if type_config in ("string"):
                for rule in rules:
                    if not re.match(r"^wf\d+$", rule) and rule not in ("fieldName", "type", "rules", "distribution", "allowedValues", "rule"):
                        error_list.append(f"Dans le champ '{rules.get('fieldName')}', le champ '{rule}' n'est pas valide.")
                    elif rule.startswith("wf") and re.match(r"^wf\d+$", rule) == False:
                       error_list.append(f"Dans le champ '{rules.get('fieldName')}', le champ '{rule}' n'est pas valide. vous avec un problème de workflow")
                   
                    elif rule == "distribution" and isinstance(rules.get("distribution"), list):
                        if all(isinstance(x, (int, float)) for x in rules.get("distribution")):
                            if 0< sum(rules.get("distribution")) > 1:
                                error_list.append(f"Dans le champ '{rules.get('fieldName')}', le champ 'distribution' : {rules.get('distribution')} n'est pas valide il doit être un nombre entre 0 et 1.")
                        else:
                            error_list.append(f"Dans le champ '{rules.get('fieldName')}', le champ 'distribution' : {rules.get('distribution')} n'est pas valide il doit être un nombre ou un float.")
                                # Vérofoier si allowedValues est défini
                        if rules.get("allowedValues", None) != None:
                            if isinstance(rules.get("allowedValues"), list):
                                if len(rules.get("rules").get("allowedValues")) != len(rules.get("distribution")):
                                            error_list.append(f"Dans le champ '{rules.get('fieldName')}', le champ 'allowedValues' : {rules.get('allowedValues')} n'est pas valide il doit être un nombre ou un float.")
                            else:
                                error_list.append(f"Dans le champ '{rules.get('fieldName')}', le champ 'allowedValues' : {rules.get('allowedValues')} n'est pas valide il doit être un nombre ou un float.")
        if type_config in ("array"):
                if end_format == "csv":
                    error_list.append(f"Dans le champ '{rules.get('fieldName')} n'est pas valide les csv ne supportent pas les tableaux")
                for rule in rules:
                    if rule not in ("fieldName", "type", "count", "fields", "rules"):
                        error_list.append(f"Dans le champ '{rules.get('fieldName')}', le champ '{rule}' n'est pas valide.")
                    if rule == "rules":
                        for elem in rules.get("rules"):
                            if elem == "count" and not isinstance(rules.get("rules").get("count"), (int, float)):
                                error_list.append(f"Dans le champ '{rules.get('fieldName')}', le champ 'count' : {rules.get('count')} n'est pas valide il doit être un nombre ou un float.")
                            if elem != "count":
                                error_list.append(f"Dans le champ '{rules.get('fieldName')}', le champ {elem} n'est pas valide et n'existe pas dans la liste des règles.")
        if type_config in ("object"):
                if end_format == "csv":
                    error_list.append(f"Dans le champ '{rules.get('fieldName')}', n'est pas valide les csv ne supportent pas les objets")
                for rule in rules:
                    if rule not in ("fieldName", "type", "fields"):
                        error_list.append(f"Dans le champ '{rules.get('fieldName')}', le champ '{rule}' n'est pas valide.")
                  
        if type_config not in ("float", "integer", "string", "bool", "date", "array", "object", "id") or type_config == None:
                error_list.append(f"Dans le champ '{rules.get('fieldName')}', le champ 'type' n'est pas valide, il ne peut être 'float', 'integer', 'string', 'boolean', 'date', 'array', 'object' ou 'id'.")
        return error_list


# data = yaml.safe_load(open("/Users/yann/Documents/GitHub/Dataset_Gneration_Front_api/fields.yaml", "r"))
# print(check_yaml_is_valid(data))

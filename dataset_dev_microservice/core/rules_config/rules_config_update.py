from fastapi import HTTPException

from database.queries.rules_config.rules_config_update import insert_or_update_rules_config


def core_insert_or_update_rules_config(
    rules_id: str,
    user_id: str,
    rules_name: str,
    rules_content: dict,
    dataset_config_id: int,
    campaign_id: str = None,
) -> bool:
    """
    save rules config
    """

    # Ajouter une fonction pour vérifier les règles mais pour cela il faut
    #appeler et récup les variable du dataset config
    reuslt_request = insert_or_update_rules_config(
        rules_id, user_id, rules_name, rules_content, dataset_config_id
    )

    if reuslt_request:
        return True
    else:
        raise HTTPException(
            status_code=400,
            detail="Error while inserting rules config",
            headers={"WWW-Authenticate": "Bearer"},
        )   
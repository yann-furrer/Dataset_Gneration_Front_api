
import os
import sys
from config import text, session
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from sqlalchemy.dialects.postgresql import JSONB

from sqlalchemy import bindparam


INSERT_OR_UPDATE_DATAMESH = """
INSERT INTO public."DataMesh"(
	"datameshName", "userId", "DatameshData", "datameshId" , "updatedAt")
	VALUES ( :datameshName, :userId, :DatameshData, :datameshId, now())
    ON CONFLICT ( "datameshId") DO UPDATE
    SET "DatameshData" = :DatameshData, "datameshName" = :datameshName, "updatedAt" = now();
    """
   
def insert_dataset_config(
    datameshId: str,
    userId: str,
    DatameshData: dict,
    datameshName: str,
) -> bool:
    try:
        session.execute(
            text(INSERT_OR_UPDATE_DATAMESH).bindparams(
    bindparam("DatameshData", type_=JSONB)),
            {
                "datameshId": datameshId,
                "userId": userId,
                "DatameshData": DatameshData,
                "datameshName": datameshName,
               
            },
        )
        session.commit()

        return True
    except Exception as e:
        session.rollback()
        print("Error while inserting datamesh config", e)
        return False
    

DELETE_DATAMESH_BY_DATAMESH_ID = """
DELETE FROM public."DataMesh" WHERE "datameshId" = :datameshId AND "userId" = :userId;
"""

def delete_datamesh_by_datamesh_id(datameshId: str, userId: str) -> bool:
    try:
        session.execute(text(DELETE_DATAMESH_BY_DATAMESH_ID), {"datameshId": datameshId, "userId": userId})
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print(f"Error while deleting datamesh by datamesh id + {userId}", e)
        return False
    

SELECT_DATAMESH_BY_DATAMESH_ID = """
SELECT "id" , "datameshName", "datameshId", "DatameshData" FROM public."Datamesh" WHERE "datameshId" = :datameshId AND "userId" = :userId;
"""

def select_datamesh_by_datamesh_id(datameshId: str, userId: str) -> bool:
    try:
        request = session.execute(text(SELECT_DATAMESH_BY_DATAMESH_ID), {"datameshId": datameshId, "userId": userId})
        result = request.fetchone()
        return result
    except Exception as e:
        session.rollback()
        print(f"Error while selecting datamesh by datamesh id {datameshId}", e)
        return False
    

SELECT_ALL_DATAMESH_BY_USER_ID = """
SELECT "id" , "datameshId", "datameshName", "updatedAt" FROM public."Datamesh" WHERE "userId" = :userId
ORDER BY "updatedAt" DESC
OFFSET :offset_min ROWS
FETCH NEXT :offset_max ROWS ONLY;
"""

def select_all_datamesh_by_user_id(userId: str, offset: int) -> bool:
     # offset et le numero de page
    # "offset" is the number of row to skip
    # "offset_max" is the number of row to take

    nb_rows_to_return = 10
    offset_min = offset * nb_rows_to_return
    offset_max = offset_min + nb_rows_to_return
    try:
        request = session.execute(text(SELECT_ALL_DATAMESH_BY_USER_ID), {"userId": userId, "offset_min": offset_min, "offset_max": offset_max})
        result = request.fetchall()
        return result
    except Exception as e:
        session.rollback()
        print(f"Error while selecting all datamesh by user id {userId}", e)
        return False
    


SELECT_DATASET_HISTORICAL_OFFSET = """
SELECT "id", "nbRows", "datasetConfigId","ownerId", "campaignId", "status", "FinishedAt", "TimeToGenerate" , "datasetName", "datasetNameSystem"
FROM public."Dataset"
WHERE "ownerId" = :ownerId
ORDER BY "FinishedAt" DESC
OFFSET :offset_min ROWS
FETCH NEXT :offset_max ROWS ONLY;
"""


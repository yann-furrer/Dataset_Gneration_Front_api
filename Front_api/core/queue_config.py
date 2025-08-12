import pika
import json, os, uuid
from typing import TypedDict, Optional
from dotenv import load_dotenv
load_dotenv()

CELERY_USER = os.getenv("CELERY_USER")
CELERY_PASSWORD = os.getenv("CELERY_PASSWORD")
CELERY_URL = os.getenv("CELERY_URL")
CELERY_PORT = os.getenv("CELERY_PORT")
CELERY_QUEUE_NAME = "celery"



#Schema de contenue de la tache
class TaskSchema(TypedDict):
    id: str

    dataset_id_row: str
    function: int
    dataset_name: str
    client_id: str
    end_format: str = "json"
    yaml_content : dict
    faker_name_list : Optional[list]
    rules: Optional[dict]
    request_type: Optional[str]
    dataset__config_parent_id : Optional[str]
    dataset_fields_list =   Optional[list]


# Utilisation
task: TaskSchema = {
    "id": 1,
    "dataset_id_row": "uuid",
    "name": "Jean Dupont",
    "email": "jean@example.com",
    "active": True,
    "age": 30
}

def send_message_to_celery_queue(message_body: TaskSchema):
    """
    Send a raw message directly to the Celery queue using Pika
    
    Args:
        message_body: The content to send as a message (will be serialized to JSON)
    """
    credentials = pika.PlainCredentials(CELERY_USER, CELERY_PASSWORD)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=CELERY_URL,
            port=CELERY_PORT,
            credentials=credentials
        )
    )
    
    channel = connection.channel()
    
    # Ensure queue exists
    channel.queue_declare(queue=CELERY_QUEUE_NAME, durable=True)
    
    # For Celery to properly recognize the task, you need appropriate message properties
    # For a properly formatted Celery task:
    task_name = "api_config.celery.celery_worker.process_list_task" 
    task_data = message_body
    
    # Format for Celery
    celery_task = {
        "id": str(uuid.uuid4()),
        "task": task_name,
        "args": [json.dumps(task_data, default=str)],  # Args must match your task's expected parameters
        "kwargs": {},  
        "retries": 0
    }
    
    # Publish the message
    channel.basic_publish(
        exchange='',
        routing_key=CELERY_QUEUE_NAME,  # Usually 'celery'
        body=json.dumps(celery_task),
        properties=pika.BasicProperties(
            delivery_mode=2,  # Persistent message
            content_type='application/json',
            content_encoding='utf-8',
        )
    )
    
    print(f"Message sent to {CELERY_QUEUE_NAME}")
    connection.close()


# # # Example to call your mock function for test queue
# mock_task = {
#     "function": "mock"  
# }

# for i in range(10):
#     send_message_to_celery_queue(mock_task)
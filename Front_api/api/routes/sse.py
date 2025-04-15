from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse
import asyncio
import json

router = APIRouter()
user_connections = {}

@router.get("/sse/{user_id}")
async def sse(user_id: str):
    if user_id not in user_connections:
        user_connections[user_id] = asyncio.Queue()

    async def event_generator():
        try:
            while True:
                message = await user_connections[user_id].get()
                yield f"data: {json.dumps({'message': message})}\n\n"
        except asyncio.CancelledError:
            del user_connections[user_id]

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.post("/notify/{user_id}")
async def notify(user_id: str, message: str):
    if user_id in user_connections:
        await user_connections[user_id].put(message)
        return {"status": "Message envoyé"}
    raise HTTPException(status_code=404, detail="Utilisateur non connecté")

@router.post("/compute-done/")
async def compute_done(user_id: str, background_tasks: BackgroundTasks):
    message = f"Votre tâche est terminée, utilisateur {user_id} !"
    background_tasks.add_task(notify, user_id=user_id, message=message)
    return {"status": "Notification en cours"}
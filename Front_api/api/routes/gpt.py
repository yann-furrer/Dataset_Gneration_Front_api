from fastapi import APIRouter, HTTPException, Request
from core.chatpgt import GPT_prompt, dataset_generation_system_message

router = APIRouter()

@router.post("/free_gpt_dataset_generation")
async def free_gpt_dataset_generation(request: Request):
    prompt = await request.json()
    if prompt is None:
        raise HTTPException(status_code=400, detail="No prompt in Body")

    result = GPT_prompt(prompt["message"], dataset_generation_system_message, 800, 1, "json_object")
    if result in ["Error", "None"]:
        raise HTTPException(status_code=400, detail="Error in chatpgt API" if result == "Error" else "Prompt Error")

    return {"message": "Free access granted!", "prompt": result}

@router.post("/free_generation_dataset")
async def free_generation_dataset(request: Request):
    dataset_data = await request.json()
    dataset_config = dataset_data["dataset_config"]
    dataset_condition = dataset_data["dataset_condition"]
    return {"config": dataset_config, "condition": dataset_condition}
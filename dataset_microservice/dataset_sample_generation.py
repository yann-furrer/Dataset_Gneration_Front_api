import asyncio, json, os
from dotenv import load_dotenv
from utils.chatgpt_api import ChatGPTAsyncClient
load_dotenv()

# import du prompt
with open("utils/prompt_sample.txt", "r") as file:
    prompt = file.read()
    prompt = prompt.split("==separateur==")


class datasetSampleGeneration(ChatGPTAsyncClient):
    """
    Permet de générer des données de type sample via l'API ChatGPT.
    """
    def __init__(self)-> None:
        super().__init__(os.getenv("OPENAI_API_KEY"))
    

    async def generate_sample(self, user_prompt: str) -> str:
        """
        Génère un dataset de type sample via l'API ChatGPT.
        Args:
            user_prompt (str): Prompt utilisé pour générer le dataset.
           
        Returns:
            str: Le dataset de type sample généré via l'API ChatGPT.
        """

        dataset_sampled = await  self.make_api_call(prompt=user_prompt, system_message=prompt[0], max_tokens=120, temperature=1, response_format="text")
        print("dataset_sampled : ", dataset_sampled)
        return dataset_sampled
    
# a = datasetSampleGeneration()
# result =  asyncio.run(a.generate_sample(user_prompt="génère moi un dataset sur les bombardement et les dictature en afrique"))

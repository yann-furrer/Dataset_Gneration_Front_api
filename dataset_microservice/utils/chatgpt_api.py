import openai
import backoff
import time, json
import os 
from dotenv import load_dotenv
load_dotenv()

with open("./generator/prompt.txt", "r", encoding="utf-8") as fichier:
    prompt_txt = fichier.read()

# Séparer les prompts en utilisant le séparateur "=seprateur="
prompts_list = prompt_txt.split("=seprateur=")

class ChatGPTAsyncClient:
    def __init__(self, model="gpt-4.1-mini"):
        self.api_key = os.getenv("OPENAI_API_KEY")
        """
        Initialise le client ChatGPT asynchrone.
        
        :param api_key: Clé API pour authentification auprès d'OpenAI.
        :param model: Modèle à utiliser pour les requêtes (par défaut : gpt-4.1-mini).
        """
        self.client = openai.AsyncOpenAI(api_key=self.api_key)
        self.model = model

    def select_prompt(self, nb_prompt: int = 0)-> str:
        """
        Prend un indice de prompt et retourne le prompt correspondant
        :param nb_prompt: indice du prompt
        :return: le prompt correspondant
        """
        try : 
            return prompts_list[nb_prompt]

        except IndexError or KeyError:
            print("prompt non trouvé : ", type(nb_prompt)  ,nb_prompt)
            return "prompt non trouvé"

    @backoff.on_exception(backoff.expo, openai.RateLimitError)
    async def make_api_call(self, prompt,system_message, max_tokens=500, temperature=1, response_format: str ="text" ) -> str:
        """
        Effectue une requête à l'API ChatGPT.

        :param prompt: Texte de la requête.
        :param temperature: Niveau de créativité de la réponse (par défaut : 0).
        :return: Réponse générée par le modèle.
        """
       
        response = await self.client.chat.completions.create(
            model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                          ],
                max_tokens=max_tokens,
                temperature=temperature,
                response_format={"type": response_format},
        )
        print("repsonse : "+ str(time.time), response.choices[0].message.content)
        return response.choices[0].message.content








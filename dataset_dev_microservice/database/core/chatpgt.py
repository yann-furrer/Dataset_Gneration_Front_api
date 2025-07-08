# from openai import OpenAI
# from dotenv import load_dotenv
# import os, json
# load_dotenv()

# client = OpenAI(api_key=os.getenv("OPEN_API_KEY") )
# dataset_generation_system_message = "Génère un dataset en format JSON, limité à une seule ligne de données. Assurez-vous que le contenu soit d'un niveau professionnel et parfaitement structuré. Si le prompt ne correspond pas à la définition d'un dataset, renvoyez {'detail' : 'Prompt Error'}"

# def GPT_prompt(prompt : str, system_message : str, max_token: int = 500, temperature : int = 1, response_format: str ="text" ) -> str:
#   #  try: 
#         completion = client.chat.completions.create(
#             model="gpt-4o",
#             store=False,
            
#             temperature=temperature,
#             max_tokens=max_token,
#             response_format={ "type": response_format }, # {"text": "json_object"},
#             messages=[
#                 {"role": "system", "content": system_message },
#                 {"role": "user", "content": prompt },
#             ]

#         )
#         print("prompt : ", prompt, "  " ,  type(prompt))
#         print(completion.choices[0].message.content, type(completion.choices[0].message.content), len(completion.choices[0].message.content))
#         if response_format == "json_object": # commence par un { ou un [
#                 data = json.loads(completion.choices[0].message.content)
#                 return data
#         else:
#             return completion.choices[0].message.content

#     # except Exception as e:
#     #     print(e)
#     #     return "Error"
   
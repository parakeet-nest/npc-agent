import json
from ollama import Client 


class Character:
    def __init__(self, name, race):
        self.name = name
        self.race = race

chat_instruction = """You are a {race}, your name is {name},
you are an expert at interpreting and answering questions based on provided sources.
Using only the provided context, answer the user's question 
to the best of your ability using only the resources provided. 
Be verbose!
"""

def chat_with_character(character: Character, description: str,ollama_url: str, model: str):
    ollama_client = Client(host=ollama_url)

    instructions = chat_instruction.format(race=character.race, name=character.name)

    msg = "🤖 [{name}] (type 'bye' to exit):> ".format(name=character.name)

    while True:
        user_input = input(msg)
        if user_input.lower() == "bye":
            print("👋 Goodbye!")
            break
        else:
            stream = ollama_client.chat(
                model=model,
                messages=[
                    {'role': 'system', 'content': instructions},
                    {'role': 'system', 'content': description},
                    {'role': 'user', 'content': user_input},
                ],
                options={"temperature":0.5},
                stream=True,
                keep_alive=1,
            )

            for chunk in stream:
                print(chunk['message']['content'], end='', flush=True)
            
            print("\n")

model="nemotron-mini"
ollama_url="http://host.docker.internal:11434"

character = Character(name="Gimli the Stout", race="dwarf")

with open('../01-character-sheet/description-'+character.race+'.md', 'r') as file:
    description = file.read()

chat_with_character(character, description, ollama_url, model)

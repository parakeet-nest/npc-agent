import json
from ollama import Client 

class Character:
    def __init__(self, name, race):
        self.name = name
        self.race = race

name_instructions = """
You are an expert NPC generator for games like D&D 5th edition. 
You have freedom to be creative to get the best possible output.
"""

name_user_tpl = """generate a random name for a role-playing game character for a {species}. 
The output should be in JSON format, with the keys 'name' and 'race'. 
Ensure the name is fantasy-themed.
"""

description_instructions = """# IDENTITY and PURPOSE
You are an expert NPC generator for games like D&D 5th edition. 
You have freedom to be creative to get the best possible output.
"""

description_steps = """# STEPS

Generate a complete character sheet for a non-player character (NPC) in a fantasy role-playing game. 
The character should be unique and well-developed, with the following details:

1. **race**: The given race.
2. **Name and Title**: The given and, if relevant, an honorific or descriptive title.
3. **Age**: Indicate the character's age.
4. **Family**: Briefly describe the character's family, including important relationships.
5. **Occupation**: What is the character's main occupation or role? Describe their skills and their role in society.
6. **Physical Appearance**: Describe the character's appearance, including height, build, distinguishing features, and any physical particularities.
7. **Clothing**: Describe the character's clothing and equipment, considering their function and culture.
8. **Food Preferences**: What are the character's food preferences? Include a specific detail that makes them unique.
9. **Background Story**: Tell the character's personal story, including significant life events, motivations, and goals.
10. **Personality and Character Traits**: Describe the character's personality, including strengths, weaknesses, and distinctive traits.
11. **Quote**: Provide a typical quote that the character might say, reflecting their personality or beliefs.

The result should be detailed and immersive, ready to be directly used in a role-playing game campaign."

# OUTPUT INSTRUCTIONS

- Output in clear, human-readable Markdown.

Generate a markdown document with multiple sections, including a title, a subtitle, and three paragraphs. Each section should be separated by a blank line (carriage return). Ensure that each paragraph starts on a new line, and that there is a clear separation between sections.

**Expected Output:**
```markdown
# Title of the Document

## Subtitle of the Document

This is the first paragraph. It provides an introduction to the topic.

This is the second paragraph. It delves deeper into the details of the topic.

This is the third paragraph. It concludes the discussion and offers final thoughts.
```
"""


def generate_character(species: str, ollama_url: str, model: str) -> Character:

    ollama_client = Client(host=ollama_url)

    instruction_content = name_instructions
    user_content = name_user_tpl.format(species=species)
    print(f"🤖 user message for name generation> {user_content}")

    completion = ollama_client.chat(
            model=model,
            messages=[
              {'role': 'system', 'content': instruction_content},
              {'role': 'user', 'content': user_content},
            ],
            options={"temperature":0.3},
            stream=False,
            format="json",
        )
    
    json_character = completion['message']['content']
    print(json_character + "\n")

    # Parse the JSON string to a dictionary
    character_data = json.loads(json_character)

    # Create a Character object from the dictionary
    character = Character(name=character_data['name'], race=character_data['race'])
    
    return character

def generate_description(character: Character, ollama_url: str, model: str) -> str:

    instruction_content = description_instructions
    steps_content = description_steps

    user_content = "Create a {race} with this name: {name}".format(race=character.race, name=character.name)
    print(f"🤖 user message for description generation> {user_content}")


    ollama_client = Client(host=ollama_url)

    stream = ollama_client.chat(
        model=model,
        messages=[
            {'role': 'system', 'content': instruction_content},
            {'role': 'system', 'content': steps_content},
            {'role': 'user', 'content': user_content},
        ],
        options={
            "temperature":0.5,
            "repeat_last_n":3,
            "repeat_penalty":2.0,
            "top_k":10,
            "top_p":0.5,
        },
        stream=True,
    )

    answer = ""

    for chunk in stream:
        content = chunk['message']['content']
        answer+=content
        print(content, end='', flush=True)

    # save content of answer to a markdown file: description.md
    # Open the file in write mode
    with open('./description-'+character.race+'.md', "w") as file:
        # Write the content to the file
        file.write(answer)
    
    print("\n")


model="nemotron-mini"
ollama_url="http://host.docker.internal:11434"

character = generate_character("dwarf", ollama_url, model)

generate_description(character, ollama_url, model)


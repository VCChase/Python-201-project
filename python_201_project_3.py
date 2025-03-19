import requests
import re
from colorama import Fore, init

init(autoreset=True)

def get_last(lst, output, default="No description available"):
    if not lst:
        return default
    
    if lst[-1].get("language", {}).get("name") == "en":
        return re.sub(r"\s+", " ", lst[-1].get(output).replace("\n", " "))
    else:
        return get_last(lst[:-1], output, default)
    
def format_input(string):
    string = string.replace("♀", "-f").replace("♂", "-m")
    string = re.sub(r"[\s:]", "-", string)
    string = re.sub(r"[\.']", "", string)
    string = re.sub(r"-+", "-", string)
    return string    

def get_pokemon(): 

    while True:
        pokemon = {
            "name": "Unknown",
            "species": "Unknown",
            "color": "Unknown",
            "description": "Unknown",
            "height": None,
            "weight": None,
            "types": [],
            "abilities": {}
        }

        user = input("Which pokemon would you like to learn about? (Type 'exit' to quit) ").lower().strip()
        if user == "exit":
            print(f"\n{Fore.GREEN}Goodbye")
            break
        user_clean = format_input(user)

        req = requests.get(f"https://pokeapi.co/api/v2/pokemon/{user_clean}")
        if req.status_code == 200:
            req = req.json()

            # Get name
            pokemon["name"] = req.get("name", "Unknown")

            # Get height and weight and convert to metric
            height = req.get("height")
            weight = req.get("weight")

            if isinstance(height, int):
                pokemon["height"] = f"{height / 10}m"
                
            if isinstance(weight, int):
                pokemon["weight"] = f"{weight / 10}kg"

            # Get types
            types = req.get("types", [])
            pokemon["types"] = [type.get("type", {}).get("name", "Unknown") for type in types] or ["Unknown"]

            # Get species, color, and flavor text
            species_data = req.get("species", {})
            pokemon["species"] = species_data.get("name", "Unknown")
            species_url = species_data.get("url", "")

            if species_url:
                species_info = requests.get(species_url).json()
                pokemon["color"] = species_info.get("color", {}).get("name", "Unknown")
                species_flavor = species_info.get("flavor_text_entries", [])
                pokemon["description"] = get_last(species_flavor, "flavor_text")

            # Get abilities
            abilities = req.get("abilities", [])
            for index, ability in enumerate(abilities):
                ability_data = ability.get("ability", {})
                ability_name = ability_data.get("name", f"Ability {index}")
                ability_url = ability_data.get("url", "")

                if ability_url:
                    ability_info = requests.get(ability_url).json()
                    ability_effects = ability_info.get("effect_entries", [])
                    pokemon["abilities"][ability_name] = get_last(ability_effects, "effect")

            # Print values
            print()
            for key, value in pokemon.items():
                if isinstance(value, list):
                    print(f"{Fore.YELLOW}{key}: {Fore.BLUE}{", ".join(value)}")
                elif isinstance(value, dict):
                    print(f"\n{Fore.YELLOW}{key}:")
                    for k, v in value.items():
                        print(f"{Fore.MAGENTA}--{k}: {Fore.BLUE}{v}\n")
                else:
                    print(f"{Fore.YELLOW}{key}: {Fore.BLUE}{value}")

            break

        else:
            print(f"\n{Fore.RED}{user} not found. Please try again")

get_pokemon()
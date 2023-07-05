'''
if there are any issues with this tool please contact me on discord
or create an issue on github.

Please download this tool only from the official release section on my Github.
Should you have acquired this tool from any other source than the official Github page
I can not guarantee for its safety.

Github: https://github.com/CallmeEchoo
Discord: u8.salem
'''
import sys
import os
import shutil

from file_handler import *
from expansion.files import *
from pory_util import pjoin


def main():
    global species

    if len(sys.argv) < 2:
        print("Please provide the path to the data file")
        return

    pory_path = os.path.dirname(os.path.abspath(__file__))
    species = sys.argv[1]

    # load config data
    config = Config(pjoin(pory_path, "config.json"))

    if config.pokeemerald_expansion:
        version_path = "expansion"
    else:
        version_path = "vanilla"

    if not (os.path.exists(pjoin(pory_path, version_path, species))) or not assetsExist(pjoin(pory_path, version_path, species)):
        raise FileNotFoundError('''
    Could not find matching directory!

    Please provide the argument for the pokemon that should be inserted.
    Example file structure:
    porymon
    ├── tomato
    │      ├── pokemon_data.json
    │      ├── anim_front.png
    │      ├── back.png
    │      ├── icon.png
    │      └── footprint.png
    ├── porymon.py
    ├── files.py
    ├── pory_util.py
    └── config.json

    Your input for inserting the pokemon "tomato" should look like this:

    "python3 porymon.py tomato" or "python porymon.py tomato"
''')

    # common paths
    include_constants = pjoin("include", "constants")
    src_data_pokemon = pjoin("src", "data", "pokemon")
    src_data_pokemon_graphics = pjoin("src", "data", "pokemon_graphics")

    # load data json
    pokemon_data = PokemonData(pjoin(pory_path, version_path, species, "pokemon_data.json"))

    # load and edit c files
    # Species definitions
    species_header = SpeciesH(pjoin(config.pokeemerald_path, include_constants, "species.h"))
    species_header.appendData(pokemon_data.species)

    species_names = SpeciesNamesH(pjoin(config.pokeemerald_path, "src", "data", "text", "species_names.h"))
    species_names.appendData(pokemon_data.species, species_header.prev_mon_name)

    species_info = SpeciesInfoH(pjoin(config.pokeemerald_path, src_data_pokemon, "species_info.h"))
    species_info.appendData(pokemon_data.formated_species_info, species_header.prev_mon_name)

    pokemon_source = PokemonC(pjoin(config.pokeemerald_path, "src", "pokemon.c"))
    pokemon_source.appendData(pokemon_data.species, species_header.prev_mon_name)

    # Pokedex
    pokedex_header = PokedexH(pjoin(config.pokeemerald_path, include_constants, "pokedex.h"))
    pokedex_header.appendData(pokemon_data.species, species_header.prev_mon_name)

    pokedex_entry = PokedexEntryH(pjoin(config.pokeemerald_path, src_data_pokemon, "pokedex_entries.h"))
    pokedex_entry.appendData(pokemon_data.formated_pokedex_data, species_header.prev_mon_name)

    pokedex_text = PokedexTextH(pjoin(config.pokeemerald_path, src_data_pokemon, "pokedex_text.h"))
    pokedex_text.appendData(pokemon_data.formated_pokedex_text, species_header.prev_mon_name)

    pokedex_orders = PokedexOrdersH(pjoin(config.pokeemerald_path, src_data_pokemon, "pokedex_orders.h"), pokedex_entry)
    pokedex_orders.appendData(pokemon_data.species, pokemon_data._pokedex_data["height"], pokemon_data._pokedex_data["weight"])

    # Evolution
    if pokemon_data.hasEvo:
        evolution_data = EvolutionH(pjoin(config.pokeemerald_path, src_data_pokemon, "evolution.h"))
        evolution_data.appendData(pokemon_data.formated_evolution_data)

    # Grapics
    graphics_declaration = GraphicsH(pjoin(config.pokeemerald_path, "include", "graphics.h"))
    graphics_declaration.appendData(pokemon_data.species, species_header.prev_mon_name)

    pokemon_header = PokemonH(pjoin(config.pokeemerald_path, "src", "data", "graphics", "pokemon.h"))
    pokemon_header.appendData(pokemon_data.species, species_header.prev_mon_name)

    pokemon_icon = PokemonIconC(pjoin(config.pokeemerald_path, "src", "pokemon_icon.c"))
    pokemon_icon.appendData(pokemon_data.species, species_header.prev_mon_name, pokemon_data.icon_pal_num)

    pokemon_animation = PokemonAnimationC(pjoin(config.pokeemerald_path, "src", "pokemon_animation.c"))
    pokemon_animation.appendData(pokemon_data.species, species_header.prev_mon_name)

    back_pic_table = BackPicTableH(pjoin(config.pokeemerald_path, src_data_pokemon_graphics, "back_pic_table.h"))
    back_pic_table.appendData(pokemon_data.species, species_header.prev_mon_name)

    front_pic_table = FrontPicTableH(pjoin(config.pokeemerald_path, src_data_pokemon_graphics, "front_pic_table.h"))
    front_pic_table.appendData(pokemon_data.species, species_header.prev_mon_name)

    back_pic_coordinates = BackPicCoordinatesH(pjoin(config.pokeemerald_path, src_data_pokemon_graphics, "back_pic_coordinates.h"))
    back_pic_coordinates.appendData(species_header.prev_mon_name, pokemon_data.formated_back_pic_coordinates)

    front_pic_coordinates = FrontPicCoordinatesH(pjoin(config.pokeemerald_path, src_data_pokemon_graphics, "front_pic_coordinates.h"))
    front_pic_coordinates.appendData(species_header.prev_mon_name, pokemon_data.formated_front_pic_coordinates)

    front_pic_anims = FrontPicAnimsH(pjoin(config.pokeemerald_path, src_data_pokemon_graphics, "front_pic_anims.h"))
    front_pic_anims.appendData(pokemon_data.species, species_header.prev_mon_name, pokemon_data.formated_front_pic_anim)

    palette_table = PaletteTableH(pjoin(config.pokeemerald_path, src_data_pokemon_graphics, "palette_table.h"))
    palette_table.appendData(pokemon_data.species, species_header.prev_mon_name)

    shiny_palette_table = ShinyPaletteTableH(pjoin(config.pokeemerald_path, src_data_pokemon_graphics, "shiny_palette_table.h"))
    shiny_palette_table.appendData(pokemon_data.species, species_header.prev_mon_name)

    # movesets
    level_up_learnset = LevelUpLearnsetsH(pjoin(config.pokeemerald_path, src_data_pokemon, "level_up_learnsets.h"))
    level_up_learnset.appendData(pokemon_data.formated_level_up_moveset, species_header.prev_mon_name)

    level_up_learnset_pointers = LevelUpLearnsetPointersH(pjoin(config.pokeemerald_path, src_data_pokemon, "level_up_learnset_pointers.h"))
    level_up_learnset_pointers.appendData(pokemon_data.species, species_header.prev_mon_name)

    teachable_lernset = TeachableLearnsetH(pjoin(config.pokeemerald_path, src_data_pokemon, "teachable_learnsets.h"))
    teachable_lernset.appendData(pokemon_data.formated_teachable_moveset, species_header.prev_mon_name)

    teachable_lernset_pointers = TeachableLearnsetPointersH(pjoin(config.pokeemerald_path, src_data_pokemon, "teachable_learnset_pointers.h"))
    teachable_lernset_pointers.appendData(pokemon_data.species, species_header.prev_mon_name)

    if pokemon_data.hasEggMove:
        egg_moveset = EggMovesH(pjoin(config.pokeemerald_path, src_data_pokemon, "egg_moves.h"))
        egg_moveset.appendData(pokemon_data.formated_egg_moveset, species_header.prev_mon_name)

    copyAssets(pjoin(pory_path, version_path, species), pjoin(config.pokeemerald_path, "graphics", "pokemon", str(species).lower()))
    writeBackAll()

    print('''
-----------------!! READ CAREFULLY !!-----------------
All changes have been made successfully! Please test the new pokemon in game now.
Make sure everything is correct and working! If something is wrong restore all files
and try again!
''')
    print("Do you want to restore all files? [y/n]", end=": ")
    while True:
        user_input = input()
        if user_input == 'y':
            print("Undoing all changes!")
            restoreAll()
            shutil.rmtree(pjoin(config.pokeemerald_path, "graphics", "pokemon", str(species).lower()))
            sys.exit()
        elif user_input == 'n':
            sys.exit()
        else:
            print("Please enter a valid character [y/n]", end=": ")


def restoreAll():
    for instance in HeaderFile.instances:
        instance.restoreFile()

def writeBackAll():
    for instance in HeaderFile.instances:
        instance.writeBack()

def assetsExist(path):
    assets = ["anim_front.png", "back.png", "footprint.png", "icon.png", "normal.pal", "shiny.pal"]
    for asset in assets:
        if os.path.isfile(pjoin(path, asset)):
            print(pjoin(path, asset), " found!")
        else:
            raise FileNotFoundError(pjoin(path, asset), " not found!")

    return True

def copyAssets(path, dst):
    if not os.path.exists(dst):
        os.mkdir(pjoin(dst))
    assets = ["anim_front.png", "back.png", "footprint.png", "icon.png", "normal.pal", "shiny.pal"]
    for asset in assets:
        shutil.copy(pjoin(path, asset), pjoin(dst, asset))


if __name__ == '__main__':
    main()
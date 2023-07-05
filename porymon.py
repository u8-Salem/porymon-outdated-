'''
Github: https://github.com/CallmeEchoo
Discord: u8.salem
'''
import sys
import os
import shutil
import importlib

from file_types import *
from pory_util import pjoin

#########################
# Child Classes PoryMon #
#########################

class Config(JsonFile):
    def __init__(self, path: str):
        super().__init__(path)

    def _initData(self):
        self.pokeemerald_path = self._file["pokeemerald-path"]
        self.pokeemerald_version = self._file["pokeemerald-version"]

def main():
    global species

    if len(sys.argv) < 2:
        print("Please provide the path to the data file")
        return

    pory_path = os.path.dirname(os.path.abspath(__file__))
    species = sys.argv[1]

    # load config data
    config = Config(pjoin(pory_path, "config.json"))

    # configure path and module
    version_path = config.pokeemerald_version
    module = importlib.import_module(f'{config.pokeemerald_version}.files')

    # raise error if some asset or the directory does not exist
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

    editFiles(pory_path, version_path, config, module)
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

def editFiles(pory_path, version_path, config, module):
    # common paths
    include_constants = pjoin("include", "constants")
    src_data_pokemon = pjoin("src", "data", "pokemon")
    src_data_pokemon_graphics = pjoin("src", "data", "pokemon_graphics")

    # load data json
    pokemon_data = module.PokemonData(pjoin(pory_path, version_path, species, "pokemon_data.json"))

    # load and edit c files
    # Species definitions
    species_header = module.SpeciesH(pjoin(config.pokeemerald_path, include_constants, "species.h"))
    species_header.appendData(pokemon_data.species)

    species_names = module.SpeciesNamesH(pjoin(config.pokeemerald_path, "src", "data", "text", "species_names.h"))
    species_names.appendData(pokemon_data.species, species_header.prev_mon_name)

    species_info = module.SpeciesInfoH(pjoin(config.pokeemerald_path, src_data_pokemon, "species_info.h"))
    species_info.appendData(pokemon_data.formated_species_info, species_header.prev_mon_name)

    pokemon_source = module.PokemonC(pjoin(config.pokeemerald_path, "src", "pokemon.c"))
    pokemon_source.appendData(pokemon_data.species, species_header.prev_mon_name)

    # Pokedex
    pokedex_header = module.PokedexH(pjoin(config.pokeemerald_path, include_constants, "pokedex.h"))
    pokedex_header.appendData(pokemon_data.species, species_header.prev_mon_name)

    pokedex_entry = module.PokedexEntryH(pjoin(config.pokeemerald_path, src_data_pokemon, "pokedex_entries.h"))
    pokedex_entry.appendData(pokemon_data.formated_pokedex_data, species_header.prev_mon_name)

    pokedex_text = module.PokedexTextH(pjoin(config.pokeemerald_path, src_data_pokemon, "pokedex_text.h"))
    pokedex_text.appendData(pokemon_data.formated_pokedex_text, species_header.prev_mon_name)

    pokedex_orders = module.PokedexOrdersH(pjoin(config.pokeemerald_path, src_data_pokemon, "pokedex_orders.h"), pokedex_entry)
    pokedex_orders.appendData(pokemon_data.species, pokemon_data._pokedex_data["height"], pokemon_data._pokedex_data["weight"])

    # Evolution
    if pokemon_data.hasEvo:
        evolution_data = module.EvolutionH(pjoin(config.pokeemerald_path, src_data_pokemon, "evolution.h"))
        evolution_data.appendData(pokemon_data.formated_evolution_data)

    # Grapics
    graphics_declaration = module.GraphicsH(pjoin(config.pokeemerald_path, "include", "graphics.h"))
    graphics_declaration.appendData(pokemon_data.species, species_header.prev_mon_name)

    pokemon_header = module.PokemonH(pjoin(config.pokeemerald_path, "src", "data", "graphics", "pokemon.h"))
    pokemon_header.appendData(pokemon_data.species, species_header.prev_mon_name)

    pokemon_icon = module.PokemonIconC(pjoin(config.pokeemerald_path, "src", "pokemon_icon.c"))
    pokemon_icon.appendData(pokemon_data.species, species_header.prev_mon_name, pokemon_data.icon_pal_num)

    pokemon_animation = module.PokemonAnimationC(pjoin(config.pokeemerald_path, "src", "pokemon_animation.c"))
    pokemon_animation.appendData(pokemon_data.species, species_header.prev_mon_name)

    back_pic_table = module.BackPicTableH(pjoin(config.pokeemerald_path, src_data_pokemon_graphics, "back_pic_table.h"))
    back_pic_table.appendData(pokemon_data.species, species_header.prev_mon_name)

    front_pic_table = module.FrontPicTableH(pjoin(config.pokeemerald_path, src_data_pokemon_graphics, "front_pic_table.h"))
    front_pic_table.appendData(pokemon_data.species, species_header.prev_mon_name)

    back_pic_coordinates = module.BackPicCoordinatesH(pjoin(config.pokeemerald_path, src_data_pokemon_graphics, "back_pic_coordinates.h"))
    back_pic_coordinates.appendData(species_header.prev_mon_name, pokemon_data.formated_back_pic_coordinates)

    front_pic_coordinates = module.FrontPicCoordinatesH(pjoin(config.pokeemerald_path, src_data_pokemon_graphics, "front_pic_coordinates.h"))
    front_pic_coordinates.appendData(species_header.prev_mon_name, pokemon_data.formated_front_pic_coordinates)

    front_pic_anims = module.FrontPicAnimsH(pjoin(config.pokeemerald_path, src_data_pokemon_graphics, "front_pic_anims.h"))
    front_pic_anims.appendData(pokemon_data.species, species_header.prev_mon_name, pokemon_data.formated_front_pic_anim)

    palette_table = module.PaletteTableH(pjoin(config.pokeemerald_path, src_data_pokemon_graphics, "palette_table.h"))
    palette_table.appendData(pokemon_data.species, species_header.prev_mon_name)

    shiny_palette_table = module.ShinyPaletteTableH(pjoin(config.pokeemerald_path, src_data_pokemon_graphics, "shiny_palette_table.h"))
    shiny_palette_table.appendData(pokemon_data.species, species_header.prev_mon_name)

    # movesets
    level_up_learnset = module.LevelUpLearnsetsH(pjoin(config.pokeemerald_path, src_data_pokemon, "level_up_learnsets.h"))
    level_up_learnset.appendData(pokemon_data.formated_level_up_moveset, species_header.prev_mon_name)

    level_up_learnset_pointers = module.LevelUpLearnsetPointersH(pjoin(config.pokeemerald_path, src_data_pokemon, "level_up_learnset_pointers.h"))
    level_up_learnset_pointers.appendData(pokemon_data.species, species_header.prev_mon_name)

    teachable_lernset = module.TeachableLearnsetH(pjoin(config.pokeemerald_path, src_data_pokemon, "teachable_learnsets.h"))
    teachable_lernset.appendData(pokemon_data.formated_teachable_moveset, species_header.prev_mon_name)

    teachable_lernset_pointers = module.TeachableLearnsetPointersH(pjoin(config.pokeemerald_path, src_data_pokemon, "teachable_learnset_pointers.h"))
    teachable_lernset_pointers.appendData(pokemon_data.species, species_header.prev_mon_name)

    if pokemon_data.hasEggMove:
        egg_moveset = module.EggMovesH(pjoin(config.pokeemerald_path, src_data_pokemon, "egg_moves.h"))
        egg_moveset.appendData(pokemon_data.formated_egg_moveset, species_header.prev_mon_name)


if __name__ == '__main__':
    main()

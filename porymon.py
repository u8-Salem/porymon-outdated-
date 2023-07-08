'''
Github: https://github.com/CallmeEchoo
Discord: u8.salem
'''
import sys
import os
import shutil
import importlib

from os.path import join
from file_types import *

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
    config = Config(join(pory_path, "config.json"))

    # configure path and module
    version_path = config.pokeemerald_version
    module = importlib.import_module(f'{config.pokeemerald_version}.files')

    if version_path == "vanilla":
        assets = ["front.png", "anim_front.png", "back.png", "footprint.png", "icon.png", "normal.pal", "shiny.pal"]
    elif version_path == "expansion":    
        assets = ["anim_front.png", "back.png", "footprint.png", "icon.png", "normal.pal", "shiny.pal"]

    # raise error if some asset or the directory does not exist
    if not (os.path.exists(join(pory_path, version_path, species))) or not assetsExist(join(pory_path, version_path, species), assets):
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
    copyAssets(join(pory_path, version_path, species), join(config.pokeemerald_path, "graphics", "pokemon", str(species).lower()), assets)
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
            shutil.rmtree(join(config.pokeemerald_path, "graphics", "pokemon", str(species).lower()))
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

def assetsExist(path, assets):
    for asset in assets:
        if os.path.isfile(join(path, asset)):
            print(join(path, asset), " found!")
        else:
            raise FileNotFoundError(join(path, asset), " not found!")

    return True

def copyAssets(path, dst, assets):
    if not os.path.exists(dst):
        os.mkdir(join(dst))
    for asset in assets:
        shutil.copy(join(path, asset), join(dst, asset))

def editFiles(pory_path, version_path, config, module):
    # common paths
    include_constants = join("include", "constants")
    src_data_pokemon = join("src", "data", "pokemon")
    src_data_pokemon_graphics = join("src", "data", "pokemon_graphics")

    # load data json
    pokemon_data = module.PokemonData(join(pory_path, version_path, species, "pokemon_data.json"))

    # Header Files
    # Species definitions
    species_header = module.SpeciesH(join(config.pokeemerald_path, include_constants, "species.h"))
    species_header.appendData(pokemon_data.species)

    species_info = module.SpeciesInfoH(join(config.pokeemerald_path, src_data_pokemon, "species_info.h"))
    species_info.appendData(pokemon_data.formated_species_info, species_header.prevSpecies)

    species_names = module.SpeciesNamesH(join(config.pokeemerald_path, "src", "data", "text", "species_names.h"))
    species_names.appendData(pokemon_data.species, species_header.prevSpecies)

    # Pokedex
    pokedex_header = module.PokedexH(join(config.pokeemerald_path, include_constants, "pokedex.h"))
    pokedex_header.appendData(pokemon_data.species, species_header.prevSpecies)

    pokedex_entry = module.PokedexEntryH(join(config.pokeemerald_path, src_data_pokemon, "pokedex_entries.h"))
    pokedex_entry.appendData(pokemon_data.formated_pokedex_data, species_header.prevSpecies)

    pokedex_text = module.PokedexTextH(join(config.pokeemerald_path, src_data_pokemon, "pokedex_text.h"))
    pokedex_text.appendData(pokemon_data.formated_pokedex_text, species_header.prevSpecies)

    pokedex_orders = module.PokedexOrdersH(join(config.pokeemerald_path, src_data_pokemon, "pokedex_orders.h"), pokedex_entry)
    pokedex_orders.appendData(pokemon_data.species, pokemon_data.pokedex_data["height"], pokemon_data.pokedex_data["weight"])

    # Evolution
    if pokemon_data.hasEvo:
        evolution_data = module.EvolutionH(join(config.pokeemerald_path, src_data_pokemon, "evolution.h"))
        evolution_data.appendData(pokemon_data.formated_evolution_data)

    # Grapics
    graphics_declaration = module.GraphicsH(join(config.pokeemerald_path, "include", "graphics.h"))
    graphics_declaration.appendData(pokemon_data.species, species_header.prevSpecies)

    pokemon_header = module.PokemonH(join(config.pokeemerald_path, "src", "data", "graphics", "pokemon.h"))
    pokemon_header.appendData(pokemon_data.species, species_header.prevSpecies)

    back_pic_table = module.BackPicTableH(join(config.pokeemerald_path, src_data_pokemon_graphics, "back_pic_table.h"))
    back_pic_table.appendData(pokemon_data.species, species_header.prevSpecies)

    front_pic_table = module.FrontPicTableH(join(config.pokeemerald_path, src_data_pokemon_graphics, "front_pic_table.h"))
    front_pic_table.appendData(pokemon_data.species, species_header.prevSpecies)

    back_pic_coordinates = module.BackPicCoordinatesH(join(config.pokeemerald_path, src_data_pokemon_graphics, "back_pic_coordinates.h"))
    back_pic_coordinates.appendData(species_header.prevSpecies, pokemon_data.formated_back_pic_coordinates)

    front_pic_coordinates = module.FrontPicCoordinatesH(join(config.pokeemerald_path, src_data_pokemon_graphics, "front_pic_coordinates.h"))
    front_pic_coordinates.appendData(species_header.prevSpecies, pokemon_data.formated_front_pic_coordinates)

    front_pic_anims = module.FrontPicAnimsH(join(config.pokeemerald_path, src_data_pokemon_graphics, "front_pic_anims.h"))
    front_pic_anims.appendData(pokemon_data.species, species_header.prevSpecies, pokemon_data.formated_front_pic_anim)

    palette_table = module.PaletteTableH(join(config.pokeemerald_path, src_data_pokemon_graphics, "palette_table.h"))
    palette_table.appendData(pokemon_data.species, species_header.prevSpecies)

    shiny_palette_table = module.ShinyPaletteTableH(join(config.pokeemerald_path, src_data_pokemon_graphics, "shiny_palette_table.h"))
    shiny_palette_table.appendData(pokemon_data.species, species_header.prevSpecies)

    footprint_table = module.FootprintTableH(join(config.pokeemerald_path, src_data_pokemon_graphics, "footprint_table.h"))
    footprint_table.appendData(pokemon_data.species, species_header.prevSpecies)

    # learnsets
    level_up_learnset = module.LevelUpLearnsetsH(join(config.pokeemerald_path, src_data_pokemon, "level_up_learnsets.h"))
    level_up_learnset.appendData(pokemon_data.formated_level_up_learnset, species_header.prevSpecies)

    level_up_learnset_pointers = module.LevelUpLearnsetPointersH(join(config.pokeemerald_path, src_data_pokemon, "level_up_learnset_pointers.h"))
    level_up_learnset_pointers.appendData(pokemon_data.species, species_header.prevSpecies)

    if pokemon_data.hasEggMove:
        egg_learnset = module.EggMovesH(join(config.pokeemerald_path, src_data_pokemon, "egg_moves.h"))
        egg_learnset.appendData(pokemon_data.formated_egg_learnset, species_header.prevSpecies)

    # Source Files
    pokemon_source = module.PokemonC(join(config.pokeemerald_path, "src", "pokemon.c"))
    pokemon_source.appendData(pokemon_data.species, species_header.prevSpecies)

    pokemon_icon = module.PokemonIconC(join(config.pokeemerald_path, "src", "pokemon_icon.c"))
    pokemon_icon.appendData(pokemon_data.species, species_header.prevSpecies, pokemon_data.icon_pal_num)

    pokemon_animation = module.PokemonAnimationC(join(config.pokeemerald_path, "src", "pokemon_animation.c"))
    pokemon_animation.appendData(pokemon_data.species, species_header.prevSpecies)


    if version_path == "vanilla":
        tmhm_learnset = module.TMHMLearnsetH(join(config.pokeemerald_path, src_data_pokemon, "tmhm_learnsets.h"))
        tmhm_learnset.appendData(pokemon_data.formated_tmhm_learnset, pokemon_data.species, species_header.prevSpecies)

        tutor_learnset = module.TutorLearnsetH(join(config.pokeemerald_path, src_data_pokemon, "tutor_learnsets.h"))
        tutor_learnset.appendData(pokemon_data.formated_tutor_learnset, pokemon_data.species, species_header.prevSpecies)

        still_front_pic_table = module.StillFrontPicTableH(join(config.pokeemerald_path, src_data_pokemon_graphics, "still_front_pic_table.h"))
        still_front_pic_table.appendData(pokemon_data.species, species_header.prevSpecies)

        anim_mon_front_pics = module.AnimMonFrontPicsC(join(config.pokeemerald_path, "src", "anim_mon_front_pics.c"))
        anim_mon_front_pics.appendData(pokemon_data.species, species_header.prevSpecies)

    elif version_path == "expansion":
        teachable_lernset = module.TeachableLearnsetH(join(config.pokeemerald_path, src_data_pokemon, "teachable_learnsets.h"))
        teachable_lernset.appendData(pokemon_data.formated_teachable_learnset, species_header.prevSpecies)

        teachable_lernset_pointers = module.TeachableLearnsetPointersH(join(config.pokeemerald_path, src_data_pokemon, "teachable_learnset_pointers.h"))
        teachable_lernset_pointers.appendData(pokemon_data.species, species_header.prevSpecies)

if __name__ == '__main__':
    main()

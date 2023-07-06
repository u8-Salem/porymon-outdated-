'''
this file contains formated string that are a little more complicated
to not clutter the PokemonData class even more
'''
import logging
log = logging.getLogger("myLogger")

def formatSpeciesInfo(name, species_info):
    formated_species_info = f'''
    [SPECIES_{name.upper()}] =
    {{
        .baseHP        = {species_info["baseStats"]["baseHP"]},
        .baseAttack    = {species_info["baseStats"]["baseAttack"]},
        .baseDefense   = {species_info["baseStats"]["baseDefense"]},
        .baseSpeed     = {species_info["baseStats"]["baseSpeed"]},
        .baseSpAttack  = {species_info["baseStats"]["baseSpAttack"]},
        .baseSpDefense = {species_info["baseStats"]["baseSpDefense"]},
        .types = {{ {species_info["types"]["type1"]}, {species_info["types"]["type2"]} }},
        .catchRate = {species_info["catchRate"]},
        .expYield = {species_info["expYield"]},
        .evYield_HP        = {species_info["evYield"]["evYield_HP"]},
        .evYield_Attack    = {species_info["evYield"]["evYield_Attack"]},
        .evYield_Defense   = {species_info["evYield"]["evYield_Defense"]},
        .evYield_SpAttack  = {species_info["evYield"]["evYield_SpAttack"]},
        .evYield_SpDefense = {species_info["evYield"]["evYield_SpDefense"]},
        .evYield_Speed     = {species_info["evYield"]["evYield_Speed"]},
        .itemCommon = {species_info["items"]["itemCommon"]},
        .itemRare = {species_info["items"]["itemRare"]},
        .genderRatio = {species_info["genderRatio"]},
        .eggCycles = {species_info["eggCycles"]},
        .friendship = {species_info["friendship"]},
        .growthRate = {species_info["growthRate"]},
        .eggGroups = {{ {species_info["eggGroups"]["eggGroup1"]}, {species_info["eggGroups"]["eggGroup2"]} }},
        .abilities = {{ {species_info["abilities"]["ability1"]}, {species_info["abilities"]["ability2"]} }},
        .bodyColor = {species_info["bodyColor"]},
        .safariZoneFleeRate = {species_info["safariZoneFleeRate"]},
        .noFlip = {str(species_info["noFlip"]).upper()},
    }},
'''
    return formated_species_info

def formatPokedexData(name, pokedex_data):
    formated_pokedex_data = f'''
    [NATIONAL_DEX_{name.upper()}] =
    {{
        .categoryName = _("{name.title()}"),
        .height = {pokedex_data["height"]},
        .weight = {pokedex_data["weight"]},
        .description = g{name.title()}PokedexText,
        .pokemonScale = {pokedex_data["pokemonScale"]},
        .pokemonOffset = {pokedex_data["pokemonOffset"]},
        .trainerScale = {pokedex_data["trainerScale"]},
        .trainerOffset = {pokedex_data["trainerOffset"]},
    }},
'''
    return formated_pokedex_data

def formatPokedexText(name, pokedex_text):
    formated_pokedex_text = f'''
const u8 g{name.title()}PokedexText[] = _(
    \"{pokedex_text["descLine1"]}\\n\"
    \"{pokedex_text["descLine2"]}\\n\"
    \"{pokedex_text["descLine3"]}\\n\"
    \"{pokedex_text["descLine4"]}\");
'''
    return formated_pokedex_text

def formatEvolutionData(name, evolution_data):
    if len(evolution_data) <= 0: #safety
        return ""

    formated_evolution_data = f'    [SPECIES_{name.upper()}]'.ljust(25) + '= {' + f'{{{evolution_data[0]["method"]}, {evolution_data[0]["param"]}, {evolution_data[0]["targetSpecies"]}}}'
    if len(evolution_data) > 1:
        for evo in evolution_data[1:]:
            formated_evolution_data += ",\n"
            formated_evolution_data += "".ljust(28) + f'{{{evo["method"]}, {evo["param"]}, {evo["targetSpecies"]}}}'
    formated_evolution_data += '},\n'
    return formated_evolution_data

def formatLevelUplearnset(name, level_up_learnset):
    formated_level_up_learnset = f'\nstatic const u16 s{name.title()}LevelUpLearnset[]'+' = {\n'
    for move in level_up_learnset:
        formated_level_up_learnset += f'    LEVEL_UP_MOVE({" " if move["level"] < 10 else ""}{move["level"]}, {move["move"]}),\n'
    formated_level_up_learnset += f'    LEVEL_UP_END\n'+'};\n'
    return formated_level_up_learnset

def formatTMHMLearnset(name, tmhm_learnset):
    formated_tmhm_learnset = f'\n    [SPECIES_{name.upper()}]'.ljust(27) + f'= TMHM_LEARNSET(TMHM({tmhm_learnset[0]["move"]})'
    if len(tmhm_learnset) > 1:
        for move in tmhm_learnset[1:]:
            formated_tmhm_learnset += "\n".ljust(41) + f'| TMHM({move["move"]})'
    formated_tmhm_learnset += "),\n"
    return formated_tmhm_learnset

def formatTutorLearnset(name, tutor_learnset):
    formated_tutor_learnset = f'\n    [SPECIES_{name.upper()}]'.ljust(32) + f'= (TUTOR({tutor_learnset[0]["move"]})'
    if len(tutor_learnset) > 1:
        for move in tutor_learnset[1:]:
            formated_tutor_learnset += "\n".ljust(33) + f'| TUTOR({move["move"]})'
    formated_tutor_learnset += "),\n"
    return formated_tutor_learnset

def formatEgglearnset(name, egg_learnset):
    i = 1
    formated_egg_learnset = f'    egg_moves({name.upper()},'
    for move in egg_learnset:
        formated_egg_learnset += f'\n        {move["move"]}'
        formated_egg_learnset += ',' if i < len(egg_learnset) else ""
        i += 1
    formated_egg_learnset += '),\n'
    return formated_egg_learnset

def formatPicCoordinates(name, pic_coordinates):
    formated_pic_coordinates = f'    [SPECIES_{name.upper()}]'.ljust(26) + f'= {{ .size = MON_COORDS_SIZE({pic_coordinates["x"]}, {pic_coordinates["y"]}), .y_offset = {" " if pic_coordinates["y_offset"] < 10 else ""}{pic_coordinates["y_offset"]} }},\n'
    return formated_pic_coordinates

def formatFrontPicAnim(name):
    formated_front_pic_anim = f'''
static const union AnimCmd sAnim_{name.title()}_1[] =
{{
    ANIMCMD_FRAME(0, 1),
    ANIMCMD_END,
}};
'''
    return formated_front_pic_anim

import sys
import re
import json

from file_types import *
from expansion.formated_strings import *

######################
# JSON files porymon #
######################

class PokemonData(JsonFile):
    def __init__(self, path: str):
        super().__init__(path)


    def _initData(self):
        self._initSpeciesInfo()
        self._initPokedex()
        self._initEvolution()
        self._initMoveData()
        self._initPicData()
        self._initAnims()

    def _initSpeciesInfo(self):
        self.species = self._file["species_info"]["species_name"]
        self.species_info = self._file["species_info"]
        self._formatSpeciesInfo()

    def _initPokedex(self):
        self.pokedex_data = self._file["pokedex_data"]
        self.pokedex_text = self._file["pokedex_data"]["description"]
        self._formatPokedex()

    def _initEvolution(self):
        self.hasEvo = True if len(self._file["evolution_data"]) > 0 else False
        if self.hasEvo:
            self.evolution_data = self._file["evolution_data"]
            self._formatEvolution()

    def _initMoveData(self):
        self.level_up_learnset = self._file["level_up_learnset"]
        self.teachable_learnset = self._file["teachable_learnset"]
        self.egg_learnset = self._file["egg_learnset"]
        self.hasEggMove = True if len(self._file["egg_learnset"]) > 0 else False
        self._formatLearnsets()

    def _initPicData(self):
        self.icon_pal_num = self._file["icon_pal_num"]
        self.back_pic_coordinates = self._file["back_pic_coordinates"]
        self.front_pic_coordinates = self._file["front_pic_coordinates"]
        self._formatPicCoordinates()

    def _initAnims(self):
        self._formatFrontPicAnims()

    def _formatSpeciesInfo(self):
        self.formated_species_info = formatSpeciesInfo(self.species, self.species_info)
    def _formatPokedex(self):
        self.formated_pokedex_data = formatPokedexData(self.species, self.pokedex_data)
        self.formated_pokedex_text = formatPokedexText(self.species, self.pokedex_text)
    def _formatEvolution(self):
        self.formated_evolution_data = formatEvolutionData(self.species, self.evolution_data)
    def _formatLearnsets(self):
        self.formated_level_up_learnset = formatLevelUplearnset(self.species, self.level_up_learnset)
        self.formated_teachable_learnset = formatTeachablelearnset(self.species, self.teachable_learnset)
        self.formated_egg_learnset = formatEgglearnset(self.species, self.egg_learnset)
    def _formatPicCoordinates(self):
        self.formated_back_pic_coordinates = formatPicCoordinates(self.species, self.back_pic_coordinates)
        self.formated_front_pic_coordinates = formatPicCoordinates(self.species, self.front_pic_coordinates)
    def _formatFrontPicAnims(self):
        self.formated_front_pic_anim = formatFrontPicAnim(self.species)

############################
# Header files pokeemerald #
############################

class SpeciesH(HeaderFile):
    def __init__(self, path: str):
        super().__init__(path)
        self._findPrevMon()

    def pokemonExists(self, species: str) -> bool:
        return False if self.findLine(f"#define SPECIES_{species.upper()}") == -1 else True

    def _findPrevMon(self):
        pattern = re.compile(r"#define SPECIES_(\w+)\s+(\d+)")
        self.prevSpeciesNum = -1

        for count, line in enumerate(self._file):
            match = re.search(pattern, line)
            if match:
                name = match.group(1)
                val = int(match.group(2))
                if val > self.prevSpeciesNum:
                    self.prevSpecies = name
                    self.prevSpeciesNum = val
                    self.prevSpeciesIdx = count


    def appendData(self, species):
        if self.pokemonExists(species):
            print(f"Species is already defined!")
            sys.exit()

        # add definition
        self.set_line(self.prevSpeciesIdx + 1, f"#define SPECIES_{species.upper()} {self.prevSpeciesNum + 1}\n\n")
        # update FORMS_START
        self.set_line(self.findLine("#define FORMS_START"), f"#define FORMS_START SPECIES_{species.upper()}\n")


class SpeciesInfoH(HeaderFile):
    def __init__(self, path):
        super().__init__(path)

    def appendData(self, formated_species_info: str, prevMon: str = "BULBASAUR"):
        idx = self.findLine("    },\n", self.findLine(prevMon.upper())) + 1
        idx = self._handleEndif(idx)
        self.insertBlankLine(idx)
        self.set_line(idx, formated_species_info)

class SpeciesNamesH(HeaderFile):
    def __init__(self, path: str):
        super().__init__(path)

    def appendData(self, species, prevMon):
        idx = self.findLine(f'SPECIES_{prevMon.upper()}') + 1
        idx = self._handleEndif(idx)
        self.insertBlankLine(idx)
        self.set_line(idx, f'    [SPECIES_{species.upper()}] = _(\"{species.title()}\"),\n')

class PokedexH(HeaderFile):
    def __init__(self, path: str):
        super().__init__(path)

    def appendData(self, species: str, prevMon: str = "BULBASAUR"):
        idx = self.findLine(prevMon) + 1
        idx = self._handleEndif(idx)
        self.insertBlankLine(idx)
        self.set_line(idx, f"    NATIONAL_DEX_{species.upper()},\n")

        # update NATIONAL_DEX_COUNT
        idx = self.findLine("#define NATIONAL_DEX_COUNT", idx)
        self.set_line(idx, f"   #define NATIONAL_DEX_COUNT  NATIONAL_DEX_{species.upper()}\n")


class PokedexEntryH(HeaderFile):
    def __init__(self, path: str):
        super().__init__(path)

    def appendData(self, formated_pokedex_entry: str, prevMon: str = "BULBASAUR"):
        idx = self.findLine("},", self.findLine(prevMon.upper())) + 1
        idx = self._handleEndif(idx)
        self.insertBlankLine(idx)
        self.set_line(idx, formated_pokedex_entry)

class PokedexTextH(HeaderFile):
    def __init__(self, path: str):
        super().__init__(path)

    def appendData(self, formated_pokedex_text: str, prevMon: str = "BULBASAUR"):
        idx = self.findLine(");", self.findLine(prevMon.title())) + 1
        self._handleEndif(idx)
        self.insertBlankLine(idx)
        self.set_line(idx, formated_pokedex_text)

class PokedexOrdersH(HeaderFile):
    _SPECIES = 0
    _HEIGHT = 1
    _WEIGHT = 2

    def __init__(self, path: str, pokedex_entry: PokedexEntryH):
        super().__init__(path)
        self._data = self._readPokedexEntry(pokedex_entry)

    def appendData(self, species, speciesHeight, speciesWeight):
        # alphabetical
        idx = self.findLine(self._findPrevMonByAlpha(species), self.findLine("gPokedexOrder_Alphabetical"))
        idx = self._handleEndif(idx)
        self.insertBlankLine(idx)
        self.set_line(idx, f'    NATIONAL_DEX_{species.upper()},\n')

        # weigh
        idx = self.findLine(self._findPrevMonByWeight(speciesWeight), self.findLine("gPokedexOrder_Weight")) + 1
        idx = self._handleEndif(idx)
        self.insertBlankLine(idx)
        self.set_line(idx, f'    NATIONAL_DEX_{species.upper()},\n')

        # height
        idx = self.findLine(self._findPrevMonByHeight(speciesHeight), self.findLine("gPokedexOrder_Height")) + 1
        idx = self._handleEndif(idx)
        self.insertBlankLine(idx)
        self.set_line(idx, f'    NATIONAL_DEX_{species.upper()},\n')

    def _findPrevMonByAlpha(self, speciesName):
        prevMon = "a"
        for mon in self._data:
            if mon[self._SPECIES].lower() > prevMon.lower() and mon[self._SPECIES].lower() < speciesName.lower():
                prevMon = mon[self._SPECIES]

        return str(prevMon)

    def _findPrevMonByWeight(self, speciesWeight):
        prevWeight = 0
        prevMon = "NONE"
        for mon in self._data:
            if int(mon[self._WEIGHT]) >= int(prevWeight) and int(mon[self._WEIGHT]) < int(speciesWeight):
                prevWeight = mon[self._WEIGHT]
                prevMon = mon[self._SPECIES]
        return str(prevMon)

    def _findPrevMonByHeight(self, speciesHeight):
        prevHeight = 0
        prevMon = "NONE"
        for mon in self._data:
            if int(mon[self._HEIGHT]) >= int(prevHeight) and int(mon[self._HEIGHT]) < int(speciesHeight):
                prevHeight = mon[self._HEIGHT]
                prevMon = mon[self._SPECIES]
        return str(prevMon)

    def _readPokedexEntry(self, pokedex_entry) -> list[str, int , int]:
        self._data = []
        pattern = re.compile(r"NATIONAL_DEX_(\w+)")
        for idx, line in enumerate(pokedex_entry.get_file()):
            match = re.search(pattern, line)
            if match:
                species = match.group(1)
                heightMatch = re.search(r"height\s+=\s+(\d+),", pokedex_entry.get_line(pokedex_entry.findLine('height', idx)))
                if heightMatch:
                    height = heightMatch.group(1)
                weightMatch = re.search(r"weight\s+=\s+(\d+),", pokedex_entry.get_line(pokedex_entry.findLine('weight', idx)))
                if weightMatch:
                    weight = weightMatch.group(1)

                if heightMatch and weightMatch:
                    self._data.append([species, height, weight])

        return self._data


class EvolutionH(HeaderFile):
    def __init__(self, path: str):
        super().__init__(path)

    def appendData(self, formated_evolution: str, prevMon: str="NONE"):
        if prevMon == "NONE":
            idx = len(self._file) - 1
            self.insertBlankLine(idx)
        else:
            idx = self.findLine(prevMon.upper()) + 1
            self.insertBlankLine(idx)

        self.set_line(idx, formated_evolution)

class GraphicsH(HeaderFile):
    def __init__(self, path: str):
        super().__init__(path)

    def appendData(self, species: str, prevMon: str = "BULBASAUR"):
        # front pic
        idx = self.findLine(f'gMonFrontPic_{prevMon.title()}') + 1
        idx = self._handleEndif(idx)
        self.insertBlankLine(idx)
        self.set_line(idx, f'extern const u32 gMonFrontPic_{species.title()}[];\n')

        # back pic
        idx = self.findLine(f'gMonBackPic_{prevMon.title()}') + 1
        idx = self._handleEndif(idx)
        self.insertBlankLine(idx)
        self.set_line(idx, f'extern const u32 gMonBackPic_{species.title()}[];\n')

        # palette
        idx = self.findLine(f'gMonPalette_{prevMon.title()}') + 1
        idx = self._handleEndif(idx)
        self.insertBlankLine(idx)
        self.set_line(idx, f'extern const u32 gMonPalette_{species.title()}[];\n')

        # shiny palette
        idx = self.findLine(f'gMonShinyPalette_{prevMon.title()}') + 1
        idx = self._handleEndif(idx)
        self.insertBlankLine(idx)
        self.set_line(idx, f'extern const u32 gMonShinyPalette_{species.title()}[];\n')

        # icon
        idx = self.findLine(f'gMonIcon_{prevMon.title()}') + 1
        idx = self._handleEndif(idx)
        self.insertBlankLine(idx)
        self.set_line(idx, f'extern const u8 gMonIcon_{species.title()}[];\n')

        #footprint
        idx = self.findLine(f'gMonFootprint_{prevMon.title()}') + 1
        idx = self._handleEndif(idx)
        self.insertBlankLine(idx)
        self.set_line(idx, f'extern const u8 gMonFootprint_{species.title()}[];\n')


class BackPicTableH(HeaderFile):
    def __init__(self, path: str):
        super().__init__(path)

    def appendData(self, species, prevMon):
        idx = self.findLine(f'{prevMon.upper()}') + 1
        idx = self._handleEndif(idx)
        self.insertBlankLine(idx)
        self.set_line(idx, f'    SPECIES_SPRITE({species.upper()}, gMonBackPic_{species.title()}),\n')

class FrontPicTableH(HeaderFile):
    def __init__(self, path: str):
        super().__init__(path)

    def appendData(self, species, prevMon):
        idx = self.findLine(f'{prevMon.upper()}') + 1
        idx = self._handleEndif(idx)
        self.insertBlankLine(idx)
        self.set_line(idx, f'    SPECIES_SPRITE({species.upper()}, gMonFrontPic_{species.title()}),\n')

class BackPicCoordinatesH(HeaderFile):
    def __init__(self, path: str):
        super().__init__(path)

    def appendData(self, prevMon, formated_back_pic_coordinates):
        idx = self.findLine(f'SPECIES_{prevMon.upper()}') + 1
        idx = self._handleEndif(idx)
        self.insertBlankLine(idx)
        self.set_line(idx, formated_back_pic_coordinates)

class FrontPicCoordinatesH(HeaderFile):
    def __init__(self, path: str):
        super().__init__(path)

    def appendData(self, prevMon, formated_front_pic_coordinates):
        idx = self.findLine(f'SPECIES_{prevMon.upper()}') + 1
        idx = self._handleEndif(idx)
        self.insertBlankLine(idx)
        self.set_line(idx, formated_front_pic_coordinates)

class FrontPicAnimsH(HeaderFile):
    def __init__(self, path: str):
        super().__init__(path)

    def appendData(self, species, prevMon, formated_front_pic_anim):
        # anim table
        idx = self.findLine("};", self.findLine(f'sAnim_{prevMon.title()}_1')) + 1
        idx = self._handleEndif(idx)
        self.insertBlankLine(idx)
        self.set_line(idx, formated_front_pic_anim)

        # single anim
        idx = self.findLine(f'SINGLE_ANIMATION({prevMon.title()})') + 1
        idx = self._handleEndif(idx)
        self.insertBlankLine(idx)
        self.set_line(idx, f'SINGLE_ANIMATION({species.title()});\n')

        # front anims ptr table
        idx = self.findLine(f'SPECIES_{prevMon.upper()}') + 1
        idx = self._handleEndif(idx)
        self.insertBlankLine(idx)
        self.set_line(idx, f'    [SPECIES_{species.upper()}]'.ljust(26) + f'= sAnims_{species.title()},\n')

class FootprintTableH(HeaderFile):
    def __init__(self, path: str):
        super().__init__(path)

    def appendData(self, species, prevMon):
        idx = self.findLine(f'SPECIES_EGG') - 1 # not happy with this
        idx = self._handleEndif(idx)
        self.insertBlankLine(idx)
        self.set_line(idx, f'    [SPECIES_{species.upper()}] = gMonFootprint_{species.title()},\n')

class PaletteTableH(HeaderFile):
    def __init__(self, path: str):
        super().__init__(path)

    def appendData(self, species, prevMon):
        idx = self.findLine(f'{prevMon.upper()}') + 1
        idx = self._handleEndif(idx)
        self.insertBlankLine(idx)
        self.set_line(idx, f'    SPECIES_PAL({species.upper()}, gMonPalette_{species.title()}),\n')

class ShinyPaletteTableH(HeaderFile):
    def __init__(self, path: str):
        super().__init__(path)

    def appendData(self, species, prevMon):
        idx = self.findLine(f'{prevMon.upper()}') + 1
        idx = self._handleEndif(idx)
        self.insertBlankLine(idx)
        self.set_line(idx, f'    SPECIES_SHINY_PAL({species.upper()}, gMonShinyPalette_{species.title()}),\n')

class PokemonH(HeaderFile):
    def __init__(self, path: str):
        super().__init__(path)

    def appendData(self, species: str, prevMon: str = "BULBASAUR"):
        # front pic
        idx = self.findLine(f'gMonFrontPic_{prevMon.title()}') + 1
        idx = self._handleEndif(idx)
        self.insertBlankLine(idx)
        self.set_line(idx, f'const u32 gMonFrontPic_{species.title()}[] = INCBIN_U32(\"graphics/pokemon/{species.casefold()}/anim_front.4bpp.lz\");\n')

        # back pic
        idx = self.findLine(f'gMonBackPic_{prevMon.title()}') + 1
        idx = self._handleEndif(idx)
        self.insertBlankLine(idx)
        self.set_line(idx, f'const u32 gMonBackPic_{species.title()}[] = INCBIN_U32(\"graphics/pokemon/{species.casefold()}/back.4bpp.lz\");\n')

        # palette
        idx = self.findLine(f'gMonPalette_{prevMon.title()}') + 1
        idx = self._handleEndif(idx)
        self.insertBlankLine(idx)
        self.set_line(idx, f'const u32 gMonPalette_{species.title()}[] = INCBIN_U32(\"graphics/pokemon/{species.casefold()}/normal.gbapal.lz\");\n')

        # shiny palette
        idx = self.findLine(f'gMonShinyPalette_{prevMon.title()}') + 1
        idx = self._handleEndif(idx)
        self.insertBlankLine(idx)
        self.set_line(idx, f'const u32 gMonShinyPalette_{species.title()}[] = INCBIN_U32(\"graphics/pokemon/{species.casefold()}/shiny.gbapal.lz\");\n')

        # icon
        idx = self.findLine(f'gMonIcon_{prevMon.title()}') + 1
        idx = self._handleEndif(idx)
        self.insertBlankLine(idx)
        self.set_line(idx, f'const u8 gMonIcon_{species.title()}[] = INCBIN_U8(\"graphics/pokemon/{species.casefold()}/icon.4bpp\");\n')

        #footprint
        idx = self.findLine(f'gMonFootprint_{prevMon.title()}') + 1
        idx = self._handleEndif(idx)
        self.insertBlankLine(idx)
        self.set_line(idx, f'const u8 gMonFootprint_{species.title()}[] = INCBIN_U8(\"graphics/pokemon/{species.casefold()}/footprint.1bpp\");\n')

class LevelUpLearnsetsH(HeaderFile):
    def __init__(self, path: str):
        super().__init__(path)

    def appendData(self, formated_level_up_learnset: str, prevMon: str = "BULBASAUR"):
        idx = self.findLine("};", self.findLine(f's{prevMon.title()}LevelUpLearnset')) + 1
        idx = self._handleEndif(idx)
        self.insertBlankLine(idx)
        self.set_line(idx, formated_level_up_learnset)

class LevelUpLearnsetPointersH(HeaderFile):
    def __init__(self, path: str):
        super().__init__(path)

    def appendData(self, species: str, prevMon: str):
        idx = self.findLine(f'SPECIES_{prevMon.upper()}')
        idx = self._handleEndif(idx)
        self.insertBlankLine(idx)
        self.set_line(idx, f'    [SPECIES_{species.upper()}] = s{species.title()}LevelUpLearnset,\n')

class TeachableLearnsetH(HeaderFile):
    def __init__(self, path: str):
        super().__init__(path)

    def appendData(self, formated_teachable_learnset: str, prevMon: str = "BULBASAUR"):
        idx = self.findLine("};", self.findLine(f's{prevMon.title()}TeachableLearnset')) + 1
        idx = self._handleEndif(idx)
        self.insertBlankLine(idx)
        self.set_line(idx, formated_teachable_learnset)

class TeachableLearnsetPointersH(HeaderFile):
    def __init__(self, path: str):
        super().__init__(path)

    def appendData(self, species: str, prevMon: str):
        idx = self.findLine(f'SPECIES_{prevMon.upper()}') + 1
        idx = self._handleEndif(idx)
        self.insertBlankLine(idx)
        self.set_line(idx, f'    [SPECIES_{species.upper()}] = s{species.title()}TeachableLearnset,\n')

class EggMovesH(HeaderFile):
    def __init__(self, path: str):
        super().__init__(path)

    def appendData(self, formated_egg_learnset: str, prevMon: str):
        # not all mons have egg moves defined
        start = self.findLine(f'egg_moves({prevMon.upper()},')
        if start < 0:
            # append to the end
            idx = self.findLine("EGG_MOVES_TERMINATOR", self.findLine("gEggMoves")) - 1
            self.insertBlankLine(idx)
            idx += 1
        else:
            # append after prev mon
            idx = self.findLine("),", start) + 1

        idx = self._handleEndif(idx)
        self.insertBlankLine(idx)
        self.set_line(idx, formated_egg_learnset)

############################
# Source Files pokeemerald #
############################

class PokemonC(SourceFile):
    def __init__(self, path: str):
        super().__init__(path)

    def appendData(self, species: str, prevMon: str, animation: str = 'ANIM_V_SQUISH_AND_BOUNCE'): # pain
        # species to national pokedex
        idx = self.findLine(f'SPECIES_TO_NATIONAL({prevMon.upper()}),') + 1
        idx = self._handleEndif(idx)
        self.insertBlankLine(idx)
        self.set_line(idx, f'    SPECIES_TO_NATIONAL({species.upper()}),\n')

        # front anim table
        idx = self.findLine(f'SPECIES_{prevMon.upper()} - 1') + 1
        idx = self._handleEndif(idx)
        self.insertBlankLine(idx)
        self.set_line(idx, f'    [SPECIES_{species.upper()} - 1]'.ljust(32) + f'= {animation.upper()},\n')

class PokemonIconC(SourceFile):
    def __init__(self, path: str):
        super().__init__(path)

    def appendData(self, species: str, prevMon: str, paletteNum: int = 0):
        # icon table
        idx = self.findLine(f'SPECIES_{prevMon.upper()}', self.findLine('gMonIconTable')) + 1
        idx = self._handleEndif(idx)
        self.insertBlankLine(idx)
        self.set_line(idx, f'    [SPECIES_{species.upper()}] = gMonIcon_{species.title()},\n')

        # palette indices
        idx = self.findLine(f'SPECIES_{prevMon.upper()}', self.findLine('gMonIconPaletteIndices')) + 1
        idx = self._handleEndif(idx)
        self.insertBlankLine(idx)
        self.set_line(idx, f'    [SPECIES_{species.upper()}] = {paletteNum},\n')

class PokemonAnimationC(SourceFile):
    def __init__(self, path: str):
        super().__init__(path)

    def appendData(self, species: str, prevMon: str, animation: str = 'BACK_ANIM_NONE'):
        start = self.findLine(f'SPECIES_{prevMon.upper()}')
        if start < 0:
            # prev mon not in list
            idx = self.findLine("};", self.findLine('sSpeciesToBackAnimSet[NUM_SPECIES]')) - 1
        else:
            idx = start + 1

        self._handleEndif(idx)
        self.insertBlankLine(idx)
        self.set_line(idx, f'    [SPECIES_{species.upper()}]'.ljust(43) + f'= {animation},\n')

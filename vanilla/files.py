import sys
import re
import json

from file_types import *
from vanilla.formated_strings import *

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
        self._species_info = self._file["species_info"]
        self._formatSpeciesInfo()

    def _initPokedex(self):
        self._pokedex_data = self._file["pokedex_data"]
        self._pokedex_text = self._file["pokedex_data"]["description"]
        self._formatPokedex()

    def _initEvolution(self):
        self.hasEvo = True if len(self._file["evolution_data"]) > 0 else False
        if self.hasEvo:
            self._evolution_data = self._file["evolution_data"]
            self._formatEvolution()

    def _initMoveData(self):
        self._level_up_learnset = self._file["level_up_learnset"]
        self._tmhm_learnset = self._file["tmhm_learnset"]
        self._tutor_learnset = self._file["tutor_learnset"]
        self._egg_learnset = self._file["egg_learnset"]
        self.hasEggMove = True if len(self._file["egg_learnset"]) > 0 else False
        self.hasTMHMMove = True if len(self._file["tmhm_learnset"]) > 0 else False
        self.hasTutorMove = True if len(self._file["tutor_learnset"]) > 0 else False
        self._formatLearnsets()

    def _initPicData(self):
        self.icon_pal_num = self._file["icon_pal_num"]
        self._back_pic_coordinates = self._file["back_pic_coordinates"]
        self._front_pic_coordinates = self._file["front_pic_coordinates"]
        self._formatPicCoordinates()

    def _initAnims(self):
        self._formatFrontPicAnims()

    def _formatSpeciesInfo(self):
        self.formated_species_info = formatSpeciesInfo(self.species, self._species_info)
    def _formatPokedex(self):
        self.formated_pokedex_data = formatPokedexData(self.species, self._pokedex_data)
        self.formated_pokedex_text = formatPokedexText(self.species, self._pokedex_text)
    def _formatEvolution(self):
        self.formated_evolution_data = formatEvolutionData(self.species, self._evolution_data)
    def _formatLearnsets(self):
        self.formated_level_up_learnset = formatLevelUplearnset(self.species, self._level_up_learnset)
        self.formated_tmhm_learnset = formatTMHMLearnset(self.species, self._tmhm_learnset)
        self.formated_tutor_learnset = formatTutorLearnset(self.species, self._tutor_learnset)
        self.formated_egg_learnset = formatEgglearnset(self.species, self._egg_learnset)
    def _formatPicCoordinates(self):
        self.formated_back_pic_coordinates = formatPicCoordinates(self.species, self._back_pic_coordinates)
        self.formated_front_pic_coordinates = formatPicCoordinates(self.species, self._front_pic_coordinates)
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
        self.eggIdx = self.findLine('#define SPECIES_EGG')
        match = re.search(r"#define\s+SPECIES_(\w+)\s+(\d+)", self.get_line(self.eggIdx-1))
        if match:
            self.prevSpecies = match.group(1)
            self.prevSpeciesNum = int(match.group(2))
        else:
            raise Error("previous species not found.")

    def appendData(self, species):
        self.insertBlankLine(self.eggIdx)
        self.set_line(self.eggIdx, f"#define SPECIES_{species.upper()} {self.prevSpeciesNum+1}\n")
        self.set_line(self.eggIdx+1, f'#define SPECIES_EGG {self.prevSpeciesNum+2}\n')
        if self.prevSpecies == "CHIMECHO":
            match = re.search(r"#define\s+SPECIES_(\w+)\s+(\d+)", self.get_line(self.eggIdx-2))
            if match:
                self.prevSpecies = match.group(1)
                self.prevSpeciesNum = int(match.group(2))
            else:
                raise Error("previous species not found.")

class SpeciesInfoH(HeaderFile):
    def __init__(self, path):
        super().__init__(path)

    def appendData(self, formated_species_info: str, prevMon: str = "BULBASAUR"):
        idx = self.findLine("    }", self.findLine(prevMon.upper()))
        if not ',' in self.get_line(idx):
            self.set_line(idx, "    },\n")
        idx += 1
        self.insertBlankLine(idx)
        self.set_line(idx, formated_species_info)

class SpeciesNamesH(HeaderFile):
    def __init__(self, path: str):
        super().__init__(path)

    def appendData(self, species, prevMon):
        idx = self.findLine(f'SPECIES_{prevMon.upper()}') + 1
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
        self.set_line(idx, f"#define NATIONAL_DEX_COUNT  NATIONAL_DEX_{species.upper()}\n")


class PokedexEntryH(HeaderFile):
    def __init__(self, path: str):
        super().__init__(path)

    def appendData(self, formated_pokedex_entry: str, prevMon: str = "BULBASAUR"):
        idx = self.findLine("},", self.findLine(prevMon.upper())) + 1
        self.insertBlankLine(idx)
        self.set_line(idx, formated_pokedex_entry)

class PokedexTextH(HeaderFile):
    def __init__(self, path: str):
        super().__init__(path)

    def appendData(self, formated_pokedex_text: str, prevMon: str = "BULBASAUR"):
        idx = self.findLine(");", self.findLine(prevMon.title())) + 1
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
        idx = self.findLine(self._findPrevMonByAlpha(species), self.findLine("gPokedexOrder_Alphabetical")) + 1
        self.insertBlankLine(idx)
        self.set_line(idx, f'    NATIONAL_DEX_{species.upper()},\n')

        # weigh
        idx = self.findLine(self._findPrevMonByWeight(speciesWeight), self.findLine("gPokedexOrder_Weight")) + 1
        self.insertBlankLine(idx)
        self.set_line(idx, f'    NATIONAL_DEX_{species.upper()},\n')

        # height
        idx = self.findLine(self._findPrevMonByHeight(speciesHeight), self.findLine("gPokedexOrder_Height")) + 1
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

        strings = [f'extern const u32 gMonFrontPic_{species.title()}[];\n',
                   f'extern const u32 gMonPalette_{species.title()}[];\n',
                   f'extern const u32 gMonBackPic_{species.title()}[];\n',
                   f'extern const u32 gMonShinyPalette_{species.title()}[];\n',
                   f'extern const u32 gMonStillFrontPic_{species.title()}[];\n',
                   f'extern const u8 gMonIcon_{species.title()}[];\n',
                   f'extern const u8 gMonFootprint_{species.title()}[];\n']

        idx = self.findLine(f'gMonFootprint_{prevMon.title()}') + 1

        for string in strings:
            self.insertBlankLine(idx)
            self.set_line(idx, string)
            idx += 1

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

class StillFrontPicTableH(HeaderFile):
    def __init__(self, path: str):
        super().__init__(path)

    def appendData(self, species: str, prevMon: str):
        idx = self.findLine(f'SPECIES_SPRITE({prevMon.upper()},') + 1
        self.insertBlankLine(idx)
        self.set_line(idx, f'    SPECIES_SPRITE({species.upper()},'.ljust(34) + f'gMonStillFrontPic_{species.title()}),\n')

class FrontPicAnimsH(HeaderFile):
    def __init__(self, path: str):
        super().__init__(path)

    def appendData(self, species, prevMon, formated_front_pic_anim):
        # anim table
        idx = self.findLine("};", self.findLine(f'sAnim_{prevMon.title()}_1')) + 1
        if self.findLine(f'sAnim_{prevMon.title()}_2', idx) > -1:
            idx = self.findLine("};", self.findLine(f'sAnim_{prevMon.title()}_2')) + 1
        self.insertBlankLine(idx)
        self.set_line(idx, formated_front_pic_anim)

        # single anim
        idx = self.findLine(f'_ANIMATION({prevMon.title()})') + 1
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
        idx = self.findLine(f'SPECIES_{prevMon.upper()}') + 1
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

        strings = [f'const u32 gMonStillFrontPic_{species.title()}[] = INCBIN_U32(\"graphics/pokemon/{species.casefold()}/front.4bpp.lz\");\n',
                   f'const u32 gMonPalette_{species.title()}[] = INCBIN_U32(\"graphics/pokemon/{species.casefold()}/normal.gbapal.lz\");\n',
                   f'const u32 gMonBackPic_{species.title()}[] = INCBIN_U32(\"graphics/pokemon/{species.casefold()}/back.4bpp.lz\");\n',
                   f'const u32 gMonShinyPalette_{species.title()}[] = INCBIN_U32(\"graphics/pokemon/{species.casefold()}/shiny.gbapal.lz\");\n',
                   f'const u8 gMonIcon_{species.title()}[] = INCBIN_U8(\"graphics/pokemon/{species.casefold()}/icon.4bpp\");\n',
                   f'const u8 gMonFootprint_{species.title()}[] = INCBIN_U8(\"graphics/pokemon/{species.casefold()}/footprint.1bpp\");\n']

        idx = self.findLine(f'gMonFootprint_{prevMon.title()}') + 1
        self.insertBlankLine(idx)
        idx += 1

        for string in strings:
            self.insertBlankLine(idx)
            self.set_line(idx, string)
            idx += 1

class LevelUpLearnsetsH(HeaderFile):
    def __init__(self, path: str):
        super().__init__(path)

    def appendData(self, formated_level_up_learnset: str, prevMon: str = "BULBASAUR"):
        idx = self.findLine("};", self.findLine(f's{prevMon.title()}LevelUpLearnset')) + 1
        self.insertBlankLine(idx)
        self.set_line(idx, formated_level_up_learnset)

class LevelUpLearnsetPointersH(HeaderFile):
    def __init__(self, path: str):
        super().__init__(path)

    def appendData(self, species: str, prevMon: str):
        idx = self.findLine(f'SPECIES_{prevMon.upper()}')
        self.insertBlankLine(idx)
        self.set_line(idx, f'    [SPECIES_{species.upper()}] = s{species.title()}LevelUpLearnset,\n')

class TMHMLearnsetH(HeaderFile):
    def __init__(self, path: str):
        super().__init__(path)

    def appendData(self, formated_tmhm_learnset: str, species: str, prevMon: str):
        idx = self.findLine("),", self.findLine(f'SPECIES_{prevMon.upper()}')) + 1
        self.insertBlankLine(idx)
        self.set_line(idx, formated_tmhm_learnset)

class TutorLearnsetH(HeaderFile):
    def __init__(self, path: str):
        super().__init__(path)

    def appendData(self, formated_tutor_learnset: str, species: str, prevMon: str):
        idx = self.findLine("),", self.findLine(f'SPECIES_{prevMon.upper()}')) + 1
        self.insertBlankLine(idx)
        self.set_line(idx, formated_tutor_learnset)

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
        self.set_line(idx, f'    [SPECIES_{species.upper()} - 1]'.ljust(30) + f'= {animation.upper()},\n')

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
        self.set_line(idx, f'    [SPECIES_{species.upper()}]'.ljust(25) + f'= {animation},\n')

class AnimMonFrontPicsC(SourceFile):
    def __init__(self, path):
        super().__init__(path)

    def appendData(self, species: str, prevMon: str):
        idx = self.findLine(f'gMonFrontPic_{prevMon.title()}') + 1
        self.insertBlankLine(idx)
        self.set_line(idx, f'const u32 gMonFrontPic_{species.title()}[] = INCBIN_U32("graphics/pokemon/{species.casefold()}/anim_front.4bpp.lz");\n')


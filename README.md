# porymon

## What is porymon?

Porymon is a simple tool that allows users to add new Pokemon to their [pokeemerald-expansion](https://github.com/rh-hideout/pokeemerald-expansion) projects, without having to edit 24(!) different files themselves.
At the moment porymon is no more than a simple Python script that can be run locally, but I hope to turn it into a full application eventually.
Please note that porymon does **NOT** work with [vanilla pokeemerald](https://github.com/pret/pokeemerald) currently and might not work with older version of the expansion. Please refer to the **Limitations** below for more information.

## How to use porymon

To use porymon simply download it from the release page and follow the instructions below.

- Extract the porymon folder inside anywhere to you PC.
- Navigate inside the porymon folder and open the `config.json`.
- Replace the current path with your own path to the pokeemerald-expansion.
    - please not that you destination folder might be named differently. Please use whatever your root directory. It is the one that contains the makefile.
    - os specific path separators matter! use the correct one.
- Create a new folder and name it after your new pokemon.
- Copy the `pokemon_data.json` from the example folder `potato` into your newly created folder and fill out all the information inside of it.
    - most of these things should be self explanatory, however make sure to use the proper macros or literals where ever necessary.
    - E.g. to assign the move "Growl" to a movepool use either `MOVE_GROWL` or `45`. I advice to use the macros however.
- Move the assets for front pic, back pic, icon and footprints into the same folder and name them as follows:
    - front pic : `front_anim.png`
    - back pic  : `back.png`
    - icon      : `icon.png`
    - footprint : `footprint.png`
    - porymon does **not** support inserting cries at the moment
- Also move your palettes into the same folder and name them as follows:
    - normal pal : `normal.pal`
    - shiny pal  : `shiny.pal`
- Open a terminal and navigate into your porymon directory.
- Run `python3 porymon.py 'pokemonname'` and replace 'pokemonname' with whatever you named your folder.
    - to test the program you may insert the example pokemon `potato`. simply run `python3 porymon.py potato` from inside your porymon directory.
    - depending on your python version or system setting try `python porymon.py 'pokemonname'` or `py porymon.py 'pokemonname'`. To use a specific version of python run `py -'version' porymon.py 'pokemonname'`
- After porymon has edited all the necessary files it will prompt you with an option to restore all files to the state they were when porymon first loaded them. I encourage you to test all changes before committing to them.

## Limitations

The current implementation of porymon is very much a work-in-progress and has several limitations that I hope to overcome eventually.

- No compatability with vanilla pokeemerald or modified/outdated version
    - due to drastic differences between a vanilla pokeemerald project and an expansion project, porymon will not work with vanilla projects at the moment. I developed it for the expansion since that is what I use personally and for the debugging and testing features it provides.
    - I hope to eventually support vanilla pokeemerald aswell but for now it will stay expansion only as I address more important matters
    - Similarly, any project that differs substantially from an up-to-date expansion project *might* not work. If in doubt, try it and see if it works.
    - Porymon was designed with customizability in mind. If you want to adapt it feel free to do so.

- Porymon does **not** check the sanity of the provided data.
    - At its core porymon is a simple "copy-paste" tool. Its primary goal is to reduce the pure writing effort. In its current form it will take any input you give it and place it into the files blindly.
    - This is something I want to add simple checks for to mitigate user errors.

- It is not possible to *correct* a pokemon after the fact from within porymon
    - Porymon will not work if the pokemon is already defined.
    - Of course you are free to edit the data "manually" at any point
    - If you have not yet accepted the changes after running porymon you may still choose to restore all files and adjust `pokemon_data.json` or your assets and then run porymon again

- Porymon is a pure Python script, meaning it has no fancy UI
    - Adding an intuitive GUI is what I aim for eventually but it is by no means a priority.
    - This obviously means that it requires Python to run

- Only "regular" pokemon can be added with porymon. No forms.
    - The expansion has a form system for regional forms or megas. Since they differ slightly from regular Pokemon it is not yet possible to add these with porymon.
    - This is on the TODO

- Anything regarding animations can not be specified in `pokemon_data.json` at the moment
    - Placeholder/Standard animations are still being added and can be modified after the fact

- Only `front_anim.png` formated front sprites. regular `front.png` may follow

- No Cry insertion.
    - eventually

- The alphabetical order in the pokedex is slightly incorrect. Will be fixed eventually.

## How can I contribute?

If you want to contribute to porymon in any way, please do so here on GitHub. Either through opening issues or making pull requests.

## SUPER IMPORTANT INFORMATION

Please note that this is my first own application and therfore probably ... **not groundbreaking**...
Porymon is a learning opportunity for me and I treat it as such. If you think certain things arent done properly feel free to offer *constructive criticism*.

At the same time it is a project I do in my free time. Should porymon ever be out of date or broken in any other form please let me know but dont expect it to be addressed immediately (or at all). I might loose interest, not have time available or move on entirely. Should I ever go MIA I am fine with anyone picking up where I left of and keep developing porymon.



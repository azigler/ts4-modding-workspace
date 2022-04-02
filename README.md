![](https://user-images.githubusercontent.com/7295363/160976635-1ca3a6ce-43b6-47c2-98e3-71d0fcb8e11f.png)

# ts4-modding-workspace

> :hammer_and_wrench: Scripting workspace for modding The Sims 4

## Features

This repository is designed to bootstrap your scripting process when making mods for The Sims 4. If you don't know where to start or can't seem to get your script files organized, check out this repository. It's designed as a boilerplate for you to customize for your own modding process. It provides the following:

- **Utility mods** (to be compiled and used as neded):
  - `hello_world`: example mod
    - `example_script.py`: includes a `hello_world` command and an example injection with a notification
    - `injector.py`: this mod's symlink to `./Utilities/injector.py`
  - `hotreload`: includes commands for reloading your `*.py` and `*.xml` files without restarting the game
    - `script_reloader.py`: hotreloads the specified `*.py` file (e.g., `r.script hello_world example_script`)
    - `settings.py`: this mod's symlink to `./Utilities/injector.py`
    - `xml_reloader.py`: hotreloads the `*.xml` file configured in `xml_reloader.py` (e.g., `r.xml`)
- **Bash scripts** (to be run with `./Scripts` as the `cwd`):
  - `compile.sh`: compiles the specified mod and puts the `*.ts4script` file in your Mods folder
    - *Example:* `sh ./compile.sh hotreload`
  - `decompile.sh`: decompiles The Sims 4 source code
    - *Example:* `sh ./decompile.sh`
- **Utility scripts** (to be [symlinked](https://www.google.com/search?q=how+to+make+a+symlink) into your mod folders/files as needed):
  - `get_dir.py`: easily fetch the directory of your mod, helpful for working with files your mod might generate or use
  - `injector.py`: inject your scripts into pre-existing game code (learn how to use [here](https://modthesims.info/showthread.php?p=4751246#post4751246) and see `@inject_to` in `./Mods/hello_world/example_script.py` for reference)

## Instructions

- Install Python 3.7.* (e.g., Python 3.7.12)
  - You may already have `python3` installed but it must be version 3.7.*! You can check with `python3 -V`.
- [Symlink](https://www.google.com/search?q=how+to+make+a+symlink) the `python3` executable into your `ts4-modding-workspace` folder as `python3`
  - *Example:* `ln -s /usr/local/Cellar/python@3.7/3.7.12_1/Frameworks/Python.framework/Versions/3.7/bin/python3.7 /ts4-modding-workspace/python3`
  - *Tip:* You can confirm the version on the local symlink with `./python3 -V`.
- Edit `./Utilities/settings.py` to point to the corresponding folders on your computer.
  - *Tip:* The included directories are from OSX, yours may vary!

## Notes

- Don't use capital letters in mod folder or file names.
- Have ideas for improving the workspace? Fork and submit a PR back to the repository!
- Instead of duplicating your shared files, have one single source and [symlink](https://www.google.com/search?q=how+to+make+a+symlink) all references (e.g., `ln -s /path/to/original /path/to/link`)

## Acknowledgments

This repository was made possible by:

- [LOT51](https://lot51.cc/)
- [Scumbumbo](https://scumbumbomods.com/)
- [thepancake1 and MizoreYukii](https://www.patreon.com/pancakemizore)
- [Deaderpool](https://deaderpool-mccc.com/)

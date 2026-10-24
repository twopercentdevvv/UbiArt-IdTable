# UbiArt-IdTable
A tool (that works properly) to generate idtable.idt for any UbiArt game.

## How to use

if you don’t know what this is for, you probably don’t need it

Put the script in the directory with your `.ipk` files and run it:

```bash
python main.py
```

Or pass a path to the folder:

```bash
python main.py /path/to/ipks
```

## Notes
- This might not work on some games (like Just Dance 2014), as there is a unknown hash which I can’t seem to reverse-engineer (*0x7BA83698*).
- The files are added in alphabetical order, each using their own bundle number (except for base game bundles). 
- If you’re working with other UbiArt games and you have issues, you can open an issue in the repo.

## Credits
- [wukko](https://github.com/wukko) for his original [generateIDTable.py](https://github.com/wukko/ubiart-id-table/blob/main/generateIDTable.py)
- [Eliott](https://github.com/MZommer) for [UbiArtPY](https://github.com/MZommer/UbiArtPY/tree/dev/UbiArtPY) (My code is based on his StringID implementation and Platforms list)
# mc_migration_tool

Unofficial Minecraft migration tool from Bedrock edition to Java edition.

## Notice

Depends on non-commercial purpose only libraries.

- <https://github.com/Amulet-Team/Amulet-NBT>
- <https://github.com/Amulet-Team/Amulet-LevelDB>


## Usage

- Python 3.10

```shell
python3 -m venv venv
source venv/bin/activate

pip3 install -r requirements.txt

python3 main.py extract_player_server_keys "/path/to/world/db"
python3 main.py players_ender_chest "/path/to/world/db"
```

- Bedrock level format reference: <https://minecraft.fandom.com/wiki/Bedrock_Edition_level_format>

## Add dependency

Add dependency to `requirements.in` and execute `pip-compile` (`pip3 install pip-tools`).

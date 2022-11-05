from leveldb import LevelDB
import amulet_nbt
from amulet_nbt import utf8_escape_decoder
from pathlib import Path


def extract_keys(args):
  db_path = args.db_path
  output_path = Path(args.output_path)

  if output_path.exists():
    raise Exception('File exists')

  db = LevelDB(db_path)
  keys = list(db.keys())

  # FIXME: UnicodeDecodeError
  key_str_list = list(map(lambda key: key.decode('utf-8'), keys))

  keys_text = '\n'.join(key_str_list) + '\n'

  if output_path.exists():
    raise Exception('File exists')

  output_path.write_text(keys_text, encoding='utf-8')


def extract_player_server_keys(args):
  db_path = args.db_path
  output_path = Path(args.output_path)

  if output_path.exists():
    raise Exception('File exists')

  db = LevelDB(db_path)
  keys = list(db.keys())

  player_server_key_list = list(filter(lambda key: key.startswith(b'player_server_'), keys))
  player_server_key_str_list = list(map(lambda key: key.decode('utf-8'), player_server_key_list))

  player_server_keys_text = '\n'.join(player_server_key_str_list) + '\n'

  if output_path.exists():
    raise Exception('File exists')

  output_path.write_text(player_server_keys_text, encoding='utf-8')


def print_players_ender_chest(args):
  db_path = args.db_path
  input_path = Path(args.input_path)
  
  db = LevelDB(db_path)
  player_key_str_list = input_path.read_text(encoding='utf-8').splitlines()
  player_key_list = list(map(lambda key: key.encode('utf-8'), player_key_str_list))

  for player_key in player_key_list:
    player_nbt = amulet_nbt.load(db.get(player_key), compressed=False, little_endian=True, string_decoder=utf8_escape_decoder)
    player = player_nbt.compound

    ender_chest_inventory = player['EnderChestInventory']
    for item_stack in ender_chest_inventory:
      line = f"{item_stack['Slot']}. {item_stack['Name']} x {item_stack['Count']}"
      line += f" (#{item_stack['Damage']})"
      if 'tag' in item_stack:
        line += f" ({item_stack['tag']})"
      print(line)


def main():
  import argparse
  parser = argparse.ArgumentParser()
  subparsers = parser.add_subparsers()
  subparser_extract_keys = subparsers.add_parser('extract_keys')
  subparser_extract_keys.add_argument('db_path', type=str)
  subparser_extract_keys.add_argument('-o', '--output_path', type=str, default='keys.txt')
  subparser_extract_keys.set_defaults(handler=extract_keys)

  subparser_extract_player_server_keys = subparsers.add_parser('extract_player_server_keys')
  subparser_extract_player_server_keys.add_argument('db_path', type=str)
  subparser_extract_player_server_keys.add_argument('-o', '--output_path', type=str, default='player_server_keys.txt')
  subparser_extract_player_server_keys.set_defaults(handler=extract_player_server_keys)

  subparser_players_ender_chest = subparsers.add_parser('players_ender_chest')
  subparser_players_ender_chest.add_argument('db_path', type=str)
  subparser_players_ender_chest.add_argument('-i', '--input_path', type=str, default='player_server_keys.txt')
  subparser_players_ender_chest.set_defaults(handler=print_players_ender_chest)

  args = parser.parse_args()
  if hasattr(args, 'handler'):
    args.handler(args)
  else:
    parser.print_help()


if __name__ == '__main__':
  main()

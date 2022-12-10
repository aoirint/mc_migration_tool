import sys
from leveldb import LevelDB
import amulet_nbt
from amulet_nbt import utf8_escape_decoder
from mutf8 import encode_modified_utf8
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import mc_migration_tool


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


def print_villagers(args):
  db_path = args.db_path

  db = LevelDB(db_path)
  for key in db.keys():
    try:
      nbt = amulet_nbt.load(db.get(key), compressed=False, little_endian=True, string_decoder=utf8_escape_decoder)
    except:
      continue

    # TAG_Compound: 10
    if nbt.tag.tag_id != 10:
      continue

    compound = nbt.compound

    identifier = str(compound.get_string('identifier')) if 'identifier' in compound else None
    if identifier != 'minecraft:villager_v2':
      continue

    villager = mc_migration_tool.bedrock.load_villager(compound)

    root = amulet_nbt._compound.CompoundTag()

    villager_data = amulet_nbt._compound.CompoundTag()

    # : Types
    java_villager_type_strings = [
      'plains',
      'desert',
      'jungle',
      'savanna',
      'snow',
      'swamp',
      'taiga',
    ]
    bedrock_villager_mark_variant = villager.mark_variant
    if len(java_villager_type_strings) <= bedrock_villager_mark_variant:
      raise Exception(f'Unknown Villager MarkVariant: {bedrock_villager_mark_variant}')
    villager_data['type'] = amulet_nbt._string.StringTag(java_villager_type_strings[bedrock_villager_mark_variant])

    # : Profession
    java_villager_profession_strings = [
      None,
      'farmer',
      'fisherman',
      'shepherd',
      'fletcher',
      'librarian',
      'cartographer',
      'cleric',
      'armorer',
      'weaponsmith',
      'toolsmith',
      'butcher',
      'leatherworker',
      'mason',
      'nitwit',
    ]
    bedrock_villager_preferred_profession = villager.preferred_profession
    if bedrock_villager_preferred_profession not in java_villager_profession_strings:
      raise Exception(f'Unknown Villager PreferredProfession: {bedrock_villager_preferred_profession}')
    villager_data['profession'] = amulet_nbt._string.StringTag(bedrock_villager_preferred_profession)

    # : Tier -> Level
    java_villager_level_ints = [
      1, # 0
      2, # 1 (spawn with profession)
      3, # 2
      4, # 3
      5, # 4 (highest)
    ]
    bedrock_villager_trade_tier = villager.trade_tier
    if len(java_villager_level_ints) <= bedrock_villager_trade_tier:
      raise Exception(f'Unknown Villager TradeTier: {bedrock_villager_trade_tier}')
    villager_data['level'] = amulet_nbt._int.IntTag(java_villager_level_ints[bedrock_villager_trade_tier])

    if villager.offers is None:
      continue

    # TODO: item id mappings
    offers = amulet_nbt._compound.CompoundTag()
    recipes = amulet_nbt._list.ListTag()
    for _recipe in villager.offers.recipes:
      recipe = amulet_nbt._compound.CompoundTag()

      # TODO: Enchantment support
      buy = amulet_nbt._compound.CompoundTag()
      buy['id'] = amulet_nbt._string.StringTag(_recipe.buy_a.name)
      buy['Count'] = amulet_nbt._int.IntTag(_recipe.buy_a.count)
      buy['Damage'] = amulet_nbt._int.IntTag(_recipe.buy_a.damage)
      recipe['buy'] = buy

      sell = amulet_nbt._compound.CompoundTag()
      sell['id'] = amulet_nbt._string.StringTag(_recipe.sell.name)
      sell['Count'] = amulet_nbt._int.IntTag(_recipe.sell.count)
      sell['Damage'] = amulet_nbt._int.IntTag(_recipe.sell.damage)
      recipe['sell'] = sell

      recipe['rewardExp'] = amulet_nbt._int.ByteTag(_recipe.reward_exp)
      recipe['maxUses'] = amulet_nbt._int.IntTag(_recipe.max_uses)
      recipes.append(recipe)

    offers['Recipes'] = recipes

    villager_data['Offers'] = offers

    root['VillagerData'] = villager_data

    print(villager, file=sys.stderr)
    print(' '.join([
      '/summon',
      'villager',
      f'{villager.pos.x:.0f}',
      f'{villager.pos.y:.0f}',
      f'{villager.pos.z:.0f}',
      root.to_snbt(),
    ]))


def main():
  import argparse
  parser = argparse.ArgumentParser()
  subparsers = parser.add_subparsers()
  subparser_extract_player_server_keys = subparsers.add_parser('extract_player_server_keys')
  subparser_extract_player_server_keys.add_argument('db_path', type=str)
  subparser_extract_player_server_keys.add_argument('-o', '--output_path', type=str, default='player_server_keys.txt')
  subparser_extract_player_server_keys.set_defaults(handler=extract_player_server_keys)

  subparser_players_ender_chest = subparsers.add_parser('players_ender_chest')
  subparser_players_ender_chest.add_argument('db_path', type=str)
  subparser_players_ender_chest.add_argument('-i', '--input_path', type=str, default='player_server_keys.txt')
  subparser_players_ender_chest.set_defaults(handler=print_players_ender_chest)

  subparser_villagers = subparsers.add_parser('villagers')
  subparser_villagers.add_argument('db_path', type=str)
  subparser_villagers.set_defaults(handler=print_villagers)

  args = parser.parse_args()
  if hasattr(args, 'handler'):
    args.handler(args)
  else:
    parser.print_help()


if __name__ == '__main__':
  main()

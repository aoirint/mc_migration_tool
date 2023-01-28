import amulet_nbt
from dataclasses import dataclass
from typing import Optional


@dataclass
class BedrockRecipeItemTagEnchItem:
  id: int
  lvl: int

@dataclass
class BedrockRecipeItemTag:
  ench: Optional[list[BedrockRecipeItemTagEnchItem]]

@dataclass
class BedrockRecipeItem:
  count: int
  damage: int
  name: str
  was_picked_up: int
  tag: Optional[BedrockRecipeItemTag]


@dataclass
class BedrockRecipe:
  buy_a: BedrockRecipeItem
  buy_b: Optional[BedrockRecipeItem]
  sell: BedrockRecipeItem
  buy_count_a: int
  buy_count_b: int
  demand: int
  max_uses: int
  price_multiplier_a: float
  price_multiplier_b: float
  reward_exp: int
  tier: int
  trader_exp: int
  uses: int


@dataclass
class BedrockOffers:
  recipes: list[BedrockRecipe]
  tier_exp_requirements: list[dict[str, int]]


BedrockTierExpRequirement = dict[str, int]


def __load_recipe_item_tag_ench_item(compound: amulet_nbt._compound.CompoundTag) -> BedrockRecipeItemTagEnchItem:
  return BedrockRecipeItemTagEnchItem(
    id=compound.get_short('id'),
    lvl=compound.get_short('lvl'),
  )

def __load_recipe_item_tag(compound: amulet_nbt._compound.CompoundTag) -> BedrockRecipeItemTag:
  ench_list = compound.get_list('ench') if 'ench' in compound else None
  ench_items = None
  if ench_list is not None:
    ench_items = []

    for ench_index in range(len(ench_list)):
      ench_item_compound = ench_list.get_compound(ench_index)
      ench_item = __load_recipe_item_tag_ench_item(ench_item_compound)
      ench_items.append(ench_item)
  
  return BedrockRecipeItemTag(
    ench=ench_items,
  )

def __load_recipe_item(compound: amulet_nbt._compound.CompoundTag) -> BedrockRecipeItem:
  tag_compound = compound.get_compound('tag') if 'tag' in compound else None
  tag = __load_recipe_item_tag(tag_compound) if tag_compound is not None else None

  return BedrockRecipeItem(
    count=int(compound.get_byte('Count')),
    damage=int(compound.get_short('Damage')),
    name=str(compound.get_string('Name')),
    was_picked_up=int(compound.get_byte('WasPickedUp')),
    tag=tag,
  )


def __load_recipe(compound: amulet_nbt._compound.CompoundTag) -> BedrockRecipe:
  return BedrockRecipe(
    buy_a=__load_recipe_item(compound.get_compound('buyA')),
    buy_b=__load_recipe_item(compound.get_compound('buyB')) if 'buyB' in compound else None,
    sell=__load_recipe_item(compound.get_compound('sell')),
    buy_count_a=int(compound.get_int('buyCountA')),
    buy_count_b=int(compound.get_int('buyCountB')),
    demand=int(compound.get_int('demand')),
    max_uses=int(compound.get_int('maxUses')),
    price_multiplier_a=float(compound.get_float('priceMultiplierA')),
    price_multiplier_b=float(compound.get_float('priceMultiplierB')),
    reward_exp=int(compound.get_byte('rewardExp')),
    tier=int(compound.get_int('tier')),
    trader_exp=int(compound.get_int('traderExp')),
    uses=int(compound.get_int('uses')),
  )


def __load_recipes(list_tag: amulet_nbt._list.ListTag) -> list[BedrockRecipe]:
  ret: list[BedrockRecipe] = []
  for index in range(len(list_tag)):
    ret.append(__load_recipe(list_tag.get_compound(index)))
  return ret


def __load_tier_exp_requirements(list_tag: amulet_nbt._list.ListTag) -> list[BedrockRecipe]:
  ret: list[dict[str, int]] = []
  for index in range(len(list_tag)):
    compound = list_tag.get_compound(index)
    key = list(compound.keys())[0]
    ret.append({
      key: int(compound.get_int(key)),
    })
  return ret


def load_offers(compound: amulet_nbt._compound.CompoundTag) -> BedrockOffers:
  recipes = __load_recipes(compound.get_list('Recipes'))
  tier_exp_requirements = __load_tier_exp_requirements(compound.get_list('TierExpRequirements'))

  return BedrockOffers(
    recipes=recipes,
    tier_exp_requirements=tier_exp_requirements,
  )

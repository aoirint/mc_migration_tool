import amulet_nbt
from dataclasses import dataclass
from typing import Optional
from .offers import BedrockOffers, load_offers
from .pos import BedrockPos, load_pos


@dataclass
class BedrockVillager:
  offers: Optional[BedrockOffers]
  pos: BedrockPos
  tags: list[str]
  identifier: Optional[str]
  preferred_profession: Optional[str]
  skin_id: int
  variant: int
  mark_variant: int
  trade_tier: int
  trade_experience: int
  trade_table_path: Optional[str]


def __load_tags(list_tag: amulet_nbt._list.ListTag) -> list[str]:
  return [ str(string_tag) for string_tag in list_tag ]


def load_villager(compound: amulet_nbt._compound.CompoundTag) -> BedrockOffers:
  return BedrockVillager(
    offers=load_offers(compound.get_compound('Offers')) if 'Offers' in compound else None,
    pos=load_pos(compound.get_list('Pos')),
    tags=__load_tags(compound.get_list('Tags')),
    identifier=str(compound.get_string('identifier')) if 'identifier' in compound else None,
    preferred_profession=str(compound.get_string('PreferredProfession')) if 'PreferredProfession' in compound else None,
    skin_id=int(compound.get_int('SkinID')),
    variant=int(compound.get_int('Variant')),
    mark_variant=int(compound.get_int('MarkVariant')),
    trade_tier=int(compound.get_int('TradeTier')),
    trade_experience=int(compound.get_int('TradeExperience')),
    trade_table_path=str(compound.get_string('TradeTablePath')) if 'TradeTablePath' in compound else None,
  )

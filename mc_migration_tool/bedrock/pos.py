import amulet_nbt
from dataclasses import dataclass


@dataclass
class BedrockPos:
  x: float
  y: float
  z: float


def load_pos(list_tag: amulet_nbt._list.ListTag) -> BedrockPos:
  return BedrockPos(
    x=float(list_tag.get_float(0)),
    y=float(list_tag.get_float(1)),
    z=float(list_tag.get_float(2)),
  )

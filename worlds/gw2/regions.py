import enum
from typing import Optional

from .options import CharacterProfession
from .rules import Rule, has_heal_skill, has_full_build


class RegionEnum(enum.Enum):
    OPEN_WORLD = enum.auto()  #needs to be first
    STORY = enum.auto()
    FRACTAL = enum.auto()
    STRIKE_MISSION = enum.auto()
    DUNGEON = enum.auto()
    RAID = enum.auto()
    WVW = enum.auto()
    PVP = enum.auto()

group_content = {RegionEnum.FRACTAL, RegionEnum.DUNGEON, RegionEnum.STRIKE_MISSION, RegionEnum.RAID, RegionEnum.PVP}
ten_man_content = {RegionEnum.STRIKE_MISSION, RegionEnum.RAID}
competitive_content = {RegionEnum.PVP, RegionEnum.WVW}

def get_region_rule(region: RegionEnum, player: int, profession: Optional[CharacterProfession]) -> Optional[Rule]:
    if region == RegionEnum.OPEN_WORLD or region == RegionEnum.PVP:
        return None
    elif region == RegionEnum.STORY:
        return Rule(player, has_heal_skill)
    elif region in group_content or region == RegionEnum.WVW:
        return Rule(player, has_full_build, profession)

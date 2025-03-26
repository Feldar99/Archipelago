from Utils import parse_yaml
from . import data
from importlib.resources import files
from typing import Dict

from .storylines import storyline_from_str
from .types import MapType, Gw2ItemData, StorylineEnum

group_content = {MapType.FRACTAL, MapType.DUNGEON, MapType.STRIKE_MISSION, MapType.RAID, MapType.PVP}
ten_man_content = {MapType.STRIKE_MISSION, MapType.RAID}
competitive_content = {MapType.PVP, MapType.WVW}


class Map:
    id: int
    name: str
    type: MapType
    entrances: set[str]
    storylines: set[StorylineEnum]
    start: dict[StorylineEnum, str]
    item: Gw2ItemData


map_data: Dict[str, Map] = {}


def load_maps():
    with files(data).joinpath("Maps.yaml").open() as f:
        parsed_data = parse_yaml(f.read())
        for value in parsed_data:
            gw2_map = Map()
            gw2_map.id = value["id"]
            gw2_map.name = value["name"]
            gw2_map.type = value["type"]
            gw2_map.entrances = value["entrances"]

            type_str = value["type"].upper()
            if type_str == "OPEN WORLD" or type_str == "CITY" or type_str == "CONVERGENCE":
                gw2_map.type = MapType.OPEN_WORLD
            elif type_str == "STRIKE MISSION":
                gw2_map.type = MapType.STRIKE_MISSION
            elif type_str == "DRAGON RESPONSE MISSION":
                gw2_map.type = MapType.STORY
            else:
                gw2_map.type = MapType[type_str]

            gw2_map.storylines = set()
            for storyline in value["storylines"]:
                gw2_map.storylines.add(storyline_from_str(storyline))

            gw2_map.start = {}
            if "start" in value:
                for start in value["start"]:
                    storyline = storyline_from_str(start)
                    gw2_map.start[storyline] = value["start"][start]

            map_data[gw2_map.name] = gw2_map


load_maps()

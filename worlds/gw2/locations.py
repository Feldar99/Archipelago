import enum
from typing import Optional

from BaseClasses import Location
from .regions import MapType, Map, map_data
from .storylines import storyline_from_str

from Utils import parse_yaml
from importlib.resources import files


class Gw2Location(Location):
    game: str = "Guild Wars 2"


class LocationType(enum.Enum):
    ACHIEVEMENT = enum.auto(value=0)
    QUEST = enum.auto()
    TRAINING = enum.auto()
    WORLD_BOSS = enum.auto()
    UNIQUE_ITEM = enum.auto()
    POINT_OF_INTEREST = enum.auto()

    def get_valid_regions(self):
        if self == LocationType.ACHIEVEMENT:
            return list(MapType)
        elif self == LocationType.QUEST:
            return [MapType.STORY]
        else:
            return [MapType.OPEN_WORLD]

    @staticmethod
    def get_auto_generated():
        return [x for x in LocationType if x.value < LocationType.UNIQUE_ITEM.value]


class LocationData:
    type: LocationType
    map: Map
    code: int
    name: str

    next_id_val = 3_828_179_903_462_517  #selected at random between 0 and 2^53-1 to minimize chance of collision

    def __init__(self, type: LocationType, region: Optional[MapType] = None, gw2_map: Map = None, name_index: int = 0,
                 name: Optional[str] = None):
        self.type = type
        if region is None:
            region = gw2_map.type
        self.map = gw2_map
        self.code = LocationData.next_id_val
        if name == None:
            self.name = region.name + " " + type.name + " " + str(name_index)
        else:
            self.name = name
        LocationData.next_id_val += 1


location_table = {}
location_groups = {}  #dict[LocationType, dict[RegionEnum, list[LocationData]]]
storyline_items = {}  #dict[Storyline, list[LocationData]]
storyline_pois = {}  #dict[Storyline, list[LocationData]]


def create_locations():
    from . import data

    MINIMUM_LOCATION_COUNT = 300

    for location_type in LocationType:
        location_groups[location_type] = {}
        for region in MapType:
            location_groups[location_type][region] = []

    for i in range(MINIMUM_LOCATION_COUNT):
        for location_type in LocationType.get_auto_generated():
            for region in location_type.get_valid_regions():
                location_groups[location_type][region].append(LocationData(type=location_type,
                                                                           region=region, name_index=i))

    with files(data).joinpath("Items.yaml").open() as f:
        item_data = parse_yaml(f.read())
        for storyline_name in item_data:
            storyline_data = item_data[storyline_name]
            for map_name in storyline_data:
                yaml_map = storyline_data[map_name]
                gw2_map = map_data[map_name]
                for item in yaml_map:

                    location_data = LocationData(type=LocationType.UNIQUE_ITEM, gw2_map=gw2_map,
                                                 name="Item: " + item)
                    location_groups[LocationType.UNIQUE_ITEM][MapType.OPEN_WORLD].append(location_data)
                    for storyline in gw2_map.storylines:
                        if storyline.value not in storyline_items:
                            storyline_items[storyline.value] = []
                        storyline_items[storyline.value].append(location_data)

    with files(data).joinpath("Pois.yaml").open() as f:
        poi_data = parse_yaml(f.read())
        for map_name in poi_data:
            yaml_map = poi_data[map_name]
            gw2_map = map_data[map_name]
            for poi in yaml_map:
                location_data = LocationData(type=LocationType.POINT_OF_INTEREST, gw2_map=gw2_map,
                                             name="POI: " + poi)
                location_groups[LocationType.POINT_OF_INTEREST][MapType.OPEN_WORLD].append(location_data)
                for storyline in gw2_map.storylines:
                    if storyline.value not in storyline_pois:
                        storyline_pois[storyline.value] = []
                    storyline_pois[storyline.value].append(location_data)

    for location_type, data in location_groups.items():
        for region_type, locations in data.items():
            for location in locations:
                location_table[location.name] = location


create_locations()

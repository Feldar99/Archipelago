import enum

from BaseClasses import Location
from .regions import RegionEnum


class Gw2Location(Location):
    game: str = "Guild Wars 2"


class LocationType(enum.Enum):
    ACHIEVEMENT = enum.auto(value=0)
    QUEST = enum.auto()
    TRAINING = enum.auto()
    WORLD_BOSS = enum.auto()

    def get_valid_regions(self):
        if self == LocationType.ACHIEVEMENT:
            return list(RegionEnum)
        elif self == LocationType.QUEST:
            return [RegionEnum.STORY]
        elif self == LocationType.TRAINING:
            return [RegionEnum.OPEN_WORLD]
        elif self == LocationType.WORLD_BOSS:
            return [RegionEnum.OPEN_WORLD]


class LocationData:
    type: LocationType
    region: RegionEnum
    code: int
    name: str

    next_id_val = 3_828_179_903_462_517  #selected at random between 0 and 2^53-1 to minimize chance of collision

    def __init__(self, type: LocationType, region: RegionEnum, name_index: int):
        self.type = type
        self.region = region
        self.code = LocationData.next_id_val
        self.name = region.name + " " + type.name + " " + str(name_index)
        LocationData.next_id_val += 1


location_table = {}
location_groups = {}  #dict[LocationType, dict[RegionEnum, list[LocationData]]]


def create_locations():
    MINIMUM_LOCATION_COUNT = 150

    for location_type in LocationType:
        location_groups[location_type] = {}
        for region in RegionEnum:
            location_groups[location_type][region] = []

    for i in range(MINIMUM_LOCATION_COUNT):
        for location_type in LocationType:
            for region in location_type.get_valid_regions():
                location_groups[location_type][region].append(LocationData(type=location_type,
                                                                            region=region, name_index=i))

    for location_type, data in location_groups.items():
        for region_type, locations in data.items():
            for location in locations:
                location_table[location.name] = location


create_locations()

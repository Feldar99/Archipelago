import enum
from typing import Set, Optional


class Weapon(enum.Enum):
    AXE = enum.auto()
    DAGGER = enum.auto()
    MACE = enum.auto()
    PISTOL = enum.auto()
    SWORD = enum.auto()
    SCEPTER = enum.auto()
    FOCUS = enum.auto()
    SHIELD = enum.auto()
    TORCH = enum.auto()
    WARHORN = enum.auto()
    GREATSWORD = enum.auto()
    HAMMER = enum.auto()
    LONGBOW = enum.auto()
    RIFLE = enum.auto()
    SHORTBOW = enum.auto()
    STAFF = enum.auto()
    HARPOONGUN = enum.auto()
    SPEAR = enum.auto()
    TRIDENT = enum.auto()


class Profession(enum.Enum):
    WARRIOR = enum.auto()
    GUARDIAN = enum.auto()
    REVENANT = enum.auto()
    THIEF = enum.auto()
    ENGINEER = enum.auto()
    RANGER = enum.auto()
    MESMER = enum.auto()
    ELEMENTALIST = enum.auto()
    NECROMANCER = enum.auto()


class Race(enum.Enum):
    ASURA = enum.auto()
    CHARR = enum.auto()
    HUMAN = enum.auto()
    NORN = enum.auto()
    SYLVARI = enum.auto()


class MapType(enum.Enum):
    OPEN_WORLD = enum.auto()  #needs to be first
    STORY = enum.auto()
    FRACTAL = enum.auto()
    STRIKE_MISSION = enum.auto()
    DUNGEON = enum.auto()
    RAID = enum.auto()
    WVW = enum.auto()
    PVP = enum.auto()


class StorylineEnum(enum.Enum):
    CORE = enum.auto(value=0)
    SEASON_1 = enum.auto()
    SEASON_2 = enum.auto()
    HEART_OF_THORNS = enum.auto()
    SEASON_3 = enum.auto()
    PATH_OF_FIRE = enum.auto()
    SEASON_4 = enum.auto()
    ICEBROOD_SAGA = enum.auto()
    END_OF_DRAGONS = enum.auto()
    SECRETS_OF_THE_OBSCURE = enum.auto()
    JANTHIR_WILDS = enum.auto()
    VISIONS_OF_ETERNITY = enum.auto()


class Spec:
    profession: Profession
    elite_spec: Optional[str]

    def __init__(self, profession: Profession, elite_spec=None):
        self.profession = profession
        self.elite_spec = elite_spec


class Gw2ItemData:
    name: str
    code: int
    quantity: int
    specs: Optional[Set[Spec]]
    race: Optional[Race]
    storyline: Optional[StorylineEnum]

    next_id_val = 3_828_179_903_462_517  #selected at random between 0 and 2^53-1 to minimize chance of collision
